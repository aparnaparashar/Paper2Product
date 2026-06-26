"""
LLM helpers — all agents routed through Groq (free, no daily limits)
"""
import json
import re
import time
from datetime import datetime
from typing import Tuple

from app.core.config import get_settings

settings = get_settings()

# Groq free tier limits:
#   llama-3.3-70b-versatile : 6,000 TPM,  30 RPM
#   llama-3.1-8b-instant    : 20,000 TPM, 30 RPM
# We sleep 3s between agents to stay well under 30 RPM.
INTER_AGENT_SLEEP = 1


def get_llm(provider: str, model: str, temperature: float = 0.3):
    if provider == "groq":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            max_tokens=4096,
        )
    # fallback — also Groq
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        max_tokens=4096,
    )


def call_llm(chain, prompt_vars: dict):
    """
    Calls the chain with retry logic tuned for Groq:
    - 429 rate limit  → wait retry_delay from response then retry (up to 4x)
    - other errors    → 3 retries with short backoff
    """
    import re as _re

    last_error = None
    for attempt in range(4):
        try:
            time.sleep(INTER_AGENT_SLEEP)   # always pace requests
            return chain.invoke(prompt_vars)

        except Exception as e:
            err_str = str(e)
            last_error = e

            # Extract retry delay from Groq 429 message if present
            # e.g. "Please try again in 26.078s"
            if "429" in err_str or "rate_limit" in err_str.lower():
                match = _re.search(r"try again in ([\d.]+)s", err_str)
                wait = float(match.group(1)) + 2 if match else (attempt + 1) * 15
                print(f"[llm_helpers] Rate limited — waiting {wait:.0f}s (attempt {attempt+1}/4)")
                time.sleep(wait)
                continue

            # Other error — short backoff
            if attempt < 3:
                time.sleep(4 * (attempt + 1))
                continue

            raise

    raise last_error


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    from app.graph.state import PRICING
    p = PRICING.get(model, (0.0006, 0.0008))
    return round((prompt_tokens / 1000 * p[0]) + (completion_tokens / 1000 * p[1]), 6)


def run_agent(
    agent_name: str,
    provider: str,
    model: str,
    prompt_template,
    prompt_vars: dict,
    project_id: str,
    temperature: float = 0.3,
) -> Tuple[dict, dict]:
    from app.core.database import SessionLocal
    from app.models.agent_run import AgentRun
    from app.graph.state import AGENT_STEPS

    label = next((s[1] for s in AGENT_STEPS if s[0] == agent_name), agent_name)
    llm = get_llm(provider, model, temperature)
    chain = prompt_template | llm

    db = SessionLocal()
    run = AgentRun(
        project_id=project_id,
        agent_name=agent_name,
        agent_label=label,
        model_used=model,
        model_provider=provider,
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()

    start = time.time()
    try:
        result = call_llm(chain, prompt_vars)
        raw = parse_json(result.content)

        # Groq returns usage in response_metadata
        usage = getattr(result, "usage_metadata", None) or {}
        if not usage:
            usage = getattr(result, "response_metadata", {}).get("token_usage", {}) or {}
        pt = _tok(usage, "input_tokens", "prompt_tokens") or 0
        ct = _tok(usage, "output_tokens", "completion_tokens") or 0

        duration = round(time.time() - start, 2)
        cost = estimate_cost(model, pt, ct)

        reasoning  = raw.pop("reasoning", [])  if isinstance(raw, dict) else []
        confidence = raw.pop("confidence", None) if isinstance(raw, dict) else None
        sources    = raw.pop("sources", [])    if isinstance(raw, dict) else []

        metadata = {
            "agent_name": agent_name, "model": model, "provider": provider,
            "reasoning": reasoning, "confidence": confidence, "sources": sources,
            "duration_seconds": duration, "prompt_tokens": pt,
            "completion_tokens": ct, "total_tokens": pt + ct,
            "estimated_cost_usd": cost,
        }

        run.output = raw; run.reasoning = reasoning; run.confidence = confidence
        run.sources = sources; run.duration_seconds = duration
        run.prompt_tokens = pt; run.completion_tokens = ct
        run.total_tokens = pt + ct; run.estimated_cost_usd = cost
        run.status = "completed"; run.completed_at = datetime.utcnow()
        db.commit()

        return raw, metadata

    except Exception as e:
        run.status = "failed"
        run.error = str(e)[:500]
        run.duration_seconds = round(time.time() - start, 2)
        db.commit()
        raise
    finally:
        db.close()


def _tok(usage, *keys) -> int:
    for k in keys:
        v = usage.get(k, 0) if isinstance(usage, dict) else getattr(usage, k, 0)
        if v: return int(v)
    return 0


def parse_json(content: str) -> dict:
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content).strip()
    start = len(content)
    for ch in ["{", "["]:
        idx = content.find(ch)
        if idx != -1:
            start = min(start, idx)
    if start == len(content):
        return {"raw": content}
    end_ch = "}" if content[start] == "{" else "]"
    end = content.rfind(end_ch)
    if end == -1:
        return {"raw": content}
    try:
        return json.loads(content[start: end + 1])
    except json.JSONDecodeError:
        cleaned = re.sub(r",\s*([}\]])", r"\1", content[start: end + 1])
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw": content}


def trunc(text: str, max_chars: int = 9000) -> str:
    if len(text) <= max_chars:
        return text
    h = max_chars // 2
    return text[:h] + "\n\n[...truncated...]\n\n" + text[-h:]
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { CheckCircle, Circle, Loader2, XCircle } from "lucide-react";
import { projectsApi } from "../api/client";

// All 15 agents shown individually, mapped to the progress % at which they complete
const STEPS = [
  { key: "research_analyst",    label: "Research Analyst",        desc: "Extracting problem, novelty & methodology", upTo: 7 },
  { key: "technical_validator", label: "Technical Validator",     desc: "Scoring innovation & reproducibility",       upTo: 21 },
  { key: "market_discovery",    label: "Market Discovery",        desc: "Identifying markets & sizing opportunity",   upTo: 21 },
  { key: "customer_persona",    label: "Customer Personas",       desc: "Profiling buyers & stakeholders",            upTo: 35 },
  { key: "competitor_intel",    label: "Competitor Intelligence", desc: "Mapping competitive landscape",              upTo: 35 },
  { key: "knowledge_graph",     label: "Knowledge Graph",         desc: "Building concept entity map",                upTo: 35 },
  { key: "product_strategist",  label: "Product Strategist",      desc: "Generating product concepts",                upTo: 56 },
  { key: "risk_analyst",        label: "Risk Analyst",            desc: "Identifying all material risks",             upTo: 56 },
  { key: "investment_agent",    label: "Investment Agent",        desc: "VC scoring & funding path",                  upTo: 56 },
  { key: "mvp_planner",         label: "MVP Planner",             desc: "Defining smallest viable product",           upTo: 70 },
  { key: "architect",           label: "Technical Architect",     desc: "Designing system architecture",              upTo: 70 },
  { key: "revenue_strategy",    label: "Revenue Strategy",        desc: "Modelling pricing & business model",         upTo: 70 },
  { key: "opportunity_scorer",  label: "Opportunity Scorer",      desc: "Multi-dimensional scoring framework",        upTo: 82 },
  { key: "debate",              label: "Agent Debate",            desc: "4 agents argue FOR / AGAINST / CHALLENGE / SKEPTICAL", upTo: 93 },
  { key: "judge",               label: "Judge Agent",             desc: "Resolving conflicts & final verdict",        upTo: 100 },
];

export default function ProcessingPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState({ status: "processing", current_agent: null, progress: "0" });

  useEffect(() => {
    const base = (process.env.REACT_APP_API_URL || "http://localhost:8000").replace(/\/+$/, "");
    const token = localStorage.getItem("token");

    const es = new EventSource(`${base}/api/projects/${projectId}/stream?token=${token}`);
    es.onmessage = (e) => {
      const d = JSON.parse(e.data);
      setStatus(d);
      if (d.status === "completed") {
        es.close();
        setTimeout(() => navigate(`/projects/${projectId}/report`), 600);
      }
      if (d.status === "failed") es.close();
    };
    es.onerror = () => es.close();

    const poll = setInterval(async () => {
      try {
        const r = await projectsApi.status(projectId);
        setStatus(r.data);
        if (r.data.status === "completed") {
          clearInterval(poll);
          setTimeout(() => navigate(`/projects/${projectId}/report`), 600);
        }
        if (r.data.status === "failed") clearInterval(poll);
      } catch {}
    }, 4000);

    return () => { es.close(); clearInterval(poll); };
  }, [projectId, navigate]);

  const progress = parseInt(status.progress || "0");

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="text-xl font-bold text-white mb-1">Analysing your research</h1>
        <p className="text-gray-400 text-sm">15 specialist agents are processing your document</p>
      </div>

      <div className="bg-gray-800 rounded-full h-1.5 mb-2 overflow-hidden">
        <div className="bg-brand-500 h-1.5 rounded-full transition-all duration-700" style={{ width: `${progress}%` }} />
      </div>
      <p className="text-center text-xs text-gray-500 mb-6">{progress}% complete</p>

      <div className="space-y-2">
        {STEPS.map((step, i) => {
          const prevUpTo = i === 0 ? 0 : STEPS[i - 1].upTo;
          const done   = progress >= step.upTo;
          const active = progress > prevUpTo && progress < step.upTo;
          const failed = status.status === "failed" && active;

          return (
            <div key={step.key}
              className={`flex items-start gap-3 p-3 rounded-lg transition-all ${
                active ? "bg-brand-500/10 border border-brand-500/20" : "bg-gray-900/50"
              }`}>
              <div className="mt-0.5 flex-shrink-0">
                {failed  ? <XCircle size={16} className="text-red-400" />
                : done   ? <CheckCircle size={16} className="text-green-400" />
                : active ? <Loader2 size={16} className="text-brand-400 animate-spin" />
                :           <Circle size={16} className="text-gray-700" />}
              </div>
              <div>
                <p className={`text-sm font-medium ${active ? "text-white" : done ? "text-gray-300" : "text-gray-600"}`}>
                  {step.label}
                </p>
                {active && <p className="text-xs text-gray-400 mt-0.5">{step.desc}</p>}
              </div>
            </div>
          );
        })}
      </div>

      {status.status === "failed" && (
        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300 text-sm">
          Analysis failed. Come Back later.
        </div>
      )}
    </div>
  );
}
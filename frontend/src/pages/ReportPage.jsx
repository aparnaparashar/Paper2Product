import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
} from "recharts";
import { Download, Brain, Clock, DollarSign, ChevronDown, ChevronUp } from "lucide-react";
import { projectsApi } from "../api/client";
import toast from "react-hot-toast";

// ── Shared UI helpers ─────────────────────────────────────────────────────────

function Tag({ children, color = "brand" }) {
  const c = { brand:"bg-blue-500/10 text-blue-300 border-blue-500/20", green:"bg-green-500/10 text-green-300 border-green-500/20",
              red:"bg-red-500/10 text-red-300 border-red-500/20", amber:"bg-amber-500/10 text-amber-300 border-amber-500/20",
              gray:"bg-gray-800 text-gray-400 border-gray-700" }[color] || "bg-gray-800 text-gray-400";
  return <span className={`inline-block text-xs px-2 py-0.5 rounded-full border font-medium ${c}`}>{children}</span>;
}

function Card({ title, icon, children, className = "" }) {
  return (
    <div className={`bg-gray-900 border border-gray-800 rounded-xl p-5 ${className}`}>
      {title && <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">{icon && <span>{icon}</span>}{title}</h3>}
      {children}
    </div>
  );
}

function ConfBadge({ v }) {
  if (v == null) return null;
  const pct = Math.round(v * 100);
  return <span className={`text-xs font-mono ${pct>=80?"text-green-400":pct>=60?"text-yellow-400":"text-red-400"}`}>{pct}% conf</span>;
}

function ReasoningBlock({ reasoning, sources, confidence }) {
  const [open, setOpen] = useState(false);
  if (!reasoning?.length && !sources?.length) return null;
  return (
    <div className="mt-3 border-t border-gray-800 pt-3">
      <button onClick={() => setOpen(!open)} className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300">
        <Brain size={11}/> {open ? "Hide" : "Show"} reasoning log <ConfBadge v={confidence}/>
        {open ? <ChevronUp size={11}/> : <ChevronDown size={11}/>}
      </button>
      {open && (
        <div className="mt-2 bg-gray-950 border border-gray-800 rounded-lg p-3 text-xs space-y-3">
          {reasoning?.length > 0 && (
            <div>
              <p className="text-gray-500 font-medium mb-1.5">Reasoning steps</p>
              {reasoning.map((r, i) => (
                <div key={i} className="flex gap-2 text-gray-300 py-0.5">
                  <span className="text-blue-400 flex-shrink-0">{i+1}.</span><span>{r}</span>
                </div>
              ))}
            </div>
          )}
          {sources?.length > 0 && (
            <div>
              <p className="text-gray-500 font-medium mb-1.5">Source citations</p>
              {sources.map((s, i) => (
                <div key={i} className="flex gap-2 text-gray-400 py-0.5">
                  <span className="text-green-500 flex-shrink-0">→</span><span>{s}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function GoNoBanner({ verdict, summary }) {
  const m = { GO:{"bg":"bg-green-500/10 border-green-500/30","t":"text-green-400","e":"✅"},
    "NO-GO":{"bg":"bg-red-500/10 border-red-500/30","t":"text-red-400","e":"❌"},
    "CONDITIONAL-GO":{"bg":"bg-amber-500/10 border-amber-500/30","t":"text-amber-400","e":"⚠️"} };
  const s = m[verdict] || m["CONDITIONAL-GO"];
  return (
    <div className={`border rounded-xl px-5 py-4 ${s.bg}`}>
      <div className="flex items-center gap-2 mb-1"><span className="text-xl">{s.e}</span><span className={`font-bold text-xl ${s.t}`}>{verdict}</span></div>
      <p className="text-gray-300 text-sm leading-relaxed">{summary}</p>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

const TABS = [
  { id:"overview",    label:"Overview"     },
  { id:"market",      label:"Market"       },
  { id:"product",     label:"Product/MVP"  },
  { id:"architecture",label:"Architecture" },
  { id:"revenue",     label:"Revenue"      },
  { id:"risk",        label:"Risk"         },
  { id:"investment",  label:"Investment"   },
  { id:"debate",      label:"Debate"       },
  { id:"knowledge",   label:"Knowledge"    },
  { id:"agents",      label:"Agent Logs"   },
];

export default function ReportPage() {
  const { projectId } = useParams();
  const [report, setReport]       = useState(null);
  const [agentRuns, setAgentRuns] = useState([]);
  const [tab, setTab]             = useState("overview");
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    Promise.all([
      projectsApi.report(projectId),
      projectsApi.agentRuns(projectId).catch(() => ({ data: [] })),
    ]).then(([r, a]) => { setReport(r.data); setAgentRuns(a.data); setLoading(false); });
  }, [projectId]);

  const doExport = async (fmt) => {
    try {
      const res = await projectsApi.export(projectId, fmt);
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${(report.title || "report").replace(/ /g,"_")}.${fmt === "markdown" ? "md" : fmt}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { toast.error("Export failed"); }
  };

  const agentMeta = (name) => agentRuns.find(r => r.agent_name === name) || {};

  if (loading) return <div className="text-center py-20 text-gray-400">Loading report...</div>;
  if (!report)  return <div className="text-center py-20 text-red-400">Report not found</div>;

  const fr   = report.final_report || {};
  const rp   = report.research_profile || {};
  const is_  = report.innovation_score || {};
  const mo   = report.market_opportunities || {};
  const cp   = Array.isArray(report.customer_personas) ? report.customer_personas : [];
  const cl   = report.competitive_landscape || {};
  const pc   = Array.isArray(report.product_concepts) ? report.product_concepts : [];
  const mvp  = report.mvp_plan || {};
  const arch = report.architecture || {};
  const rev  = report.revenue_strategy || {};
  const risk = report.risk_profile || {};
  const inv  = report.investment_score || {};
  const opp  = report.opportunity_scores || {};
  const kg   = report.knowledge_graph || {};
  const dbt  = Array.isArray(report.debate_transcript) ? report.debate_transcript : [];

  const dims = opp.dimensions || {};
  const radarData = Object.entries(dims).map(([k, v]) => ({
    subject: k.replace(/_/g," ").split(" ").map(w=>w[0]?.toUpperCase()+w.slice(1)).slice(0,2).join(" "),
    A: typeof v === "object" ? v.score : v,
  }));
  const barData = Object.entries(dims).map(([k, v]) => ({
    name: k.replace(/_/g," ").split(" ").map(w=>w[0]?.toUpperCase()+w.slice(1)).join(" "),
    score: typeof v === "object" ? v.score : v,
    rationale: typeof v === "object" ? v.rationale || "" : "",
  }));

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">{report.title}</h1>
          <p className="text-gray-400 text-sm mt-1">{rp.domain} · {rp.maturity_level}</p>
          {report.total_cost_usd != null && (
            <p className="text-gray-600 text-xs mt-0.5 flex items-center gap-3">
              <span className="flex items-center gap-1"><DollarSign size={10}/>${report.total_cost_usd} cost</span>
              <span className="flex items-center gap-1"><Clock size={10}/>{report.total_duration_sec}s</span>
              <span>{((report.total_tokens||{}).total||0).toLocaleString()} tokens</span>
            </p>
          )}
        </div>
        <div className="flex gap-2">
          {["markdown","pdf","docx"].map(fmt => (
            <button key={fmt} onClick={() => doExport(fmt)}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-gray-300 transition-colors">
              <Download size={11}/>{fmt.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-0.5 overflow-x-auto pb-1 mb-6 border-b border-gray-800">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-3 py-2 text-xs rounded-t-lg whitespace-nowrap transition-colors ${tab===t.id?"bg-gray-900 border border-b-gray-900 border-gray-800 text-brand-400 font-medium -mb-px":"text-gray-400 hover:text-gray-200"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW ── */}
      {tab === "overview" && (
        <div className="space-y-5">
          <GoNoBanner verdict={fr.go_no_go} summary={fr.executive_summary} />

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { l:"Opp Score",  v: opp.weighted_final_score != null ? `${opp.weighted_final_score}/10` : "—" },
              { l:"Innovation", v: is_.innovation_score != null ? `${is_.innovation_score}/10` : "—" },
              { l:"Investment", v: inv.investment_score != null ? `${inv.investment_score}/100` : "—" },
              { l:"Market $B",  v: mo.primary_market?.size_usd_billion ?? "—" },
              { l:"Risk",       v: risk.overall_risk_level ?? "—" },
            ].map(m => (
              <div key={m.l} className="bg-gray-900 border border-gray-800 rounded-xl p-3 text-center">
                <p className="text-xs text-gray-500 mb-1">{m.l}</p>
                <p className="font-bold text-white">{m.v}</p>
              </div>
            ))}
          </div>

          {radarData.length > 0 && (
            <div className="grid md:grid-cols-2 gap-5">
              <Card title="Opportunity radar" >
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#374151"/><PolarAngleAxis dataKey="subject" tick={{fill:"#9ca3af",fontSize:10}}/>
                    <Radar dataKey="A" stroke="#4f6ef7" fill="#4f6ef7" fillOpacity={0.25}/>
                  </RadarChart>
                </ResponsiveContainer>
              </Card>
              <Card title="Score breakdown" >
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={barData} layout="vertical" margin={{left:0}}>
                    <XAxis type="number" domain={[0,10]} tick={{fill:"#6b7280",fontSize:9}} tickLine={false}/>
                    <YAxis dataKey="name" type="category" tick={{fill:"#9ca3af",fontSize:9}} width={88} tickLine={false}/>
                    <Tooltip contentStyle={{background:"#111827",border:"1px solid #374151",borderRadius:8,fontSize:11}}
                      formatter={(v,n,p) => [v, (p.payload.rationale||"").slice(0,60)]}/>
                    <Bar dataKey="score" radius={[0,3,3,0]}>
                      {barData.map((d,i) => <Cell key={i} fill={d.score>=8?"#22c55e":d.score>=6?"#4f6ef7":"#f59e0b"}/>)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <p className="text-center text-xs text-gray-400 mt-1">{opp.score_interpretation}</p>
              </Card>
            </div>
          )}

          {opp.improvement_levers?.length > 0 && (
            <Card title="Score improvement levers" >
              {opp.improvement_levers.map((l,i) => (
                <div key={i} className="flex gap-2 text-sm mb-1.5">
                  <span className="text-green-400 flex-shrink-0">↑</span><span className="text-gray-300">{l}</span>
                </div>
              ))}
            </Card>
          )}

          <Card title="Research profile" >
            <div className="space-y-2 text-sm">
              <div><span className="text-gray-500">Problem: </span><span className="text-gray-200">{rp.problem}</span></div>
              <div><span className="text-gray-500">Novelty: </span><span className="text-gray-200">{rp.novelty}</span></div>
              <div className="flex flex-wrap gap-1 mt-2">{(rp.key_technologies||[]).map((t,i)=><Tag key={i}>{t}</Tag>)}</div>
            </div>
            <ReasoningBlock reasoning={agentMeta("research_analyst").reasoning} sources={agentMeta("research_analyst").sources} confidence={agentMeta("research_analyst").confidence}/>
          </Card>

          {fr.final_recommendation_paragraphs?.length > 0 && (
            <Card title="Final recommendation" >
              {fr.final_recommendation_paragraphs.map((p,i) => <p key={i} className="text-sm text-gray-300 leading-relaxed mb-2">{p}</p>)}
            </Card>
          )}
        </div>
      )}

      {/* ── MARKET ── */}
      {tab === "market" && (
        <div className="space-y-5">
          <Card title="Primary market" >
            <p className="text-xl font-bold text-white mb-1">{mo.primary_market?.name}</p>
            <p className="text-gray-400 text-sm mb-3">{mo.primary_market?.description}</p>
            <div className="flex gap-8 text-sm">
              <div><p className="text-xs text-gray-500">Size</p><p className="text-green-400 font-bold">${mo.primary_market?.size_usd_billion}B</p></div>
              <div><p className="text-xs text-gray-500">Growth</p><p className="text-green-400 font-bold">{mo.primary_market?.growth_rate_pct}% CAGR</p></div>
              <div><p className="text-xs text-gray-500">Timing</p><p className="text-brand-400 font-bold">{mo.market_timing}</p></div>
            </div>
            <ReasoningBlock reasoning={agentMeta("market_discovery").reasoning} sources={agentMeta("market_discovery").sources} confidence={agentMeta("market_discovery").confidence}/>
          </Card>

          <Card title="Use cases" >
            <div className="space-y-3">
              {(mo.use_cases||[]).map((uc,i) => (
                <div key={i} className="border border-gray-800 rounded-lg p-3">
                  <div className="flex justify-between mb-1">
                    <p className="text-sm font-medium text-white">{uc.title}</p>
                    <Tag color={uc.urgency==="high"?"red":uc.urgency==="medium"?"amber":"green"}>{uc.urgency}</Tag>
                  </div>
                  <p className="text-xs text-gray-400">{uc.description}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Customer personas" >
            <div className="grid md:grid-cols-2 gap-4">
              {cp.map((p,i) => (
                <div key={i} className="bg-gray-800/50 rounded-lg p-4 text-sm">
                  <p className="font-semibold text-white">{p.name}</p>
                  <p className="text-xs text-gray-400 mb-2">{p.role} · {p.company_size}</p>
                  <p className="text-xs text-gray-300 italic mb-2">"{p.quote}"</p>
                  <p className="text-xs"><span className="text-gray-500">Budget: </span><span className="text-green-400">{p.budget_range}</span></p>
                </div>
              ))}
            </div>
            <ReasoningBlock reasoning={agentMeta("customer_persona").reasoning} sources={agentMeta("customer_persona").sources} confidence={agentMeta("customer_persona").confidence}/>
          </Card>

          <Card title="Competitive landscape" >
            <div className="space-y-2 mb-4">
              {(cl.direct_competitors||[]).map((c,i) => (
                <div key={i} className="flex gap-3 py-2 border-b border-gray-800 text-sm last:border-0">
                  <div className="flex-1"><p className="text-white font-medium">{c.name}</p><p className="text-xs text-gray-400">{c.description}</p></div>
                  <p className="text-xs text-gray-500 max-w-32 text-right">{c.weakness}</p>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mb-1.5">Whitespace opportunities</p>
            <div className="flex flex-wrap gap-1">{(cl.whitespace_opportunities||[]).map((w,i) => <Tag key={i} color="green">{w}</Tag>)}</div>
            <ReasoningBlock reasoning={agentMeta("competitor_intel").reasoning} sources={agentMeta("competitor_intel").sources} confidence={agentMeta("competitor_intel").confidence}/>
          </Card>
        </div>
      )}

      {/* ── PRODUCT / MVP ── */}
      {tab === "product" && (
        <div className="space-y-5">
          {pc.filter(Boolean).map((c,i) => (
            <Card key={i} title={c.product_name || `Concept ${i+1}`} >
              <p className="text-brand-300 italic text-sm mb-3">{c.tagline}</p>
              <div className="grid md:grid-cols-2 gap-3 text-sm mb-2">
                <div><p className="text-xs text-gray-500">Category</p><p className="text-white">{c.category}</p></div>
                <div><p className="text-xs text-gray-500">Target</p><p className="text-white">{c.target_persona}</p></div>
              </div>
              <p className="text-gray-300 text-sm">{c.core_value_proposition}</p>
            </Card>
          ))}

          <Card title="MVP plan" >
            <p className="text-gray-300 text-sm mb-4">{mvp.mvp_description}</p>
            <div className="grid grid-cols-3 gap-3 text-center mb-4">
              <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-500">Timeline</p><p className="text-white font-bold text-sm mt-1">{mvp.time_to_mvp}</p></div>
              <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-500">Cost</p><p className="text-white font-bold text-sm mt-1">${(mvp.estimated_cost_usd||{}).min?.toLocaleString()}–${(mvp.estimated_cost_usd||{}).max?.toLocaleString()}</p></div>
              <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-500">Team</p><p className="text-white font-bold text-sm mt-1">{(mvp.team_needed||[]).length} roles</p></div>
            </div>
            <p className="text-xs text-gray-500 mb-2">Must-have features</p>
            <div className="space-y-1 mb-4">
              {(mvp.must_have_features||[]).map((f,i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-500 flex-shrink-0"/>
                  <span className="text-gray-300">{typeof f==="string"?f:f.feature}</span>
                  {typeof f==="object"&&f.effort && <Tag color={f.effort==="high"?"red":f.effort==="medium"?"amber":"green"}>{f.effort}</Tag>}
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mb-1.5">Excluded from MVP</p>
            <div className="flex flex-wrap gap-1">{(mvp.explicitly_exclude||[]).map((x,i) => <Tag key={i} color="red">{x}</Tag>)}</div>
            <ReasoningBlock reasoning={agentMeta("mvp_planner").reasoning} sources={agentMeta("mvp_planner").sources} confidence={agentMeta("mvp_planner").confidence}/>
          </Card>
        </div>
      )}

      {/* ── ARCHITECTURE ── */}
      {tab === "architecture" && (
        <div className="space-y-5">
          <div className="grid md:grid-cols-3 gap-4">
            {[
              {l:"Backend",  v:`${arch.backend?.framework} (${arch.backend?.language})`},
              {l:"Frontend", v:`${arch.frontend?.framework} · ${arch.frontend?.ui_library}`},
              {l:"Cloud",    v:arch.infrastructure?.cloud},
            ].map(item => <Card key={item.l} title={item.l}><p className="text-white text-sm font-medium">{item.v}</p></Card>)}
          </div>
          <Card title="AI / ML stack" >
            <div className="space-y-2 text-sm">
              <div><span className="text-gray-500 text-xs">Models: </span><div className="flex flex-wrap gap-1 mt-1">{(arch.ai_ml_stack?.model_providers||[]).map((m,i)=><Tag key={i}>{m}</Tag>)}</div></div>
              <div><span className="text-gray-500 text-xs">Frameworks: </span><div className="flex flex-wrap gap-1 mt-1">{(arch.ai_ml_stack?.frameworks||[]).map((f,i)=><Tag key={i}>{f}</Tag>)}</div></div>
            </div>
            <ReasoningBlock reasoning={agentMeta("architect").reasoning} sources={agentMeta("architect").sources} confidence={agentMeta("architect").confidence}/>
          </Card>
          <Card title="Data storage" >
            {(arch.data_storage||[]).map((d,i) => (
              <div key={i} className="flex gap-3 py-2 border-b border-gray-800 text-sm last:border-0">
                <span className="text-brand-400 font-medium w-28 flex-shrink-0">{d.type}</span>
                <span className="text-gray-300">{d.purpose}</span>
              </div>
            ))}
          </Card>
          <Card title="Infrastructure cost" >
            <div className="flex gap-10 text-sm">
              <div><p className="text-xs text-gray-500">MVP / month</p><p className="text-white font-bold">${arch.infrastructure?.estimated_monthly_cost_usd?.mvp}/mo</p></div>
              <div><p className="text-xs text-gray-500">At scale / month</p><p className="text-white font-bold">${arch.infrastructure?.estimated_monthly_cost_usd?.scale_10k_users}/mo</p></div>
            </div>
          </Card>
        </div>
      )}

      {/* ── REVENUE ── */}
      {tab === "revenue" && (
        <div className="space-y-5">
          <Card title="Business model" >
            <p className="text-2xl font-bold text-brand-400 mb-2">{rev.recommended_model}</p>
            <p className="text-gray-300 text-sm">{rev.rationale}</p>
            <ReasoningBlock reasoning={agentMeta("revenue_strategy").reasoning} sources={agentMeta("revenue_strategy").sources} confidence={agentMeta("revenue_strategy").confidence}/>
          </Card>
          <Card title="Pricing tiers" >
            <div className="grid md:grid-cols-3 gap-4">
              {(rev.pricing_tiers||[]).map((tier,i) => (
                <div key={i} className="bg-gray-800 rounded-xl p-4 text-sm">
                  <p className="font-semibold text-white">{tier.name}</p>
                  <p className="text-2xl font-bold text-brand-400 my-2">{tier.price}</p>
                  <p className="text-xs text-gray-400 mb-2">{tier.target}</p>
                  <ul className="space-y-1">{(tier.features||[]).slice(0,4).map((f,j)=><li key={j} className="text-xs text-gray-300 flex gap-1.5"><span className="text-green-400">✓</span>{f}</li>)}</ul>
                </div>
              ))}
            </div>
          </Card>
          <Card title="Revenue projections" >
            <div className="grid md:grid-cols-3 gap-4 text-center">
              {Object.entries(rev.revenue_projections||{}).map(([period,data]) => (
                <div key={period} className="bg-gray-800 rounded-lg p-4">
                  <p className="text-xs text-gray-500 uppercase mb-1">{period.replace(/_/g," ")}</p>
                  <p className="text-white font-bold">{data.customers} customers</p>
                  <p className="text-green-400 text-sm">${((data.mrr_usd||data.arr_usd||0)).toLocaleString()}{data.mrr_usd?" MRR":" ARR"}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* ── RISK ── */}
      {tab === "risk" && (
        <div className="space-y-5">
          <Card title="Risk overview" >
            <p className="text-2xl font-bold text-white mb-1">{risk.overall_risk_level?.toUpperCase()}</p>
            <p className="text-gray-300 text-sm mb-3">{risk.risk_verdict}</p>
            <p className="text-xs text-gray-500 mb-2">Top 3 risks</p>
            {(risk.top_3_risks||[]).map((r,i) => <div key={i} className="flex gap-2 text-sm py-0.5"><span className="text-red-400">{i+1}.</span><span className="text-red-300">{r}</span></div>)}
            <ReasoningBlock reasoning={agentMeta("risk_analyst").reasoning} sources={agentMeta("risk_analyst").sources} confidence={agentMeta("risk_analyst").confidence}/>
          </Card>
          {[{k:"technical_risks",l:"Technical"},{k:"market_risks",l:"Market"},{k:"regulatory_risks",l:"Regulatory"},{k:"competitive_risks",l:"Competitive"}].map(({k,l,i}) => (
            <Card key={k} title={l+" risks"} icon={i}>
              <div className="space-y-3">
                {(risk[k]||[]).map((r,j) => (
                  <div key={j} className="text-sm border-l-2 border-gray-700 pl-3">
                    <p className="text-white">{r.risk}</p>
                    <p className="text-gray-400 text-xs mt-0.5">Mitigation: {r.mitigation}</p>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* ── INVESTMENT ── */}
      {tab === "investment" && (
        <div className="space-y-5">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center">
            <p className="text-xs text-gray-500 mb-1">Investment score</p>
            <p className="text-6xl font-bold text-brand-400">{inv.investment_score}</p>
            <p className="text-gray-400 text-sm">/100 · <span className="text-brand-300">{inv.investment_verdict}</span></p>
            {opp.score_vs_benchmarks && <p className="text-xs text-gray-600 mt-1">{opp.score_vs_benchmarks.percentile}th percentile</p>}
          </div>
          <Card title="Funding path" >
            <div className="space-y-3">
              {Object.entries(inv.funding_path||{}).map(([round,data]) => (
                <div key={round} className="flex gap-4 py-3 border-b border-gray-800 text-sm last:border-0">
                  <div className="w-20 flex-shrink-0">
                    <p className="text-xs text-gray-500 uppercase">{round.replace(/_/g," ")}</p>
                    <p className="text-white font-bold">${((data.amount_usd||0)/1e6).toFixed(1)}M</p>
                  </div>
                  <div>{(data.milestones||data.use_of_funds||data.metrics_needed||[]).map((m,i) => <p key={i} className="text-xs text-gray-400">• {m}</p>)}</div>
                </div>
              ))}
            </div>
          </Card>
          <Card title="Investment memo" >
            <p className="text-gray-300 text-sm leading-relaxed mb-4">{inv.investment_memo_summary}</p>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div><p className="text-xs text-gray-500 mb-1"> Bull case</p><p className="text-green-300">{inv.bull_case}</p></div>
              <div><p className="text-xs text-gray-500 mb-1"> Bear case</p><p className="text-red-300">{inv.bear_case}</p></div>
            </div>
            <ReasoningBlock reasoning={agentMeta("investment_agent").reasoning} sources={agentMeta("investment_agent").sources} confidence={agentMeta("investment_agent").confidence}/>
          </Card>
        </div>
      )}

      {/* ── DEBATE ── */}
      {tab === "debate" && (
        <div className="space-y-5">
          <Card title="Agent debate transcript" >
            <p className="text-xs text-gray-500 mb-4">4 agents argued their positions. The Judge read this transcript before making the final ruling.</p>
            <div className="space-y-4">
              {dbt.map((entry, i) => {
                const colors = { FOR:"border-green-500/40 bg-green-500/5", AGAINST:"border-red-500/40 bg-red-500/5",
                  CHALLENGE:"border-amber-500/40 bg-amber-500/5", SKEPTICAL:"border-orange-500/40 bg-orange-500/5" };
                return (
                  <div key={i} className={`border rounded-xl p-4 ${colors[entry.position] || "border-gray-700 bg-gray-800/30"}`}>
                    <div className="flex justify-between mb-2">
                      <span className="font-semibold text-sm text-white">{entry.agent}</span>
                      <div className="flex items-center gap-2">
                        <Tag color={entry.position==="FOR"?"green":entry.position==="AGAINST"?"red":"amber"}>{entry.position}</Tag>
                        <ConfBadge v={entry.confidence}/>
                      </div>
                    </div>
                    <p className="text-xs text-gray-300 italic mb-2">"{entry.strongest_point}"</p>
                    <ul className="space-y-1">
                      {(entry.arguments||[]).map((a,j) => <li key={j} className="text-xs text-gray-400 flex gap-2"><span className="text-gray-600">{j+1}.</span>{a}</li>)}
                    </ul>
                  </div>
                );
              })}
            </div>
          </Card>

          {fr.debate_resolution?.length > 0 && (
            <Card title="Judge's conflict resolutions" >
              <div className="space-y-4">
                {fr.debate_resolution.map((c,i) => (
                  <div key={i} className="border border-gray-800 rounded-lg p-4 text-sm">
                    <p className="text-gray-400 text-xs mb-1 font-medium uppercase">Conflict</p>
                    <p className="text-white mb-3">{c.conflict}</p>
                    <div className="grid md:grid-cols-2 gap-3 mb-3">
                      <div className="bg-green-500/5 rounded p-2"><p className="text-xs text-green-400 mb-0.5">Product argued:</p><p className="text-xs text-gray-300">{c.product_argument}</p></div>
                      <div className="bg-red-500/5 rounded p-2"><p className="text-xs text-red-400 mb-0.5">Risk argued:</p><p className="text-xs text-gray-300">{c.risk_argument}</p></div>
                    </div>
                    <div className="bg-brand-500/5 border border-brand-500/20 rounded p-3">
                      <p className="text-xs text-brand-400 mb-0.5"> Judge ruling:</p>
                      <p className="text-xs text-white">{c.judge_ruling}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}

      {/* ── KNOWLEDGE GRAPH ── */}
      {tab === "knowledge" && (
        <div className="space-y-5">
          <Card title="Concept knowledge graph" >
            <p className="text-sm text-gray-400 mb-3">{kg.graph_insight}</p>
            <p className="text-xs text-gray-500 mb-3">Core concept: <span className="text-white font-medium">{kg.core_concept}</span></p>
            <div className="grid md:grid-cols-2 gap-4">
              {(kg.concept_clusters||[]).map((cl,i) => (
                <div key={i} className="bg-gray-800/50 rounded-lg p-4">
                  <p className="text-sm font-medium text-white mb-1">{cl.cluster_name}</p>
                  <p className="text-xs text-gray-400 mb-2">{cl.insight}</p>
                  <div className="flex flex-wrap gap-1">
                    {(cl.entity_ids||[]).map((eid,j) => {
                      const entity = (kg.entities||[]).find(e => e.id === eid);
                      return entity ? <Tag key={j}>{entity.label}</Tag> : null;
                    })}
                  </div>
                </div>
              ))}
            </div>
          </Card>
          <Card title="Entities" >
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead><tr className="border-b border-gray-800 text-gray-500 text-left"><th className="py-2 pr-4">Entity</th><th className="py-2 pr-4">Type</th><th className="py-2">Description</th></tr></thead>
                <tbody>
                  {(kg.entities||[]).map((e,i) => (
                    <tr key={i} className="border-b border-gray-800/50">
                      <td className="py-1.5 pr-4 text-white font-medium">{e.label}</td>
                      <td className="py-1.5 pr-4"><Tag>{e.type}</Tag></td>
                      <td className="py-1.5 text-gray-400">{e.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {(kg.relationships||[]).length > 0 && (
              <div className="mt-4">
                <p className="text-xs text-gray-500 mb-2">Relationships</p>
                <div className="flex flex-wrap gap-2">
                  {kg.relationships.map((r,i) => {
                    const from = (kg.entities||[]).find(e => e.id === r.from)?.label || r.from;
                    const to   = (kg.entities||[]).find(e => e.id === r.to)?.label || r.to;
                    return <span key={i} className="text-xs bg-gray-800 rounded-full px-3 py-1 text-gray-300">{from} <span className="text-gray-500">→{r.label}→</span> {to}</span>;
                  })}
                </div>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* ── AGENT LOGS ── */}
      {tab === "agents" && (
        <div className="space-y-4">
          <Card title="Agent execution log — full traceability" >
            <div className="grid grid-cols-3 gap-3 mb-5 text-center">
              <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-500">Duration</p><p className="text-white font-bold">{report.total_duration_sec}s</p></div>
              <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-500">Tokens</p><p className="text-white font-bold">{((report.total_tokens||{}).total||0).toLocaleString()}</p></div>
              <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-500">Cost</p><p className="text-white font-bold">${report.total_cost_usd}</p></div>
            </div>
            <div className="space-y-2">
              {agentRuns.map((run,i) => <AgentRow key={i} run={run}/>)}
              {agentRuns.length === 0 && <p className="text-gray-500 text-sm">No agent run data yet.</p>}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

function AgentRow({ run }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-800 rounded-lg overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center gap-3 p-3 hover:bg-gray-800/40 text-left transition-colors">
        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${run.status==="completed"?"bg-green-400":run.status==="failed"?"bg-red-400":"bg-yellow-400"}`}/>
        <span className="text-sm font-medium text-white flex-1">{run.agent_label || run.agent_name}</span>
        <span className="text-xs text-gray-500 font-mono">{run.model_used}</span>
        <span className="text-xs text-gray-500 flex items-center gap-1"><Clock size={9}/>{run.duration_seconds}s</span>
        <span className="text-xs text-gray-500 flex items-center gap-1"><DollarSign size={9}/>${run.estimated_cost_usd}</span>
        {run.confidence != null && <span className="text-xs text-brand-400">{Math.round(run.confidence*100)}%</span>}
        {open ? <ChevronUp size={12} className="text-gray-500"/> : <ChevronDown size={12} className="text-gray-500"/>}
      </button>
      {open && (
        <div className="border-t border-gray-800 p-4 bg-gray-950 text-xs space-y-3">
          <div className="grid grid-cols-4 gap-3 text-center">
            <div><p className="text-gray-500">Provider</p><p className="text-white">{run.model_provider}</p></div>
            <div><p className="text-gray-500">Prompt tokens</p><p className="text-white">{run.prompt_tokens?.toLocaleString()}</p></div>
            <div><p className="text-gray-500">Completion</p><p className="text-white">{run.completion_tokens?.toLocaleString()}</p></div>
            <div><p className="text-gray-500">Est. cost</p><p className="text-white">${run.estimated_cost_usd}</p></div>
          </div>
          {run.reasoning?.length > 0 && (
            <div>
              <p className="text-gray-500 mb-1.5 font-medium">Reasoning steps</p>
              {run.reasoning.map((r,i) => <div key={i} className="flex gap-2 text-gray-300 py-0.5"><span className="text-blue-400">{i+1}.</span>{r}</div>)}
            </div>
          )}
          {run.sources?.length > 0 && (
            <div>
              <p className="text-gray-500 mb-1.5 font-medium">Source citations</p>
              {run.sources.map((s,i) => <div key={i} className="flex gap-2 text-gray-400 py-0.5"><span className="text-green-400">→</span>{s}</div>)}
            </div>
          )}
          {run.error && <p className="text-red-400">Error: {run.error}</p>}
        </div>
      )}
    </div>
  );
}

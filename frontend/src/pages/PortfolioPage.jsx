import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { projectsApi } from "../api/client";
import { Trophy, TrendingUp, AlertTriangle, DollarSign } from "lucide-react";

const GoTag = ({ v }) => {
  const s = { GO: "text-green-400 bg-green-500/10", "NO-GO": "text-red-400 bg-red-500/10", "CONDITIONAL-GO": "text-amber-400 bg-amber-500/10" };
  return v ? <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${s[v] || s["CONDITIONAL-GO"]}`}>{v}</span> : null;
};

const RiskTag = ({ v }) => {
  const s = { low: "text-green-400", medium: "text-yellow-400", high: "text-orange-400", "very-high": "text-red-400" };
  return v ? <span className={`text-xs ${s[v] || "text-gray-400"}`}>{v}</span> : null;
};

export default function PortfolioPage() {
  const [items, setItems]   = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.portfolio().then(r => { setItems(r.data); setLoading(false); });
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-400">Loading portfolio...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Trophy size={22} className="text-amber-400" /> Portfolio ranking
        </h1>
        <p className="text-gray-400 text-sm mt-1">All completed analyses ranked by opportunity score</p>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 border-2 border-dashed border-gray-800 rounded-2xl">
          <Trophy className="mx-auto text-gray-700 mb-3" size={36} />
          <p className="text-gray-400">No completed analyses yet</p>
          <Link to="/upload" className="mt-4 inline-block bg-brand-500 text-white px-4 py-2 rounded-lg text-sm">Analyse a paper</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item, i) => (
            <Link key={item.project_id} to={`/projects/${item.project_id}/report`}
              className="flex items-center gap-4 bg-gray-900 border border-gray-800 hover:border-gray-600 rounded-xl p-4 transition-colors">
              {/* Rank */}
              <div className="w-8 flex-shrink-0 text-center">
                {i === 0 ? <span className="text-xl">🥇</span>
                : i === 1 ? <span className="text-xl">🥈</span>
                : i === 2 ? <span className="text-xl">🥉</span>
                : <span className="text-gray-500 font-bold text-sm">#{i + 1}</span>}
              </div>

              {/* Title */}
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium text-sm truncate">{item.title}</p>
                <p className="text-gray-500 text-xs mt-0.5">{new Date(item.created_at).toLocaleDateString()}</p>
              </div>

              {/* Scores */}
              <div className="hidden md:flex items-center gap-5 text-sm">
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-0.5">Opp. Score</p>
                  <p className="font-bold text-white">{item.final_score ?? "—"}<span className="text-gray-500 text-xs">/10</span></p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-0.5">Investment</p>
                  <p className="font-bold text-brand-400">{item.investment_score ?? "—"}<span className="text-gray-500 text-xs">/100</span></p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-0.5">Market $B</p>
                  <p className="font-bold text-green-400">{item.market_size ?? "—"}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-0.5">Risk</p>
                  <RiskTag v={item.risk_level} />
                </div>
              </div>

              <GoTag v={item.go_no_go} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

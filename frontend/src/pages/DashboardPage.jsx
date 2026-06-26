import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, FileText, Loader2, CheckCircle, XCircle, Clock, Trash2 } from "lucide-react";
import { projectsApi } from "../api/client";
import toast from "react-hot-toast";

const StatusIcon = ({ s }) => ({
  completed:  <CheckCircle size={13} className="text-green-400" />,
  failed:     <XCircle size={13} className="text-red-400" />,
  processing: <Loader2 size={13} className="text-brand-400 animate-spin" />,
}[s] || <Clock size={13} className="text-gray-500" />);

export default function DashboardPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading]   = useState(true);

  const load = () => projectsApi.list().then(r => { setProjects(r.data); setLoading(false); });
  useEffect(() => { load(); }, []);

  const del = async (e, id) => {
    e.preventDefault();
    if (!window.confirm("Delete this project?")) return;
    await projectsApi.delete(id);
    toast.success("Deleted");
    load();
  };

  if (loading) return <div className="text-center py-20 text-gray-400">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Your analyses</h1>
          <p className="text-gray-400 text-sm mt-0.5">{projects.length} project{projects.length !== 1 ? "s" : ""}</p>
        </div>
        <Link to="/upload" className="flex items-center gap-1.5 bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          <Plus size={15} /> New analysis
        </Link>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed border-gray-800 rounded-2xl">
          <FileText className="mx-auto text-gray-700 mb-3" size={36} />
          <p className="text-gray-400 font-medium mb-1">No analyses yet</p>
          <p className="text-gray-500 text-sm mb-5">Upload a research paper to get started</p>
          <Link to="/upload" className="bg-brand-500 hover:bg-brand-600 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">
            Upload research
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {projects.map(p => (
            <Link key={p.id} to={p.status === "completed" ? `/projects/${p.id}/report` : `/projects/${p.id}`}
              className="flex items-center gap-3 bg-gray-900 border border-gray-800 hover:border-gray-600 rounded-xl p-4 transition-colors group">
              <FileText size={16} className="text-gray-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium text-sm truncate">{p.title}</p>
                <p className="text-gray-500 text-xs mt-0.5">{p.file_name || "Text input"} · {new Date(p.created_at).toLocaleDateString()}</p>
              </div>
              {p.status === "processing" && (
                <div className="w-20 flex-shrink-0">
                  <div className="bg-gray-800 rounded-full h-1 overflow-hidden">
                    <div className="bg-brand-500 h-1 rounded-full" style={{ width: `${p.progress}%` }} />
                  </div>
                  <p className="text-xs text-gray-500 text-center mt-0.5">{p.progress}%</p>
                </div>
              )}
              {p.total_cost_usd != null && <span className="text-xs text-gray-600">${p.total_cost_usd}</span>}
              <div className="flex items-center gap-1.5">
                <StatusIcon s={p.status} />
                <span className="text-xs text-gray-400 hidden sm:block">{p.status}</span>
              </div>
              <button onClick={e => del(e, p.id)} className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-red-400 text-gray-600">
                <Trash2 size={13} />
              </button>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

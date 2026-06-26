import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, Loader2, X } from "lucide-react";
import { projectsApi } from "../api/client";
import toast from "react-hot-toast";

export default function UploadPage() {
  const [file, setFile]       = useState(null);
  const [abstract, setAbstract] = useState("");
  const [title, setTitle]     = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onDrop = useCallback((accepted) => { if (accepted[0]) setFile(accepted[0]); }, []);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "application/pdf": [".pdf"], "text/plain": [".txt"], "text/markdown": [".md"] }, maxFiles: 1,
  });

  const submit = async (e) => {
    e.preventDefault();
    if (!file && abstract.trim().length < 100) { toast.error("Upload a file or paste at least 100 characters"); return; }
    setLoading(true);
    try {
      const fd = new FormData();
      if (file) fd.append("file", file);
      if (abstract) fd.append("abstract", abstract);
      fd.append("title", title || (file ? file.name.replace(/\.[^.]+$/, "") : "Research Analysis"));
      const res = await projectsApi.create(fd);
      toast.success("Analysis started — 15 agents are now working!");
      navigate(`/projects/${res.data.project_id}`);
    } catch (err) { toast.error(err.response?.data?.detail || "Upload failed"); }
    finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-white mb-1">New analysis</h1>
      <p className="text-gray-400 text-sm mb-8">Upload a research paper or paste an abstract. 15 AI agents will analyse it end-to-end.</p>

      <form onSubmit={submit} className="space-y-5">
        <div>
          <label htmlFor="project_title" className="block text-xs text-gray-400 mb-1">Project title (optional)</label>
          <input id="project_title" name="project_title" type="text" value={title} onChange={e => setTitle(e.target.value)}
            placeholder="e.g. CRISPR Gene Editing Commercialisation"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>

        <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${isDragActive ? "border-brand-500 bg-brand-500/5" : "border-gray-700 hover:border-gray-500"}`}>
          <input {...getInputProps({ id: "research_file", name: "research_file" })} />
          {file ? (
            <div className="flex items-center justify-center gap-3">
              <FileText size={18} className="text-green-400" />
              <span className="text-sm text-green-300 font-medium">{file.name}</span>
              <button type="button" onClick={e => { e.stopPropagation(); setFile(null); }} className="text-gray-500 hover:text-gray-300">
                <X size={14} />
              </button>
            </div>
          ) : (
            <div>
              <Upload className="mx-auto mb-3 text-gray-500" size={28} />
              <p className="text-gray-300 text-sm font-medium">Drop a PDF, TXT, or MD file here</p>
              <p className="text-gray-500 text-xs mt-1">or click to browse</p>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-gray-800" />
          <span className="text-gray-500 text-xs">or paste abstract</span>
          <div className="flex-1 h-px bg-gray-800" />
        </div>

        <label htmlFor="abstract" className="sr-only">Research abstract or full text</label>
        <textarea id="abstract" name="abstract" value={abstract} onChange={e => setAbstract(e.target.value)} rows={6}
          placeholder="Paste your research abstract, description, or full paper text here..."
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none" />

        <button type="submit" disabled={loading}
          className="w-full bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-medium py-3 rounded-lg text-sm transition-colors flex items-center justify-center gap-2">
          {loading ? <><Loader2 size={16} className="animate-spin" />Starting analysis...</> : "Analyse research — 15 agents →"}
        </button>
      </form>
    </div>
  );
}
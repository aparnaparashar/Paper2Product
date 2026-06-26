import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import toast from "react-hot-toast";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handle = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === "login") await login(form.email, form.password);
      else await register(form.email, form.password, form.full_name);
      navigate("/");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Authentication failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-32 h-20 rounded-xl overflow-hidden border-2 border-white bg-white flex items-center justify-center">
              <img src="/logo.jpg" alt="Paper2Product logo" className="w-full h-full object-contain" />
            </div>
            <span className="text-white font-bold text-3xl">Paper2Product</span>
          </div>
          <h1 className="text-2xl font-bold text-white">{mode === "login" ? "Welcome back" : "Create account"}</h1>
          <p className="text-gray-400 text-sm mt-1">From Research To Product</p>
        </div>
        <form onSubmit={handle} className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
          {mode === "register" && (
            <div>
              <label htmlFor="full_name" className="block text-xs text-gray-400 mb-1">Full name</label>
              <input id="full_name" name="full_name" type="text" autoComplete="name" value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="Your name" />
            </div>
          )}
          <div>
            <label htmlFor="email" className="block text-xs text-gray-400 mb-1">Email</label>
            <input id="email" name="email" type="email" autoComplete="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="you@example.com" />
          </div>
          <div>
            <label htmlFor="password" className="block text-xs text-gray-400 mb-1">Password</label>
            <input id="password" name="password" type="password" autoComplete="current-password" required value={form.password} onChange={e => setForm({...form, password: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="••••••••" />
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg text-sm transition-colors">
            {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          {mode === "login" ? "No account? " : "Have an account? "}
          <button onClick={() => setMode(mode === "login" ? "register" : "login")} className="text-brand-400 hover:underline">
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}

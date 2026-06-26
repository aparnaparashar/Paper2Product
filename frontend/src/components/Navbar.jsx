import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { LogOut, Plus, LayoutDashboard, BarChart2 } from "lucide-react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <nav className="bg-gray-950 border-b border-gray-800 px-4 py-3 sticky top-0 z-50">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-lg overflow-hidden border border-white bg-white flex items-center justify-center">
            <img src="/logo2_1.png" alt="Paper2Product logo" className="w-10 h-10 object-contain" />
          </div>
          <span className="text-white font-semibold text-sm hidden sm:block">Paper2Product</span>
        </Link>
        <div className="flex items-center gap-1">
          <Link to="/" className="flex items-center gap-1.5 text-gray-400 hover:text-white text-sm px-3 py-1.5 rounded-lg hover:bg-gray-800 transition-colors">
            <LayoutDashboard size={14} /><span className="hidden sm:block">Dashboard</span>
          </Link>
          <Link to="/portfolio" className="flex items-center gap-1.5 text-gray-400 hover:text-white text-sm px-3 py-1.5 rounded-lg hover:bg-gray-800 transition-colors">
            <BarChart2 size={14} /><span className="hidden sm:block">Portfolio</span>
          </Link>
          <Link to="/upload" className="flex items-center gap-1.5 bg-brand-500 hover:bg-brand-600 text-white text-sm px-3 py-1.5 rounded-lg transition-colors">
            <Plus size={14} /><span className="hidden sm:block">New</span>
          </Link>
          {user && (
            <div className="flex items-center gap-2 ml-2 pl-2 border-l border-gray-800">
              <span className="text-gray-500 text-xs hidden sm:block truncate max-w-32">{user.email}</span>
              <button onClick={() => { logout(); navigate("/login"); }} className="text-gray-400 hover:text-white p-1.5 rounded-lg hover:bg-gray-800 transition-colors">
                <LogOut size={14} />
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

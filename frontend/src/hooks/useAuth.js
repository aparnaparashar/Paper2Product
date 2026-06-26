import { createContext, useContext, useState, useEffect } from "react";
import { authApi } from "../api/client";

const Ctx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (localStorage.getItem("token")) {
      authApi.me().then(r => setUser(r.data)).catch(() => localStorage.removeItem("token")).finally(() => setLoading(false));
    } else { setLoading(false); }
  }, []);

  const login = async (email, password) => {
    const r = await authApi.login({ email, password });
    localStorage.setItem("token", r.data.access_token);
    const me = await authApi.me();
    setUser(me.data);
    return me.data;
  };

  const register = async (email, password, full_name) => {
    await authApi.register({ email, password, full_name });
    return login(email, password);
  };

  const logout = () => { localStorage.removeItem("token"); setUser(null); };

  return <Ctx.Provider value={{ user, loading, login, register, logout }}>{children}</Ctx.Provider>;
}

export const useAuth = () => useContext(Ctx);

import axios from "axios";

const api = axios.create({
  baseURL: (process.env.REACT_APP_API_URL || "http://localhost:8000").replace(/\/+$/, ""),
});

api.interceptors.request.use((c) => {
  const t = localStorage.getItem("token");
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) { localStorage.removeItem("token"); window.location.href = "/login"; }
    return Promise.reject(err);
  }
);

export default api;

export const authApi = {
  register: (d) => api.post("/api/auth/register", d),
  login:    (d) => api.post("/api/auth/login", d),
  me:       ()  => api.get("/api/auth/me"),
};

export const projectsApi = {
  list:      ()        => api.get("/api/projects"),
  create:    (fd)      => api.post("/api/projects", fd, { headers: { "Content-Type": "multipart/form-data" } }),
  status:    (id)      => api.get(`/api/projects/${id}/status`),
  report:    (id)      => api.get(`/api/projects/${id}/report`),
  agentRuns: (id)      => api.get(`/api/projects/${id}/agents`),
  hitl:      (id, d)   => api.post(`/api/projects/${id}/hitl`, d),
  export:    (id, fmt) => api.get(`/api/projects/${id}/export/${fmt}`, { responseType: "blob" }),
  portfolio: ()        => api.get("/api/projects/portfolio/ranked"),
  delete:    (id)      => api.delete(`/api/projects/${id}`),
};
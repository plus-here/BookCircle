import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

const http = axios.create({
  baseURL: BASE,
  timeout: 15000,
});

// ✅ 每次请求都直接从 localStorage 读取（避免 pinia/循环依赖导致拿不到 token）
http.interceptors.request.use((config) => {
  const access = localStorage.getItem("admin_access");
  if (access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

let refreshingPromise = null;

http.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config || {};

    if (!err.response) return Promise.reject(err);

    // ✅ 401 才尝试 refresh，并且防止死循环
    if (err.response.status === 401 && !original.__retried) {
      const refresh = localStorage.getItem("admin_refresh");
      if (!refresh) return Promise.reject(err);

      original.__retried = true;

      try {
        if (!refreshingPromise) {
          refreshingPromise = axios.post(
            `${BASE}/auth/refresh/`,
            { refresh },
            { timeout: 15000 }
          );
        }

        const resp = await refreshingPromise;
        refreshingPromise = null;

        const newAccess = resp.data.access;
        localStorage.setItem("admin_access", newAccess);

        // ✅ 用新 token 重放
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${newAccess}`;

        return http(original);
      } catch (e) {
        refreshingPromise = null;
        localStorage.removeItem("admin_access");
        localStorage.removeItem("admin_refresh");
        window.location.href = "/login";
        return Promise.reject(e);
      }
    }

    return Promise.reject(err);
  }
);

export default http;

// src/api.js
import axios from "axios";

function defaultApiBase() {
  return "/api";
}

function isPageOnLoopback() {
  return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
}

function isLoopbackUrl(value) {
  return /^(https?|wss?):\/\/(localhost|127\.0\.0\.1|\[::1\])/i.test(String(value || ""));
}

function usableEnvUrl(value) {
  if (!value) return "";
  if (!isPageOnLoopback() && isLoopbackUrl(value)) return "";
  return value;
}

export const API_BASE = usableEnvUrl(import.meta.env.VITE_API_BASE) || defaultApiBase();

function defaultWsBase() {
  if (/^https?:\/\//.test(API_BASE)) {
    return API_BASE
      .replace(/^http/, "ws")
      .replace(/\/api\/?$/, "")
      .replace(/:8000$/, ":8001");
  }

  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${wsProtocol}//${window.location.host}`;
}

export const WS_BASE = usableEnvUrl(import.meta.env.VITE_WS_BASE) || defaultWsBase();

export function readIceServers() {
  const raw = import.meta.env.VITE_RTC_ICE_SERVERS;
  if (!raw) {
    return [
      { urls: "stun:stun.l.google.com:19302" },
      { urls: "stun:stun.cloudflare.com:3478" },
    ];
  }

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch {
    return raw
      .split(",")
      .map((url) => url.trim())
      .filter(Boolean)
      .map((url) => ({ urls: url }));
  }
}

export const RTC_CONFIG = {
  iceServers: readIceServers(),
  iceTransportPolicy: import.meta.env.VITE_RTC_ICE_TRANSPORT_POLICY || "all",
};

export const api = axios.create({
  baseURL: API_BASE,
});

// 每次请求都从 localStorage 取 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ===== 自动刷新 access 并重试一次 =====
let refreshPromise = null;

async function refreshAccessToken() {
  if (!refreshPromise) {
    const refresh = localStorage.getItem("refresh");
    if (!refresh) throw new Error("no_refresh_token");

    refreshPromise = axios
      .post(`${API_BASE}/auth/refresh/`, { refresh }, { headers: { "Content-Type": "application/json" } })
      .then((res) => res.data)
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const status = err?.response?.status;
    const original = err?.config;

    if (status === 401 && original && !original._retry) {
      original._retry = true;
      try {
        const data = await refreshAccessToken();
        localStorage.setItem("access", data.access);

        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (e) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        alert("登录已过期，请重新登录");
        const current = `${window.location.pathname}${window.location.search}`;
        const redirect = current && current !== "/login" ? `?redirect=${encodeURIComponent(current)}` : "";
        window.location.assign(`/login${redirect}`);
      }
    }

    return Promise.reject(err);
  }
);

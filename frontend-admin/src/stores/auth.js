import { defineStore } from "pinia";
import { jwtDecode } from "jwt-decode";
import http from "../api/http";

// ✅ 命名导出（你项目里大多数地方用这个）
export const useAuthStore = defineStore("auth", {
  state: () => ({
    access: localStorage.getItem("admin_access") || "",
    refresh: localStorage.getItem("admin_refresh") || "",
  }),
  getters: {
    isLoggedIn: (s) => !!s.access,
    username: (s) => {
      try {
        if (!s.access) return "";
        const payload = jwtDecode(s.access);
        return payload.username || payload.user_id || "admin";
      } catch {
        return "admin";
      }
    },
  },
  actions: {
    setTokens({ access, refresh }) {
      this.access = access || "";
      this.refresh = refresh || "";
      if (access) localStorage.setItem("admin_access", access);
      else localStorage.removeItem("admin_access");
      if (refresh) localStorage.setItem("admin_refresh", refresh);
      else localStorage.removeItem("admin_refresh");
    },
    setAccess(access) {
      this.access = access || "";
      if (access) localStorage.setItem("admin_access", access);
      else localStorage.removeItem("admin_access");
    },
    logout() {
      this.access = "";
      this.refresh = "";
      localStorage.removeItem("admin_access");
      localStorage.removeItem("admin_refresh");
    },
    async login(username, password) {
      const res = await http.post("/auth/login/", { username, password });
      this.setTokens(res.data);
    },
  },
});

// ✅ 额外：默认导出（防止某处写了 import useAuthStore from ...）
export default useAuthStore;

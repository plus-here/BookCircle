// src/auth.js
import { ref } from "vue";

// 统一从 localStorage 初始化
export const accessToken = ref(localStorage.getItem("access") || "");
export const refreshToken = ref(localStorage.getItem("refresh") || "");
export const isLoggedIn = ref(!!accessToken.value);

// 任何地方只要登录/退出，广播一个事件，让所有页面同步
function broadcastAuthChanged() {
  window.dispatchEvent(new Event("auth-changed"));
}

export function setTokens(access, refresh) {
  accessToken.value = access || "";
  refreshToken.value = refresh || "";

  localStorage.setItem("access", accessToken.value);
  localStorage.setItem("refresh", refreshToken.value);

  isLoggedIn.value = !!accessToken.value;
  broadcastAuthChanged();
}

export function clearTokens() {
  accessToken.value = "";
  refreshToken.value = "";

  localStorage.removeItem("access");
  localStorage.removeItem("refresh");

  isLoggedIn.value = false;
  broadcastAuthChanged();
}

// ✅ 关键：监听 auth-changed，让“别的页面/别的模块实例”也能同步
window.addEventListener("auth-changed", () => {
  accessToken.value = localStorage.getItem("access") || "";
  refreshToken.value = localStorage.getItem("refresh") || "";
  isLoggedIn.value = !!accessToken.value;
});

// （可选）多标签页同步（比如开了两个标签页）
window.addEventListener("storage", (e) => {
  if (e.key === "access" || e.key === "refresh") {
    broadcastAuthChanged();
  }
});

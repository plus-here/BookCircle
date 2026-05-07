import { defineStore } from "pinia";

export const useUiStore = defineStore("ui", {
  state: () => ({
    theme: localStorage.getItem("admin_theme") || "light", // light | dark
    collapsed: localStorage.getItem("admin_collapsed") === "1",
  }),
  actions: {
    applyTheme() {
      const root = document.documentElement;
      if (this.theme === "dark") root.classList.add("dark");
      else root.classList.remove("dark");
      localStorage.setItem("admin_theme", this.theme);
    },
    toggleTheme() {
      this.theme = this.theme === "dark" ? "light" : "dark";
      this.applyTheme();
    },
    applyCollapsed() {
      localStorage.setItem("admin_collapsed", this.collapsed ? "1" : "0");
    },
    toggleCollapsed() {
      this.collapsed = !this.collapsed;
      this.applyCollapsed();
    },
    init() {
      this.applyTheme();
      this.applyCollapsed();
    },
  },
});

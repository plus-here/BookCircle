import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import zhCn from "element-plus/dist/locale/zh-cn.mjs";
import "element-plus/dist/index.css";
import "element-plus/theme-chalk/dark/css-vars.css"; // ✅ ElementPlus 暗黑变量

import App from "./App.vue";
import router from "./router";
import "./styles/base.css";

import { useUiStore } from "./stores/ui";

import "./styles/admin-theme.css";

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);

useUiStore(pinia).init(); // ✅ 启动时应用主题/折叠状态

app.use(router);
app.use(ElementPlus);
app.mount("#app");
app.use(ElementPlus, { locale: zhCn });
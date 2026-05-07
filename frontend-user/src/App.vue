<template>
  <div>
    <header class="topbar">
      <div class="container topbar__inner">
        <router-link class="brand" to="/">
          <div class="brand__logo">📚</div>
          <div class="brand__text">
            <div class="brand__title">书圈</div>
            <div class="brand__sub">用户端</div>
          </div>
        </router-link>

        <nav class="nav" aria-label="主导航">
          <router-link to="/" class="nav__link">主页</router-link>
          <router-link to="/shelf" class="nav__link">书架</router-link>
          <router-link to="/clubs" class="nav__link">社团</router-link>
          <router-link to="/groups" class="nav__link">群组</router-link>
          <router-link to="/dm" class="nav__link">私聊</router-link>
          <router-link to="/activities" class="nav__link">活动</router-link>
          <router-link to="/my-activities" class="nav__link">我的活动</router-link>
          <router-link to="/announcements" class="nav__link">公告</router-link>
        </nav>

        <div class="actions">
          <!-- 未登录 -->
          <template v-if="!isLoggedIn">
            <router-link class="btn btn-ghost" to="/login">登录</router-link>
            <router-link class="btn btn-primary" to="/register">注册</router-link>
          </template>

          <!-- 已登录：头像下拉 -->
          <template v-else>
            <div class="user" ref="menuRef">
              <button class="user-btn" type="button" @click="toggleMenu">
                <span class="avatar">
                  <img :src="userAvatar(me)" :alt="me?.username || 'avatar'" />
                </span>

                <span class="user-name">{{ me?.username || "已登录" }}</span>
                <span class="chev" :class="{ open: menuOpen }">▾</span>
              </button>

              <div v-if="menuOpen" class="menu">
                <router-link class="menu-item" to="/profile" @click="closeMenu">
                  👤 个人中心
                </router-link>
                <router-link class="menu-item" to="/my-activities" @click="closeMenu">
                  🎯 我的活动
                </router-link>
                <router-link class="menu-item" to="/dm" @click="closeMenu">
                  💬 私聊
                </router-link>

                <div class="menu-divider"></div>

                <button class="menu-item danger" type="button" @click="onLogout">
                  🚪 退出登录
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </header>

    <main class="container page">
      <router-view />
    </main>

    <div class="toast-stack" aria-live="polite" aria-atomic="true">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        <span class="toast-dot"></span>
        <span class="toast-text">{{ toast.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { api } from "./api"; // ✅ 如果你的 api 路径不同，改成正确相对路径
import { userAvatar } from "./utils/media";

const router = useRouter();
const route = useRoute();

const authTick = ref(0);
const me = ref(null);
const toasts = ref([]);
let toastId = 0;
let nativeAlert = null;

const isLoggedIn = computed(() => {
  route.fullPath;
  authTick.value;
  return !!localStorage.getItem("access");
});

async function loadMe() {
  if (!localStorage.getItem("access")) {
    me.value = null;
    return;
  }
  try {
    const res = await api.get("/auth/me/");
    me.value = res.data;
  } catch {
    me.value = null;
  }
}

function showToast(message, type = "info") {
  const id = ++toastId;
  toasts.value.push({ id, message: String(message || ""), type });
  window.setTimeout(() => {
    toasts.value = toasts.value.filter((item) => item.id !== id);
  }, 2600);
}

function onToastEvent(e) {
  showToast(e.detail?.message, e.detail?.type || "info");
}

// 退出登录
function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  authTick.value++;
  showToast("已退出登录", "success");
  router.push("/");
}

function onStorage(e) {
  if (e.key === "access" || e.key === "refresh") {
    authTick.value++;
  }
}

/* 下拉菜单 */
const menuOpen = ref(false);
const menuRef = ref(null);

function toggleMenu() {
  menuOpen.value = !menuOpen.value;
}

function closeMenu() {
  menuOpen.value = false;
}

function onLogout() {
  closeMenu();
  logout();
}

// 点击外部关闭
function onDocClick(e) {
  if (!menuOpen.value) return;
  const el = menuRef.value;
  if (el && !el.contains(e.target)) closeMenu();
}

// ESC 关闭
function onKeydown(e) {
  if (e.key === "Escape") closeMenu();
}

watch(isLoggedIn, async (v) => {
  if (v) await loadMe();
  else me.value = null;
});

// 路由变化也顺便收起菜单（更自然）
watch(
  () => route.fullPath,
  () => closeMenu()
);

onMounted(async () => {
  nativeAlert = window.alert;
  window.alert = (message) => showToast(message, "info");
  window.addEventListener("bookcircle:toast", onToastEvent);
  window.addEventListener("storage", onStorage);
  document.addEventListener("click", onDocClick);
  window.addEventListener("keydown", onKeydown);

  if (isLoggedIn.value) await loadMe();
});

onBeforeUnmount(() => {
  if (nativeAlert) window.alert = nativeAlert;
  window.removeEventListener("bookcircle:toast", onToastEvent);
  window.removeEventListener("storage", onStorage);
  document.removeEventListener("click", onDocClick);
  window.removeEventListener("keydown", onKeydown);
});
</script>

<style scoped>
.container{
  width: min(1100px, calc(100% - 32px));
  margin: 0 auto;
}
.page{ padding: 14px 0 24px; }

.toast-stack{
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 80;
  display:flex;
  flex-direction: column;
  gap: 10px;
  width: min(360px, calc(100vw - 36px));
  pointer-events: none;
}
.toast{
  display:flex;
  align-items:flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,.10);
  background: rgba(255,255,255,.94);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.14);
  backdrop-filter: blur(10px);
  color: rgba(15,23,42,.86);
}
.toast.success{ border-color: rgba(16,185,129,.22); }
.toast.error{ border-color: rgba(239,68,68,.25); }
.toast-dot{
  width: 9px;
  height: 9px;
  margin-top: 5px;
  border-radius: 999px;
  background: #2563eb;
  flex: 0 0 auto;
}
.toast.success .toast-dot{ background: #10b981; }
.toast.error .toast-dot{ background: #ef4444; }
.toast-text{
  font-size: 13px;
  line-height: 1.45;
  font-weight: 800;
}

.topbar{
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid rgba(15, 23, 42, 0.10);
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.14), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.12), transparent 60%),
    rgba(255,255,255,0.78);
  backdrop-filter: blur(10px);
}

.topbar__inner{
  display:flex;
  align-items:center;
  gap: 12px;
  padding: 10px 0;
}

/* 品牌 */
.brand{
  display:flex;
  align-items:center;
  gap: 10px;
  text-decoration: none;
  color: rgba(15,23,42,.92);
  flex: 0 0 auto;
}
.brand__logo{
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  user-select:none;
}
.brand__text{ display:flex; flex-direction: column; line-height: 1.1; }
.brand__title{ font-weight: 1000; font-size: 16px; letter-spacing: .2px; }
.brand__sub{ margin-top: 2px; font-size: 11px; color: rgba(15,23,42,.55); font-weight: 900; }

/* 导航 */
.nav{
  flex: 1;
  display:flex;
  align-items:center;
  gap: 6px;
  overflow:auto;
  padding: 4px 4px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.08);
  background: rgba(255,255,255,0.55);
  scrollbar-width: none;
}
.nav::-webkit-scrollbar{ display:none; }
.nav__link{
  flex: 0 0 auto;
  text-decoration: none;
  font-weight: 900;
  font-size: 12px;
  color: rgba(15,23,42,.78);
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid transparent;
  transition: .15s;
  white-space: nowrap;
}
.nav__link:hover{ background: rgba(15,23,42,0.04); }
.nav__link.router-link-active{
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border-color: rgba(37,99,235,.16);
}

/* 右侧按钮区 */
.actions{
  display:flex;
  align-items:center;
  gap: 10px;
  flex: 0 0 auto;
}

/* 通用按钮 */
.btn{
  display:inline-flex;
  align-items:center;
  justify-content: center;
  gap: 8px;
  padding: 9px 12px;
  border-radius: 12px;
  font-weight: 1000;
  font-size: 12px;
  text-decoration: none;
  cursor: pointer;
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(255,255,255,0.70);
  color: rgba(15,23,42,.88);
  transition: .15s;
  white-space: nowrap;
}
.btn:hover{ transform: translateY(-1px); }
.btn:active{ transform: translateY(0px); }

.btn-ghost:hover{ background: rgba(15,23,42,0.04); }
.btn-primary{
  border: 0;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
}

/* 用户下拉 */
.user{ position: relative; }
.user-btn{
  display:flex;
  align-items:center;
  gap: 10px;
  padding: 7px 10px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(255,255,255,0.70);
  cursor: pointer;
  transition: .15s;
}
.user-btn:hover{ background: rgba(15,23,42,0.04); }

.avatar{
  width: 30px;
  height: 30px;
  border-radius: 12px;
  overflow: hidden;
  display:grid;
  place-items:center;
  flex: 0 0 auto;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(15,23,42,0.04);
}
.avatar img{ width:100%; height:100%; object-fit: cover; display:block; }
.avatar.placeholder{
  color:#fff;
  font-weight: 1000;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: 0;
}
.user-name{
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 1000;
  font-size: 12px;
  color: rgba(15,23,42,.88);
}
.chev{
  font-size: 12px;
  color: rgba(15,23,42,.55);
  transition: .15s;
}
.chev.open{ transform: rotate(180deg); }

.menu{
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 190px;
  border-radius: 16px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.92);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.12);
  overflow: hidden;
}

.menu-item{
  width: 100%;
  display:flex;
  align-items:center;
  gap: 10px;
  padding: 10px 12px;
  font-weight: 900;
  font-size: 12px;
  color: rgba(15,23,42,.86);
  text-decoration: none;
  background: transparent;
  border: 0;
  cursor: pointer;
  text-align: left;
}
.menu-item:hover{ background: rgba(15,23,42,0.04); }
.menu-divider{ height: 1px; background: rgba(15,23,42,0.10); }

.menu-item.danger{
  color: rgba(127,29,29,1);
}
.menu-item.danger:hover{
  background: rgba(239, 68, 68, 0.10);
}

/* 小屏适配 */
@media (max-width: 520px){
  .user-name{ display:none; }
}
</style>

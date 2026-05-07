<template>
  <div class="login-page">
    <div class="login-card">
      <div class="header">
        <div class="brand">
          <div class="logo">🔐</div>
          <div class="brand-text">
            <h3 class="title">登录</h3>
            <p class="sub">欢迎回来，输入账号密码继续</p>
          </div>
        </div>
      </div>

      <transition name="fade">
        <div v-if="errorMsg" class="alert" role="alert" aria-live="polite">
          <div class="alert-icon">!</div>
          <div class="alert-body">
            <div class="alert-title">登录失败</div>
            <div class="alert-text">{{ errorMsg }}</div>
          </div>
        </div>
      </transition>

      <div class="form">
        <label class="field">
          <span class="label">用户名</span>
          <input
            v-model="username"
            placeholder="请输入用户名"
            autocomplete="username"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            @keydown.enter="login"
          />
        </label>

        <label class="field">
          <span class="label">密码</span>
          <input
            v-model="password"
            placeholder="请输入密码"
            type="password"
            autocomplete="current-password"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            @keydown.enter="login"
          />
        </label>

        <button class="btn-primary" @click="login">登录</button>
        <button class="btn-demo" type="button" @click="demoLogin">使用手机演示账号</button>

        <div class="footer">
          <span>还没有账号？</span>
          <router-link class="link" to="/register">去注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "../api";

const router = useRouter();
const route = useRoute();
const username = ref("");
const password = ref("");
const errorMsg = ref("");

async function login() {
  errorMsg.value = "";
  const normalizedUsername = username.value.trim().toLowerCase();
  try {
    const res = await api.post("/auth/login/", {
      username: normalizedUsername,
      password: password.value,
    });

    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);

    // ✅ 视觉更好：不用 alert 打断体验
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    router.push(redirect.startsWith("/") ? redirect : "/");
  } catch (err) {
    if (!err?.response) {
      errorMsg.value = "连接服务器失败，请确认手机和电脑在同一网络，并使用电脑局域网地址访问。";
      return;
    }
    errorMsg.value = "用户名或密码错误，请检查后重试。";
  }
}

function demoLogin() {
  username.value = "zhouqian";
  password.value = "12345678";
  login();
}
</script>

<style scoped>
.login-page{
  min-height: calc(100vh - 72px);
  display: grid;
  place-items: center;
  padding: 28px 16px;
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.18), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.16), transparent 60%),
    #f6f7fb;
}

.login-card{
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 16px 40px rgba(2, 6, 23, 0.10);
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.header{
  padding: 18px 18px 10px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  background: linear-gradient(135deg, rgba(59,130,246,.10), rgba(37,99,235,.06));
}

.brand{
  display:flex;
  align-items:center;
  gap: 12px;
}

.logo{
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display:grid;
  place-items:center;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.25);
  user-select:none;
}

.title{
  margin: 0;
  font-size: 18px;
  letter-spacing: .2px;
}

.sub{
  margin: 3px 0 0;
  font-size: 13px;
  color: rgba(15,23,42,.65);
}

.form{
  padding: 16px 18px 18px;
  display:flex;
  flex-direction: column;
  gap: 12px;
}

.field{
  display:flex;
  flex-direction: column;
  gap: 6px;
}

.label{
  font-size: 12px;
  color: rgba(15,23,42,.70);
}

input{
  width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.14);
  background: rgba(255,255,255,0.92);
  outline: none;
  transition: .15s;
  font-size: 14px;
}

input:focus{
  border-color: rgba(59,130,246,0.60);
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}

.btn-primary{
  margin-top: 4px;
  width: 100%;
  padding: 11px 12px;
  border: 0;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.22);
  transition: .15s;
}

.btn-primary:hover{ transform: translateY(-1px); }
.btn-primary:active{ transform: translateY(0px); }

.btn-demo{
  width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(37,99,235,.18);
  background: rgba(37,99,235,.08);
  color: #2563eb;
  cursor: pointer;
  font-weight: 900;
}
.btn-demo:hover{ background: rgba(37,99,235,.12); }

.footer{
  margin-top: 6px;
  display:flex;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(15,23,42,.65);
}

.link{
  color: #2563eb;
  text-decoration: none;
  font-weight: 700;
}
.link:hover{ text-decoration: underline; }

.alert{
  margin: 12px 18px 0;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(239, 68, 68, 0.25);
  background: rgba(254, 226, 226, 0.80);
  display:flex;
  gap: 10px;
  align-items:flex-start;
}

.alert-icon{
  width: 22px;
  height: 22px;
  border-radius: 999px;
  display:grid;
  place-items:center;
  font-weight: 900;
  color: #b91c1c;
  background: rgba(239, 68, 68, 0.18);
  user-select:none;
  flex: 0 0 auto;
}

.alert-title{
  font-size: 13px;
  font-weight: 800;
  color: #7f1d1d;
  margin-bottom: 2px;
}

.alert-text{
  font-size: 12px;
  color: rgba(127, 29, 29, 0.95);
  line-height: 1.45;
  word-break: break-word;
}

.fade-enter-active, .fade-leave-active{ transition: opacity .15s; }
.fade-enter-from, .fade-leave-to{ opacity: 0; }
</style>

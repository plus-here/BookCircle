<template>
  <div class="register-page">
    <div class="register-card">
      <div class="header">
        <div class="brand">
          <div class="logo">📚</div>
          <div class="brand-text">
            <h3 class="title">创建账号</h3>
            <p class="sub">加入书圈，开始你的阅读之旅</p>
          </div>
        </div>
      </div>

      <transition name="fade">
        <div v-if="errorMsg" class="alert" role="alert" aria-live="polite">
          <div class="alert-icon">!</div>
          <div class="alert-body">
            <div class="alert-title">注册失败</div>
            <div class="alert-text">{{ errorMsg }}</div>
          </div>
        </div>
      </transition>

      <div class="form">
        <label class="field">
          <span class="label">用户名</span>
          <input v-model="username" placeholder="例如：booklover_01" autocomplete="username" />
        </label>

        <label class="field">
          <span class="label">邮箱</span>
          <input v-model="email" placeholder="例如：name@example.com" autocomplete="email" />
        </label>

        <label class="field">
          <span class="label">密码</span>
          <input v-model="password" placeholder="至少 8 位" type="password" autocomplete="new-password" />
        </label>

        <label class="field">
          <span class="label">确认密码</span>
          <input v-model="password2" placeholder="再输入一次密码" type="password" autocomplete="new-password" />
        </label>

        <div class="tips">
          密码建议：至少 8 位，避免全数字、避免过于常见密码。
        </div>

        <button class="btn-primary" @click="register">
          注册
        </button>

        <div class="footer">
          <span>已有账号？</span>
          <router-link class="link" to="/login">去登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";

const router = useRouter();

const username = ref("");
const email = ref("");
const password = ref("");
const password2 = ref("");

const errorMsg = ref("");
// ① 英文错误 → 中文兜底翻译
function translateError(msg) {
  if (!msg) return msg;

  // 精确匹配（完全相同的句子）
  const exactMap = {
    "This field may not be blank.": "不能为空",
    "This field is required.": "必填项",
    "Enter a valid email address.": "邮箱格式不正确",
    "User with this username already exists.": "用户名已存在",
    "User with this email already exists.": "邮箱已存在",
    "A user with that username already exists.": "用户名已存在",
    "A user with that email already exists.": "邮箱已存在",
  };
  if (exactMap[msg]) return exactMap[msg];

  // 规则匹配（包含某些关键词的句子）
  const rules = [
    { test: (m) => m.includes("too short") && m.includes("at least"), to: "密码太短（至少 8 位）" },
    { test: (m) => m.includes("too common"), to: "密码太常见，请换一个更复杂的密码" },
    { test: (m) => m.includes("entirely numeric"), to: "密码不能全是数字" },
    { test: (m) => m.includes("didn't match") || m.includes("did not match"), to: "两次输入的密码不一致" },
    { test: (m) => m.includes("valid email") || m.includes("valid email address"), to: "邮箱格式不正确" },
  ];

  for (const r of rules) {
    if (r.test(msg)) return r.to;
  }

  // 不认识的就原样返回（至少不丢信息）
  return msg;
}

function formatErrors(data) {
  if (!data || typeof data !== "object") return "注册失败，请检查输入。";

  const fieldNameMap = {
    username: "用户名",
    email: "邮箱",
    password: "密码",
    password2: "确认密码",
    detail: "错误",
    non_field_errors: "错误",
  };

  const parts = [];
  for (const [k, v] of Object.entries(data)) {
    const label = fieldNameMap[k] || k;

    if (Array.isArray(v)) {
      parts.push(`${label}：${v.map(translateError).join("；")}`);
    } else if (typeof v === "string") {
      parts.push(`${label}：${translateError(v)}`);
    } else {
      parts.push(`${label}：${translateError(JSON.stringify(v))}`);
    }
  }
  return parts.length ? parts.join(" | ") : "注册失败，请检查输入。";
}


async function register() {
  errorMsg.value = "";
  try {
    await api.post("/auth/register/", {
      username: username.value,
      email: email.value,
      password: password.value,
      password2: password2.value,
    });
    alert("注册成功，请登录");
    router.push("/login");
  } catch (e) {
    errorMsg.value = formatErrors(e?.response?.data);
  }
}
</script>


<style scoped>
.register-page{
  min-height: calc(100vh - 72px);
  display: grid;
  place-items: center;
  padding: 28px 16px;
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.18), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.16), transparent 60%),
    #f6f7fb;
}

.register-card{
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

.tips{
  font-size: 12px;
  color: rgba(15,23,42,.62);
  background: rgba(15,23,42,.03);
  border: 1px dashed rgba(15,23,42,.10);
  padding: 10px 12px;
  border-radius: 12px;
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

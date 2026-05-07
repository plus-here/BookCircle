<template>
  <div class="wrap">
    <div class="panel">
      <div class="brand">
        <div class="logo">📚</div>
        <div>
          <div class="title">BookCircle Admin</div>
          <div class="sub">使用 Django 管理员账号登录（需 staff 权限）</div>
        </div>
      </div>

      <el-form :model="form" label-position="top" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="admin" clearable />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="••••••••" />
        </el-form-item>

        <el-button type="primary" :loading="loading" style="width:100%;" @click="doLogin">
          登录
        </el-button>
      </el-form>

      <div v-if="err" class="err">{{ err }}</div>

      <div class="tip">
        提示：如果登录失败，请确认账号具备 <b>staff</b> 权限（后端控制）。
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const form = reactive({ username: "", password: "" });
const loading = ref(false);
const err = ref("");

async function doLogin() {
  err.value = "";
  loading.value = true;
  try {
    await auth.login(form.username, form.password);
    ElMessage.success("登录成功");
    router.push("/");
  } catch (e) {
    err.value = e?.response?.data?.detail || "登录失败：用户名/密码错误或无权限";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.wrap{
  min-height: 100vh;
  display:grid;
  place-items:center;
  padding: 18px;
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.18), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.16), transparent 60%),
    var(--bg);
}

.panel{
  width: min(440px, 100%);
  padding: 20px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--card);
  box-shadow: var(--shadow);
}

.brand{
  display:flex;
  align-items:center;
  gap: 12px;
  margin-bottom: 16px;
}
.logo{
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display:grid;
  place-items:center;
  background: rgba(37,99,235,.12);
  border: 1px solid rgba(37,99,235,.18);
  user-select:none;
}
.title{
  font-weight: 1000;
  font-size: 18px;
  letter-spacing: .2px;
}
.sub{
  margin-top: 4px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.4;
}

.err{
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.10);
  border: 1px solid rgba(239, 68, 68, 0.18);
  color: rgba(127,29,29,1);
  font-weight: 900;
  font-size: 12px;
}

.tip{
  margin-top: 12px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.5;
}
</style>

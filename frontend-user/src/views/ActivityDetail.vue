<template>
  <div class="page">
    <!-- 顶部 -->
    <div class="hero">
      <div>
        <h3 class="h1">活动详情</h3>
        <p class="sub">查看活动信息并进行报名。</p>
      </div>

      <div class="hero-right">
        <router-link class="btn-ghost" to="/activities">返回列表</router-link>
        <router-link class="btn-ghost" to="/my-activities">我的报名</router-link>
        <button class="btn-primary" :disabled="loading" @click="load">
          {{ loading ? "刷新中..." : "刷新" }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="card pad">
      <div class="skeleton title"></div>
      <div class="skeleton line w55"></div>
      <div class="skeleton line w85"></div>
      <div class="divider"></div>
      <div class="skeleton block"></div>
      <div class="row" style="margin-top:12px;">
        <div class="skeleton btn"></div>
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="!item" class="card pad">
      <div class="empty">
        <div class="empty-icon">📭</div>
        <div class="empty-title">未找到活动</div>
        <div class="empty-sub">请返回活动列表重新选择。</div>
        <router-link class="btn-primary" to="/activities">回到活动列表</router-link>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="stack">
      <!-- 主信息 -->
      <div class="card pad">
        <div class="top">
          <div class="title">{{ item.title }}</div>
          <span class="badge">#{{ item.id }}</span>
        </div>

        <div class="meta">
          <div class="meta-row">
            <span class="meta-dot"></span>
            <span class="muted">开始：{{ fmt(item.start_time) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-dot"></span>
            <span class="muted">结束：{{ fmt(item.end_time) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-dot"></span>
            <span class="muted">地点：{{ item.location || "-" }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-dot"></span>
            <span class="muted">名额：{{ slotLabel(item) }}</span>
          </div>
        </div>

        <div class="desc">
          {{ item.description || "（暂无描述）" }}
        </div>

        <div class="actions">
          <router-link v-if="!hasToken" class="btn-primary" :to="loginTarget">
            登录后报名
          </router-link>
          <button v-else-if="isSigned" class="btn-danger" @click="cancelSignup" :disabled="cancelling">
            {{ cancelling ? "取消中..." : "取消报名" }}
          </button>
          <button v-else class="btn-primary" @click="signup" :disabled="signing || item.is_full">
            {{ item.is_full ? "名额已满" : signing ? "报名中..." : "我要报名" }}
          </button>
          <span v-if="isSigned" class="msg success">已报名</span>
          <div class="msg" v-if="msg">{{ msg }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api";

const route = useRoute();
const id = computed(() => route.params.id);

const item = ref(null);
const signedSignup = ref(null);
const loading = ref(false);
const signing = ref(false);
const cancelling = ref(false);
const msg = ref("");
const hasToken = computed(() => !!localStorage.getItem("access"));
const isSigned = computed(() => signedSignup.value?.status === "signed");
const loginTarget = computed(() => ({ path: "/login", query: { redirect: route.fullPath } }));

function fmt(v) {
  if (!v) return "-";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v).replace("T", " ").replace("Z", "") : d.toLocaleString();
}

async function load() {
  loading.value = true;
  msg.value = "";
  signedSignup.value = null;
  try {
    const res = await api.get(`/activities/${id.value}/`);
    item.value = res.data;
    if (hasToken.value) await loadMySignup();
  } catch (e) {
    item.value = null;
    msg.value = "加载失败";
  } finally {
    loading.value = false;
  }
}

function slotLabel(activity) {
  const signed = activity?.signed_count || 0;
  if (!activity?.capacity) return `${signed} 人已报名，不限名额`;
  if (activity.is_full) return `${signed}/${activity.capacity}，名额已满`;
  return `${signed}/${activity.capacity}，剩余 ${activity.remaining_slots} 位`;
}

async function loadMySignup() {
  try {
    const res = await api.get("/activities/my/signups/");
    signedSignup.value = (res.data || []).find((s) => String(s.activity) === String(id.value)) || null;
  } catch {
    signedSignup.value = null;
  }
}

async function signup() {
  if (!hasToken.value) {
    msg.value = "请先登录后再报名";
    return;
  }
  signing.value = true;
  msg.value = "";
  try {
    const res = await api.post(`/activities/${id.value}/signup/`);
    signedSignup.value = res.data;
    msg.value = "报名成功";
  } catch (e) {
    msg.value =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      "报名失败（可能已报名/不允许报名）";
  } finally {
    signing.value = false;
  }
}

async function cancelSignup() {
  cancelling.value = true;
  msg.value = "";
  try {
    await api.post(`/activities/${id.value}/signup/cancel/`);
    signedSignup.value = null;
    msg.value = "已取消报名";
  } catch (e) {
    msg.value = e?.response?.data?.detail || "取消报名失败";
  } finally {
    cancelling.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.page{ display:flex; flex-direction: column; gap: 14px; padding: 6px 0 24px; }
.stack{ display:flex; flex-direction: column; gap: 14px; }

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.sub{ margin: 6px 0 0; font-size: 13px; color: rgba(15,23,42,.65); line-height: 1.5; }
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.hero{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.18), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.16), transparent 60%),
    rgba(255,255,255,0.75);
  backdrop-filter: blur(10px);
}
.hero-right{ display:flex; align-items:center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }

.btn-primary{
  display:inline-flex; align-items:center; justify-content:center;
  text-decoration:none;
  border: 0; cursor: pointer; font-weight: 900;
  padding: 10px 12px; border-radius: 12px; color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  transition: .15s; white-space: nowrap;
}
.btn-primary:hover{ transform: translateY(-1px); }
.btn-primary:active{ transform: translateY(0px); }
.btn-primary:disabled{ opacity:.6; cursor:not-allowed; transform:none; }

.btn-danger{
  border: 1px solid rgba(239,68,68,.22);
  cursor: pointer;
  font-weight: 900;
  padding: 10px 12px;
  border-radius: 12px;
  color: rgba(127,29,29,1);
  background: rgba(239,68,68,.10);
  transition: .15s;
  white-space: nowrap;
}
.btn-danger:hover{ transform: translateY(-1px); background: rgba(239,68,68,.14); }
.btn-danger:disabled{ opacity:.6; cursor:not-allowed; transform:none; }

.btn-ghost{
  display:inline-flex;
  align-items:center;
  justify-content: center;
  text-decoration: none;
  font-weight: 900;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15,23,42,0.14);
  color: rgba(15,23,42,.88);
  background: rgba(255,255,255,0.70);
  transition: .15s;
  white-space: nowrap;
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

.top{ display:flex; align-items:flex-start; justify-content: space-between; gap: 10px; }
.title{ font-weight: 1000; font-size: 18px; line-height: 1.2; }
.badge{
  flex: 0 0 auto;
  font-size: 11px; font-weight: 900;
  padding: 4px 8px; border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}

.meta{ margin-top: 10px; display:flex; flex-direction: column; gap: 6px; }
.meta-row{ display:flex; align-items:center; gap: 8px; }
.meta-dot{ width: 6px; height: 6px; border-radius: 999px; background: rgba(37,99,235,.55); }

.desc{
  margin-top: 12px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
  white-space: pre-wrap;
  line-height: 1.6;
  color: rgba(15,23,42,.85);
  font-size: 14px;
}

.actions{
  margin-top: 14px;
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items:center;
}
.msg{
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid rgba(37,99,235,.18);
  background: rgba(37,99,235,.08);
  color: rgba(15,23,42,.75);
  font-size: 12px;
  font-weight: 900;
}
.msg.success{
  border-color: rgba(16,185,129,.22);
  background: rgba(16,185,129,.10);
  color: rgba(6,95,70,1);
}

.empty{ text-align: center; }
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

.divider{ height: 1px; background: rgba(15,23,42,0.10); margin: 12px 0; }
.row{ display:flex; gap: 10px; align-items:center; }

.skeleton{ position: relative; background: rgba(15,23,42,0.06); border-radius: 12px; overflow: hidden; }
.skeleton::after{
  content:""; position:absolute; inset:0; transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
  animation: shimmer 1.1s infinite;
}
.skeleton.title{ height: 18px; width: 70%; }
.skeleton.line{ height: 10px; margin-top: 10px; }
.skeleton.block{ height: 80px; margin-top: 10px; border-radius: 14px; }
.skeleton.btn{ height: 38px; width: 120px; border-radius: 12px; }
.w55{ width: 55%; } .w85{ width: 85%; }
@keyframes shimmer{ 100%{ transform: translateX(100%); } }
</style>

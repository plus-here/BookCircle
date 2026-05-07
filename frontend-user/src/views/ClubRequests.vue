<template>
  <div class="page">
    <!-- 顶部栏 -->
    <div class="hero">
      <div>
        <h3 class="h1">入社申请审批</h3>
        <p class="sub">只有社团 owner / admin 才能访问并处理申请。</p>
      </div>

      <div class="hero-right">
        <div class="pill">
          <span class="dot"></span>
          <span>待审批 {{ requests.length }} 条</span>
        </div>

        <button class="btn-primary" :disabled="loading" @click="load">
          {{ loading ? "刷新中..." : "刷新" }}
        </button>
      </div>
    </div>

    <!-- 权限提示卡 -->
    <div class="notice card pad">
      <div class="notice-icon">🛡️</div>
      <div class="notice-body">
        <div class="notice-title">权限说明</div>
        <div class="notice-sub">
          只有社团管理员可以查看和处理入社申请。
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid">
      <div v-for="i in 4" :key="i" class="card pad skeleton">
        <div class="sk-line w60"></div>
        <div class="sk-line w85"></div>
        <div class="sk-line w70"></div>
        <div class="row" style="margin-top:12px;">
          <div class="sk-btn"></div>
          <div class="sk-btn ghost"></div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-else>
      <div v-if="requests.length === 0" class="empty card pad">
        <div class="empty-icon">✅</div>
        <div class="empty-title">暂无待审批申请</div>
        <div class="empty-sub">当有新申请时会出现在这里。</div>
      </div>

      <div v-else class="grid">
        <div class="req card pad" v-for="r in requests" :key="r.id">
          <div class="req-top">
            <div class="req-user">
              <div class="avatar">{{ (r.user_username || "U").charAt(0).toUpperCase() }}</div>
              <div class="req-user-info">
                <div class="req-name">
                  {{ r.user_username }}
                  <span class="small">（user_id: {{ r.user }}）</span>
                </div>
                <div class="req-meta">
                  <span class="meta-dot"></span>
                  <span>申请时间：{{ formatTime(r.created_at) }}</span>
                </div>
              </div>
            </div>

            <div class="badge">申请 #{{ r.id }}</div>
          </div>

          <div class="reason">
            <div class="reason-title">理由</div>
            <div class="reason-text">{{ r.reason || "无" }}</div>
          </div>

          <div class="actions">
            <button class="btn-approve" :disabled="loading" @click="approve(r.id)">通过</button>
            <button class="btn-reject" :disabled="loading" @click="reject(r.id)">拒绝</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api";

const route = useRoute();
const clubId = route.params.id;

const loading = ref(false);
const requests = ref([]);

async function load() {
  loading.value = true;
  try {
    requests.value = (await api.get(`/clubs/${clubId}/requests/`)).data;
  } catch (e) {
    alert("加载失败：你可能不是社团管理员，或未登录");
    requests.value = [];
  } finally {
    loading.value = false;
  }
}

async function approve(requestId) {
  await api.post(`/requests/${requestId}/approve/`);
  alert("已通过");
  await load();
}

async function reject(requestId) {
  await api.post(`/requests/${requestId}/reject/`);
  alert("已拒绝");
  await load();
}

function formatTime(v) {
  if (!v) return "";
  return String(v).replace("T", " ").replace("Z", "");
}

onMounted(load);
</script>

<style scoped>
.page{
  display:flex;
  flex-direction: column;
  gap: 14px;
  padding: 6px 0 24px;
}

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.sub{
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}
.small{ font-size: 12px; color: rgba(15,23,42,.60); }

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.row{ display:flex; gap: 10px; align-items:center; flex-wrap: wrap; }

/* hero */
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
.hero-right{ display:flex; align-items:center; gap: 10px; }

.pill{
  display:flex;
  align-items:center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.70);
  box-shadow: 0 10px 22px rgba(2, 6, 23, 0.06);
  font-size: 12px;
  color: rgba(15,23,42,.75);
  white-space: nowrap;
}
.dot{
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.btn-primary{
  border: 0;
  cursor: pointer;
  font-weight: 900;
  padding: 10px 12px;
  border-radius: 12px;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  transition: .15s;
  white-space: nowrap;
}
.btn-primary:hover{ transform: translateY(-1px); }
.btn-primary:active{ transform: translateY(0px); }
.btn-primary:disabled{
  opacity: .6;
  cursor: not-allowed;
  transform: none;
}

/* notice */
.notice{
  display:flex;
  gap: 12px;
  align-items:flex-start;
}
.notice-icon{
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  flex: 0 0 auto;
}
.notice-title{ font-weight: 1000; }
.notice-sub{
  margin-top: 4px;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}

/* grid */
.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 760px){
  .grid{ grid-template-columns: 1fr; }
}

/* request card */
.req{ display:flex; flex-direction: column; gap: 12px; transition: .15s; }
.req:hover{
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08);
}

.req-top{
  display:flex;
  align-items:flex-start;
  justify-content: space-between;
  gap: 10px;
}
.req-user{
  display:flex;
  gap: 10px;
  align-items:center;
  min-width: 0;
}
.avatar{
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  font-weight: 1000;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  flex: 0 0 auto;
  user-select:none;
}
.req-user-info{ min-width: 0; }
.req-name{
  font-weight: 1000;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.req-meta{
  margin-top: 4px;
  display:flex;
  align-items:center;
  gap: 8px;
  font-size: 12px;
  color: rgba(15,23,42,.60);
}
.meta-dot{
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: rgba(37,99,235,.55);
}
.badge{
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 900;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}

/* reason */
.reason{
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
}
.reason-title{ font-weight: 1000; font-size: 12px; color: rgba(15,23,42,.75); }
.reason-text{ margin-top: 6px; font-size: 13px; color: rgba(15,23,42,.82); line-height: 1.55; word-break: break-word; }

/* actions */
.actions{ display:flex; gap: 10px; flex-wrap: wrap; }

.btn-approve{
  border: 0;
  cursor: pointer;
  font-weight: 1000;
  padding: 10px 12px;
  border-radius: 12px;
  color: #065f46;
  background: rgba(16,185,129,0.14);
  border: 1px solid rgba(16,185,129,0.20);
  transition: .15s;
}
.btn-approve:hover{ background: rgba(16,185,129,0.18); }

.btn-reject{
  border: 0;
  cursor: pointer;
  font-weight: 1000;
  padding: 10px 12px;
  border-radius: 12px;
  color: #7f1d1d;
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.20);
  transition: .15s;
}
.btn-reject:hover{ background: rgba(239, 68, 68, 0.18); }

.btn-approve:disabled,
.btn-reject:disabled{
  opacity: .6;
  cursor: not-allowed;
}

/* empty */
.empty{ text-align: center; }
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

/* skeleton */
.skeleton{ position: relative; overflow: hidden; }
.skeleton::after{
  content:"";
  position:absolute;
  inset:0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
  animation: shimmer 1.1s infinite;
}
.sk-line{
  height: 10px;
  border-radius: 999px;
  background: rgba(15,23,42,0.06);
  margin-top: 10px;
}
.sk-btn{
  height: 36px;
  width: 110px;
  border-radius: 12px;
  background: rgba(15,23,42,0.06);
}
.sk-btn.ghost{ width: 92px; }

.w60{ width: 60%; }
.w85{ width: 85%; }
.w70{ width: 70%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

<template>
  <div class="page">
    <!-- Loading -->
    <div v-if="loading" class="card pad">
      <div class="skeleton title"></div>
      <div class="skeleton line w55"></div>
      <div class="skeleton line w85"></div>
      <div class="divider"></div>
      <div class="skeleton block"></div>
      <div class="skeleton block short"></div>
    </div>

    <!-- Content -->
    <div v-else-if="club" class="stack">
      <!-- 社团信息 -->
      <div class="hero">
        <div class="hero-top">
          <div class="hero-name" :title="club.name">{{ club.name }}</div>
          <div class="hero-tags">
            <span class="tag">成员 {{ club.members_count }}</span>
            <span class="tag gray">团长 {{ club.owner_username }}</span>
          </div>
        </div>

        <div class="hero-desc">
          {{ club.description || "暂无简介。" }}
        </div>
      </div>

      <div class="card pad">
        <div class="section-head">
          <h4 class="h2">成员</h4>
          <div class="muted">展示最近加入的 {{ members.length }} 位成员</div>
        </div>
        <div v-if="members.length === 0" class="empty compact">
          <div class="empty-title">暂无成员信息</div>
          <div class="empty-sub">成员加入后会显示在这里。</div>
        </div>
        <div v-else class="member-grid">
          <div v-for="m in members" :key="m.id" class="member">
            <div class="member-avatar">{{ (m.user_username || "?").charAt(0).toUpperCase() }}</div>
            <div class="member-body">
              <div class="member-name">{{ m.user_username }}</div>
              <div class="member-role">{{ roleLabel(m.role) }} · {{ fmtDate(m.joined_at) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的状态 / 申请加入 -->
      <div v-if="statusLoaded" class="status card pad">
        <!-- 已加入 -->
        <div v-if="meStatus.is_member" class="status-row">
          <div class="status-icon ok">✓</div>
          <div class="status-body">
            <div class="status-title">你已加入该社团</div>
            <div class="status-sub">
              角色：<b>{{ meStatus.role }}</b>
              <span v-if="isAdmin">
                · <router-link class="link" :to="`/clubs/${club.id}/requests`">审批入社申请</router-link>
              </span>
            </div>
          </div>
        </div>

        <!-- 待审批 -->
        <div v-else-if="meStatus.join_request_status === 'pending'" class="status-row">
          <div class="status-icon warn">⏳</div>
          <div class="status-body">
            <div class="status-title">申请已提交</div>
            <div class="status-sub">等待管理员审批，通过后即可进入社团活动。</div>
          </div>
        </div>

        <!-- 未加入：申请 -->
        <div v-else class="apply">
          <div class="apply-title">申请加入社团</div>
          <div class="apply-sub">可以填写简单理由（可选），例如：想一起读书交流。</div>

          <div class="apply-row">
            <div class="input-wrap">
              <span class="icon">✍️</span>
              <input v-model="reason" class="input" placeholder="申请理由（可选）" />
            </div>
            <button class="btn-primary" @click="apply">提交申请</button>
          </div>
        </div>
      </div>

      <!-- 未登录提示 -->
      <div v-else class="notice card pad">
        <div class="notice-row">
          <div class="status-icon gray">🔒</div>
          <div class="status-body">
            <div class="status-title">未登录</div>
            <div class="status-sub">
              未登录时无法显示入社状态。你可以先去 <router-link class="link" to="/login">登录</router-link> 再回来查看。
            </div>
          </div>
        </div>
      </div>

      <!-- 板块 -->
      <div class="card pad">
        <div class="section-head">
          <h4 class="h2">板块</h4>
          <div class="muted">共 {{ sections.length }} 个</div>
        </div>

        <div v-if="sections.length === 0" class="empty">
          <div class="empty-icon">🧩</div>
          <div class="empty-title">暂无板块</div>
          <div class="empty-sub">管理员创建板块后，大家就可以在里面发帖交流。</div>
        </div>

        <div v-else class="grid">
          <div class="sec" v-for="s in sections" :key="s.id">
            <div class="sec-name" :title="s.name">{{ s.name }}</div>
            <div class="sec-sub">点击进入查看帖子与讨论</div>
            <router-link class="link-btn" :to="`/sections/${s.id}/posts`">进入板块 →</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="card pad">
      <div class="empty">
        <div class="empty-icon">📭</div>
        <div class="empty-title">没有找到该社团</div>
        <div class="empty-sub">请返回社团列表重新选择。</div>
        <router-link class="btn-ghost" to="/clubs">返回社团列表</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api";

const route = useRoute();
const loading = ref(false);

const club = ref(null);
const sections = ref([]);
const members = ref([]);

const reason = ref("");

const statusLoaded = ref(false);
const meStatus = ref({
  is_member: false,
  role: null,
  join_request_status: null,
  join_request_id: null,
});

const isAdmin = computed(() => ["owner", "admin"].includes(meStatus.value.role || ""));

function roleLabel(role) {
  return { owner: "团长", admin: "管理员", member: "成员" }[role] || "成员";
}

function fmtDate(v) {
  if (!v) return "-";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v).replace("T", " ").replace("Z", "") : d.toLocaleDateString();
}

async function load() {
  loading.value = true;
  try {
    const id = route.params.id;
    club.value = (await api.get(`/clubs/${id}/`)).data;
    sections.value = (await api.get(`/clubs/${id}/sections/`)).data;
    members.value = (await api.get(`/clubs/${id}/members/`)).data;

    // 如果已登录，获取我在社团的状态（未登录会 401，我们就忽略）
    try {
      const st = await api.get(`/clubs/${id}/me/`);
      meStatus.value = st.data;
      statusLoaded.value = true;
    } catch {
      statusLoaded.value = false;
    }
  } finally {
    loading.value = false;
  }
}

async function apply() {
  try {
    const id = route.params.id;
    await api.post(`/clubs/${id}/join/`, { reason: reason.value });
    alert("申请已提交（待审批）");
    await load();
  } catch {
    alert("申请失败：可能未登录/已是成员/已申请过");
  }
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

.stack{ display:flex; flex-direction: column; gap: 14px; }
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.h2{ margin: 0; font-size: 16px; }

/* hero */
.hero{
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.18), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.16), transparent 60%),
    rgba(255,255,255,0.75);
  backdrop-filter: blur(10px);
}
.hero-top{
  display:flex;
  align-items:flex-start;
  justify-content: space-between;
  gap: 10px;
}
.hero-name{
  font-weight: 1000;
  font-size: 18px;
  letter-spacing: .2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
.hero-tags{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  flex: 0 0 auto;
}
.tag{
  font-size: 11px;
  font-weight: 900;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}
.tag.gray{
  color: rgba(15,23,42,.70);
  background: rgba(15,23,42,.06);
  border-color: rgba(15,23,42,.10);
}
.hero-desc{
  margin-top: 10px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
  font-size: 13px;
  line-height: 1.55;
  color: rgba(15,23,42,.82);
}

/* status */
.status-row, .notice-row{
  display:flex;
  gap: 12px;
  align-items:flex-start;
}
.status-icon{
  width: 34px;
  height: 34px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  font-weight: 1000;
  user-select:none;
  flex: 0 0 auto;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
}
.status-icon.ok{
  color: rgba(16,185,129,1);
  background: rgba(16,185,129,.10);
  border-color: rgba(16,185,129,.16);
}
.status-icon.warn{
  color: rgba(245,158,11,1);
  background: rgba(245,158,11,.10);
  border-color: rgba(245,158,11,.18);
}
.status-icon.gray{
  color: rgba(15,23,42,.70);
  background: rgba(15,23,42,.06);
  border-color: rgba(15,23,42,.10);
}

.status-title{ font-weight: 1000; }
.status-sub{
  margin-top: 4px;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}
.link{
  color: #2563eb;
  text-decoration: none;
  font-weight: 900;
}
.link:hover{ text-decoration: underline; }

/* apply */
.apply-title{ font-weight: 1000; }
.apply-sub{
  margin-top: 4px;
  font-size: 13px;
  color: rgba(15,23,42,.65);
}
.apply-row{
  margin-top: 10px;
  display:flex;
  gap: 10px;
  align-items:center;
  flex-wrap: wrap;
}
.input-wrap{
  flex: 1;
  min-width: 240px;
  display:flex;
  align-items:center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.14);
  background: rgba(255,255,255,0.92);
  transition: .15s;
}
.input-wrap:focus-within{
  border-color: rgba(59,130,246,0.60);
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}
.icon{ opacity: .75; user-select:none; }
.input{
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  font-size: 14px;
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
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

/* sections */
.section-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.grid{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 900px){
  .grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px){
  .grid{ grid-template-columns: 1fr; }
}
.sec{
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.70);
  transition: .15s;
}
.sec:hover{
  transform: translateY(-1px);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.sec-name{
  font-weight: 1000;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sec-sub{
  margin-top: 6px;
  font-size: 12px;
  color: rgba(15,23,42,.62);
  min-height: 32px;
}

.link-btn{
  margin-top: 10px;
  display:inline-flex;
  align-items:center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 900;
  font-size: 12px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.08);
  border: 1px solid rgba(37,99,235,.18);
  transition: .15s;
}
.link-btn:hover{ background: rgba(37,99,235,.12); }

.member-grid{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.member{
  display:flex;
  align-items:center;
  gap: 10px;
  padding: 10px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
}
.member-avatar{
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display:grid;
  place-items:center;
  color:#fff;
  font-weight: 1000;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  flex: 0 0 auto;
}
.member-body{ min-width: 0; }
.member-name{
  font-weight: 1000;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.member-role{
  margin-top: 2px;
  color: rgba(15,23,42,.60);
  font-size: 12px;
}
@media (max-width: 900px){
  .member-grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px){
  .member-grid{ grid-template-columns: 1fr; }
}

/* empty */
.empty{
  padding: 18px;
  border-radius: 16px;
  border: 1px dashed rgba(15, 23, 42, 0.16);
  background: rgba(255,255,255,0.70);
  text-align: center;
}
.empty.compact{ padding: 12px; }
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

.divider{
  height: 1px;
  background: rgba(15,23,42,0.10);
  margin: 12px 0;
}

/* skeleton */
.skeleton{
  position: relative;
  background: rgba(15,23,42,0.06);
  border-radius: 12px;
  overflow: hidden;
}
.skeleton::after{
  content:"";
  position:absolute;
  inset:0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
  animation: shimmer 1.1s infinite;
}
.skeleton.title{ height: 18px; width: 60%; }
.skeleton.line{ height: 10px; margin-top: 10px; }
.skeleton.block{ height: 70px; margin-top: 10px; border-radius: 14px; }
.skeleton.block.short{ height: 52px; }

.w55{ width: 55%; }
.w85{ width: 85%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

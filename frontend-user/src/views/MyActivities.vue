<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">我的活动</div>
        <h1 class="ux-title">管理已经报名的阅读活动</h1>
        <p class="ux-lead">集中查看报名记录、活动入口和报名时间，方便你回到对应活动继续确认安排。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ items.length }} 条报名</div>
        <router-link class="btn-ghost" to="/activities">活动列表</router-link>
        <button class="btn-primary" :disabled="!hasToken || loading" @click="load">
          {{ loading ? "刷新中..." : "刷新记录" }}
        </button>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">报名总数</div>
        <div class="ux-stat__value">{{ items.length }}</div>
        <div class="ux-stat__hint">你参与过的活动</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">最近报名</div>
        <div class="ux-stat__value">{{ latestSignup }}</div>
        <div class="ux-stat__hint">快速判断记录是否更新</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">活动入口</div>
        <div class="ux-stat__value">{{ uniqueActivityCount }}</div>
        <div class="ux-stat__hint">可跳转查看详情</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">账号状态</div>
        <div class="ux-stat__value">{{ hasToken ? "正常" : "未登录" }}</div>
        <div class="ux-stat__hint">登录后同步报名</div>
      </div>
    </section>

    <section v-if="!hasToken" class="ux-empty">
      <div class="ux-empty__icon">登</div>
      <div class="ux-empty__title">登录后查看报名记录</div>
      <div class="ux-empty__sub">报名记录会跟随账号保存，登录后可以继续查看活动详情。</div>
      <div class="ux-actions">
        <router-link class="ux-link" to="/login">去登录 →</router-link>
      </div>
    </section>

    <section v-else class="ux-panel">
      <div class="ux-panel__head">
        <div>
          <h2 class="ux-section-title">报名记录</h2>
          <div class="ux-section-sub">按报名时间展示，点击可回到活动详情页。</div>
        </div>
      </div>

      <div v-if="loading" class="ux-grid">
        <div v-for="i in 6" :key="i" class="card pad skeleton">
          <div class="sk-line w70"></div>
          <div class="sk-line w45"></div>
          <div class="sk-btn"></div>
        </div>
      </div>

      <div v-else-if="items.length === 0" class="ux-empty">
        <div class="ux-empty__icon">报</div>
        <div class="ux-empty__title">你还没有报名任何活动</div>
        <div class="ux-empty__sub">去活动列表看看近期的读书会、挑战和分享活动。</div>
        <div class="ux-actions">
          <router-link class="ux-link" to="/activities">浏览活动 →</router-link>
        </div>
      </div>

      <div v-else class="ux-grid">
        <article v-for="s in items" :key="s.id" class="ux-card">
          <div class="ux-card__top">
            <div class="ux-card__identity">
              <div class="ux-avatar">{{ (s.activity_title || "活").charAt(0) }}</div>
              <div>
                <div class="ux-card__title" :title="s.activity_title || `活动#${s.activity}`">
                  {{ s.activity_title || `活动#${s.activity}` }}
                </div>
                <div class="ux-section-sub">报名时间：{{ fmt(s.created_at) }}</div>
              </div>
            </div>
            <span class="ux-chip primary">报名 #{{ s.id }}</span>
          </div>

          <div class="ux-meta">
            <span class="ux-chip success">已报名</span>
            <span class="ux-chip">活动 #{{ s.activity }}</span>
          </div>

          <div class="ux-actions">
            <router-link class="ux-link" :to="`/activities/${s.activity}`">查看活动 →</router-link>
            <button class="danger-link" type="button" :disabled="cancellingId === s.id" @click="cancelSignup(s)">
              {{ cancellingId === s.id ? "取消中..." : "取消报名" }}
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { api } from "../api";

const items = ref([]);
const loading = ref(false);
const cancellingId = ref(null);
const hasToken = computed(() => !!localStorage.getItem("access"));
const uniqueActivityCount = computed(() => new Set(items.value.map((item) => item.activity)).size);
const latestSignup = computed(() => {
  if (!items.value.length) return "-";
  return fmt(items.value[0]?.created_at).split(" ")[0] || "-";
});

function fmt(v) {
  if (!v) return "-";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v).replace("T", " ").replace("Z", "") : d.toLocaleString();
}

async function load() {
  if (!hasToken.value) return;
  loading.value = true;
  try {
    const res = await api.get("/activities/my/signups/");
    items.value = res.data || [];
  } catch {
    window.alert("报名记录加载失败");
  } finally {
    loading.value = false;
  }
}

async function cancelSignup(signup) {
  if (!signup?.activity) return;
  cancellingId.value = signup.id;
  try {
    await api.post(`/activities/${signup.activity}/signup/cancel/`);
    items.value = items.value.filter((item) => item.id !== signup.id);
    window.alert("已取消报名");
  } catch (e) {
    window.alert(e?.response?.data?.detail || "取消报名失败");
  } finally {
    cancellingId.value = null;
  }
}

onMounted(load);
</script>

<style scoped>
.page{ display:flex; flex-direction: column; gap: 14px; padding: 6px 0 24px; }

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
.hero-right{
  display:flex;
  align-items:center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.pill{
  display:flex; align-items:center; gap: 8px;
  padding: 8px 12px; border-radius: 999px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.70);
  box-shadow: 0 10px 22px rgba(2, 6, 23, 0.06);
  font-size: 12px; color: rgba(15,23,42,.75);
  white-space: nowrap;
}
.dot{ width: 8px; height: 8px; border-radius: 999px; background: linear-gradient(135deg, #3b82f6, #2563eb); }

.btn-primary{
  border: 0; cursor: pointer; font-weight: 900;
  padding: 10px 12px; border-radius: 12px; color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  transition: .15s; white-space: nowrap;
}
.btn-primary:hover{ transform: translateY(-1px); }
.btn-primary:active{ transform: translateY(0px); }
.btn-primary:disabled{ opacity:.6; cursor:not-allowed; transform:none; }

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

/* grid */
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

/* item */
.signup{ display:flex; flex-direction: column; gap: 10px; transition: .15s; }
.signup:hover{ transform: translateY(-1px); box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08); }

.top{ display:flex; align-items:flex-start; justify-content: space-between; gap: 10px; }
.title{
  font-weight: 1000; font-size: 14px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  min-width: 0;
}
.badge{
  flex: 0 0 auto;
  font-size: 11px; font-weight: 900;
  padding: 4px 8px; border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}

.meta{ display:flex; flex-direction: column; gap: 6px; }
.meta-row{ display:flex; align-items:center; gap: 8px; }
.meta-dot{ width: 6px; height: 6px; border-radius: 999px; background: rgba(37,99,235,.55); }

.actions{ margin-top: auto; }
.link-btn{
  display:inline-flex; align-items:center; gap: 6px;
  padding: 8px 10px; border-radius: 12px;
  text-decoration: none; font-weight: 900; font-size: 12px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.08);
  border: 1px solid rgba(37,99,235,.18);
  transition: .15s; white-space: nowrap;
}
.link-btn:hover{ background: rgba(37,99,235,.12); }

.danger-link{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid rgba(239,68,68,.22);
  color: rgba(127,29,29,1);
  background: rgba(239,68,68,.08);
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
  transition: .15s;
  white-space: nowrap;
}
.danger-link:hover{ background: rgba(239,68,68,.13); }
.danger-link:disabled{ opacity:.6; cursor:not-allowed; }

/* empty */
.empty{ text-align: center; }
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

/* skeleton */
.skeleton{ position: relative; overflow: hidden; }
.skeleton::after{
  content:""; position:absolute; inset:0; transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
  animation: shimmer 1.1s infinite;
}
.sk-line{ height: 10px; border-radius: 999px; background: rgba(15,23,42,0.06); margin-top: 10px; }
.sk-btn{ height: 34px; width: 120px; border-radius: 12px; background: rgba(15,23,42,0.06); margin-top: 10px; }
.w70{ width: 70%; } .w45{ width: 45%; }
@keyframes shimmer{ 100%{ transform: translateX(100%); } }
</style>

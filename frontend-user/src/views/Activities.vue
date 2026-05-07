<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">活动中心</div>
        <h1 class="ux-title">发现近期共读、分享会和阅读挑战</h1>
        <p class="ux-lead">把线下交流、线上共读和打卡挑战集中到这里，按时间快速判断是否值得报名。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ upcomingCount }} 个未结束</div>
        <button class="btn-primary" :disabled="loading" @click="load">
          {{ loading ? "刷新中..." : "刷新活动" }}
        </button>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">全部活动</div>
        <div class="ux-stat__value">{{ items.length }}</div>
        <div class="ux-stat__hint">当前可查看的活动</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">未结束</div>
        <div class="ux-stat__value">{{ upcomingCount }}</div>
        <div class="ux-stat__hint">适合优先查看</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">活动地点</div>
        <div class="ux-stat__value">{{ placeCount }}</div>
        <div class="ux-stat__hint">覆盖不同阅读场景</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">筛选结果</div>
        <div class="ux-stat__value">{{ filteredItems.length }}</div>
        <div class="ux-stat__hint">{{ filter === "upcoming" ? "只看未结束活动" : "展示所有活动" }}</div>
      </div>
    </section>

    <section class="ux-panel">
      <div class="ux-panel__head">
        <div>
          <h2 class="ux-section-title">活动列表</h2>
          <div class="ux-section-sub">按活动时间、地点和状态浏览，详情页可完成报名。</div>
        </div>
        <div class="row">
          <button class="btn-ghost" :class="{ active: filter === 'all' }" @click="filter = 'all'">全部</button>
          <button class="btn-ghost" :class="{ active: filter === 'upcoming' }" @click="filter = 'upcoming'">未结束</button>
        </div>
      </div>

      <div v-if="loading" class="ux-grid">
        <div v-for="i in 6" :key="i" class="card pad skeleton">
          <div class="sk-line w70"></div>
          <div class="sk-line w45"></div>
          <div class="sk-line w85"></div>
          <div class="sk-btn"></div>
        </div>
      </div>

      <div v-else-if="filteredItems.length === 0" class="ux-empty">
        <div class="ux-empty__icon">活</div>
        <div class="ux-empty__title">暂时没有匹配的活动</div>
        <div class="ux-empty__sub">切换筛选条件，或稍后回来看看新的共读和分享活动。</div>
      </div>

      <div v-else class="ux-grid">
        <article v-for="a in filteredItems" :key="a.id" class="ux-card">
          <div class="ux-card__top">
            <div class="ux-card__identity">
              <div class="ux-avatar">{{ (a.title || "活").charAt(0) }}</div>
              <div>
                <div class="ux-card__title" :title="a.title">{{ a.title }}</div>
                <div class="ux-section-sub">{{ periodLabel(a) }}</div>
              </div>
            </div>
            <span class="ux-chip primary">#{{ a.id }}</span>
          </div>

          <div class="ux-meta">
            <span class="ux-chip" :class="{ success: isUpcoming(a), warn: !isUpcoming(a) }">
              {{ isUpcoming(a) ? "未结束" : "已结束" }}
            </span>
            <span class="ux-chip">{{ a.location || "地点待定" }}</span>
            <span class="ux-chip" :class="{ warn: a.is_full }">{{ slotLabel(a) }}</span>
          </div>

          <div class="ux-card__desc">{{ a.description || "暂无活动介绍，进入详情可查看完整安排。" }}</div>

          <div class="ux-actions">
            <router-link class="ux-link" :to="`/activities/${a.id}`">查看详情 →</router-link>
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
const filter = ref("all");

const upcomingCount = computed(() => items.value.filter(isUpcoming).length);
const placeCount = computed(() => new Set(items.value.map((item) => item.location).filter(Boolean)).size);
const filteredItems = computed(() => {
  if (filter.value === "upcoming") return items.value.filter(isUpcoming);
  return items.value;
});

function fmt(v) {
  if (!v) return "-";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v).replace("T", " ").replace("Z", "") : d.toLocaleString();
}

function isUpcoming(item) {
  const end = new Date(item?.end_time || item?.start_time || "");
  if (Number.isNaN(end.getTime())) return true;
  return end.getTime() >= Date.now();
}

function periodLabel(item) {
  return `${fmt(item.start_time)} - ${fmt(item.end_time)}`;
}

function slotLabel(item) {
  const signed = item?.signed_count || 0;
  if (!item?.capacity) return `${signed} 人报名 · 不限名额`;
  if (item.is_full) return `${signed}/${item.capacity} · 名额已满`;
  return `${signed}/${item.capacity} · 剩 ${item.remaining_slots} 位`;
}

async function load() {
  loading.value = true;
  try {
    const res = await api.get("/activities/");
    items.value = res.data || [];
  } finally {
    loading.value = false;
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
.hero-right{ display:flex; align-items:center; gap: 10px; }

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

/* card item */
.act{ display:flex; flex-direction: column; gap: 10px; transition: .15s; }
.act:hover{ transform: translateY(-1px); box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08); }

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
.w70{ width: 70%; } .w45{ width: 45%; } .w85{ width: 85%; }
@keyframes shimmer{ 100%{ transform: translateX(100%); } }
</style>

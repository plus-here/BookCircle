<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">站内公告</div>
        <h1 class="ux-title">系统通知、规则更新和重要提醒</h1>
        <p class="ux-lead">把需要用户知道的信息集中呈现，最新公告优先展示，减少错过重要通知的可能。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ items.length }} 条公告</div>
        <button class="btn-primary" :disabled="loading" @click="load">
          {{ loading ? "刷新中..." : "刷新公告" }}
        </button>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">公告数量</div>
        <div class="ux-stat__value">{{ items.length }}</div>
        <div class="ux-stat__hint">当前可读内容</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">最新发布时间</div>
        <div class="ux-stat__value">{{ latestDate }}</div>
        <div class="ux-stat__hint">以管理员发布为准</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">阅读入口</div>
        <div class="ux-stat__value">详情</div>
        <div class="ux-stat__hint">每条公告支持单独查看</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">展示状态</div>
        <div class="ux-stat__value">{{ loading ? "更新中" : "已同步" }}</div>
        <div class="ux-stat__hint">刷新可获取最新内容</div>
      </div>
    </section>

    <section class="ux-panel">
      <div class="ux-panel__head">
        <div>
          <h2 class="ux-section-title">公告列表</h2>
          <div class="ux-section-sub">重要通知建议逐条查看，确认平台最新安排。</div>
        </div>
      </div>

      <div v-if="loading" class="ux-grid two">
        <div v-for="i in 6" :key="i" class="card pad skeleton">
          <div class="sk-line w75"></div>
          <div class="sk-line w45"></div>
        </div>
      </div>

      <div v-else-if="items.length === 0" class="ux-empty">
        <div class="ux-empty__icon">告</div>
        <div class="ux-empty__title">暂无公告</div>
        <div class="ux-empty__sub">有新的系统通知或平台更新时，会在这里集中展示。</div>
      </div>

      <div v-else class="ux-list">
        <article class="ux-card ann-row" v-for="(a, index) in items" :key="a.id">
          <div class="ux-card__top">
            <div class="ux-card__identity">
              <div class="ux-avatar">{{ index + 1 }}</div>
              <div>
                <router-link class="ux-card__title ann-title" :to="`/announcements/${a.id}`" :title="a.title">
                  {{ a.title }}
                </router-link>
                <div class="ux-section-sub">发布时间 {{ fmt(a.published_at) }}</div>
              </div>
            </div>
            <span class="ux-chip" :class="index === 0 ? 'success' : 'primary'">
              {{ index === 0 ? "最新" : `#${a.id}` }}
            </span>
          </div>

          <div class="ux-actions">
            <router-link class="ux-link" :to="`/announcements/${a.id}`">查看公告 →</router-link>
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
const latestDate = computed(() => {
  if (!items.value.length) return "-";
  return fmt(items.value[0]?.published_at).split(" ")[0] || "-";
});

function fmt(t) {
  if (!t) return "-";
  const d = new Date(t);
  return Number.isNaN(d.getTime()) ? t : d.toLocaleString();
}

async function load() {
  loading.value = true;
  try {
    const res = await api.get("/announcements/");
    items.value = res.data || [];
  } finally {
    loading.value = false;
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

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.sub{
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}

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

/* list */
.list{
  display:flex;
  flex-direction: column;
  gap: 12px;
}

.ann{
  padding: 14px;
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 12px;
  transition: .15s;
}
.ann:hover{
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08);
}
.ann-left{
  display:flex;
  align-items:center;
  gap: 12px;
  min-width: 0;
}
.icon{
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  flex: 0 0 auto;
  user-select:none;
}
.ann-body{ min-width: 0; }

.title{
  display:block;
  font-weight: 1000;
  font-size: 14px;
  color: rgba(15,23,42,.92);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.title:hover{ text-decoration: underline; }

.meta{ margin-top: 6px; }
.tag{
  display:inline-flex;
  align-items:center;
  gap: 6px;
  font-size: 11px;
  font-weight: 900;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}

.open{
  flex: 0 0 auto;
  text-decoration: none;
  font-weight: 1000;
  font-size: 12px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.08);
  border: 1px solid rgba(37,99,235,.18);
  padding: 8px 10px;
  border-radius: 12px;
  transition: .15s;
  white-space: nowrap;
}
.open:hover{ background: rgba(37,99,235,.12); }

/* empty */
.empty{
  text-align: center;
}
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

/* loading grid skeleton */
.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 720px){
  .grid{ grid-template-columns: 1fr; }
}

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
.w75{ width: 75%; }
.w45{ width: 45%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

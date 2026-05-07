<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">书团广场</div>
        <h1 class="ux-title">找到适合自己的长期阅读社群</h1>
        <p class="ux-lead">社团承载板块、帖子和成员关系，适合持续共读、主题交流和沉淀讨论内容。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ clubs.length }} 个社团</div>
        <div class="ux-pill">{{ totalMembers }} 位成员</div>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">社团总数</div>
        <div class="ux-stat__value">{{ clubs.length }}</div>
        <div class="ux-stat__hint">当前可浏览社团</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">成员规模</div>
        <div class="ux-stat__value">{{ totalMembers }}</div>
        <div class="ux-stat__hint">所有社团成员合计</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">平均人数</div>
        <div class="ux-stat__value">{{ avgMembers }}</div>
        <div class="ux-stat__hint">帮你判断活跃度</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">搜索状态</div>
        <div class="ux-stat__value">{{ q ? "筛选" : "全部" }}</div>
        <div class="ux-stat__hint">{{ q || "未输入关键词" }}</div>
      </div>
    </section>

    <section class="ux-panel">
      <div class="ux-panel__head">
        <div>
          <h2 class="ux-section-title">探索社团</h2>
          <div class="ux-section-sub">搜索名称或简介，进入社团后可查看板块并提交入社申请。</div>
        </div>
      </div>

      <div class="ux-search">
        <input class="ux-search__input" v-model="q" placeholder="搜索社团名称 / 简介" @keydown.enter="load" />
        <button class="btn-primary" :disabled="loading" @click="load">
          {{ loading ? "搜索中..." : "搜索" }}
        </button>
        <button class="btn-ghost" :disabled="loading || !q" @click="q=''; load();">清空</button>
      </div>
    </section>

    <section class="ux-panel">
      <div class="ux-panel__head">
        <div>
          <h2 class="ux-section-title">社团列表</h2>
          <div class="ux-section-sub">成员数越高通常代表讨论更活跃，进入详情可查看板块结构。</div>
        </div>
      </div>

      <div v-if="loading" class="ux-grid">
        <div v-for="i in 6" :key="i" class="club card skeleton">
          <div class="sk-line w60"></div>
          <div class="sk-line w85"></div>
          <div class="sk-line w70"></div>
          <div class="sk-btn"></div>
        </div>
      </div>

      <div v-else-if="clubs.length === 0" class="ux-empty">
        <div class="ux-empty__icon">社</div>
        <div class="ux-empty__title">没有找到社团</div>
        <div class="ux-empty__sub">换个关键词试试，或清空搜索条件查看全部社团。</div>
      </div>

      <div v-else class="ux-grid">
        <article class="ux-card" v-for="c in clubs" :key="c.id">
          <div class="ux-card__top">
            <div class="ux-card__identity">
              <div class="ux-avatar">{{ (c.name || "社").charAt(0) }}</div>
              <div>
                <div class="ux-card__title" :title="c.name">{{ c.name }}</div>
                <div class="ux-section-sub">读者社群 · 可进入板块讨论</div>
              </div>
            </div>
            <span class="ux-chip primary">成员 {{ c.members_count }}</span>
          </div>

          <div class="ux-card__desc">{{ c.description || "暂无简介，进入社团后可以查看板块与帖子。" }}</div>

          <div class="ux-meta">
            <span class="ux-chip">{{ memberScale(c.members_count) }}</span>
            <span class="ux-chip success">开放浏览</span>
          </div>

          <div class="ux-actions">
            <router-link class="ux-link" :to="`/clubs/${c.id}`">进入社团 →</router-link>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { api } from "../api";

const clubs = ref([]);
const q = ref("");
const loading = ref(false);
const totalMembers = computed(() => clubs.value.reduce((sum, club) => sum + Number(club.members_count || 0), 0));
const avgMembers = computed(() => (clubs.value.length ? Math.round(totalMembers.value / clubs.value.length) : 0));

function memberScale(count) {
  const n = Number(count || 0);
  if (n >= 20) return "大型社团";
  if (n >= 8) return "活跃社团";
  return "小组交流";
}

async function load() {
  loading.value = true;
  try {
    const res = await api.get("/clubs/", { params: q.value ? { q: q.value } : {} });
    clubs.value = res.data;
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

/* card */
.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}

/* 搜索 */
.search{ padding: 14px; }
.search-row{ display:flex; gap: 10px; align-items:center; }
.search-input{
  flex: 1;
  display:flex;
  align-items:center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.14);
  background: rgba(255,255,255,0.92);
  transition: .15s;
}
.search-input:focus-within{
  border-color: rgba(59,130,246,0.60);
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}
.search-input input{
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  font-size: 14px;
}
.icon{ opacity: .75; user-select:none; }
.tip{ margin-top: 10px; font-size: 12px; color: rgba(15,23,42,.60); }

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

.btn-ghost{
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(255,255,255,0.70);
  color: rgba(15,23,42,.88);
  font-weight: 900;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: .15s;
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

/* 网格 */
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

/* 单个社团卡片 */
.club{
  padding: 14px;
  display:flex;
  flex-direction: column;
  gap: 10px;
  transition: .15s;
}
.club:hover{
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08);
}

.club-top{
  display:flex;
  align-items:flex-start;
  justify-content: space-between;
  gap: 10px;
}
.club-name{
  font-weight: 1000;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.club-desc{
  font-size: 12px;
  color: rgba(15,23,42,.70);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 56px;
}

.club-actions{ margin-top: auto; }

.link-btn{
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

/* 空状态 */
.empty{
  padding: 22px;
  text-align: center;
}
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
}
.sk-btn{
  height: 34px;
  width: 120px;
  border-radius: 12px;
  background: rgba(15,23,42,0.06);
  margin-top: 6px;
}
.w60{ width: 60%; }
.w85{ width: 85%; }
.w70{ width: 70%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">个人书架</div>
        <h1 class="ux-title">继续你的阅读进度</h1>
        <p class="ux-lead">把喜欢的书收藏起来，系统会记录最近读到的章节，让你下次回来能直接接上。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ items.length }} 本藏书</div>
        <div class="ux-pill">{{ progressCount }} 本有进度</div>
        <button class="btn-primary" :disabled="!hasToken || loading" @click="load">
          {{ loading ? "刷新中..." : "刷新书架" }}
        </button>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">书架总数</div>
        <div class="ux-stat__value">{{ items.length }}</div>
        <div class="ux-stat__hint">已加入书架的书</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">有进度</div>
        <div class="ux-stat__value">{{ progressCount }}</div>
        <div class="ux-stat__hint">可以继续阅读</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">未开始</div>
        <div class="ux-stat__value">{{ notStartedCount }}</div>
        <div class="ux-stat__hint">适合加入下一本计划</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">账号状态</div>
        <div class="ux-stat__value">{{ hasToken ? "已同步" : "未登录" }}</div>
        <div class="ux-stat__hint">阅读进度跟随账号保存</div>
      </div>
    </section>

    <!-- 未登录提示 -->
    <div v-if="!hasToken" class="notice">
      <div class="notice-icon">🔒</div>
      <div class="notice-body">
        <div class="notice-title">你还没有登录</div>
        <div class="notice-sub">
          请先去 <router-link class="link" to="/login">登录</router-link>，再加入书架。
        </div>
      </div>
    </div>

    <!-- 已登录：列表区 -->
    <div v-else class="stack">
      <!-- Loading 骨架屏 -->
      <div v-if="loading" class="grid">
        <div v-for="i in 6" :key="i" class="item skeleton">
          <div class="cover"></div>
          <div class="body">
            <div class="line w70"></div>
            <div class="line w55"></div>
            <div class="line w85"></div>
            <div class="row" style="margin-top:10px;">
              <div class="btn-s"></div>
              <div class="btn-s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 非 loading -->
      <div v-else>
        <!-- 空状态 -->
        <div v-if="items.length === 0" class="empty">
          <div class="empty-icon">🗂️</div>
          <div class="empty-title">书架还是空的</div>
          <div class="empty-sub">
            去书籍详情页点击“加入书架”，就会出现在这里啦。
          </div>
          <router-link class="btn-ghost" to="/">去逛逛书籍库</router-link>
        </div>

        <!-- 列表 -->
        <div v-else class="grid">
          <div v-for="it in items" :key="it.id" class="item">
            <div class="cover cover-photo" :style="coverStyle(it.book)">
              <div class="cover-badge">{{ (it.book?.title || "书").charAt(0) }}</div>
            </div>

            <div class="body">
              <div class="title-row">
                <span class="tag" v-if="it.last_read_chapter_info">有进度</span>
                <span class="tag gray" v-else>未开始</span>
              </div>

              <div class="title" :title="it.book.title">{{ it.book.title }}</div>
              <div class="author">{{ it.book.author }}</div>

              <div class="progress" :class="{ emptyProgress: !it.last_read_chapter_info }">
                <template v-if="it.last_read_chapter_info">
                  <div class="progress-label">当前进度</div>
                  <div class="progress-text">
                    读到：第 {{ it.last_read_chapter_info.order }} 章 {{ it.last_read_chapter_info.title }}
                  </div>
                </template>
                <template v-else>
                  <div class="progress-label">还未开始</div>
                  <div class="progress-text muted">
                    打开详情页选择章节，开始记录你的阅读进度。
                  </div>
                </template>
              </div>

              <div class="actions">
                <router-link class="btn-ghost" :to="`/books/${it.book.id}`">继续阅读</router-link>
                <button class="btn-danger" @click="remove(it.book.id)">移出书架</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { api } from "../api";
import { coverStyle } from "../utils/media";

const items = ref([]);
const loading = ref(false);

const hasToken = computed(() => !!localStorage.getItem("access")); // 第26行
const progressCount = computed(() => items.value.filter((item) => item.last_read_chapter_info).length);
const notStartedCount = computed(() => Math.max(items.value.length - progressCount.value, 0));

async function load() {
  if (!hasToken.value) return; // 第29行
  loading.value = true;
  try {
    const res = await api.get("/shelf/");
    items.value = res.data;
  } catch {
    items.value = [];
  } finally {
    loading.value = false;
  }
}

async function remove(bookId) {
  await api.delete(`/shelf/${bookId}/`);
  await load();
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
.row{ display:flex; gap: 10px; align-items:center; flex-wrap: wrap; }

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.sub{
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}
.muted{ color: rgba(15,23,42,.60); }

/* 顶部 */
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

/* 未登录提示 */
.notice{
  display:flex;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
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
.notice-sub{ margin-top: 4px; color: rgba(15,23,42,.65); font-size: 13px; }
.link{ color: #2563eb; text-decoration: none; font-weight: 900; }
.link:hover{ text-decoration: underline; }

/* 网格列表 */
.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 760px){
  .grid{ grid-template-columns: 1fr; }
}

.item{
  display:flex;
  gap: 16px;
  min-height: 190px;
  padding: 16px;
  border-radius: 20px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background:
    linear-gradient(135deg, rgba(255,255,255,.94), rgba(248,250,252,.84));
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
  transition: .15s;
  overflow: hidden;
}
.item:hover{
  transform: translateY(-2px);
  border-color: rgba(37,99,235,.18);
  box-shadow: 0 20px 44px rgba(2, 6, 23, 0.10);
}

.cover{
  width: 112px;
  height: 154px;
  border-radius: 18px;
  background:
    radial-gradient(160px 90px at 20% 10%, rgba(59,130,246,.25), transparent 60%),
    radial-gradient(140px 80px at 90% 0%, rgba(20,184,166,.20), transparent 60%),
    linear-gradient(135deg, rgba(37,99,235,.12), rgba(20,184,166,.07));
  border: 1px solid rgba(15, 23, 42, 0.08);
  display:block;
  padding: 10px;
  flex: 0 0 auto;
  overflow: hidden;
  position: relative;
}
.cover-photo{
  background-size: cover;
  background-position: center;
  box-shadow: inset 0 -72px 80px rgba(15, 23, 42, 0.38);
}
.cover-badge{
  position:absolute;
  left: 10px;
  top: 10px;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  color:#fff;
  font-weight: 900;
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  user-select:none;
}

.body{
  flex: 1;
  min-width: 0;
  display:flex;
  flex-direction: column;
  gap: 8px;
  padding: 2px 0;
}
.title-row{
  display:flex;
  align-items:center;
  justify-content: flex-start;
  gap: 10px;
}
.title{
  font-weight: 1000;
  font-size: 18px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.author{ font-size: 12px; color: rgba(15,23,42,.65); }

.tag{
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 900;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
}
.tag.gray{
  color: rgba(15,23,42,.65);
  background: rgba(15,23,42,.06);
  border-color: rgba(15,23,42,.10);
}

.progress{
  margin-top: 4px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(37,99,235,.07);
  border: 1px solid rgba(37,99,235,.12);
}
.progress.emptyProgress{
  background: rgba(15,23,42,.04);
  border-color: rgba(15,23,42,.08);
}
.progress-label{
  margin-bottom: 4px;
  color: rgba(37,99,235,1);
  font-size: 11px;
  font-weight: 1000;
}
.progress-text{
  font-size: 12px;
  color: rgba(15,23,42,.70);
  line-height: 1.45;
}

/* 操作按钮 */
.actions{
  margin-top: auto;
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-ghost{
  display:inline-flex;
  align-items:center;
  justify-content: center;
  text-decoration: none;
  font-weight: 900;
  padding: 9px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15,23,42,0.14);
  color: rgba(15,23,42,.88);
  background: rgba(255,255,255,0.65);
  transition: .15s;
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

.btn-danger{
  border: 0;
  cursor: pointer;
  font-weight: 900;
  padding: 9px 12px;
  border-radius: 12px;
  color: #7f1d1d;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.18);
  transition: .15s;
}
.btn-danger:hover{ background: rgba(239, 68, 68, 0.16); }

/* 空状态 */
.empty{
  padding: 22px;
  border-radius: 16px;
  border: 1px dashed rgba(15, 23, 42, 0.16);
  background: rgba(255,255,255,0.75);
  text-align: center;
}
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

/* skeleton */
.skeleton .cover,
.skeleton .line,
.skeleton .btn-s{
  position: relative;
  background: rgba(15,23,42,0.06);
  border-radius: 12px;
  overflow: hidden;
}
.skeleton .cover::after,
.skeleton .line::after,
.skeleton .btn-s::after{
  content:"";
  position:absolute;
  inset:0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
  animation: shimmer 1.1s infinite;
}
.skeleton .body{ gap: 10px; padding-top: 4px; }
.line{ height: 10px; border-radius: 999px; }
.w70{ width: 70%; }
.w55{ width: 55%; }
.w85{ width: 85%; }
.btn-s{ height: 34px; width: 96px; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

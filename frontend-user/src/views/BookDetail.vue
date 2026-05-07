<template>
  <div class="page">
    <!-- Loading -->
    <div v-if="loading" class="card pad">
      <div class="skeleton title"></div>
      <div class="skeleton line w60"></div>
      <div class="skeleton line w85"></div>
      <div class="skeleton line w75"></div>
      <div class="row" style="margin-top:12px;">
        <div class="skeleton btn"></div>
        <div class="skeleton btn"></div>
      </div>
    </div>

    <!-- Data -->
    <div v-else-if="book" class="stack">
      <!-- 书籍信息卡 -->
      <div class="book-hero">
        <div class="cover cover-photo" :style="coverStyle(book)">
          <div class="cover-badge">{{ (book.title || "书").charAt(0) }}</div>
          <div class="cover-meta">
            <div class="cover-meta-title">{{ book.title }}</div>
            <div class="cover-meta-sub">{{ book.author }}</div>
          </div>
        </div>

        <div class="hero-body">
          <div class="hero-top">
            <h3 class="h1">{{ book.title }}</h3>
            <div class="author">作者：{{ book.author }}</div>
          </div>

          <div class="desc">
            {{ book.description || "暂无简介。" }}
          </div>

          <div class="stats">
            <div class="stat">
              <div class="stat-num">{{ book.chapters_count }}</div>
              <div class="stat-label">章节</div>
            </div>
            <div class="stat">
              <div class="stat-num">📖</div>
              <div class="stat-label">阅读</div>
            </div>
            <div class="stat">
              <div class="stat-num">💬</div>
              <div class="stat-label">交流</div>
            </div>
          </div>

          <div class="actions">
            <button class="btn-primary" @click="addToShelf">加入书架</button>
            <router-link class="btn-ghost" to="/shelf">去我的书架</router-link>
          </div>
        </div>
      </div>

      <!-- 章节列表 -->
      <div class="card pad">
        <div class="section-head">
          <h4 class="h2">章节列表</h4>
          <div class="muted">共 {{ chapters.length }} 章</div>
        </div>

        <div v-if="chapters.length === 0" class="empty">
          <div class="empty-icon">🗂️</div>
          <div class="empty-title">暂无章节</div>
          <div class="empty-sub">请在管理端添加章节后再来阅读。</div>
        </div>

        <div v-else class="chapter-list">
          <div v-for="c in chapters" :key="c.id" class="chapter-item">
            <div class="chapter-left">
              <div class="chapter-order">{{ c.order }}</div>
              <div class="chapter-title" :title="c.title">
                {{ c.title }}
              </div>
            </div>
            <router-link class="read-btn" :to="`/chapters/${c.id}`">阅读 →</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="card pad">
      <div class="empty">
        <div class="empty-icon">📭</div>
        <div class="empty-title">没有找到这本书</div>
        <div class="empty-sub">请返回首页重新选择书籍。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api";
import { coverStyle } from "../utils/media";

const route = useRoute();
const book = ref(null);
const chapters = ref([]);
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    const id = route.params.id;
    const b = await api.get(`/books/${id}/`);
    book.value = b.data;

    const c = await api.get(`/books/${id}/chapters/`);
    chapters.value = c.data;
  } finally {
    loading.value = false;
  }
}

async function addToShelf() {
  try {
    await api.post("/shelf/", { book_id: Number(route.params.id) });
    alert("加入书架成功");
  } catch (e) {
    alert("加入失败：请先登录，或稍后再试");
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

/* 复用标题类（如果你已有 global.css，也能共存） */
.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.h2{ margin: 0; font-size: 16px; }
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.stack{ display:flex; flex-direction: column; gap: 14px; }
.row{ display:flex; gap: 10px; align-items: center; flex-wrap: wrap; }

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
  background: rgba(255,255,255,0.65);
  transition: .15s;
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

/* 书籍 hero 卡 */
.book-hero{
  display:flex;
  gap: 14px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.18), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.16), transparent 60%),
    rgba(255,255,255,0.75);
  backdrop-filter: blur(10px);
}
@media (max-width: 720px){
  .book-hero{ flex-direction: column; }
}

.cover{
  width: 140px;
  height: 184px;
  border-radius: 18px;
  background:
    radial-gradient(220px 120px at 20% 10%, rgba(59,130,246,.25), transparent 60%),
    radial-gradient(190px 110px at 90% 0%, rgba(37,99,235,.20), transparent 60%),
    linear-gradient(135deg, rgba(59,130,246,.10), rgba(37,99,235,.06));
  border: 1px solid rgba(15, 23, 42, 0.08);
  display:flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 12px;
  flex: 0 0 auto;
  overflow: hidden;
}

.cover-photo{
  background-size: cover;
  background-position: center;
  box-shadow: inset 0 -76px 96px rgba(15, 23, 42, 0.38);
}

.cover-badge{
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  color:#fff;
  font-weight: 900;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  user-select:none;
}
.cover-meta-title{
  padding: 6px 7px 2px;
  border-radius: 10px 10px 0 0;
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(6px);
  font-size: 12px;
  font-weight: 900;
  color: rgba(15,23,42,.85);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cover-meta-sub{
  padding: 0 7px 6px;
  border-radius: 0 0 10px 10px;
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(6px);
  font-size: 11px;
  color: rgba(15,23,42,.60);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hero-body{
  flex: 1;
  min-width: 0;
  display:flex;
  flex-direction: column;
  gap: 10px;
}
.author{
  margin-top: 6px;
  font-size: 12px;
  color: rgba(15,23,42,.62);
}

.desc{
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
  color: rgba(15,23,42,.82);
  line-height: 1.55;
  font-size: 13px;
}

.stats{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
}
.stat{
  min-width: 90px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
}
.stat-num{
  font-weight: 1000;
  font-size: 16px;
}
.stat-label{
  margin-top: 2px;
  font-size: 12px;
  color: rgba(15,23,42,.60);
}

.actions{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 2px;
}

/* 章节列表 */
.section-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.chapter-list{
  display:flex;
  flex-direction: column;
  gap: 10px;
}

.chapter-item{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
  transition: .15s;
}
.chapter-item:hover{
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(2, 6, 23, 0.06);
}

.chapter-left{
  display:flex;
  align-items:center;
  gap: 10px;
  min-width: 0;
}
.chapter-order{
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display:grid;
  place-items:center;
  font-weight: 900;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  flex: 0 0 auto;
}
.chapter-title{
  font-weight: 900;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.read-btn{
  flex: 0 0 auto;
  text-decoration: none;
  font-weight: 900;
  font-size: 12px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.08);
  border: 1px solid rgba(37,99,235,.18);
  padding: 8px 10px;
  border-radius: 12px;
  transition: .15s;
}
.read-btn:hover{
  background: rgba(37,99,235,.12);
}

/* 空状态 */
.empty{
  padding: 18px;
  border-radius: 16px;
  border: 1px dashed rgba(15, 23, 42, 0.16);
  background: rgba(255,255,255,0.70);
  text-align: center;
}
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 900; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

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
.skeleton.line{ height: 10px; }
.skeleton.btn{ height: 38px; width: 120px; border-radius: 12px; }
.w60{ width: 60%; }
.w85{ width: 85%; }
.w75{ width: 75%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

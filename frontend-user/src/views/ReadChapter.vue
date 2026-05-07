<template>
  <div class="page">
    <!-- Loading -->
    <div v-if="loading" class="card pad">
      <div class="skeleton title"></div>
      <div class="skeleton line w45"></div>
      <div class="divider"></div>
      <div class="skeleton para"></div>
      <div class="skeleton para"></div>
      <div class="skeleton para short"></div>
      <div class="row" style="margin-top:14px;">
        <div class="skeleton btn"></div>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="chapter" class="stack">
      <!-- 顶部信息 -->
      <div class="hero">
        <div class="hero-top">
          <div class="badge">第 {{ chapter.order }} 章</div>
          <div class="muted">阅读模式</div>
        </div>

        <h3 class="h1">{{ chapter.title }}</h3>
        <p class="sub">
          建议：电脑按 <b>Ctrl +</b> / <b>Ctrl -</b> 调整字号；手机可横屏阅读更舒服。
        </p>

        <div class="actions">
          <button class="btn-primary" @click="markProgress">记录阅读进度</button>
          <button class="btn-ghost" @click="saveBookmark">添加书签</button>
        </div>
      </div>

      <!-- 正文阅读区 -->
      <div class="reader card pad">
        <div class="reader-head">
          <div class="reader-dot"></div>
          <div class="reader-title">正文</div>
        </div>

        <!-- 用 <pre> 保留换行，但排版像文章 -->
        <pre class="content">{{ chapter.content }}</pre>

        <div class="reader-foot">
          <span class="muted">已到底部</span>
          <button class="btn-ghost" @click="markProgress">再记录一次</button>
        </div>
      </div>

      <div class="card pad">
        <div class="reader-head">
          <div class="reader-dot"></div>
          <div class="reader-title">我的书签</div>
        </div>
        <div class="bookmark-form">
          <input v-model="bookmarkNote" class="bookmark-input" maxlength="255" placeholder="给这一章留一句备注（可选）" />
          <button class="btn-primary" :disabled="savingBookmark" @click="saveBookmark">
            {{ savingBookmark ? "保存中..." : "保存书签" }}
          </button>
        </div>

        <div v-if="bookmarks.length === 0" class="empty compact">
          <div class="empty-title">这一章还没有书签</div>
          <div class="empty-sub">保存后可以回到这一章继续阅读。</div>
        </div>
        <div v-else class="bookmark-list">
          <div v-for="b in bookmarks" :key="b.id" class="bookmark-item">
            <div>
              <div class="bookmark-title">第 {{ b.chapter_order }} 章 · {{ b.chapter_title }}</div>
              <div class="bookmark-note">{{ b.note || "无备注" }}</div>
            </div>
            <button class="btn-danger" @click="removeBookmark(b.id)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="card pad">
      <div class="empty">
        <div class="empty-icon">📭</div>
        <div class="empty-title">没有找到该章节</div>
        <div class="empty-sub">请返回上一页重新选择章节。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api";

const route = useRoute();
const chapter = ref(null);
const loading = ref(false);
const bookmarks = ref([]);
const bookmarkNote = ref("");
const savingBookmark = ref(false);

async function load() {
  loading.value = true;
  try {
    const id = route.params.id;
    const res = await api.get(`/chapters/${id}/`);
    chapter.value = res.data;
    await loadBookmarks();
  } finally {
    loading.value = false;
  }
}

async function loadBookmarks() {
  if (!chapter.value || !localStorage.getItem("access")) return;
  try {
    const res = await api.get(`/bookmarks/?book_id=${chapter.value.book}`);
    bookmarks.value = (res.data || []).filter((item) => item.chapter === chapter.value.id);
  } catch {
    bookmarks.value = [];
  }
}

async function markProgress() {
  try {
    await api.patch("/shelf/progress/", {
      book_id: chapter.value.book,
      chapter_id: chapter.value.id,
    });
    alert("已记录阅读进度");
  } catch (e) {
    if (e?.response?.status === 404 && localStorage.getItem("access")) {
      try {
        await api.post("/shelf/", { book_id: chapter.value.book });
        await api.patch("/shelf/progress/", {
          book_id: chapter.value.book,
          chapter_id: chapter.value.id,
        });
        alert("已加入书架并记录阅读进度");
        return;
      } catch {
        // Fall through to the shared message.
      }
    }
    alert("记录失败：请先登录后再阅读");
  }
}

async function saveBookmark() {
  if (!chapter.value) return;
  savingBookmark.value = true;
  try {
    await api.post("/bookmarks/", {
      chapter: chapter.value.id,
      note: bookmarkNote.value,
    });
    bookmarkNote.value = "";
    await loadBookmarks();
    alert("书签已保存");
  } catch {
    alert("保存书签失败：请先登录");
  } finally {
    savingBookmark.value = false;
  }
}

async function removeBookmark(id) {
  try {
    await api.delete(`/bookmarks/${id}/`);
    bookmarks.value = bookmarks.value.filter((item) => item.id !== id);
    alert("书签已删除");
  } catch {
    alert("删除书签失败");
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

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.stack{ display:flex; flex-direction: column; gap: 14px; }
.row{ display:flex; gap: 10px; align-items: center; flex-wrap: wrap; }

.h1{
  margin: 0;
  font-size: 20px;
  letter-spacing: .2px;
}
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }
.sub{
  margin: 8px 0 0;
  color: rgba(15,23,42,.62);
  font-size: 13px;
  line-height: 1.55;
}

.divider{
  height: 1px;
  background: rgba(15,23,42,0.10);
  margin: 12px 0;
}

/* 顶部 hero */
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
  align-items:center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.badge{
  display:inline-flex;
  align-items:center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 12px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
}

.actions{ margin-top: 12px; }

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
  padding: 9px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15,23,42,0.14);
  color: rgba(15,23,42,.88);
  background: rgba(255,255,255,0.65);
  transition: .15s;
  cursor: pointer;
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

/* 阅读器正文 */
.reader{ position: relative; }
.reader-head{
  display:flex;
  align-items:center;
  gap: 10px;
  margin-bottom: 10px;
}
.reader-dot{
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.reader-title{
  font-weight: 1000;
  font-size: 13px;
}

.content{
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.9;
  font-size: 15px;
  letter-spacing: 0.2px;
  color: rgba(15,23,42,.88);
  margin: 0;
}

/* 底部 */
.reader-foot{
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(15,23,42,0.10);
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 10px;
}

.bookmark-form{
  display:flex;
  gap: 10px;
  align-items:center;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.bookmark-input{
  flex: 1;
  min-width: 220px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(255,255,255,0.82);
  outline: none;
}
.bookmark-input:focus{
  border-color: rgba(59,130,246,0.60);
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}
.bookmark-list{
  display:flex;
  flex-direction: column;
  gap: 10px;
}
.bookmark-item{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
}
.bookmark-title{ font-weight: 1000; }
.bookmark-note{
  margin-top: 4px;
  color: rgba(15,23,42,.62);
  font-size: 13px;
}
.btn-danger{
  border: 1px solid rgba(239,68,68,.22);
  cursor: pointer;
  font-weight: 900;
  padding: 9px 12px;
  border-radius: 12px;
  color: rgba(127,29,29,1);
  background: rgba(239,68,68,.10);
  transition: .15s;
}
.btn-danger:hover{ background: rgba(239,68,68,.14); }

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
.empty.compact{ padding: 12px; }

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
.skeleton.title{ height: 18px; width: 55%; }
.skeleton.line{ height: 10px; margin-top: 10px; }
.skeleton.para{ height: 56px; margin-top: 10px; border-radius: 14px; }
.skeleton.para.short{ height: 40px; }
.skeleton.btn{ height: 38px; width: 140px; border-radius: 12px; margin-top: 8px; }
.w45{ width: 45%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

<template>
  <div class="page">
    <!-- 顶部栏 -->
    <div class="hero">
      <div>
        <h3 class="h1">板块帖子</h3>
        <p class="sub">在这里发布主题，和社团成员一起讨论。</p>
      </div>

      <button class="btn-primary" :disabled="loading" @click="load">
        {{ loading ? "刷新中..." : "刷新" }}
      </button>
    </div>

    <!-- 发帖卡片 -->
    <div class="card pad">
      <div class="section-head">
        <div>
          <div class="h2">发帖</div>
          <div class="muted">注意：必须是社团成员才能发帖。</div>
        </div>
        <div class="pill">
          <span class="dot"></span>
          <span>{{ posts.length }} 帖</span>
        </div>
      </div>

      <div class="form">
        <label class="field">
          <span class="label">标题</span>
          <div class="input-wrap">
            <span class="icon">📝</span>
            <input v-model="title" class="input" placeholder="写一个清晰的标题" />
          </div>
        </label>

        <label class="field">
          <span class="label">内容</span>
          <textarea v-model="content" class="textarea" rows="5" placeholder="说说你的想法..."></textarea>
        </label>

        <div class="actions">
          <button class="btn-primary" @click="createPost">发布</button>
          <button class="btn-ghost" type="button" @click="title=''; content=''">清空</button>
        </div>
      </div>
    </div>

    <!-- Loading 骨架屏 -->
    <div v-if="loading" class="grid">
      <div v-for="i in 6" :key="i" class="post card pad skeleton">
        <div class="sk-line w70"></div>
        <div class="sk-line w45"></div>
        <div class="sk-line w85"></div>
        <div class="sk-btn"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="posts.length === 0" class="empty card pad">
      <div class="empty-icon">💭</div>
      <div class="empty-title">还没有帖子</div>
      <div class="empty-sub">你可以发布第一条帖子，开启讨论。</div>
    </div>

    <!-- 帖子列表 -->
    <div v-else class="grid">
      <div class="post card pad" v-for="p in posts" :key="p.id">
        <div class="post-top">
          <div class="post-title" :title="p.title">{{ p.title }}</div>
          <div class="badge">评论 {{ p.comments_count }}</div>
        </div>

        <div class="post-meta">
          <span class="meta-dot"></span>
          <span>{{ formatTime(p.created_at) }}</span>
        </div>

        <div class="post-actions">
          <router-link class="link-btn" :to="`/posts/${p.id}`">查看详情 →</router-link>
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
const posts = ref([]);

const title = ref("");
const content = ref("");

const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    const id = route.params.id;
    posts.value = (await api.get(`/sections/${id}/posts/`)).data;
  } finally {
    loading.value = false;
  }
}

async function createPost() {
  try {
    const id = route.params.id;
    await api.post(`/sections/${id}/posts/`, { title: title.value, content: content.value });
    title.value = "";
    content.value = "";
    await load();
    alert("发布成功");
  } catch {
    alert("发布失败：请先登录并加入社团");
  }
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

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.h2{ font-weight: 1000; }
.sub{
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }

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

.section-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
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

/* 表单 */
.form{
  display:flex;
  flex-direction: column;
  gap: 12px;
}
.field{ display:flex; flex-direction: column; gap: 6px; }
.label{ font-size: 12px; color: rgba(15,23,42,.70); }

.input-wrap{
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

.textarea{
  width: 100%;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.14);
  background: rgba(255,255,255,0.92);
  outline: none;
  transition: .15s;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
}
.textarea:focus{
  border-color: rgba(59,130,246,0.60);
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}

.actions{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 2px;
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

/* 帖子列表网格 */
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

.post{
  display:flex;
  flex-direction: column;
  gap: 10px;
  transition: .15s;
}
.post:hover{
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08);
}

.post-top{
  display:flex;
  align-items:flex-start;
  justify-content: space-between;
  gap: 10px;
}
.post-title{
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

.post-meta{
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

.post-actions{ margin-top: auto; }

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
.w70{ width: 70%; }
.w45{ width: 45%; }
.w85{ width: 85%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

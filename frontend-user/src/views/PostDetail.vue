<template>
  <div class="page">
    <!-- Loading -->
    <div v-if="loading" class="card pad">
      <div class="skeleton title"></div>
      <div class="skeleton line w45"></div>
      <div class="divider"></div>
      <div class="skeleton block"></div>
      <div class="skeleton block short"></div>
      <div class="row" style="margin-top:12px;">
        <div class="skeleton btn"></div>
        <div class="skeleton btn"></div>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="post" class="stack">
      <!-- 头部信息 -->
      <div class="hero">
        <div class="hero-top">
          <h3 class="h1" :title="post.title">{{ post.title }}</h3>
          <span class="tag">发布于 {{ formatTime(post.created_at) }}</span>
        </div>

        <div class="content card pad reader">
          <div class="reader-head">
            <div class="dot"></div>
            <div class="reader-title">正文</div>
          </div>
          <pre class="text">{{ post.content }}</pre>
        </div>
      </div>

      <!-- 发表评论 -->
      <div class="card pad">
        <div class="section-head">
          <div>
            <div class="h2">发表评论</div>
            <div class="muted">注意：必须是社团成员才能评论。</div>
          </div>
        </div>

        <div class="comment-box">
          <div class="input-wrap">
            <span class="icon">💬</span>
            <input v-model="comment" class="input" placeholder="输入评论内容（回车发送）" @keydown.enter="sendComment" />
          </div>
          <button class="btn-primary" @click="sendComment">发送</button>
        </div>
      </div>

      <!-- 评论列表 -->
      <div class="card pad">
        <div class="section-head">
          <div class="h2">评论列表</div>
          <button class="btn-ghost" @click="loadComments">刷新评论</button>
        </div>

        <div v-if="comments.length === 0" class="empty">
          <div class="empty-icon">🗨️</div>
          <div class="empty-title">还没有评论</div>
          <div class="empty-sub">成为第一个发表评论的人吧。</div>
        </div>

        <div v-else class="list">
          <div class="comment-item" v-for="c in comments" :key="c.id">
            <div class="comment-content">{{ c.content }}</div>
            <div class="comment-time">{{ formatTime(c.created_at) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="card pad">
      <div class="empty">
        <div class="empty-icon">📭</div>
        <div class="empty-title">没有找到该帖子</div>
        <div class="empty-sub">请返回上一页重新选择帖子。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api";

const route = useRoute();
const loading = ref(false);

const post = ref(null);
const comments = ref([]);
const comment = ref("");

async function load() {
  loading.value = true;
  try {
    const id = route.params.id;
    post.value = (await api.get(`/posts/${id}/`)).data;
    comments.value = (await api.get(`/posts/${id}/comments/`)).data;
  } finally {
    loading.value = false;
  }
}

async function loadComments() {
  const id = route.params.id;
  comments.value = (await api.get(`/posts/${id}/comments/`)).data;
}

async function sendComment() {
  try {
    const id = route.params.id;
    await api.post(`/posts/${id}/comments/`, { content: comment.value });
    comment.value = "";
    await loadComments();
    alert("评论成功");
  } catch {
    alert("评论失败：请先登录并加入社团");
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

.stack{ display:flex; flex-direction: column; gap: 14px; }
.row{ display:flex; gap: 10px; align-items:center; flex-wrap: wrap; }

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.h1{
  margin: 0;
  font-size: 20px;
  letter-spacing: .2px;
}
.h2{ font-weight: 1000; }
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }

.hero{
  display:flex;
  flex-direction: column;
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

.hero-top{
  display:flex;
  align-items:flex-start;
  justify-content: space-between;
  gap: 10px;
}
.tag{
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

/* 正文阅读区 */
.reader{
  background: rgba(255,255,255,0.75);
}
.reader-head{
  display:flex;
  align-items:center;
  gap: 10px;
  margin-bottom: 10px;
}
.dot{
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.reader-title{
  font-weight: 1000;
  font-size: 13px;
}
.text{
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.9;
  font-size: 15px;
  letter-spacing: 0.2px;
  color: rgba(15,23,42,.88);
}

/* 发表评论 */
.section-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}
.comment-box{
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
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(255,255,255,0.70);
  color: rgba(15,23,42,.88);
  font-weight: 900;
  padding: 9px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: .15s;
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

/* 评论列表 */
.list{
  display:flex;
  flex-direction: column;
  gap: 10px;
}
.comment-item{
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
}
.comment-content{
  font-size: 13px;
  line-height: 1.6;
  color: rgba(15,23,42,.86);
  word-break: break-word;
}
.comment-time{
  margin-top: 6px;
  font-size: 12px;
  color: rgba(15,23,42,.60);
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
.skeleton.btn{ height: 38px; width: 120px; border-radius: 12px; }

.w45{ width: 45%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

<template>
  <div class="page">
    <!-- 顶部栏 -->
    <div class="hero">
      <div class="hero-left">
        <h3 class="h1">公告详情</h3>
        <p class="sub">系统通知与更新说明</p>
      </div>

      <div class="hero-right">
        <router-link class="btn-ghost" to="/announcements">返回列表</router-link>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="card pad">
      <div class="skeleton title"></div>
      <div class="skeleton line w45"></div>
      <div class="divider"></div>
      <div class="skeleton block"></div>
      <div class="skeleton block short"></div>
    </div>

    <!-- Not found -->
    <div v-else-if="!item" class="card pad">
      <div class="empty">
        <div class="empty-icon">📭</div>
        <div class="empty-title">公告不存在或未发布</div>
        <div class="empty-sub">请返回公告列表查看其它公告。</div>
        <router-link class="btn-primary" to="/announcements">回到公告列表</router-link>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="stack">
      <!-- 标题区 -->
      <div class="article-head">
        <div class="article-badge">📣 公告</div>
        <h3 class="article-title">{{ item.title }}</h3>
        <div class="meta">
          <span class="meta-dot"></span>
          <span>发布时间：{{ fmt(item.published_at) }}</span>
        </div>
      </div>

      <!-- 正文区（富文本） -->
      <div class="card pad">
        <!-- ✅ 富文本安全渲染 -->
        <div class="rich" v-html="safeHtml"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api";
import DOMPurify from "dompurify";

const route = useRoute();

const item = ref(null);
const loading = ref(false);

const safeHtml = computed(() => DOMPurify.sanitize(item.value?.content || ""));

function fmt(t) {
  if (!t) return "-";
  const d = new Date(t);
  return Number.isNaN(d.getTime()) ? t : d.toLocaleString();
}

async function load() {
  loading.value = true;
  try {
    const res = await api.get(`/announcements/${route.params.id}/`);
    item.value = res.data;
  } catch {
    item.value = null;
  } finally {
    loading.value = false;
  }
}

watch(() => route.params.id, load);
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

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.sub{
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}

/* 顶部 hero */
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

.btn-primary{
  display:inline-flex;
  align-items:center;
  justify-content: center;
  text-decoration: none;
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

/* 文章头 */
.article-head{
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background:
    radial-gradient(900px 420px at 10% -10%, rgba(59,130,246,.18), transparent 55%),
    radial-gradient(700px 360px at 95% 0%, rgba(37,99,235,.16), transparent 60%),
    rgba(255,255,255,0.75);
  backdrop-filter: blur(10px);
}
.article-badge{
  display:inline-flex;
  align-items:center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 1000;
  font-size: 12px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
}
.article-title{
  margin: 10px 0 0;
  font-size: 20px;
  letter-spacing: .2px;
}
.meta{
  margin-top: 8px;
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

/* 富文本排版（重点） */
.rich{
  line-height: 1.85;
  color: rgba(15,23,42,.88);
  font-size: 15px;
  word-break: break-word;
}

/* 标题 */
.rich :deep(h1),
.rich :deep(h2),
.rich :deep(h3){
  margin: 14px 0 10px;
  line-height: 1.25;
}
.rich :deep(h1){ font-size: 20px; }
.rich :deep(h2){ font-size: 18px; }
.rich :deep(h3){ font-size: 16px; }

/* 段落/列表 */
.rich :deep(p){ margin: 10px 0; }
.rich :deep(ul),
.rich :deep(ol){ padding-left: 18px; margin: 10px 0; }
.rich :deep(li){ margin: 6px 0; }

/* 引用 */
.rich :deep(blockquote){
  margin: 12px 0;
  padding: 10px 12px;
  border-left: 4px solid rgba(37,99,235,.55);
  background: rgba(37,99,235,.06);
  border-radius: 12px;
}

/* 图片 */
.rich :deep(img){
  max-width: 100%;
  height: auto;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
  margin: 10px 0;
}

/* 表格 */
.rich :deep(table){
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  overflow: hidden;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
}
.rich :deep(th),
.rich :deep(td){
  border-bottom: 1px solid rgba(15,23,42,0.08);
  padding: 10px 12px;
  text-align: left;
  font-size: 13px;
}
.rich :deep(th){
  background: rgba(15,23,42,0.04);
  font-weight: 900;
}

/* 代码块 */
.rich :deep(pre){
  padding: 12px;
  border-radius: 14px;
  background: rgba(15,23,42,0.05);
  border: 1px solid rgba(15,23,42,0.08);
  overflow: auto;
}
.rich :deep(code){
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 13px;
}

/* 空状态 */
.empty{
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
.skeleton.title{ height: 18px; width: 70%; }
.skeleton.line{ height: 10px; margin-top: 10px; }
.skeleton.block{ height: 80px; margin-top: 10px; border-radius: 14px; }
.skeleton.block.short{ height: 58px; }

.w45{ width: 45%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

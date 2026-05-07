<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">个人中心</div>
        <h1 class="ux-title">维护你的公开资料和账号形象</h1>
        <p class="ux-lead">头像、用户名、邮箱和简介会帮助其他读者在社团、群组和私聊里更快认识你。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ me?.username ? "已登录" : "未登录" }}</div>
        <button v-if="hasToken" class="btn-primary" :disabled="loading" @click="loadMe">
          {{ loading ? "刷新中..." : "刷新资料" }}
        </button>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">用户名</div>
        <div class="ux-stat__value">{{ me?.username || "-" }}</div>
        <div class="ux-stat__hint">站内展示名称</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">邮箱</div>
        <div class="ux-stat__value">{{ me?.email ? "已填写" : "未填写" }}</div>
        <div class="ux-stat__hint">用于完善账号信息</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">简介</div>
        <div class="ux-stat__value">{{ bio ? "已填写" : "未填写" }}</div>
        <div class="ux-stat__hint">展示你的阅读偏好</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">头像</div>
        <div class="ux-stat__value">{{ me?.avatar ? "已上传" : "默认" }}</div>
        <div class="ux-stat__hint">清晰头像更易识别</div>
      </div>
    </section>

    <!-- 未登录 -->
    <div v-if="!hasToken" class="card pad notice">
      <div class="notice-icon">🔒</div>
      <div>
        <div class="notice-title">你还没有登录</div>
        <div class="notice-sub">
          请先去 <router-link class="link" to="/login">登录</router-link>，再查看个人信息。
        </div>
      </div>
    </div>

    <!-- 已登录 -->
    <div v-else class="stack">
      <!-- Loading 骨架屏 -->
      <div v-if="loading" class="card pad">
        <div class="skeleton title"></div>
        <div class="skeleton line w60"></div>
        <div class="skeleton line w45"></div>
        <div class="divider"></div>
        <div class="skeleton block"></div>
        <div class="skeleton block short"></div>
      </div>

      <!-- 内容 -->
      <div v-else-if="me" class="grid">
        <!-- 左侧：基本信息 + 简介 -->
        <div class="card pad">
          <div class="section-head">
            <div>
              <div class="h2">基础信息</div>
              <div class="muted">你对外展示的账号信息</div>
            </div>
          </div>

          <div class="info">
            <div class="info-row">
              <div class="label">用户名</div>
              <div class="value">{{ me.username }}</div>
            </div>
            <div class="info-row">
              <div class="label">邮箱</div>
              <div class="value">{{ me.email || "-" }}</div>
            </div>
          </div>

          <div class="divider"></div>

          <div class="section-head" style="margin-bottom: 10px;">
            <div>
              <div class="h2">简介</div>
              <div class="muted">写一句话介绍你自己（可随时修改）</div>
            </div>
          </div>

          <div class="field">
            <div class="input-wrap">
              <span class="icon">✍️</span>
              <input
                v-model="bio"
                class="input"
                placeholder="例如：喜欢科幻、历史、心理学，欢迎交流。"
                @keydown.enter="saveBio"
              />
            </div>

            <div class="actions">
              <button class="btn-primary" @click="saveBio">保存简介</button>
              <button class="btn-ghost" type="button" @click="bio = me.bio || ''">恢复</button>
            </div>
          </div>
        </div>

        <!-- 右侧：头像 -->
        <div class="card pad">
          <div class="section-head">
            <div>
              <div class="h2">头像</div>
              <div class="muted">上传一张清晰头像（建议正方形）</div>
            </div>
          </div>

          <div class="avatar-box">
            <div class="avatar-preview">
              <img
                :src="userAvatar(me)"
                :alt="me.username || 'avatar'"
              />
            </div>

            <div class="avatar-meta">
              <div class="avatar-name">{{ me.username }}</div>
              <div class="muted">支持 jpg/png/webp，上传后会立即生效</div>
            </div>
          </div>

          <div class="divider"></div>

          <div class="upload">
            <label class="file">
              <input type="file" accept="image/*" @change="onFileChange" />
              <span class="file-btn">选择图片</span>
              <span class="file-name">{{ file ? file.name : "未选择文件" }}</span>
            </label>

            <div class="actions">
              <button class="btn-primary" @click="uploadAvatar" :disabled="!file">
                上传头像
              </button>
              <button class="btn-danger" type="button" :disabled="!file" @click="file=null">
                取消选择
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 兜底：无 me -->
      <div v-else class="card pad">
        <div class="empty">
          <div class="empty-icon">📭</div>
          <div class="empty-title">无法加载个人信息</div>
          <div class="empty-sub">请重新登录后再试。</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { api } from "../api";
import { userAvatar } from "../utils/media";

const hasToken = computed(() => !!localStorage.getItem("access"));

const loading = ref(false);
const me = ref(null);
const bio = ref("");
const file = ref(null);

async function loadMe() {
  if (!hasToken.value) return;
  loading.value = true;
  try {
    const res = await api.get("/auth/me/");
    me.value = res.data;
    bio.value = res.data.bio || "";
  } finally {
    loading.value = false;
  }
}

async function saveBio() {
  try {
    await api.patch("/auth/me/", { bio: bio.value });
    alert("简介已保存");
    await loadMe();
  } catch {
    alert("保存失败，请稍后再试");
  }
}

function onFileChange(e) {
  file.value = e.target.files?.[0] || null;
}

async function uploadAvatar() {
  if (!file.value) return;
  const form = new FormData();
  form.append("avatar", file.value);

  try {
    await api.patch("/auth/me/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    alert("头像上传成功");
    file.value = null;
    await loadMe();
  } catch {
    alert("头像上传失败，请换一张图片再试");
  }
}

onMounted(loadMe);
</script>

<style scoped>
.page{ display:flex; flex-direction: column; gap: 14px; padding: 6px 0 24px; }
.stack{ display:flex; flex-direction: column; gap: 14px; }

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.h2{ font-weight: 1000; }
.sub{ margin: 6px 0 0; font-size: 13px; color: rgba(15,23,42,.65); line-height: 1.5; }
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }

.card{
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.86);
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
}
.pad{ padding: 16px; }

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
.hero-right{ display:flex; align-items:center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }

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

/* notice */
.notice{ display:flex; gap: 12px; align-items:flex-start; }
.notice-icon{
  width: 40px; height: 40px; border-radius: 14px;
  display:grid; place-items:center;
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  flex: 0 0 auto;
}
.notice-title{ font-weight: 1000; }
.notice-sub{ margin-top: 4px; font-size: 13px; color: rgba(15,23,42,.65); line-height: 1.5; }
.link{ color: #2563eb; text-decoration: none; font-weight: 900; }
.link:hover{ text-decoration: underline; }

/* layout grid */
.grid{
  display:grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 12px;
}
@media (max-width: 900px){
  .grid{ grid-template-columns: 1fr; }
}

.section-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.info{ display:flex; flex-direction: column; gap: 10px; }
.info-row{
  display:flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
}
.label{ font-size: 12px; color: rgba(15,23,42,.60); font-weight: 900; }
.value{ font-size: 13px; color: rgba(15,23,42,.88); font-weight: 1000; overflow:hidden; text-overflow: ellipsis; white-space: nowrap; }

.divider{ height: 1px; background: rgba(15,23,42,0.10); margin: 12px 0; }

.field{ display:flex; flex-direction: column; gap: 10px; }
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
.input{ width: 100%; border: 0; outline: none; background: transparent; font-size: 14px; }

.actions{ display:flex; gap: 10px; flex-wrap: wrap; }

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
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(255,255,255,0.70);
  color: rgba(15,23,42,.88);
  font-weight: 900;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: .15s;
  white-space: nowrap;
}
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

.btn-danger{
  border: 0;
  cursor: pointer;
  font-weight: 1000;
  padding: 10px 12px;
  border-radius: 12px;
  color: #7f1d1d;
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.20);
  transition: .15s;
  white-space: nowrap;
}
.btn-danger:hover{ background: rgba(239, 68, 68, 0.18); }
.btn-danger:disabled{ opacity:.6; cursor:not-allowed; }

/* avatar */
.avatar-box{
  display:flex;
  gap: 12px;
  align-items:center;
}
.avatar-preview{
  width: 84px;
  height: 84px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(15,23,42,0.04);
  display:grid;
  place-items:center;
  flex: 0 0 auto;
}
.avatar-preview img{
  width:100%;
  height:100%;
  object-fit: cover;
}
.avatar-placeholder{
  width: 100%;
  height: 100%;
  display:grid;
  place-items:center;
  font-weight: 1000;
  color:#fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.avatar-meta{ min-width: 0; }
.avatar-name{ font-weight: 1000; font-size: 14px; }

/* file input */
.upload{ display:flex; flex-direction: column; gap: 10px; }
.file{
  display:flex;
  gap: 10px;
  align-items:center;
  flex-wrap: wrap;
}
.file input{ display:none; }
.file-btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding: 9px 12px;
  border-radius: 12px;
  border: 1px solid rgba(15,23,42,0.14);
  background: rgba(255,255,255,0.70);
  font-weight: 1000;
  cursor: pointer;
}
.file-name{ font-size: 12px; color: rgba(15,23,42,.65); }

/* skeleton */
.skeleton{ position: relative; background: rgba(15,23,42,0.06); border-radius: 12px; overflow: hidden; }
.skeleton::after{
  content:""; position:absolute; inset:0; transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
  animation: shimmer 1.1s infinite;
}
.skeleton.title{ height: 18px; width: 60%; }
.skeleton.line{ height: 10px; margin-top: 10px; }
.skeleton.block{ height: 80px; margin-top: 10px; border-radius: 14px; }
.skeleton.block.short{ height: 56px; }
.w60{ width: 60%; } .w45{ width: 45%; }
@keyframes shimmer{ 100%{ transform: translateX(100%); } }

/* empty */
.empty{ text-align: center; }
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }
</style>

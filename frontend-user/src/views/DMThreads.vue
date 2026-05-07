<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">私聊会话</div>
        <h1 class="ux-title">把一对一讨论延续下去</h1>
        <p class="ux-lead">从书评、社团讨论到临时约读，私聊会保留最近消息，并支持进入会话后发起视频通话。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ threads.length }} 个会话</div>
        <div class="ux-pill">{{ activeThreadCount }} 个有消息</div>
        <button class="btn-primary" :disabled="!hasToken || loading" @click="load">
          {{ loading ? "刷新中..." : "刷新会话" }}
        </button>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">全部会话</div>
        <div class="ux-stat__value">{{ threads.length }}</div>
        <div class="ux-stat__hint">你发起或参与的私聊</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">已有消息</div>
        <div class="ux-stat__value">{{ activeThreadCount }}</div>
        <div class="ux-stat__hint">可继续接着聊</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">新会话</div>
        <div class="ux-stat__value">{{ emptyThreadCount }}</div>
        <div class="ux-stat__hint">还没有发送消息</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">账号状态</div>
        <div class="ux-stat__value">{{ hasToken ? "正常" : "未登录" }}</div>
        <div class="ux-stat__hint">登录后同步会话</div>
      </div>
    </section>

    <section v-if="!hasToken" class="ux-empty">
      <div class="ux-empty__icon">登</div>
      <div class="ux-empty__title">登录后发起私聊</div>
      <div class="ux-empty__sub">私聊会话与账号绑定，登录后可继续历史对话。</div>
      <div class="ux-actions">
        <router-link class="ux-link" to="/login">去登录 →</router-link>
      </div>
    </section>

    <template v-else>
      <section class="ux-panel">
        <div class="ux-panel__head">
          <div>
            <h2 class="ux-section-title">发起私聊</h2>
            <div class="ux-section-sub">输入对方用户名，系统会创建或返回已有会话。</div>
          </div>
        </div>

        <div class="form-row">
          <div class="input-wrap">
            <span class="icon">人</span>
            <input
              class="input"
              v-model="toUsername"
              placeholder="输入对方用户名"
              @keydown.enter="createThread"
            />
          </div>

          <button class="btn-primary" :disabled="loading" @click="createThread">开始聊天</button>
        </div>
      </section>

      <section class="ux-panel">
        <div class="ux-panel__head">
          <div>
            <h2 class="ux-section-title">会话列表</h2>
            <div class="ux-section-sub">展示最近消息摘要，进入后可文字聊天或发起视频通话。</div>
          </div>
        </div>

        <div v-if="loading" class="ux-grid two">
          <div v-for="i in 6" :key="i" class="card pad skeleton">
            <div class="sk-line w60"></div>
            <div class="sk-line w85"></div>
            <div class="sk-line w45"></div>
            <div class="sk-btn"></div>
          </div>
        </div>

        <div v-else-if="threads.length === 0" class="ux-empty">
          <div class="ux-empty__icon">聊</div>
          <div class="ux-empty__title">暂无私聊会话</div>
          <div class="ux-empty__sub">输入用户名发起私聊后，会话会出现在这里。</div>
        </div>

        <div v-else class="ux-grid two">
          <article class="ux-card" v-for="t in threads" :key="t.id">
            <div class="ux-card__top">
              <div class="ux-card__identity">
                <div class="ux-avatar">{{ (t.other_username || "U").charAt(0).toUpperCase() }}</div>
                <div>
                  <div class="ux-card__title" :title="t.other_username">{{ t.other_username }}</div>
                  <div class="ux-section-sub" v-if="t.last_message">
                    {{ t.last_message.sender_username }}：{{ short(t.last_message.content) }}
                  </div>
                  <div class="ux-section-sub" v-else>暂无消息，发一句问候开始交流。</div>
                </div>
              </div>
              <span class="ux-chip primary">#{{ t.id }}</span>
            </div>

            <div class="ux-meta">
              <span class="ux-chip" :class="t.last_message ? 'success' : ''">
                {{ t.last_message ? "可继续" : "新会话" }}
              </span>
              <span class="ux-chip">1 对 1</span>
            </div>

            <div class="ux-actions">
              <router-link class="ux-link" :to="`/dm/${t.id}`">进入聊天 →</router-link>
            </div>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { api } from "../api";
import { useRouter } from "vue-router";

const router = useRouter();

const hasToken = computed(() => !!localStorage.getItem("access"));
const threads = ref([]);
const toUsername = ref("");
const loading = ref(false);
const activeThreadCount = computed(() => threads.value.filter((thread) => thread.last_message).length);
const emptyThreadCount = computed(() => Math.max(threads.value.length - activeThreadCount.value, 0));

function short(s, n = 36) {
  const v = String(s || "");
  return v.length > n ? v.slice(0, n) + "…" : v;
}

async function load() {
  if (!hasToken.value) return;
  loading.value = true;
  try {
    threads.value = (await api.get("/dm/threads/")).data || [];
  } finally {
    loading.value = false;
  }
}

async function createThread() {
  const u = toUsername.value.trim();
  if (!u) return alert("请输入对方用户名");

  try {
    loading.value = true;
    const res = await api.post("/dm/threads/create/", { to_username: u });
    toUsername.value = "";
    await load();
    router.push(`/dm/${res.data.id}`);
  } catch (e) {
    alert("创建失败：请确认用户名存在，且不能和自己聊天");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
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

.notice{ display:flex; gap: 12px; align-items:flex-start; }
.notice-icon{
  width: 40px; height: 40px; border-radius: 14px;
  display:grid; place-items:center;
  background: rgba(37,99,235,.10); border: 1px solid rgba(37,99,235,.16);
  flex: 0 0 auto;
}
.notice-title{ font-weight: 1000; }
.notice-sub{ margin-top: 4px; font-size: 13px; color: rgba(15,23,42,.65); line-height: 1.5; }
.link{ color: #2563eb; text-decoration: none; font-weight: 900; }
.link:hover{ text-decoration: underline; }

.section-head{ display:flex; align-items:flex-end; justify-content: space-between; gap: 10px; margin-bottom: 10px; }

.form-row{ display:flex; gap: 10px; align-items:center; flex-wrap: wrap; }
.input-wrap{
  flex: 1; min-width: 260px;
  display:flex; align-items:center; gap: 8px;
  padding: 10px 12px; border-radius: 14px;
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

.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 860px){
  .grid{ grid-template-columns: 1fr; }
}

.thread{ display:flex; flex-direction: column; gap: 12px; transition: .15s; }
.thread:hover{ transform: translateY(-1px); box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08); }

.top{ display:flex; align-items:flex-start; justify-content: space-between; gap: 10px; }
.user{ display:flex; gap: 10px; align-items:center; min-width: 0; }
.avatar{
  width: 40px; height: 40px; border-radius: 14px;
  display:grid; place-items:center;
  font-weight: 1000; color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
  flex: 0 0 auto; user-select:none;
}
.user-info{ min-width: 0; }
.name{ font-weight: 1000; font-size: 14px; overflow:hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta{ margin-top: 6px; display:flex; align-items:center; gap: 8px; }
.meta-dot{ width: 6px; height: 6px; border-radius: 999px; background: rgba(37,99,235,.55); }

.badge{
  flex: 0 0 auto;
  font-size: 11px; font-weight: 900;
  padding: 4px 8px; border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}

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
.w60{ width: 60%; } .w85{ width: 85%; } .w45{ width: 45%; }
@keyframes shimmer{ 100%{ transform: translateX(100%); } }
</style>

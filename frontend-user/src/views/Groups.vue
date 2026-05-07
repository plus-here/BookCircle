<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">即时群组</div>
        <h1 class="ux-title">加入一个正在聊天的阅读小组</h1>
        <p class="ux-lead">群组适合更轻量的即时交流：约读、同步进度、临时讨论和读后感分享。</p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ groups.length }} 个群</div>
        <div class="ux-pill">{{ joinedCount }} 个已加入</div>
        <button class="btn-primary" :disabled="!hasToken || loading" @click="load">
          {{ loading ? "刷新中..." : "刷新群组" }}
        </button>
      </div>
    </section>

    <section class="ux-stats">
      <div class="ux-stat">
        <div class="ux-stat__label">全部群组</div>
        <div class="ux-stat__value">{{ groups.length }}</div>
        <div class="ux-stat__hint">公开可加入群组</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">我已加入</div>
        <div class="ux-stat__value">{{ joinedCount }}</div>
        <div class="ux-stat__hint">可直接进入聊天</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">成员总数</div>
        <div class="ux-stat__value">{{ memberTotal }}</div>
        <div class="ux-stat__hint">群组参与规模</div>
      </div>
      <div class="ux-stat">
        <div class="ux-stat__label">我的角色</div>
        <div class="ux-stat__value">{{ ownerCount }}</div>
        <div class="ux-stat__hint">你创建的群组数</div>
      </div>
    </section>

    <section v-if="!hasToken" class="ux-empty">
      <div class="ux-empty__icon">登</div>
      <div class="ux-empty__title">登录后使用群组聊天</div>
      <div class="ux-empty__sub">登录后可以创建群组、加入讨论，并通过 WebSocket 收发实时消息。</div>
      <div class="ux-actions">
        <router-link class="ux-link" to="/login">去登录 →</router-link>
      </div>
    </section>

    <template v-else>
      <section class="ux-panel">
        <div class="ux-panel__head">
          <div>
            <h2 class="ux-section-title">创建群组</h2>
            <div class="ux-section-sub">给群组一个清晰主题，其他读者更容易判断是否加入。</div>
          </div>
        </div>

        <div class="form mature-form">
          <div class="field">
            <span class="label">群名</span>
            <div class="input-wrap">
              <span class="icon">群</span>
              <input class="input" v-model="name" placeholder="例如：科幻读书会" />
            </div>
          </div>

          <div class="field">
            <span class="label">简介（可选）</span>
            <div class="input-wrap">
              <span class="icon">介</span>
              <input class="input" v-model="description" placeholder="一句话介绍这个群" />
            </div>
          </div>

          <div class="actions">
            <button class="btn-primary" :disabled="loading" @click="createGroup">创建群组</button>
            <button class="btn-ghost" type="button" :disabled="loading" @click="name=''; description=''">清空</button>
          </div>
        </div>
      </section>

      <section class="ux-panel">
        <div class="ux-panel__head">
          <div>
            <h2 class="ux-section-title">群组列表</h2>
            <div class="ux-section-sub">已加入的群组会标记角色，群主不可直接退出自己创建的群。</div>
          </div>
        </div>

        <div v-if="loading" class="ux-grid">
          <div v-for="i in 6" :key="i" class="card pad skeleton">
            <div class="sk-line w70"></div>
            <div class="sk-line w45"></div>
            <div class="sk-line w85"></div>
            <div class="row" style="margin-top:12px;">
              <div class="sk-btn"></div>
              <div class="sk-btn ghost"></div>
              <div class="sk-btn ghost"></div>
            </div>
          </div>
        </div>

        <div v-else-if="groups.length === 0" class="ux-empty">
          <div class="ux-empty__icon">群</div>
          <div class="ux-empty__title">还没有群组</div>
          <div class="ux-empty__sub">你可以先创建一个群组，邀请朋友一起讨论一本书或一个主题。</div>
        </div>

        <div v-else class="ux-grid">
          <article v-for="g in groups" :key="g.id" class="ux-card">
            <div class="ux-card__top">
              <div class="ux-card__identity">
                <div class="ux-avatar">{{ (g.name || "群").charAt(0) }}</div>
                <div>
                  <div class="ux-card__title" :title="g.name">{{ g.name }}</div>
                  <div class="ux-section-sub">创建者：{{ g.creator_username }}</div>
                </div>
              </div>
              <span class="ux-chip primary">成员 {{ g.members_count }}</span>
            </div>

            <div class="ux-card__desc">{{ g.description || "暂无简介，进入聊天后可以直接发起讨论。" }}</div>

            <div class="ux-meta">
              <span class="ux-chip" :class="g.is_member ? 'success' : 'primary'">
                {{ g.is_member ? `已加入${g.my_role ? ` · ${roleLabel(g.my_role)}` : ""}` : "可加入" }}
              </span>
              <span v-if="g.my_role === 'owner'" class="ux-chip warn">你创建的群</span>
            </div>

            <div class="ux-actions">
              <router-link class="ux-link" :to="`/groups/${g.id}`">进入聊天 →</router-link>
              <button class="btn-ghost" :disabled="loading || g.is_member" @click="join(g.id)">加入</button>
              <button class="btn-danger" :disabled="loading || !g.is_member || g.my_role === 'owner'" @click="leave(g.id)">退出</button>
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

const hasToken = computed(() => !!localStorage.getItem("access"));

const groups = ref([]);
const name = ref("");
const description = ref("");
const loading = ref(false);
const joinedCount = computed(() => groups.value.filter((group) => group.is_member).length);
const ownerCount = computed(() => groups.value.filter((group) => group.my_role === "owner").length);
const memberTotal = computed(() => groups.value.reduce((sum, group) => sum + Number(group.members_count || 0), 0));

function roleLabel(role) {
  if (role === "owner") return "群主";
  if (role === "admin") return "管理员";
  return "成员";
}

async function load() {
  if (!hasToken.value) return;
  loading.value = true;
  try {
    groups.value = (await api.get("/groups/")).data;
  } finally {
    loading.value = false;
  }
}

async function createGroup() {
  if (!name.value.trim()) {
    alert("请输入群名");
    return;
  }
  try {
    await api.post("/groups/", { name: name.value, description: description.value, is_public: true });
    name.value = "";
    description.value = "";
    await load();
    alert("创建成功");
  } catch {
    alert("创建失败，请稍后再试");
  }
}

async function join(groupId) {
  try {
    await api.post(`/groups/${groupId}/join/`);
    alert("已加入");
    await load();
  } catch {
    alert("加入失败，可能已经在群组中");
  }
}

async function leave(groupId) {
  try {
    await api.post(`/groups/${groupId}/leave/`);
    alert("已退出");
    await load();
  } catch {
    alert("退出失败，请稍后再试");
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

.stack{ display:flex; flex-direction: column; gap: 14px; }
.row{ display:flex; gap: 10px; align-items:center; flex-wrap: wrap; }

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.h2{ font-weight: 1000; }
.sub{
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(15,23,42,.65);
  line-height: 1.5;
}
.muted{ color: rgba(15,23,42,.60); font-size: 12px; }

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
.btn-primary:disabled{ opacity: .6; cursor: not-allowed; transform:none; }

/* notice */
.notice{
  display:flex;
  gap: 12px;
  align-items:flex-start;
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
.notice-sub{ margin-top: 4px; font-size: 13px; color: rgba(15,23,42,.65); line-height: 1.5; }
.link{ color: #2563eb; text-decoration: none; font-weight: 900; }
.link:hover{ text-decoration: underline; }

/* form */
.form{ display:flex; flex-direction: column; gap: 12px; }
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
.actions{ display:flex; gap: 10px; flex-wrap: wrap; }

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
.btn-ghost:disabled{ opacity:.6; cursor:not-allowed; }

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
}
.btn-danger:hover{ background: rgba(239, 68, 68, 0.18); }
.btn-danger:disabled{ opacity:.6; cursor:not-allowed; }

/* groups grid */
.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 860px){
  .grid{ grid-template-columns: 1fr; }
}

.group{ display:flex; flex-direction: column; gap: 10px; transition: .15s; }
.group:hover{ transform: translateY(-1px); box-shadow: 0 18px 40px rgba(2, 6, 23, 0.08); }

.top{
  display:flex;
  align-items:flex-start;
  justify-content: space-between;
  gap: 10px;
}
.name{
  font-weight: 1000;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
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
.desc{
  font-size: 12px;
  color: rgba(15,23,42,.70);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 56px;
}
.meta{
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
  white-space: nowrap;
}
.link-btn:hover{ background: rgba(37,99,235,.12); }

/* empty */
.empty{ text-align: center; }
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
  margin-top: 10px;
}
.sk-btn{
  height: 36px;
  width: 110px;
  border-radius: 12px;
  background: rgba(15,23,42,0.06);
}
.sk-btn.ghost{ width: 92px; }

.w70{ width: 70%; }
.w45{ width: 45%; }
.w85{ width: 85%; }

@keyframes shimmer{
  100%{ transform: translateX(100%); }
}
</style>

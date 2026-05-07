<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">群组实时聊天</div>
        <h1 class="ux-title">群组 #{{ groupId }}</h1>
        <p class="ux-lead">
          <span class="status-dot" :class="{ ok: wsConnected }"></span>
          连接状态：{{ wsStatus || "未连接" }}。消息会实时同步，历史记录也会保留。
        </p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ messages.length }} 条消息</div>
        <button class="btn-ghost" :disabled="loadingHistory" @click="loadHistory">
          {{ loadingHistory ? "刷新中..." : "刷新历史" }}
        </button>
      </div>
    </section>

    <!-- 未登录 -->
    <div v-if="!hasToken" class="card pad notice">
      <div class="notice-icon">🔒</div>
      <div>
        <div class="notice-title">你还没有登录</div>
        <div class="notice-sub">
          请先去 <router-link class="link" to="/login">登录</router-link>，再进入群聊。
        </div>
      </div>
    </div>

    <!-- 聊天区 -->
    <div v-else class="chat card">
      <!-- 消息列表 -->
      <div class="messages" ref="box">
        <div v-if="messages.length === 0" class="empty">
          <div class="empty-icon">💬</div>
          <div class="empty-title">还没有消息</div>
          <div class="empty-sub">发一条消息，开始聊天吧。</div>
        </div>

        <div v-else class="msg-list">
          <div
            v-for="m in messages"
            :key="m._key"
            class="msg"
            :class="{ mine: isMine(m) }"
          >
            <!-- 头像 -->
            <div class="avatar">
              {{ (m.sender_username || "U").charAt(0).toUpperCase() }}
            </div>

            <div class="bubble-wrap">
              <div class="meta">
                <span class="name">{{ isMine(m) ? "我" : m.sender_username }}</span>

                <span class="right-meta">
                  <span v-if="m.pending" class="pending">发送中…</span>
                  <span class="time">{{ fmtTime(m.created_at) }}</span>
                </span>
              </div>

              <div class="bubble" :class="{ pending: m.pending }">
                {{ m.message }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="composer">
        <div class="input-wrap">
          <span class="icon">✉️</span>
          <input
            class="input"
            v-model="text"
            placeholder="输入消息…（回车发送）"
            @keydown.enter="send"
          />
        </div>

        <button class="btn-primary" :disabled="!canSend" @click="send">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import { api, WS_BASE } from "../api";

const route = useRoute();
const groupId = computed(() => route.params.id);
const hasToken = computed(() => !!localStorage.getItem("access"));

const messages = ref([]);
const text = ref("");
const wsStatus = ref("");
const wsConnected = ref(false);
const myUsername = ref("");
const box = ref(null);
const loadingHistory = ref(false);

let ws = null;
let alive = true;

// ====== 工具：JWT 解码（支持 base64url）======
function decodeJwtPayload(token) {
  try {
    const b64 = token.split(".")[1];
    const normalized = b64.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized + "===".slice((normalized.length + 3) % 4);
    return JSON.parse(atob(padded));
  } catch {
    return null;
  }
}

const myUserId = computed(() => {
  const token = localStorage.getItem("access");
  if (!token) return null;
  const payload = decodeJwtPayload(token);
  return payload?.user_id != null ? Number(payload.user_id) : null;
});

// ====== 我是谁（用于“自己消息靠右”）======
async function loadMe() {
  try {
    const res = await api.get("/auth/me/");
    myUsername.value = res.data.username || "";
  } catch {
    myUsername.value = "";
  }
}

// ====== 是否我的消息（优先 sender_id，其次 username）======
function isMine(m) {
  if (myUserId.value != null && m.sender_id != null) {
    return Number(m.sender_id) === Number(myUserId.value);
  }
  if (myUsername.value) {
    return m.sender_username === myUsername.value;
  }
  return false;
}

// ====== 时间统一显示（解决“新消息短、历史长”）======
function fmtTime(v) {
  if (!v) return "";
  const d = new Date(v);
  if (!Number.isNaN(d.getTime())) return d.toLocaleString();
  return String(v)
    .replace("T", " ")
    .replace("Z", "")
    .replace("+00:00", "");
}

// ====== 滚动：只有接近底部才自动滚到底，避免翻历史被拉回 ======
function isNearBottom() {
  if (!box.value) return true;
  const el = box.value;
  return el.scrollHeight - (el.scrollTop + el.clientHeight) < 140;
}

function scrollBottom(force = false) {
  nextTick(() => {
    if (!box.value) return;
    if (!force && !isNearBottom()) return;
    box.value.scrollTop = box.value.scrollHeight;
  });
}

// ====== 去重：记录已收到的 server message id ======
const seenIds = new Set();

// ====== 本地“发送中”队列（用于和服务器回推匹配去重）======
const pendingQueue = []; // { key, msg, t }

// ====== 拉历史 ======
async function loadHistory() {
  if (!hasToken.value) return;
  loadingHistory.value = true;
  try {
    const res = await api.get(`/groups/${groupId.value}/messages/`);
    const list = (res.data || []).map((x) => {
      const id = x.id;
      if (id != null) seenIds.add(id);
      return {
        id,
        _key: `h-${id}`,
        sender_username: x.sender_username,
        sender_id: x.sender || x.sender_id || null,
        message: x.content ?? x.message ?? "",
        created_at: x.created_at,
        pending: false,
      };
    });
    messages.value = list;
    scrollBottom(true);
  } finally {
    loadingHistory.value = false;
  }
}

// ====== WS 连接（带自动重连）======
let reconnectTimer = null;
let reconnectDelay = 1000;

function clearReconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  reconnectDelay = 1000;
}

function scheduleReconnect() {
  if (!alive) return;
  if (!hasToken.value) return;
  clearReconnect();
  const delay = reconnectDelay;
  reconnectDelay = Math.min(reconnectDelay * 2, 10000);
  wsStatus.value = `断线重连中...（${Math.round(delay / 1000)}s）`;
  reconnectTimer = setTimeout(() => {
    connectWs();
  }, delay);
}

function connectWs() {
  const token = localStorage.getItem("access");
  if (!token) return;

  // 先关掉旧连接
  try {
    if (ws) ws.close();
  } catch {}
  ws = null;

  wsConnected.value = false;
  wsStatus.value = "连接中...";

  const url = `${WS_BASE}/ws/groups/${groupId.value}/?token=${encodeURIComponent(token)}`;
  ws = new WebSocket(url);

  ws.onopen = () => {
    wsConnected.value = true;
    wsStatus.value = "已连接";
    clearReconnect();
  };

  ws.onclose = (e) => {
    wsConnected.value = false;
    wsStatus.value = `已断开（code=${e.code} reason=${e.reason || "无"}）`;

    // 1000 通常是正常关闭（比如切换页面/手动关闭），不重连
    if (alive && e.code !== 1000) {
      scheduleReconnect();
    }
  };

  ws.onerror = () => {
    wsConnected.value = false;
    wsStatus.value = "连接失败，请稍后重试";
  };

  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      const serverId = data.id;

      // 若 serverId 已见过，直接忽略（防止重复）
      if (serverId != null && seenIds.has(serverId)) return;
      if (serverId != null) seenIds.add(serverId);

      const incoming = {
        id: serverId ?? null,
        _key: `ws-${serverId ?? Date.now()}-${Math.random().toString(16).slice(2)}`,
        sender_username: data.sender_username,
        sender_id: data.sender || data.sender_id || null,
        message: data.message ?? data.content ?? "",
        created_at: data.created_at,
        pending: false,
      };

      // 如果这条是“我发的”，尝试把本地 pending 消息替换掉（去重）
      const mine = isMine(incoming);
      if (mine && pendingQueue.length) {
        const now = Date.now();
        const idx = pendingQueue.findIndex(
          (p) => p.msg === incoming.message && now - p.t < 8000
        );
        if (idx >= 0) {
          const { key } = pendingQueue.splice(idx, 1)[0];
          const pos = messages.value.findIndex((m) => m._key === key);
          if (pos >= 0) messages.value.splice(pos, 1);
        }
      }

      messages.value.push(incoming);
      scrollBottom(mine);
    } catch {}
  };
}

const canSend = computed(() => {
  const msg = text.value.trim();
  return !!msg && wsConnected.value && ws && ws.readyState === WebSocket.OPEN;
});

// ====== 发送（本地立即显示 + pending）======
function send() {
  const msg = text.value.trim();
  if (!msg) return;

  // 没连上也别丢：提示一下（你也可以改成 toast）
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    wsStatus.value = "未连接，发送失败（请稍后重试）";
    return;
  }

  // 本地立即显示
  const localKey = `local-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const localMsg = {
    id: null,
    _key: localKey,
    sender_username: myUsername.value || "我",
    sender_id: myUserId.value ?? null,
    message: msg,
    created_at: new Date().toISOString(),
    pending: true,
  };
  messages.value.push(localMsg);
  pendingQueue.push({ key: localKey, msg, t: Date.now() });
  scrollBottom(true);

  ws.send(JSON.stringify({ message: msg }));
  text.value = "";
}

// ====== 生命周期 ======
onMounted(async () => {
  alive = true;
  await loadMe();
  await loadHistory();
  connectWs();
});

watch(
  () => groupId.value,
  async () => {
    // 切换群：清空并重连
    seenIds.clear();
    pendingQueue.splice(0, pendingQueue.length);
    messages.value = [];
    await loadHistory();
    connectWs();
  }
);

onBeforeUnmount(() => {
  alive = false;
  clearReconnect();
  try {
    if (ws) ws.close(1000, "bye");
  } catch {}
  ws = null;
});
</script>

<style scoped>
.page{
  display:flex;
  flex-direction: column;
  gap: 14px;
  padding: 6px 0 24px;
}

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
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
.title-row{ display:flex; align-items:center; gap: 10px; }
.badge{
  font-size: 11px;
  font-weight: 900;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}
.sub{
  margin-top: 8px;
  display:flex;
  align-items:center;
  gap: 8px;
}
.status-dot{
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(15,23,42,.25);
}
.status-dot.ok{ background: rgba(16,185,129,1); }

/* buttons */
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
.btn-primary:disabled{ opacity: .6; cursor: not-allowed; transform:none; }
.btn-primary:hover{ transform: translateY(-1px); }
.btn-primary:active{ transform: translateY(0px); }

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
.btn-ghost:disabled{ opacity: .6; cursor: not-allowed; }
.btn-ghost:hover{ background: rgba(15,23,42,0.04); }

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

/* chat */
.chat{
  display:flex;
  flex-direction: column;
  overflow: hidden;
  height: calc(100vh - 260px);
  min-height: 520px;
}
@media (max-width: 720px){
  .chat{ height: calc(100vh - 290px); min-height: 460px; }
}

.messages{
  flex: 1;
  overflow: auto;
  padding: 14px;
  background:
    radial-gradient(500px 240px at 10% 0%, rgba(59,130,246,.10), transparent 60%),
    rgba(255,255,255,0.55);
}

.msg-list{ display:flex; flex-direction: column; gap: 12px; }

.msg{
  display:flex;
  align-items:flex-end;
  gap: 10px;
}
.msg.mine{ flex-direction: row-reverse; }

.avatar{
  width: 34px;
  height: 34px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  font-weight: 1000;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
  user-select:none;
  flex: 0 0 auto;
}

.bubble-wrap{ min-width: 0; max-width: 78%; }

.meta{
  display:flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
  font-size: 12px;
  color: rgba(15,23,42,.62);
}
.msg.mine .meta{ justify-content: flex-end; }
.name{ font-weight: 900; }
.right-meta{ display:inline-flex; gap: 10px; align-items:center; }
.time{ color: rgba(15,23,42,.55); }
.pending{
  font-weight: 900;
  color: rgba(245,158,11,1);
  background: rgba(245,158,11,.10);
  border: 1px solid rgba(245,158,11,.18);
  padding: 2px 8px;
  border-radius: 999px;
}

.bubble{
  display:inline-block;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.82);
  line-height: 1.6;
  font-size: 14px;
  color: rgba(15,23,42,.88);
  word-break: break-word;
  box-shadow: 0 10px 22px rgba(2, 6, 23, 0.05);
}
.msg.mine .bubble{
  background: rgba(37,99,235,0.12);
  border-color: rgba(37,99,235,0.18);
}
.bubble.pending{ opacity: .75; }

/* composer */
.composer{
  padding: 12px;
  border-top: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.86);
  display:flex;
  gap: 10px;
  align-items:center;
}

.input-wrap{
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

/* empty */
.empty{
  padding: 22px;
  border-radius: 16px;
  border: 1px dashed rgba(15, 23, 42, 0.16);
  background: rgba(255,255,255,0.75);
  text-align: center;
  margin-top: 8px;
}
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 1000; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }
</style>

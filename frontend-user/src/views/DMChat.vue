<template>
  <div class="ux-page">
    <section class="ux-hero">
      <div class="ux-hero__main">
        <div class="ux-kicker">一对一会话</div>
        <h1 class="ux-title">私聊 #{{ threadId }}</h1>
        <p class="ux-lead">
          <span class="status-dot" :class="{ ok: wsConnected }"></span>
          消息连接：{{ wsStatus }}，通话状态：{{ callStatus }}。
        </p>
      </div>

      <div class="ux-hero__actions">
        <div class="ux-pill">{{ messages.length }} 条消息</div>
        <div class="ux-pill">{{ calling ? "通话中" : "可发起通话" }}</div>
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
          请先去 <router-link class="link" to="/login">登录</router-link>，再进入私聊。
        </div>
      </div>
    </div>

    <div v-else class="stack">
      <!-- 聊天区 -->
      <div class="chat card">
        <div class="messages" ref="box">
          <div v-if="messages.length === 0" class="empty">
            <div class="empty-icon">💬</div>
            <div class="empty-title">还没有消息</div>
            <div class="empty-sub">发一条消息开始聊天吧。</div>
          </div>

          <div v-else class="msg-list">
            <div
              v-for="m in messages"
              :key="m._key"
              class="msg"
              :class="{ mine: isMine(m) }"
            >
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

        <div class="composer">
          <div class="input-wrap">
            <span class="icon">✉️</span>
            <input class="input" v-model="text" placeholder="输入消息…（回车发送）" @keydown.enter="sendText" />
          </div>
          <button class="btn-primary" :disabled="!canSendText" @click="sendText">发送</button>
        </div>
      </div>

      <!-- 视频通话面板 -->
      <div class="card pad">
        <div class="section-head">
          <div>
            <div class="h2">视频通话（1 对 1）</div>
            <div class="muted">首次会弹摄像头/麦克风授权，建议戴耳机避免回音。</div>
          </div>

          <span class="chip" :class="{ on: calling }">{{ calling ? "通话中" : "空闲" }}</span>
        </div>

        <div class="call-actions">
          <button class="btn-primary" @click="startVideoCall" :disabled="calling || !wsConnected">
            发起视频通话
          </button>
          <button class="btn-danger" @click="hangup(true)" :disabled="!calling">
            挂断
          </button>
        </div>

        <div class="call-status" :class="{ error: isCallError, ok: calling }">
          <span class="status-dot" :class="{ ok: calling }"></span>
          <span>{{ callStatus }}</span>
        </div>

        <div v-if="incomingOffer" class="incoming-call">
          <div class="incoming-pulse">视频</div>
          <div class="incoming-body">
            <div class="incoming-title">{{ incomingFrom || "对方" }} 邀请你视频通话</div>
            <div class="incoming-sub">你可以先接听，再授权摄像头和麦克风。</div>
          </div>
          <div class="incoming-actions">
            <button class="btn-primary" type="button" @click="acceptIncomingCall">接听</button>
            <button class="btn-danger" type="button" @click="rejectIncomingCall">挂断</button>
          </div>
        </div>

        <div class="videos">
          <div class="video-card">
            <div class="video-title">本地画面</div>
            <video ref="localVideo" autoplay playsinline muted></video>
          </div>

          <div class="video-card">
            <div class="video-title">对方画面</div>
            <video ref="remoteVideo" autoplay playsinline></video>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import { api, WS_BASE, RTC_CONFIG } from "../api";

const route = useRoute();
const threadId = computed(() => route.params.id);
const hasToken = computed(() => !!localStorage.getItem("access"));

const messages = ref([]);
const text = ref("");
const wsStatus = ref("未连接");
const wsConnected = ref(false);
const myUsername = ref("");
const box = ref(null);
const loadingHistory = ref(false);

let ws = null;
let alive = true;

// ====== WebRTC（视频）状态 ======
const callStatus = ref("空闲");
const calling = ref(false);
const isCallError = computed(() => callStatus.value.includes("失败") || callStatus.value.includes("权限"));
const incomingOffer = ref(null);
const incomingFrom = ref("");

let pc = null;
let localStream = null;
const pendingIceCandidates = [];
let activeCallId = "";

const localVideo = ref(null);
const remoteVideo = ref(null);

const rtcConfig = RTC_CONFIG;

// ====== JWT 解码（base64url）======
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

async function loadMe() {
  try {
    const res = await api.get("/auth/me/");
    myUsername.value = res.data.username || "";
  } catch {
    myUsername.value = "";
  }
}

function isMine(m) {
  if (myUserId.value != null && m.sender_id != null) {
    return Number(m.sender_id) === Number(myUserId.value);
  }
  if (myUsername.value) return m.sender_username === myUsername.value;
  return false;
}

function fmtTime(v) {
  if (!v) return "";
  const d = new Date(v);
  if (!Number.isNaN(d.getTime())) return d.toLocaleString();
  return String(v).replace("T", " ").replace("Z", "").replace("+00:00", "");
}

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

// ====== 去重 + 本地 pending ======
const seenIds = new Set();
const pendingQueue = []; // { key, msg, t }

// ====== 历史 ======
async function loadHistory() {
  if (!hasToken.value) return;
  loadingHistory.value = true;
  try {
    const res = await api.get(`/dm/threads/${threadId.value}/messages/`);
    const list = (res.data || []).map((x) => {
      if (x.id != null) seenIds.add(x.id);
      return {
        id: x.id,
        _key: `h-${x.id}`,
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

// ====== WS 自动重连 ======
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
  if (!alive || !hasToken.value) return;
  clearReconnect();
  const delay = reconnectDelay;
  reconnectDelay = Math.min(reconnectDelay * 2, 10000);
  wsStatus.value = `断线重连中...（${Math.round(delay / 1000)}s）`;
  reconnectTimer = setTimeout(() => connectWs(), delay);
}

function connectWs() {
  const token = localStorage.getItem("access");
  if (!token) return;

  try { if (ws) ws.close(); } catch {}
  ws = null;

  wsConnected.value = false;
  wsStatus.value = "连接中...";

  const url = `${WS_BASE}/ws/dm/${threadId.value}/?token=${encodeURIComponent(token)}`;
  ws = new WebSocket(url);

  ws.onopen = () => {
    wsConnected.value = true;
    wsStatus.value = "已连接";
    clearReconnect();
  };

  ws.onclose = (e) => {
    wsConnected.value = false;
    wsStatus.value = `已断开(code=${e.code})`;
    if (alive && e.code !== 1000) scheduleReconnect();
  };

  ws.onerror = () => {
    wsConnected.value = false;
    wsStatus.value = "连接错误";
  };

  ws.onmessage = async (e) => {
    try {
      const data = JSON.parse(e.data);

      // 1) 普通私聊消息
      if (data.type === "dm_message") {
        const serverId = data.id;

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

        // 如果是我发的：尝试替换本地 pending（避免重复）
        if (isMine(incoming) && pendingQueue.length) {
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
        scrollBottom(isMine(incoming));
        return;
      }

      // 2) WebRTC 信令
      if (data.type === "dm_signal" && data.signal) {
        const s = data.signal;
        if (s.type === "offer") onOffer(s, data.from);
        if (s.type === "answer") await onAnswer(s.data);
        if (s.type === "ice") await onIce(s.data);
        if (s.type === "hangup") hangup(false);
        if (s.type === "reject") {
          hangup(false);
          callStatus.value = s.reason === "busy" ? "对方正在通话中" : "对方已挂断";
        }
      }
    } catch {}
  };
}

const canSendText = computed(() => {
  const msg = text.value.trim();
  return !!msg && wsConnected.value && ws && ws.readyState === WebSocket.OPEN;
});

// ====== 发送文字：本地立即显示 + pending ======
function sendText() {
  const msg = text.value.trim();
  if (!msg) return;

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    wsStatus.value = "未连接，发送失败（请稍后重试）";
    return;
  }

  const localKey = `local-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  messages.value.push({
    id: null,
    _key: localKey,
    sender_username: myUsername.value || "我",
    sender_id: myUserId.value ?? null,
    message: msg,
    created_at: new Date().toISOString(),
    pending: true,
  });
  pendingQueue.push({ key: localKey, msg, t: Date.now() });
  scrollBottom(true);

  ws.send(JSON.stringify({ message: msg }));
  text.value = "";
}

// ====== WebRTC 视频通话核心 ======
function sendSignal(payload) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ signal: payload }));
}

async function ensurePeerConnection() {
  if (pc) return;

  pc = new RTCPeerConnection(rtcConfig);

  pc.onconnectionstatechange = () => {
    if (!pc) return;
    const state = pc.connectionState;
    if (state === "connected") callStatus.value = "通话中";
    if (state === "connecting") callStatus.value = "正在建立媒体连接...";
    if (state === "failed") callStatus.value = "媒体连接失败，请检查网络或 TURN 配置";
    if (state === "disconnected") callStatus.value = "媒体连接已中断，正在等待恢复";
    if (state === "closed") callStatus.value = "空闲";
  };

  pc.oniceconnectionstatechange = () => {
    if (!pc) return;
    if (pc.iceConnectionState === "checking") {
      callStatus.value = "正在穿透网络...";
    }
    if (pc.iceConnectionState === "failed") {
      callStatus.value = "网络穿透失败，跨公网需要 TURN 服务";
    }
  };

  pc.onicecandidate = (e) => {
    if (e.candidate) {
      sendSignal({ type: "ice", data: e.candidate.toJSON ? e.candidate.toJSON() : e.candidate });
    }
  };

  pc.ontrack = (e) => {
    const stream = e.streams[0];
    if (remoteVideo.value) remoteVideo.value.srcObject = stream;
  };
}

async function getMedia() {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("当前浏览器或访问方式不支持摄像头/麦克风，请使用 HTTPS 或 localhost");
  }

  if (localStream) return;
  localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });

  if (localVideo.value) localVideo.value.srcObject = localStream;
  localStream.getTracks().forEach((t) => pc.addTrack(t, localStream));
}

async function startVideoCall() {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    callStatus.value = "WebSocket 未连接，无法发起通话";
    return;
  }
  if (incomingOffer.value) {
    callStatus.value = "请先处理当前来电";
    return;
  }

  try {
    activeCallId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    calling.value = true;
    callStatus.value = "获取摄像头/麦克风权限...";

    await ensurePeerConnection();
    await getMedia();

    callStatus.value = "创建 offer...";
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    sendSignal({ type: "offer", data: offer, callId: activeCallId });
    callStatus.value = "已发起，等待对方接听...";
  } catch (err) {
    if (err?.name === "NotAllowedError") {
      callStatus.value = "发起失败：请允许摄像头和麦克风权限";
    } else if (err?.name === "NotFoundError") {
      callStatus.value = "发起失败：未找到可用摄像头或麦克风";
    } else if (err?.message) {
      callStatus.value = `发起失败：${err.message}`;
    } else {
      callStatus.value = `发起失败：${err?.name || err}`;
    }
    cleanup(false, false);
  }
}

function onOffer(signal, from) {
  if (calling.value || incomingOffer.value) {
    sendSignal({ type: "reject", reason: "busy", callId: signal.callId });
    return;
  }
  activeCallId = signal.callId || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  incomingOffer.value = signal.data;
  incomingFrom.value = from || "对方";
  callStatus.value = `${incomingFrom.value} 发来视频通话`;
}

async function acceptIncomingCall() {
  const offer = incomingOffer.value;
  if (!offer) return;
  incomingOffer.value = null;

  try {
    calling.value = true;
    callStatus.value = "接听中（获取摄像头/麦克风）...";

    await ensurePeerConnection();
    await getMedia();

    await pc.setRemoteDescription(offer);
    await flushPendingIceCandidates();
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    sendSignal({ type: "answer", data: answer, callId: activeCallId });
    callStatus.value = "通话中...";
  } catch (err) {
    if (err?.name === "NotAllowedError") {
      callStatus.value = "接听失败：请允许摄像头和麦克风权限";
    } else if (err?.name === "NotFoundError") {
      callStatus.value = "接听失败：未找到可用摄像头或麦克风";
    } else if (err?.message) {
      callStatus.value = `接听失败：${err.message}`;
    } else {
      callStatus.value = `接听失败：${err?.name || err}`;
    }
    cleanup(false, false);
  }
}

function rejectIncomingCall() {
  if (!incomingOffer.value) return;
  sendSignal({ type: "reject", callId: activeCallId });
  incomingOffer.value = null;
  incomingFrom.value = "";
  activeCallId = "";
  callStatus.value = "已挂断来电";
}

async function onAnswer(answer) {
  if (!pc) return;
  await pc.setRemoteDescription(answer);
  await flushPendingIceCandidates();
  callStatus.value = "通话中...";
}

async function onIce(candidate) {
  if (!pc || !pc.remoteDescription) {
    pendingIceCandidates.push(candidate);
    return;
  }
  try {
    await pc.addIceCandidate(candidate);
  } catch {}
}

async function flushPendingIceCandidates() {
  if (!pc || !pc.remoteDescription) return;
  while (pendingIceCandidates.length) {
    const candidate = pendingIceCandidates.shift();
    try {
      await pc.addIceCandidate(candidate);
    } catch {}
  }
}

function cleanup(sendToOther, resetStatus = true) {
  if (sendToOther) sendSignal({ type: "hangup" });

  calling.value = false;
  if (resetStatus) callStatus.value = "空闲";
  incomingOffer.value = null;
  incomingFrom.value = "";
  activeCallId = "";
  pendingIceCandidates.splice(0, pendingIceCandidates.length);

  if (pc) {
    pc.close();
    pc = null;
  }
  if (localStream) {
    localStream.getTracks().forEach((t) => t.stop());
    localStream = null;
  }

  if (localVideo.value) localVideo.value.srcObject = null;
  if (remoteVideo.value) remoteVideo.value.srcObject = null;
}

function hangup(sendToOther) {
  cleanup(sendToOther);
}

// ====== 生命周期 ======
onMounted(async () => {
  alive = true;
  await loadMe();
  await loadHistory();
  connectWs();
});

watch(
  () => threadId.value,
  async () => {
    // 切换会话：清空并重连
    cleanup(false);
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
  cleanup(false);
  try { if (ws) ws.close(1000, "bye"); } catch {}
  ws = null;
});
</script>

<style scoped>
.page{ display:flex; flex-direction: column; gap: 14px; padding: 6px 0 24px; }
.stack{ display:flex; flex-direction: column; gap: 14px; }

.h1{ margin: 0; font-size: 20px; letter-spacing: .2px; }
.h2{ font-weight: 1000; }
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
.title-row{ display:flex; align-items:center; gap: 10px; }
.badge{
  font-size: 11px; font-weight: 900;
  padding: 4px 8px; border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  white-space: nowrap;
}
.sub{
  margin-top: 8px;
  display:flex; align-items:center; gap: 8px;
  flex-wrap: wrap;
}
.sep{ color: rgba(15,23,42,.35); }
.status-dot{
  width: 8px; height: 8px; border-radius: 999px;
  background: rgba(15,23,42,.25);
}
.status-dot.ok{ background: rgba(16,185,129,1); }

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
.btn-ghost:disabled{ opacity:.6; cursor:not-allowed; }
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
}
.btn-danger:hover{ background: rgba(239, 68, 68, 0.18); }
.btn-danger:disabled{ opacity:.6; cursor:not-allowed; }

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
.msg{ display:flex; align-items:flex-end; gap: 10px; }
.msg.mine{ flex-direction: row-reverse; }

.avatar{
  width: 34px; height: 34px; border-radius: 14px;
  display:grid; place-items:center;
  font-weight: 1000; color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
  user-select:none; flex: 0 0 auto;
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
.input{ width: 100%; border: 0; outline: none; background: transparent; font-size: 14px; }

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

/* call panel */
.section-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}
.chip{
  font-size: 11px;
  font-weight: 1000;
  padding: 4px 10px;
  border-radius: 999px;
  color: rgba(15,23,42,.70);
  background: rgba(15,23,42,.06);
  border: 1px solid rgba(15,23,42,.10);
  white-space: nowrap;
}
.chip.on{
  color: rgba(16,185,129,1);
  background: rgba(16,185,129,.10);
  border-color: rgba(16,185,129,.18);
}

.call-actions{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.call-status{
  display:flex;
  align-items:center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.72);
  color: rgba(15,23,42,.72);
  font-size: 13px;
  font-weight: 900;
  line-height: 1.45;
}
.call-status.ok{
  color: rgba(4,120,87,1);
  border-color: rgba(16,185,129,.18);
  background: rgba(16,185,129,.08);
}
.call-status.error{
  color: rgba(127,29,29,1);
  border-color: rgba(239,68,68,.22);
  background: rgba(239,68,68,.09);
}

.incoming-call{
  display:flex;
  align-items:center;
  gap: 14px;
  margin-bottom: 12px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(37,99,235,.22);
  background:
    radial-gradient(420px 180px at 0% 0%, rgba(37,99,235,.16), transparent 58%),
    rgba(255,255,255,.88);
  box-shadow: 0 18px 42px rgba(37,99,235,.12);
}
.incoming-pulse{
  width: 50px;
  height: 50px;
  border-radius: 18px;
  display:grid;
  place-items:center;
  flex: 0 0 auto;
  color:#fff;
  font-size: 12px;
  font-weight: 1000;
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  box-shadow: 0 0 0 8px rgba(37,99,235,.10);
}
.incoming-body{
  min-width: 0;
  flex: 1;
}
.incoming-title{
  font-weight: 1000;
  color: rgba(15,23,42,.92);
}
.incoming-sub{
  margin-top: 4px;
  color: rgba(15,23,42,.60);
  font-size: 12px;
  line-height: 1.5;
}
.incoming-actions{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content:flex-end;
}

.videos{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 860px){
  .videos{ grid-template-columns: 1fr; }
}

.video-card{
  border-radius: 16px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.70);
  padding: 12px;
}
.video-title{
  font-size: 12px;
  font-weight: 1000;
  color: rgba(15,23,42,.70);
  margin-bottom: 8px;
}
video{
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(15,23,42,0.04);
}
</style>

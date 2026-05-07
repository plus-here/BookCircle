<template>
  <div class="home">
    <div class="hero">
      <div class="hero-left">
        <div class="eyebrow">BookCircle Reading Hub</div>
        <h1 class="hero-title">把阅读、社群和活动放在同一个地方</h1>
        <p class="hero-sub">发现值得读的书，加入同好社团，记录进度，并在活动和聊天里把阅读继续下去。</p>

        <div class="hero-actions">
          <a class="btn primary" href="#books">浏览书籍</a>
          <router-link class="btn secondary" to="/clubs">加入社团</router-link>
        </div>
      </div>

      <div class="hero-right">
        <div class="hero-metric">
          <span>书库藏书</span>
          <strong>{{ books.length }}</strong>
          <small>当前可浏览</small>
        </div>
        <div class="hero-note">
          <span class="dot"></span>
          <span>从选书到加入书架，再到讨论和报名活动，一条线完成。</span>
        </div>
      </div>
    </div>

    <section class="quick-grid" aria-label="阅读入口">
      <router-link class="quick-card" to="/">
        <span class="quick-icon">📚</span>
        <span>
          <strong>找一本书</strong>
          <small>按书名或作者快速检索</small>
        </span>
      </router-link>
      <router-link class="quick-card" to="/shelf">
        <span class="quick-icon">🗂️</span>
        <span>
          <strong>继续阅读</strong>
          <small>回到上次读到的章节</small>
        </span>
      </router-link>
      <router-link class="quick-card" to="/groups">
        <span class="quick-icon">💬</span>
        <span>
          <strong>参与讨论</strong>
          <small>在群组和私聊里交流</small>
        </span>
      </router-link>
      <router-link class="quick-card" to="/activities">
        <span class="quick-icon">🎯</span>
        <span>
          <strong>报名活动</strong>
          <small>读书会、打卡和分享会</small>
        </span>
      </router-link>
    </section>

    <div class="search">
      <div class="search-row">
        <div class="search-input">
          <span class="icon">🔎</span>
          <input
            v-model="q"
            placeholder="搜索书名 / 作者（按回车搜索）"
            @keydown.enter="loadBooks"
          />
        </div>
        <button class="btn" @click="loadBooks">搜索</button>
      </div>
      <div class="search-tip">提示：支持模糊搜索，例如输入 “金庸” 或 “活着”。</div>
    </div>

    <section class="feature-band">
      <div>
        <div class="section-kicker">Today's Path</div>
        <h2 class="section-title">今天可以这样开始</h2>
      </div>
      <div class="path-list">
        <div class="path-item">
          <span>01</span>
          <strong>挑一本想读的书</strong>
          <small>先从书籍库里找到感兴趣的主题。</small>
        </div>
        <div class="path-item">
          <span>02</span>
          <strong>加入书架记录进度</strong>
          <small>章节进度会沉淀成自己的阅读轨迹。</small>
        </div>
        <div class="path-item">
          <span>03</span>
          <strong>去社群交换想法</strong>
          <small>把读到的句子、疑问和灵感聊起来。</small>
        </div>
      </div>
    </section>

    <div id="books" class="section-head">
      <div>
        <div class="section-kicker">Library</div>
        <h2 class="section-title">精选书籍</h2>
      </div>
      <span class="count-pill">{{ displayBooks.length }} 本</span>
    </div>

    <div v-if="loading" class="grid">
      <div v-for="i in 6" :key="i" class="book skeleton">
        <div class="cover"></div>
        <div class="body">
          <div class="line w70"></div>
          <div class="line w50"></div>
          <div class="line w40"></div>
        </div>
      </div>
    </div>

    <div v-else>
      <div v-if="books.length === 0" class="empty sample-note">
        <div class="empty-icon">📭</div>
        <div class="empty-title">暂无真实书籍，先展示一组示例内容</div>
        <div class="empty-sub">
          你可以先去管理端添加书籍；后台上传封面后，这里会自动优先显示真实图片。
        </div>
      </div>

      <div class="grid">
        <div v-for="b in displayBooks" :key="b.id" class="book">
          <div class="cover cover-photo" :style="coverStyle(b)">
            <div class="cover-badge">{{ (b.title || "书").charAt(0) }}</div>
          </div>

          <div class="body">
            <div class="book-label">推荐阅读</div>
            <div class="title" :title="b.title">{{ b.title }}</div>
            <div class="author">{{ b.author }}</div>
            <p class="book-desc">加入书架后可继续追踪章节进度，也可以在社团里分享读后感。</p>

            <div class="actions">
              <router-link v-if="!b.isSample" class="link-btn" :to="`/books/${b.id}`">
                查看详情 →
              </router-link>
              <span v-else class="link-btn link-btn-muted">示例封面</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <section class="community">
      <div class="community-copy">
        <div class="section-kicker">Community</div>
        <h2 class="section-title">读完一章之后，还有人等你交流</h2>
        <p>从书籍详情到社团、群组、私聊和活动，书圈把阅读后的讨论和行动接住。</p>
      </div>
      <div class="community-actions">
        <router-link class="community-link" to="/clubs">
          <strong>社团广场</strong>
          <small>找到兴趣相近的读书组织</small>
        </router-link>
        <router-link class="community-link" to="/announcements">
          <strong>公告中心</strong>
          <small>查看平台最新动态</small>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { api } from "../api";
import { coverStyle } from "../utils/media";

const books = ref([]);
const q = ref("");
const loading = ref(false);
const sampleBooks = [
  { id: "sample-1", title: "深夜图书馆", author: "示例作者", isSample: true },
  { id: "sample-2", title: "城市与阅读", author: "BookCircle", isSample: true },
  { id: "sample-3", title: "一页之间", author: "社区精选", isSample: true },
];
const displayBooks = computed(() => (books.value.length ? books.value : sampleBooks));

async function loadBooks() {
  loading.value = true;
  try {
    const res = await api.get("/books/", { params: q.value ? { q: q.value } : {} });
    books.value = res.data;
  } finally {
    loading.value = false;
  }
}

onMounted(loadBooks);
</script>

<style scoped>
.home{
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 6px 0 28px;
}

.hero{
  position: relative;
  display:flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 18px;
  min-height: 280px;
  padding: 28px;
  border-radius: 20px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(10px);
  overflow: hidden;
  box-shadow: 0 20px 54px rgba(15, 23, 42, 0.10);
}

.hero::before{
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(248,250,252,0.96) 0%, rgba(248,250,252,0.76) 46%, rgba(248,250,252,0.38) 100%),
    url("https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1400&q=80");
  background-size: cover;
  background-position: center right;
  opacity: .9;
}

.hero-left,
.hero-right{
  position: relative;
  z-index: 1;
}

.hero-left{
  flex: 1;
  min-width: 0;
  display:flex;
  flex-direction: column;
  justify-content: center;
}
.hero-right{
  width: 230px;
  display:flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 10px;
}
@media (max-width: 860px){
  .hero{ padding: 22px; min-height: auto; }
  .hero{ flex-direction: column; }
  .hero-right{ width: 100%; }
}

.eyebrow,
.section-kicker{
  font-size: 11px;
  font-weight: 1000;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: rgba(37,99,235,1);
}

.hero-title{
  max-width: 680px;
  margin: 8px 0 0;
  font-size: 36px;
  line-height: 1.12;
  letter-spacing: 0;
}

.hero-sub{
  max-width: 560px;
  margin: 12px 0 0;
  color: rgba(15,23,42,.65);
  font-size: 15px;
  line-height: 1.65;
}

.hero-actions{
  margin-top: 20px;
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-height: 42px;
  padding: 0 16px;
  border-radius: 14px;
  text-decoration: none;
  font-weight: 900;
  border: 1px solid transparent;
  transition: .15s;
}
.btn:hover{ transform: translateY(-1px); }
.btn.primary{
  color:#fff;
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  box-shadow: 0 14px 28px rgba(37, 99, 235, .22);
}
.btn.secondary{
  color: rgba(15,23,42,.86);
  background: rgba(255,255,255,.72);
  border-color: rgba(15,23,42,.12);
}

.hero-metric,
.hero-note{
  border: 1px solid rgba(15, 23, 42, .10);
  background: rgba(255,255,255,.78);
  box-shadow: 0 14px 30px rgba(2, 6, 23, .08);
  backdrop-filter: blur(10px);
}
.hero-metric{
  padding: 16px;
  border-radius: 18px;
}
.hero-metric span,
.hero-metric small{
  display:block;
  color: rgba(15,23,42,.60);
  font-size: 12px;
}
.hero-metric strong{
  display:block;
  margin: 4px 0;
  font-size: 40px;
  line-height: 1;
}
.hero-note{
  display:flex;
  gap: 8px;
  align-items:flex-start;
  padding: 12px;
  border-radius: 16px;
  color: rgba(15,23,42,.68);
  font-size: 12px;
  line-height: 1.5;
}

.quick-grid{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 900px){
  .quick-grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px){
  .quick-grid{ grid-template-columns: 1fr; }
}
.quick-card{
  display:flex;
  align-items:center;
  gap: 10px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(255,255,255,0.84);
  box-shadow: 0 12px 28px rgba(2, 6, 23, 0.06);
  text-decoration: none;
  color: inherit;
  transition: .15s;
}
.quick-card:hover{
  transform: translateY(-1px);
  border-color: rgba(37,99,235,.18);
  box-shadow: 0 18px 36px rgba(2, 6, 23, 0.08);
}
.quick-icon{
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  background: linear-gradient(135deg, rgba(37,99,235,.12), rgba(20,184,166,.12));
  border: 1px solid rgba(37,99,235,.14);
  flex: 0 0 auto;
}
.quick-card strong{ display:block; font-size: 14px; }
.quick-card small{
  display:block;
  margin-top: 2px;
  color: rgba(15,23,42,.60);
  font-size: 12px;
  line-height: 1.35;
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
  background: linear-gradient(135deg, var(--primary, #3b82f6), var(--primary-2, #2563eb));
}
.search{
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.88);
  box-shadow: 0 16px 38px rgba(2, 6, 23, 0.08);
}
.search-row{ display:flex; gap: 10px; align-items:center; }
.search-input{
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
.search-input:focus-within{
  border-color: rgba(59,130,246,0.60);
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}
.search-input .icon{ opacity: .75; user-select:none; }
.search-input input{
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  font-size: 15px;
}
.search .btn{
  min-height: 46px;
  padding: 0 18px;
  border: 0;
  cursor: pointer;
  font-weight: 900;
  border-radius: 14px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  transition: .15s;
  white-space: nowrap;
}
.search .btn:active{ transform: translateY(0px); }
.search-tip{ margin-top: 10px; font-size: 12px; color: rgba(15,23,42,.60); }

.feature-band,
.community{
  border-radius: 20px;
  border: 1px solid rgba(15, 23, 42, .10);
  background: rgba(255,255,255,.86);
  box-shadow: 0 14px 34px rgba(2, 6, 23, .07);
}
.feature-band{
  display:grid;
  grid-template-columns: 220px 1fr;
  gap: 16px;
  padding: 18px;
}
@media (max-width: 760px){
  .feature-band{ grid-template-columns: 1fr; }
}
.section-title{
  margin: 4px 0 0;
  font-size: 22px;
  line-height: 1.2;
  letter-spacing: 0;
}
.path-list{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
@media (max-width: 760px){
  .path-list{ grid-template-columns: 1fr; }
}
.path-item{
  padding: 14px;
  border-radius: 16px;
  background: rgba(248,250,252,.88);
  border: 1px solid rgba(15,23,42,.08);
}
.path-item span{
  display:inline-flex;
  margin-bottom: 10px;
  color: rgba(37,99,235,1);
  font-weight: 1000;
  font-size: 12px;
}
.path-item strong{ display:block; font-size: 14px; }
.path-item small{
  display:block;
  margin-top: 6px;
  color: rgba(15,23,42,.60);
  line-height: 1.45;
}
.section-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-top: 4px;
}
.count-pill{
  display:inline-flex;
  align-items:center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  font-size: 12px;
  font-weight: 1000;
}

.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
@media (max-width: 680px){ .grid{ grid-template-columns: 1fr; } }

.book{
  display:flex;
  gap: 16px;
  padding: 16px;
  min-height: 190px;
  border-radius: 20px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background:
    linear-gradient(135deg, rgba(255,255,255,.94), rgba(248,250,252,.84));
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.06);
  transition: .15s;
  overflow: hidden;
}
.book:hover{
  transform: translateY(-2px);
  border-color: rgba(37,99,235,.18);
  box-shadow: 0 20px 44px rgba(2, 6, 23, 0.10);
}

.cover{
  width: 112px;
  height: 154px;
  border-radius: 18px;
  background:
    radial-gradient(160px 90px at 20% 10%, rgba(59,130,246,.25), transparent 60%),
    radial-gradient(140px 80px at 90% 0%, rgba(20,184,166,.20), transparent 60%),
    linear-gradient(135deg, rgba(37,99,235,.12), rgba(20,184,166,.07));
  border: 1px solid rgba(15, 23, 42, 0.08);
  display:block;
  padding: 10px;
  flex: 0 0 auto;
  overflow: hidden;
  position: relative;
}

.cover-photo{
  background-size: cover;
  background-position: center;
  box-shadow: inset 0 -72px 80px rgba(15, 23, 42, 0.38);
}

.cover-badge{
  position:absolute;
  left: 10px;
  top: 10px;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  color:#fff;
  font-weight: 900;
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.20);
  user-select:none;
}

.body{
  flex: 1;
  min-width: 0;
  display:flex;
  flex-direction: column;
  gap: 8px;
  padding: 2px 0;
}
.book-label{
  align-self: flex-start;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(20, 83, 45, 1);
  background: rgba(20,184,166,.12);
  border: 1px solid rgba(20,184,166,.18);
  font-size: 11px;
  font-weight: 1000;
}
.title{
  font-weight: 1000;
  font-size: 18px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.author{ font-size: 12px; color: rgba(15,23,42,.65); }
.book-desc{
  margin: 0;
  color: rgba(15,23,42,.62);
  font-size: 12px;
  line-height: 1.55;
}

.actions{ margin-top: auto; display:flex; justify-content: flex-start; }
.link-btn{
  display:inline-flex;
  align-items:center;
  gap: 6px;
  min-height: 36px;
  padding: 0 12px;
  border-radius: 13px;
  text-decoration: none;
  font-weight: 900;
  font-size: 12px;
  color: rgba(37,99,235,1);
  background: rgba(37,99,235,.08);
  border: 1px solid rgba(37,99,235,.18);
  transition: .15s;
}
.link-btn:hover{ background: rgba(37,99,235,.12); }
.link-btn-muted{
  color: rgba(15,23,42,.64);
  background: rgba(15,23,42,.06);
  border-color: rgba(15,23,42,.10);
}

/* 空状态 */
.empty{
  padding: 22px;
  border-radius: 16px;
  border: 1px dashed rgba(15, 23, 42, 0.16);
  background: rgba(255,255,255,0.75);
  text-align: center;
}
.sample-note{
  margin-bottom: 12px;
  text-align: left;
  border-style: solid;
  background: rgba(255,255,255,0.86);
}
.empty-icon{ font-size: 28px; }
.empty-title{ margin-top: 8px; font-weight: 900; }
.empty-sub{ margin-top: 6px; font-size: 12px; color: rgba(15,23,42,.65); line-height: 1.5; }

.community{
  display:grid;
  grid-template-columns: 1fr 360px;
  gap: 18px;
  padding: 20px;
}
@media (max-width: 820px){
  .community{ grid-template-columns: 1fr; }
}
.community-copy p{
  max-width: 560px;
  margin: 10px 0 0;
  color: rgba(15,23,42,.64);
  line-height: 1.65;
}
.community-actions{
  display:grid;
  gap: 10px;
}
.community-link{
  display:flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  border-radius: 16px;
  text-decoration: none;
  color: inherit;
  background: rgba(248,250,252,.88);
  border: 1px solid rgba(15,23,42,.08);
  transition: .15s;
}
.community-link:hover{
  transform: translateY(-1px);
  border-color: rgba(37,99,235,.18);
}
.community-link small{
  color: rgba(15,23,42,.60);
}

/* skeleton */
.skeleton{ overflow: hidden; }
.skeleton .cover,
.skeleton .line{ position: relative; background: rgba(15,23,42,0.06); }
.skeleton .cover::after,
.skeleton .line::after{
  content:"";
  position:absolute;
  inset:0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
  animation: shimmer 1.1s infinite;
}
.skeleton .body{ gap: 10px; padding-top: 4px; }
.line{ height: 10px; border-radius: 999px; }
.w70{ width: 70%; } .w50{ width: 50%; } .w40{ width: 40%; }
@keyframes shimmer{ 100%{ transform: translateX(100%); } }
</style>

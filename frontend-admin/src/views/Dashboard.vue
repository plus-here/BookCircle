<template>
  <div class="dash">
    <!-- KPI -->
    <div class="kpi">
      <div class="kpi-card card">
        <div class="kpi-top">
          <div class="kpi-icon">👤</div>
          <div class="kpi-meta">
            <div class="kpi-label">用户数</div>
            <div class="kpi-value">{{ c.users }}</div>
          </div>
        </div>
        <div class="kpi-sub">平台注册用户总数</div>
      </div>

      <div class="kpi-card card">
        <div class="kpi-top">
          <div class="kpi-icon">📚</div>
          <div class="kpi-meta">
            <div class="kpi-label">书籍数</div>
            <div class="kpi-value">{{ c.books }}</div>
          </div>
        </div>
        <div class="kpi-sub">书库中已创建的书籍</div>
      </div>

      <div class="kpi-card card">
        <div class="kpi-top">
          <div class="kpi-icon">📣</div>
          <div class="kpi-meta">
            <div class="kpi-label">已发布公告</div>
            <div class="kpi-value">{{ c.announcements_published }}</div>
          </div>
        </div>
        <div class="kpi-sub">累计已发布数量</div>
      </div>

      <div class="kpi-card card">
        <div class="kpi-top">
          <div class="kpi-icon">🗂️</div>
          <div class="kpi-meta">
            <div class="kpi-label">书架条目</div>
            <div class="kpi-value">{{ c.shelf_items }}</div>
          </div>
        </div>
        <div class="kpi-sub">用户书架累计加入次数</div>
      </div>
    </div>

    <!-- Charts row 1 -->
    <div class="grid2">
      <div class="panel card">
        <div class="panel-head">
          <div>
            <div class="panel-title">公告发布趋势</div>
            <div class="panel-sub">近 14 天（已发布）</div>
          </div>
        </div>
        <div ref="annEl" class="chart"></div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <div class="panel-title">加入书架趋势</div>
            <div class="panel-sub">近 14 天</div>
          </div>
        </div>
        <div ref="shelfEl" class="chart"></div>
      </div>
    </div>

    <!-- Charts row 2 -->
    <div class="grid3">
      <div class="panel card">
        <div class="panel-head">
          <div>
            <div class="panel-title">新增用户趋势</div>
            <div class="panel-sub">近 14 天</div>
          </div>
        </div>
        <div ref="userEl" class="chart chart-sm"></div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <div class="panel-title">最新公告</div>
            <div class="panel-sub">最近创建的公告</div>
          </div>
        </div>

        <el-table :data="latest" size="small" style="width:100%;">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="title" label="标题" show-overflow-tooltip />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_published ? 'success' : 'info'">
                {{ row.is_published ? "已发布" : "草稿" }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="table-foot" v-if="latest.length === 0">
          暂无公告
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from "vue";
import * as echarts from "echarts";
import http from "../api/http";
import { ElMessage } from "element-plus";

const annEl = ref(null);
const shelfEl = ref(null);
const userEl = ref(null);

const c = ref({
  users: 0,
  books: 0,
  chapters: 0,
  shelf_items: 0,
  announcements_total: 0,
  announcements_published: 0,
  announcements_draft: 0,
});

const latest = ref([]);

/** 保存图表实例，避免重复 init + 重复绑定 resize */
const charts = {
  ann: null,
  shelf: null,
  user: null,
};

function toAxis(series) {
  const x = (series || []).map((i) => i.date);
  const y = (series || []).map((i) => i.count);
  return { x, y };
}

function baseOption({ x, y, type, name }) {
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 44, right: 18, top: 24, bottom: 34 },
    xAxis: {
      type: "category",
      data: x,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: "rgba(15,23,42,0.20)" } },
      axisLabel: { color: "rgba(15,23,42,0.65)" },
    },
    yAxis: {
      type: "value",
      axisLine: { show: false },
      splitLine: { lineStyle: { color: "rgba(15,23,42,0.08)" } },
      axisLabel: { color: "rgba(15,23,42,0.65)" },
    },
    series: [
      type === "bar"
        ? { type: "bar", data: y, name, barMaxWidth: 22 }
        : { type: "line", data: y, name, smooth: true, symbolSize: 6 },
    ],
  };
}

function ensureChart(dom, key) {
  if (!dom) return null;
  const existed = charts[key];
  if (existed && !existed.isDisposed?.()) return existed;

  const chart = echarts.init(dom);
  charts[key] = chart;
  return chart;
}

function renderLine(dom, key, title, series) {
  const chart = ensureChart(dom, key);
  if (!chart) return;
  const { x, y } = toAxis(series);
  chart.setOption(baseOption({ x, y, type: "line", name: title }), true);
}

function renderBar(dom, key, title, series) {
  const chart = ensureChart(dom, key);
  if (!chart) return;
  const { x, y } = toAxis(series);
  chart.setOption(baseOption({ x, y, type: "bar", name: title }), true);
}

function onResize() {
  Object.values(charts).forEach((c) => c && c.resize());
}

async function load() {
  try {
    const res = await http.get("/admin/stats/");
    c.value = res.data.counts || c.value;
    latest.value = res.data.latest?.announcements || [];

    const s = res.data.series || {};
    renderLine(annEl.value, "ann", "公告发布（已发布）", s.announcements_published_14d);
    renderBar(shelfEl.value, "shelf", "加入书架", s.shelf_added_14d);
    renderLine(userEl.value, "user", "新增用户", s.users_new_14d);

    onResize();
  } catch (e) {
    ElMessage.error("仪表盘加载失败：请检查是否已登录管理员 / 统计接口是否可用");
  }
}

onMounted(() => {
  window.addEventListener("resize", onResize);
  load();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  Object.keys(charts).forEach((k) => {
    if (charts[k]) {
      charts[k].dispose();
      charts[k] = null;
    }
  });
});
</script>

<style scoped>
.dash{
  display:grid;
  gap: 16px;
}

.kpi{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}
@media (max-width: 1000px){
  .kpi{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px){
  .kpi{ grid-template-columns: 1fr; }
}

.kpi-card{
  padding: 14px;
  position: relative;
  overflow: hidden;
}
.kpi-card::after{
  content:"";
  position:absolute;
  inset:-40px -80px auto auto;
  width: 180px;
  height: 180px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(59,130,246,.18), transparent 60%);
  pointer-events:none;
}
.kpi-top{
  display:flex;
  align-items:center;
  gap: 12px;
}
.kpi-icon{
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display:grid;
  place-items:center;
  background: rgba(37,99,235,.10);
  border: 1px solid rgba(37,99,235,.16);
  user-select:none;
  flex: 0 0 auto;
}
.kpi-label{
  color: var(--muted);
  font-weight: 900;
  font-size: 12px;
}
.kpi-value{
  font-size: 28px;
  font-weight: 1000;
  letter-spacing: .2px;
}
.kpi-sub{
  margin-top: 10px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.4;
}

.grid2{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
@media (max-width: 900px){
  .grid2{ grid-template-columns: 1fr; }
}

.grid3{
  display:grid;
  grid-template-columns: 1fr 0.9fr;
  gap: 16px;
}
@media (max-width: 900px){
  .grid3{ grid-template-columns: 1fr; }
}

.panel{
  padding: 16px;
  overflow: hidden;
}
.panel-head{
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}
.panel-title{
  font-weight: 1000;
}
.panel-sub{
  margin-top: 4px;
  font-size: 12px;
  color: var(--muted);
}

.chart{ height: 300px; }
.chart-sm{ height: 280px; }

.table-foot{
  margin-top: 10px;
  font-size: 12px;
  color: var(--muted);
}
</style>

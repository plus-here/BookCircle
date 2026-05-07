<template>
  <div class="wrap">
    <!-- 顶部标题区 -->
    <div class="page-head card">
      <div>
        <div class="title">用户管理</div>
        <div class="sub">查询用户、启用/禁用账号（禁用后用户端无法登录）。</div>
      </div>

      <div class="head-actions">
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 搜索区 -->
    <div class="card pad">
      <div class="filters">
        <el-input
          v-model="q"
          placeholder="按用户名搜索（回车查询）"
          style="width: 320px;"
          clearable
          @keyup.enter="load"
        >
          <template #prefix>🔎</template>
        </el-input>

        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="reset">重置</el-button>

        <div class="count">共 <b>{{ items.length }}</b> 个用户</div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="card pad">
      <el-table :data="items" v-loading="loading" style="width:100%;" empty-text="暂无用户">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="username" label="用户名" width="180" />
        <el-table-column prop="email" label="邮箱" min-width="220" show-overflow-tooltip />

        <el-table-column label="启用" width="150">
          <template #default="{ row }">
            <div class="switch-row">
              <el-switch
                v-model="row.is_active"
                :loading="row.__updating"
                @change="toggleActive(row)"
              />
              <span class="muted">{{ row.is_active ? "启用" : "禁用" }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="管理员" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_staff ? 'success' : 'info'">
              {{ row.is_staff ? "是" : "否" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="190" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="muted">{{ fmt(row.created_at) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="hint muted">
        提示：禁用用户会影响登录；管理员（staff）用户建议不要随意禁用。
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const items = ref([]);
const loading = ref(false);
const q = ref("");

// 简单防抖：避免频繁点击/回车导致重复请求
let timer = null;

function fmt(t) {
  if (!t) return "-";
  const d = new Date(t);
  return Number.isNaN(d.getTime()) ? String(t).replace("T", " ").replace("Z", "") : d.toLocaleString();
}

function reset() {
  q.value = "";
  load();
}

async function load() {
  if (timer) clearTimeout(timer);
  timer = setTimeout(async () => {
    loading.value = true;
    try {
      const res = await http.get(`/admin/users/?q=${encodeURIComponent(q.value || "")}`);
      // 给每行加一个本地 updating 状态（不影响后端字段）
      items.value = (res.data || []).map((x) => ({ ...x, __updating: false }));
    } catch {
      ElMessage.error("加载失败：请确认管理员权限/接口可用");
      items.value = [];
    } finally {
      loading.value = false;
    }
  }, 300);
}

async function toggleActive(row) {
  const old = !row.is_active; // 因为 v-model 已经先切换了
  row.__updating = true;

  try {
    // 你后端要求带 email（你原代码就是这样），这里保持一致
    await http.patch(`/admin/users/${row.id}/`, {
      is_active: row.is_active,
      email: row.email,
    });
    ElMessage.success("已更新");
  } catch {
    ElMessage.error("更新失败");
    row.is_active = old;
  } finally {
    row.__updating = false;
  }
}

onMounted(load);
</script>

<style scoped>
.wrap{ display:grid; gap: 14px; }

.card{
  border-radius: var(--radius, 16px);
  border: 1px solid var(--border);
  background: var(--card);
  box-shadow: var(--shadow);
}
.pad{ padding: 16px; }

.page-head{
  padding: 16px;
  display:flex;
  align-items:flex-end;
  justify-content: space-between;
  gap: 12px;
}
.title{ font-size: 18px; font-weight: 1000; }
.sub{ margin-top: 6px; font-size: 12px; color: var(--muted); line-height: 1.5; }
.head-actions{ display:flex; gap: 10px; flex-wrap: wrap; }

.filters{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items:center;
}
.count{
  margin-left:auto;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
}

.muted{ color: var(--muted); }

.switch-row{
  display:flex;
  align-items:center;
  gap: 10px;
}

.hint{
  margin-top: 12px;
  font-size: 12px;
  line-height: 1.5;
}
</style>

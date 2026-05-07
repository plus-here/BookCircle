<template>
  <div class="wrap">
    <!-- 顶部标题区 -->
    <div class="page-head card">
      <div>
        <div class="title">活动管理</div>
        <div class="sub">创建、编辑、发布/撤回活动，并分发到指定社团（成员才可报名）。</div>
      </div>

      <div class="head-actions">
        <el-button type="primary" @click="openCreate">新建活动</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="card pad">
      <div class="filters">
        <el-input
          v-model="q"
          placeholder="搜索标题/描述/地点关键字"
          style="width: 320px;"
          clearable
          @keyup.enter="page=1"
        >
          <template #prefix>🔎</template>
        </el-input>

        <el-select v-model="status" placeholder="状态" style="width: 160px;" clearable>
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
        </el-select>

        <el-button type="primary" @click="page=1">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>

        <div class="count">共 <b>{{ filtered.length }}</b> 场</div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="card pad">
      <el-table
        :data="paged"
        v-loading="loading"
        style="width:100%;"
        empty-text="暂无活动"
      >
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />

        <el-table-column label="时间" min-width="280">
          <template #default="{ row }">
            <div class="time-col">
              <div class="muted">开始：{{ fmt(row.start_time) }}</div>
              <div class="muted">结束：{{ fmt(row.end_time) }}</div>
              <div class="muted">截止：{{ fmt(row.signup_deadline) }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="location" label="地点" width="180" show-overflow-tooltip />

        <el-table-column label="名额" width="140">
          <template #default="{ row }">
            <span class="muted">
              {{ row.capacity ? `${row.signed_count || 0}/${row.capacity}` : `${row.signed_count || 0}/不限` }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'">
              {{ row.status === "published" ? "已发布" : "草稿" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="发布" width="140">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status === 'published'"
              inline-prompt
              active-text="已发布"
              inactive-text="草稿"
              :loading="row.__updating"
              @change="(v)=>togglePublish(row, v)"
            />
          </template>
        </el-table-column>

        <el-table-column label="分发社团" min-width="220">
          <template #default="{ row }">
            <span class="muted" v-if="(row.target_clubs || []).length === 0">未分发</span>
            <span v-else class="muted">
              {{ row.target_clubs.map(x=>x.name).join("、") }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openPreview(row)">预览</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>

            <el-popconfirm title="确定删除该活动吗？" @confirm="remove(row.id)">
              <template #reference>
                <el-button size="small" type="danger" plain style="margin-left:10px;">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          background
          layout="prev, pager, next, jumper"
          :total="filtered.length"
          :page-size="pageSize"
          v-model:current-page="page"
        />
      </div>
    </div>

    <!-- 新建/编辑 Dialog -->
    <el-dialog
      v-model="dlg"
      :title="editingId ? '编辑活动' : '新建活动'"
      width="900px"
      destroy-on-close
    >
      <el-form label-width="110px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入活动标题" maxlength="120" show-word-limit />
        </el-form-item>

        <el-form-item label="地点">
          <el-input v-model="form.location" placeholder="例如：图书馆报告厅 / 线上会议" />
        </el-form-item>

        <el-form-item label="开始时间">
          <div class="dt-row">
            <input class="dt" type="datetime-local" v-model="form.start_time_local" />
            <span class="muted dt-tip">选择即可，自动生成格式</span>
          </div>
        </el-form-item>

        <el-form-item label="结束时间">
          <div class="dt-row">
            <input class="dt" type="datetime-local" v-model="form.end_time_local" />
            <span class="muted dt-tip">可不填</span>
          </div>
        </el-form-item>

        <el-form-item label="报名截止">
          <div class="dt-row">
            <input class="dt" type="datetime-local" v-model="form.signup_deadline_local" />
            <span class="muted dt-tip">可不填，留空代表不限制</span>
          </div>
        </el-form-item>

        <el-form-item label="活动名额">
          <el-input-number v-model="form.capacity" :min="0" :max="9999" />
          <div class="muted tip">0 代表不限制名额，用户端会显示报名人数和剩余席位。</div>
        </el-form-item>

        <el-form-item label="分发社团">
          <el-select
            v-model="form.target_club_ids"
            multiple
            filterable
            clearable
            style="width:100%;"
            placeholder="选择要分发的社团（可多选）"
          >
            <el-option
              v-for="c in clubs"
              :key="c.id"
              :label="`${c.name}（ID:${c.id}）`"
              :value="c.id"
            />
          </el-select>
          <div class="muted tip">只允许所选社团成员报名（你后端就是这样校验的）。</div>
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="8" placeholder="请输入活动详情..." />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch
            :model-value="form.status === 'published'"
            inline-prompt
            active-text="已发布"
            inactive-text="草稿"
            @change="(v)=> form.status = v ? 'published' : 'draft'"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">
          {{ saving ? "保存中..." : "保存" }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览 Drawer -->
    <el-drawer v-model="drawer" title="活动预览" size="560px">
      <div v-if="preview" class="preview-wrap">
        <div class="preview-title">{{ preview.title }}</div>
        <div class="muted">状态：{{ preview.status === "published" ? "已发布" : "草稿" }}</div>
        <div class="muted">开始：{{ fmt(preview.start_time) }}</div>
        <div class="muted">结束：{{ fmt(preview.end_time) }}</div>
        <div class="muted">截止：{{ fmt(preview.signup_deadline) }}</div>
        <div class="muted">名额：{{ preview.capacity ? `${preview.signed_count || 0}/${preview.capacity}` : `${preview.signed_count || 0}/不限` }}</div>
        <div class="muted">地点：{{ preview.location || "-" }}</div>

        <div class="preview-card card">
          <div class="preview-sub">活动描述</div>
          <div class="preview-text">{{ preview.description || "（暂无描述）" }}</div>
        </div>

        <div class="muted">
          分发社团：{{ (preview.target_clubs||[]).length ? preview.target_clubs.map(x=>x.name).join("、") : "未分发" }}
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const loading = ref(false);
const saving = ref(false);

const items = ref([]);
const clubs = ref([]);

const q = ref("");
const status = ref("");

const page = ref(1);
const pageSize = 10;

const dlg = ref(false);
const editingId = ref(null);
const form = reactive({
  title: "",
  description: "",
  location: "",
  // 给 UI 用的（datetime-local）
  start_time_local: "",
  end_time_local: "",
  signup_deadline_local: "",
  // 其他字段
  capacity: 0,
  status: "draft",
  target_club_ids: [],
});


const drawer = ref(false);
const preview = ref(null);

function fmt(v) {
  if (!v) return "-";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v).replace("T", " ").replace("Z", "") : d.toLocaleString();
}

function toLocalInputValue(iso) {
  // 把后端返回的 ISO 时间转成 datetime-local 需要的格式：YYYY-MM-DDTHH:mm
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  const yyyy = d.getFullYear();
  const mm = pad(d.getMonth() + 1);
  const dd = pad(d.getDate());
  const hh = pad(d.getHours());
  const mi = pad(d.getMinutes());
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}`;
}

function localInputToIso(localVal) {
  // localVal: "YYYY-MM-DDTHH:mm"
  if (!localVal) return null;
  // 统一补秒，生成 "YYYY-MM-DDTHH:mm:ss"
  return `${localVal}:00`;
}


function strip(s) {
  return String(s || "").trim().toLowerCase();
}

const filtered = computed(() => {
  const kw = strip(q.value);
  return items.value.filter((x) => {
    if (status.value === "published" && x.status !== "published") return false;
    if (status.value === "draft" && x.status !== "draft") return false;
    if (!kw) return true;

    return (
      strip(x.title).includes(kw) ||
      strip(x.description).includes(kw) ||
      strip(x.location).includes(kw)
    );
  });
});

const paged = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filtered.value.slice(start, start + pageSize);
});

watch([q, status], () => (page.value = 1));

function resetFilters() {
  q.value = "";
  status.value = "";
  page.value = 1;
}

async function loadClubs() {
  // ⚠️ 如果你的社团管理接口不是这个路径，把这里改成正确的
  // 常见：/admin/clubs/ 或 /clubs/
  try {
    const res = await http.get("/admin/clubs/");
    clubs.value = res.data || [];
  } catch {
    // 若 admin/clubs 不存在，尝试普通 clubs
    try {
      const res2 = await http.get("/clubs/");
      clubs.value = res2.data || [];
    } catch {
      clubs.value = [];
    }
  }
}

async function load() {
  loading.value = true;
  try {
    const res = await http.get("/admin/activities/");
    items.value = (res.data || []).map((x) => ({ ...x, __updating: false }));
    page.value = 1;
  } catch (e) {
    ElMessage.error("加载失败：请确认已按提示把 ActivityDetailView 改为可更新/删除，并确保管理员已登录");
    items.value = [];
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingId.value = null;
  Object.assign(form, {
    title: "",
    description: "",
    location: "",
    start_time_local: "",
    end_time_local: "",
    signup_deadline_local: "",
    capacity: 0,
    status: "draft",
    target_club_ids: [],
  });
  dlg.value = true;
}


function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, {
    title: row.title || "",
    description: row.description || "",
    location: row.location || "",
    start_time_local: toLocalInputValue(row.start_time),
    end_time_local: toLocalInputValue(row.end_time),
    signup_deadline_local: toLocalInputValue(row.signup_deadline),
    capacity: Number(row.capacity || 0),
    status: row.status || "draft",
    target_club_ids: (row.target_clubs || []).map((x) => x.id),
  });
  dlg.value = true;
}


function openPreview(row) {
  preview.value = row;
  drawer.value = true;
}

async function save() {
  const title = (form.title || "").trim();
  if (!title) return ElMessage.warning("标题不能为空");

  // ✅ 用 datetime-local 的字段转换成后端要的字符串
  const startIso = localInputToIso(form.start_time_local);
  const endIso = localInputToIso(form.end_time_local);
  const deadlineIso = localInputToIso(form.signup_deadline_local);

  // ✅ 后端目前要求 end_time 不能为空：所以这里强制要求用户必须选
  if (!startIso) return ElMessage.warning("请选择开始时间");
  if (!endIso) return ElMessage.warning("请选择结束时间（后端要求必填）");

  saving.value = true;
  try {
    const payload = {
      title,
      description: form.description || "",
      location: form.location || "",
      start_time: startIso,
      end_time: endIso,
      capacity: Number(form.capacity || 0),
      status: form.status,
      target_club_ids: form.target_club_ids || [],
    };

    // ✅ signup_deadline 可选：不填就不传（别传 null）
    if (deadlineIso) payload.signup_deadline = deadlineIso;

    if (editingId.value) {
      await http.patch(`/admin/activities/${editingId.value}/`, payload);
      ElMessage.success("已保存");
    } else {
      await http.post("/admin/activities/", payload);
      ElMessage.success("已创建");
    }

    dlg.value = false;
    await load();
  } catch (e) {
    // ✅ 把后端返回的字段错误直接显示出来（以后你就不用猜）
    const data = e?.response?.data;
    if (data) {
      ElMessage.error(`保存失败：${JSON.stringify(data)}`);
    } else {
      ElMessage.error("保存失败：请检查字段格式/权限/后端日志");
    }
  } finally {
    saving.value = false;
  }
}


async function togglePublish(row, toPublish) {
  const old = row.status;
  row.__updating = true;
  row.status = toPublish ? "published" : "draft";

  try {
    await http.patch(`/admin/activities/${row.id}/`, { status: row.status });
    ElMessage.success(toPublish ? "已发布" : "已撤回为草稿");
  } catch {
    ElMessage.error("操作失败");
    row.status = old;
  } finally {
    row.__updating = false;
  }
}

async function remove(id) {
  try {
    await http.delete(`/admin/activities/${id}/`);
    ElMessage.success("已删除");
    await load();
  } catch {
    ElMessage.error("删除失败");
  }
}

onMounted(async () => {
  await loadClubs();
  await load();
});
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

.pager{
  margin-top: 14px;
  display:flex;
  justify-content: flex-end;
}

.time-col{ display:grid; gap: 2px; }

.tip{ margin-top: 6px; }

.preview-wrap{ display:grid; gap: 10px; }
.preview-title{ font-size: 18px; font-weight: 1000; }
.preview-card{ padding: 12px; }
.preview-sub{ font-weight: 1000; margin-bottom: 6px; }
.preview-text{ white-space: pre-wrap; line-height: 1.7; }

.dt-row{
  width: 100%;
  display:flex;
  align-items:center;
  gap: 10px;
  flex-wrap: wrap;
}
.dt{
  width: 320px;
  max-width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.85);
  color: var(--text);
  outline: none;
}
html.dark .dt{
  background: rgba(17,24,39,0.72);
}
.dt:focus{
  border-color: rgba(59,130,246,0.60);
  box-shadow: 0 0 0 4px rgba(59,130,246,0.12);
}
.dt-tip{ font-size: 12px; }

</style>

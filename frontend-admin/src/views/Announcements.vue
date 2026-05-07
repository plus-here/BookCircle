<template>
  <div class="wrap">
    <!-- 顶部标题区 -->
    <div class="page-head card">
      <div>
        <div class="title">公告管理</div>
        <div class="sub">创建、编辑、发布/撤回公告。用户端只显示已发布内容。</div>
      </div>

      <div class="head-actions">
        <el-button type="primary" @click="openCreate">新建公告</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="card pad">
      <div class="filters">
        <el-input
          v-model="q"
          placeholder="搜索标题/内容关键字"
          style="width:280px;"
          clearable
        >
          <template #prefix>🔎</template>
        </el-input>

        <el-select v-model="status" placeholder="状态" style="width:160px;" clearable>
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
        </el-select>

        <el-button type="primary" @click="page=1">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>

        <div class="count">共 <b>{{ filtered.length }}</b> 条</div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="card pad">
      <el-table :data="paged" v-loading="loading" style="width:100%;" empty-text="暂无公告">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'">
              {{ row.is_published ? "已发布" : "草稿" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="发布时间" width="190">
          <template #default="{ row }">
            <span class="muted">{{ fmt(row.published_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="380" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openPreview(row)">预览</el-button>

            <el-switch
              v-model="row.is_published"
              inline-prompt
              active-text="已发布"
              inactive-text="草稿"
              style="margin-left:10px;"
              @change="togglePublish(row)"
            />

            <el-button size="small" style="margin-left:10px;" @click="openEdit(row)">编辑</el-button>

            <el-popconfirm title="确定删除这条公告吗？" @confirm="remove(row.id)">
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
    <el-dialog v-model="dlg" :title="editingId ? '编辑公告' : '新建公告'" width="820px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>

        <el-form-item label="内容">
          <RichTextEditor v-model="form.content" placeholder="请输入公告内容..." />
        </el-form-item>

        <el-form-item label="发布状态">
          <el-switch v-model="form.is_published" inline-prompt active-text="已发布" inactive-text="草稿" />
          <div class="muted tip">打开“已发布”后，用户端才会显示。</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览 Drawer -->
    <el-drawer v-model="drawer" title="公告预览" size="520px">
      <div v-if="preview" class="preview-wrap">
        <div class="preview-title">{{ preview.title }}</div>
        <div class="muted">发布时间：{{ fmt(preview.published_at) }}</div>

        <div class="preview-card card" v-html="safe(preview.content)"></div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

import RichTextEditor from "../components/RichTextEditor.vue";
import DOMPurify from "dompurify";

const loading = ref(false);
const saving = ref(false);

const items = ref([]);
const q = ref("");
const status = ref("");

const page = ref(1);
const pageSize = 10;

const dlg = ref(false);
const editingId = ref(null);
const form = reactive({ title: "", content: "", is_published: false });

const drawer = ref(false);
const preview = ref(null);

function fmt(t) {
  if (!t) return "-";
  const d = new Date(t);
  return Number.isNaN(d.getTime()) ? String(t).replace("T", " ").replace("Z", "") : d.toLocaleString();
}

function safe(html) {
  return DOMPurify.sanitize(html || "");
}

function stripHtml(s) {
  return (s || "").replace(/<[^>]*>/g, " ");
}

const filtered = computed(() => {
  const kw = q.value.trim().toLowerCase();
  return items.value.filter((x) => {
    if (status.value === "published" && !x.is_published) return false;
    if (status.value === "draft" && x.is_published) return false;
    if (!kw) return true;

    const title = (x.title || "").toLowerCase();
    const contentText = stripHtml(x.content).toLowerCase();
    return title.includes(kw) || contentText.includes(kw);
  });
});

const paged = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filtered.value.slice(start, start + pageSize);
});

// ✅ 过滤条件变化时回到第一页
watch([q, status], () => {
  page.value = 1;
});

async function load() {
  loading.value = true;
  try {
    const res = await http.get("/admin/announcements/");
    items.value = res.data || [];
    page.value = 1;
  } catch {
    ElMessage.error("加载失败：请确认已使用管理员（staff）账号登录");
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  q.value = "";
  status.value = "";
  page.value = 1;
}

function openCreate() {
  editingId.value = null;
  form.title = "";
  form.content = "";
  form.is_published = false;
  dlg.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  form.title = row.title;
  form.content = row.content || "";
  form.is_published = !!row.is_published;
  dlg.value = true;
}

function openPreview(row) {
  preview.value = row;
  drawer.value = true;
}

async function save() {
  if (!form.title.trim()) return ElMessage.warning("标题不能为空");
  saving.value = true;
  try {
    if (editingId.value) {
      await http.put(`/admin/announcements/${editingId.value}/`, {
        title: form.title,
        content: form.content,
        is_published: form.is_published,
      });
      ElMessage.success("已保存");
    } else {
      await http.post("/admin/announcements/", {
        title: form.title,
        content: form.content,
        is_published: form.is_published,
      });
      ElMessage.success("已创建");
    }
    dlg.value = false;
    await load();
  } catch {
    ElMessage.error("保存失败：请检查接口/权限/后端日志");
  } finally {
    saving.value = false;
  }
}

async function togglePublish(row) {
  try {
    await http.patch(`/admin/announcements/${row.id}/`, { is_published: row.is_published });
    ElMessage.success(row.is_published ? "已发布" : "已设为草稿");
    await load();
  } catch {
    ElMessage.error("操作失败");
    row.is_published = !row.is_published;
  }
}

async function remove(id) {
  try {
    await http.delete(`/admin/announcements/${id}/`);
    ElMessage.success("已删除");
    await load();
  } catch {
    ElMessage.error("删除失败");
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
.tip{ margin-top: 6px; }

.pager{
  margin-top: 14px;
  display:flex;
  justify-content: flex-end;
}

.preview-wrap{ display:grid; gap: 10px; }
.preview-title{ font-size: 18px; font-weight: 1000; }
.preview-card{
  padding: 12px;
  line-height: 1.8;
  word-break: break-word;
}
</style>

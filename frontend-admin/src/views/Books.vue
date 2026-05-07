<template>
  <div class="wrap">
    <!-- 顶部标题区 -->
    <div class="page-head card">
      <div>
        <div class="title">书籍管理</div>
        <div class="sub">维护书库内容（封面、作者、简介、发布状态）。</div>
      </div>

      <div class="head-actions">
        <el-button type="primary" @click="openCreate">新建书籍</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="card pad">
      <div class="filters">
        <el-input
          v-model="q"
          placeholder="搜索书名/作者"
          style="width: 280px;"
          clearable
          @keyup.enter="page=1"
        >
          <template #prefix>🔎</template>
        </el-input>

        <el-select v-model="status" placeholder="状态" style="width: 160px;" clearable>
          <el-option label="已发布" value="published" />
          <el-option label="隐藏" value="hidden" />
        </el-select>

        <el-button type="primary" @click="page=1">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>

        <div class="count">共 <b>{{ filtered.length }}</b> 本</div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="card pad">
      <el-table :data="paged" v-loading="loading" style="width:100%;" empty-text="暂无书籍">
        <el-table-column label="封面" width="92">
          <template #default="{ row }">
            <img
              v-if="row.cover_url"
              :src="row.cover_url"
              class="cover"
              alt="cover"
            />
            <div v-else class="cover ph"></div>
          </template>
        </el-table-column>

        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="书名" min-width="220" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="180" show-overflow-tooltip />

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'">
              {{ row.is_published ? "已发布" : "隐藏" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>

            <el-popconfirm title="确定删除这本书吗？" @confirm="remove(row.id)">
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
      :title="editingId ? '编辑书籍' : '新建书籍'"
      width="820px"
      destroy-on-close
      @closed="cleanupPreview"
    >
      <el-form label-width="110px">
        <el-form-item label="书名">
          <el-input v-model="form.title" placeholder="请输入书名" />
        </el-form-item>

        <el-form-item label="作者">
          <el-input v-model="form.author" placeholder="请输入作者" />
        </el-form-item>

        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="6" placeholder="请输入简介（可选）" />
        </el-form-item>

        <el-form-item label="封面">
          <div class="upload-row">
            <el-upload
              :auto-upload="false"
              :limit="1"
              :on-change="onCoverChange"
              :show-file-list="true"
              accept="image/*"
            >
              <el-button>选择图片</el-button>
            </el-upload>

            <div class="muted tip">
              建议比例接近 3:4，清晰不拉伸。
            </div>
          </div>

          <div v-if="coverPreview" class="preview-img">
            <img :src="coverPreview" alt="preview" />
          </div>
        </el-form-item>

        <el-form-item label="发布状态">
          <el-switch v-model="form.is_published" inline-prompt active-text="已发布" inactive-text="隐藏" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">
          {{ saving ? "保存中..." : "保存" }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const loading = ref(false);
const saving = ref(false);
const items = ref([]);

const q = ref("");
const status = ref("");

const page = ref(1);
const pageSize = 10;

const dlg = ref(false);
const editingId = ref(null);
const form = reactive({ title: "", author: "", description: "", is_published: true });

const coverFile = ref(null);
const coverPreview = ref("");

// ✅ 释放 URL.createObjectURL，避免内存泄漏
let objectUrl = "";

function cleanupPreview() {
  coverFile.value = null;
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);
    objectUrl = "";
  }
  // 注意：编辑时 coverPreview 可能是 row.cover_url（非 objectUrl），这里清空即可
  coverPreview.value = "";
}

function onCoverChange(file) {
  coverFile.value = file.raw || null;

  // 先释放旧的 objectUrl
  if (objectUrl) URL.revokeObjectURL(objectUrl);

  objectUrl = coverFile.value ? URL.createObjectURL(coverFile.value) : "";
  coverPreview.value = objectUrl || "";
}

const filtered = computed(() => {
  const kw = q.value.trim().toLowerCase();
  return items.value.filter((x) => {
    if (status.value === "published" && !x.is_published) return false;
    if (status.value === "hidden" && x.is_published) return false;
    if (!kw) return true;
    return (x.title || "").toLowerCase().includes(kw) || (x.author || "").toLowerCase().includes(kw);
  });
});

const paged = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filtered.value.slice(start, start + pageSize);
});

// ✅ 搜索/筛选变化时自动回第一页
watch([q, status], () => {
  page.value = 1;
});

async function load() {
  loading.value = true;
  try {
    const res = await http.get("/admin/books/");
    items.value = res.data || [];
    page.value = 1;
  } catch {
    ElMessage.error("加载失败：请确认管理员权限/接口是否可用");
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
  Object.assign(form, { title: "", author: "", description: "", is_published: true });
  cleanupPreview();
  dlg.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, {
    title: row.title || "",
    author: row.author || "",
    description: row.description || "",
    is_published: !!row.is_published,
  });

  // 编辑时先不带 file，仅预览已有 cover_url
  coverFile.value = null;
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);
    objectUrl = "";
  }
  coverPreview.value = row.cover_url || "";
  dlg.value = true;
}

async function save() {
  if (!form.title.trim()) return ElMessage.warning("书名不能为空");
  saving.value = true;
  try {
    const fd = new FormData();
    fd.append("title", form.title);
    fd.append("author", form.author);
    fd.append("description", form.description);
    fd.append("is_published", form.is_published ? "true" : "false");
    if (coverFile.value) fd.append("cover", coverFile.value);

    if (editingId.value) {
      await http.patch(`/admin/books/${editingId.value}/`, fd);
      ElMessage.success("已保存");
    } else {
      await http.post("/admin/books/", fd);
      ElMessage.success("已创建");
    }

    dlg.value = false;
    cleanupPreview();
    await load();
  } catch {
    ElMessage.error("保存失败：请检查接口/权限/后端日志");
  } finally {
    saving.value = false;
  }
}

async function remove(id) {
  try {
    await http.delete(`/admin/books/${id}/`);
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

.filters{ display:flex; gap: 10px; flex-wrap: wrap; align-items:center; }
.count{
  margin-left:auto;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
}

.pager{
  margin-top: 14px;
  display:flex;
  justify-content: flex-end;
}

.muted{ color: var(--muted); }
.tip{ margin-top: 6px; }

.cover{
  width: 46px;
  height: 62px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(15,23,42,0.04);
}
.cover.ph{
  width: 46px;
  height: 62px;
  border-radius: 10px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(15,23,42,0.06);
}

.upload-row{
  display:flex;
  gap: 12px;
  align-items:center;
  flex-wrap: wrap;
}

.preview-img{
  margin-top: 10px;
}
.preview-img img{
  width: 120px;
  height: 160px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(15,23,42,0.10);
  background: rgba(15,23,42,0.04);
}
</style>

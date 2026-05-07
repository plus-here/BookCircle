<template>
  <div class="wrap">
    <!-- 顶部标题区 -->
    <div class="page-head card">
      <div>
        <div class="title">章节管理</div>
        <div class="sub">先选择一本书，再管理该书的章节（顺序、标题、内容）。</div>
      </div>

      <div class="head-actions">
        <el-button @click="loadChapters" :disabled="!bookId">刷新</el-button>
        <el-button type="primary" :disabled="!bookId" @click="openCreate">新建章节</el-button>
      </div>
    </div>

    <!-- 选择书籍 -->
    <div class="card pad">
      <div class="filters">
        <el-select
          v-model="bookId"
          placeholder="请选择书籍"
          style="width: 360px;"
          filterable
          clearable
          @change="onBookChange"
        >
          <el-option
            v-for="b in books"
            :key="b.id"
            :label="`${b.title}（ID: ${b.id}）`"
            :value="b.id"
          />
        </el-select>

        <div class="count" v-if="bookId">
          当前书籍：<b>{{ currentBookName }}</b> ｜ 共 <b>{{ itemsSorted.length }}</b> 章
        </div>

        <div class="count" v-else>
          请选择一本书以加载章节
        </div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="card pad">
      <el-table
        :data="itemsSorted"
        v-loading="loading"
        style="width:100%;"
        empty-text="暂无章节（请选择书籍后可新建）"
      >
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="order" label="顺序" width="110" />
        <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />

        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除该章节吗？" @confirm="remove(row.id)">
              <template #reference>
                <el-button size="small" type="danger" plain style="margin-left:10px;">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建/编辑 Dialog -->
    <el-dialog
      v-model="dlg"
      :title="editingId ? '编辑章节' : '新建章节'"
      width="860px"
      destroy-on-close
    >
      <el-form label-width="110px">
        <el-form-item label="所属书籍">
          <el-select v-model="form.book" style="width:100%;" filterable>
            <el-option v-for="b in books" :key="b.id" :label="`${b.title}（ID: ${b.id}）`" :value="b.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="顺序">
          <el-input v-model.number="form.order" type="number" />
          <div class="muted tip">建议从 1 开始，数字越小越靠前。</div>
        </el-form-item>

        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入章节标题" />
        </el-form-item>

        <el-form-item label="内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="14"
            placeholder="请输入章节正文..."
            class="content-area"
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
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const books = ref([]);
const bookId = ref(null);

const items = ref([]);
const loading = ref(false);
const saving = ref(false);

const dlg = ref(false);
const editingId = ref(null);
const form = reactive({ book: null, order: 1, title: "", content: "" });

const currentBookName = computed(() => {
  const b = books.value.find((x) => x.id === bookId.value);
  return b?.title || "-";
});

// ✅ 按 order 排序显示
const itemsSorted = computed(() => {
  return [...items.value].sort((a, b) => (Number(a.order) || 0) - (Number(b.order) || 0));
});

async function loadBooks() {
  try {
    const res = await http.get("/admin/books/");
    books.value = res.data || [];
  } catch {
    ElMessage.error("加载书籍列表失败：请检查管理员权限/接口");
  }
}

async function loadChapters() {
  if (!bookId.value) {
    items.value = [];
    return;
  }
  loading.value = true;
  try {
    const res = await http.get(`/admin/chapters/?book=${bookId.value}`);
    items.value = res.data || [];
  } catch {
    ElMessage.error("加载章节失败：请检查接口/权限");
  } finally {
    loading.value = false;
  }
}

function onBookChange() {
  // 选择书籍后自动加载章节
  loadChapters();
}

function openCreate() {
  if (!bookId.value) return;
  editingId.value = null;
  Object.assign(form, { book: bookId.value, order: 1, title: "", content: "" });
  dlg.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, {
    book: row.book,
    order: row.order,
    title: row.title || "",
    content: row.content || "",
  });
  dlg.value = true;
}

async function save() {
  if (!form.book) return ElMessage.warning("请选择所属书籍");
  if (!form.title.trim()) return ElMessage.warning("章节标题不能为空");

  saving.value = true;
  try {
    if (editingId.value) {
      await http.patch(`/admin/chapters/${editingId.value}/`, form);
      ElMessage.success("已保存");
    } else {
      await http.post("/admin/chapters/", form);
      ElMessage.success("已创建");
    }
    dlg.value = false;

    // 如果修改了所属书籍，保持列表与选择一致
    if (Number(form.book) === Number(bookId.value)) {
      await loadChapters();
    } else {
      // 若把章节挪到别的书：重新加载当前书章节
      await loadChapters();
    }
  } catch {
    ElMessage.error("保存失败：请检查接口/权限/后端日志");
  } finally {
    saving.value = false;
  }
}

async function remove(id) {
  try {
    await http.delete(`/admin/chapters/${id}/`);
    ElMessage.success("已删除");
    await loadChapters();
  } catch {
    ElMessage.error("删除失败");
  }
}

onMounted(async () => {
  await loadBooks();
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
.tip{ margin-top: 6px; }

:deep(.content-area textarea){
  line-height: 1.7;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
}
</style>

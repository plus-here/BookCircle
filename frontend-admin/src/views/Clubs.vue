<template>
  <div class="wrap">
    <!-- 顶部标题区 -->
    <div class="page-head card">
      <div>
        <div class="title">社团管理</div>
        <div class="sub">管理社团信息、板块、入社申请（审批）。</div>
      </div>

      <div class="head-actions">
        <el-button type="primary" @click="openCreate">新建社团</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="card pad">
      <div class="filters">
        <el-input
          v-model="q"
          placeholder="搜索社团名称/简介"
          style="width: 320px;"
          clearable
          @keyup.enter="load"
        >
          <template #prefix>🔎</template>
        </el-input>

        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>

        <div class="count">共 <b>{{ items.length }}</b> 个社团</div>
      </div>
    </div>

    <!-- 列表 -->
    <div class="card pad">
      <el-table :data="items" v-loading="loading" style="width:100%;" empty-text="暂无社团">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="name" label="社团名称" min-width="220" show-overflow-tooltip />
        <el-table-column prop="owner_username" label="团长" width="160" show-overflow-tooltip />
        <el-table-column prop="members_count" label="成员数" width="110" />
        <el-table-column prop="created_at" label="创建时间" width="190" show-overflow-tooltip>
          <template #default="{ row }"><span class="muted">{{ fmt(row.created_at) }}</span></template>
        </el-table-column>

        <el-table-column label="操作" width="380" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openManage(row)">管理</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>

            <el-popconfirm title="确定删除该社团吗？（危险：不可恢复）" @confirm="removeClub(row.id)">
              <template #reference>
                <el-button size="small" type="danger" plain style="margin-left:10px;">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建/编辑社团 -->
    <el-dialog v-model="dlgClub" :title="editingClubId ? '编辑社团' : '新建社团'" width="720px" destroy-on-close>
      <el-form label-width="110px">
        <el-form-item label="社团名称">
          <el-input v-model="clubForm.name" placeholder="请输入社团名称" maxlength="60" show-word-limit />
        </el-form-item>
        <el-form-item label="社团简介">
          <el-input v-model="clubForm.description" type="textarea" :rows="6" placeholder="请输入社团简介（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dlgClub=false">取消</el-button>
        <el-button type="primary" :loading="savingClub" @click="saveClub">
          {{ savingClub ? "保存中..." : "保存" }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 管理抽屉：板块 + 入社申请 -->
    <el-drawer v-model="drawer" :title="manageTitle" size="760px" destroy-on-close>
      <div class="drawer-wrap">
        <el-tabs v-model="tab">
          <!-- 基本信息 -->
          <el-tab-pane label="基本信息" name="base">
            <div class="card pad">
              <div class="kv"><b>社团名称：</b>{{ current?.name }}</div>
              <div class="kv"><b>团长：</b>{{ current?.owner_username || "-" }}</div>
              <div class="kv"><b>成员数：</b>{{ current?.members_count ?? "-" }}</div>
              <div class="kv"><b>创建时间：</b>{{ fmt(current?.created_at) }}</div>
              <div class="kv" style="margin-top:10px;">
                <b>简介：</b>
                <div class="muted" style="margin-top:6px; white-space:pre-wrap; line-height:1.7;">
                  {{ current?.description || "（暂无简介）" }}
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 板块管理 -->
          <el-tab-pane label="板块管理" name="sections">
            <div class="card pad">
              <div class="row">
                <div class="muted">板块用于社团发帖分类，按“顺序”从小到大显示。</div>
                <el-button type="primary" @click="openSectionCreate">新建板块</el-button>
              </div>

              <el-table :data="sections" v-loading="loadingSections" style="width:100%; margin-top:12px;" empty-text="暂无板块">
                <el-table-column prop="id" label="ID" width="90" />
                <el-table-column prop="order" label="顺序" width="110" />
                <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip />
                <el-table-column label="操作" width="240" fixed="right">
                  <template #default="{ row }">
                    <el-button size="small" @click="openSectionEdit(row)">编辑</el-button>
                    <el-popconfirm title="确定删除该板块吗？" @confirm="removeSection(row.id)">
                      <template #reference>
                        <el-button size="small" type="danger" plain style="margin-left:10px;">删除</el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- 入社申请 -->
          <el-tab-pane label="入社申请" name="requests">
            <div class="card pad">
              <div class="row">
                <div class="muted">仅显示待审批（pending）的申请。</div>
                <el-button @click="loadRequests">刷新申请</el-button>
              </div>

              <el-table :data="requests" v-loading="loadingReq" style="width:100%; margin-top:12px;" empty-text="暂无待审批申请">
                <el-table-column prop="id" label="ID" width="90" />
                <el-table-column prop="user_username" label="申请人" width="160" />
                <el-table-column prop="reason" label="理由" min-width="220" show-overflow-tooltip />
                <el-table-column prop="created_at" label="申请时间" width="190" show-overflow-tooltip>
                  <template #default="{ row }"><span class="muted">{{ fmt(row.created_at) }}</span></template>
                </el-table-column>
                <el-table-column label="操作" width="220" fixed="right">
                  <template #default="{ row }">
                    <el-button type="success" size="small" :loading="row.__loading" @click="approve(row)">通过</el-button>
                    <el-button type="warning" size="small" :loading="row.__loading" style="margin-left:10px;" @click="reject(row)">拒绝</el-button>
                  </template>
                </el-table-column>
              </el-table>

              <div class="muted tip" v-if="reqHint">{{ reqHint }}</div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>

    <!-- 新建/编辑板块 -->
    <el-dialog v-model="dlgSection" :title="editingSectionId ? '编辑板块' : '新建板块'" width="640px" destroy-on-close>
      <el-form label-width="110px">
        <el-form-item label="名称">
          <el-input v-model="sectionForm.name" placeholder="例如：读书分享 / 书评 / 问答" />
        </el-form-item>
        <el-form-item label="顺序">
          <el-input v-model.number="sectionForm.order" type="number" />
          <div class="muted tip">数字越小越靠前。</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dlgSection=false">取消</el-button>
        <el-button type="primary" :loading="savingSection" @click="saveSection">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const loading = ref(false);
const items = ref([]);
const q = ref("");

function fmt(v) {
  if (!v) return "-";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v).replace("T", " ").replace("Z", "") : d.toLocaleString();
}

/* ============ 社团列表 ============ */
async function load() {
  loading.value = true;
  try {
    const res = await http.get("/admin/clubs/", { params: q.value ? { q: q.value } : {} });
    items.value = res.data || [];
  } catch (e) {
    ElMessage.error(e?.response?.status === 404 ? "后端未提供 /admin/clubs/ 接口" : "加载社团失败");
    items.value = [];
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  q.value = "";
  load();
}

/* ============ 新建/编辑社团 ============ */
const dlgClub = ref(false);
const savingClub = ref(false);
const editingClubId = ref(null);
const clubForm = reactive({ name: "", description: "" });

function openCreate() {
  editingClubId.value = null;
  clubForm.name = "";
  clubForm.description = "";
  dlgClub.value = true;
}

function openEdit(row) {
  editingClubId.value = row.id;
  clubForm.name = row.name || "";
  clubForm.description = row.description || "";
  dlgClub.value = true;
}

async function saveClub() {
  if (!clubForm.name.trim()) return ElMessage.warning("社团名称不能为空");
  savingClub.value = true;
  try {
    const payload = { name: clubForm.name, description: clubForm.description };

    if (editingClubId.value) {
      await http.patch(`/admin/clubs/${editingClubId.value}/`, payload);
      ElMessage.success("已保存");
    } else {
      await http.post("/admin/clubs/", payload);
      ElMessage.success("已创建");
    }

    dlgClub.value = false;
    await load();
  } catch {
    ElMessage.error("保存失败：请检查接口/权限/后端日志");
  } finally {
    savingClub.value = false;
  }
}

async function removeClub(id) {
  try {
    await http.delete(`/admin/clubs/${id}/`);
    ElMessage.success("已删除");
    await load();
  } catch {
    ElMessage.error("删除失败");
  }
}

/* ============ 管理抽屉 ============ */
const drawer = ref(false);
const current = ref(null);
const tab = ref("base");
const manageTitle = computed(() => current.value ? `管理：${current.value.name}` : "社团管理");

function openManage(row) {
  current.value = row;
  tab.value = "base";
  drawer.value = true;
  loadSections();
  loadRequests();
}

/* ============ 板块管理 ============ */
const sections = ref([]);
const loadingSections = ref(false);

async function loadSections() {
  if (!current.value?.id) return;
  loadingSections.value = true;
  try {
    const res = await http.get(`/admin/clubs/${current.value.id}/sections/`);
    sections.value = res.data || [];
  } catch (e) {
    // 如果你后端没做 admin sections，可以提示
    ElMessage.error(e?.response?.status === 404 ? "后端未提供板块管理接口（/admin/clubs/<id>/sections/）" : "加载板块失败");
    sections.value = [];
  } finally {
    loadingSections.value = false;
  }
}

const dlgSection = ref(false);
const savingSection = ref(false);
const editingSectionId = ref(null);
const sectionForm = reactive({ name: "", order: 1 });

function openSectionCreate() {
  if (!current.value?.id) return;
  editingSectionId.value = null;
  sectionForm.name = "";
  sectionForm.order = 1;
  dlgSection.value = true;
}

function openSectionEdit(row) {
  editingSectionId.value = row.id;
  sectionForm.name = row.name || "";
  sectionForm.order = Number(row.order) || 1;
  dlgSection.value = true;
}

async function saveSection() {
  if (!current.value?.id) return;
  if (!sectionForm.name.trim()) return ElMessage.warning("板块名称不能为空");

  savingSection.value = true;
  try {
    const payload = { name: sectionForm.name, order: sectionForm.order };

    if (editingSectionId.value) {
      await http.patch(`/admin/sections/${editingSectionId.value}/`, payload);
      ElMessage.success("已保存");
    } else {
      await http.post(`/admin/clubs/${current.value.id}/sections/`, payload);
      ElMessage.success("已创建");
    }

    dlgSection.value = false;
    await loadSections();
  } catch {
    ElMessage.error("保存板块失败：请检查接口/权限");
  } finally {
    savingSection.value = false;
  }
}

async function removeSection(sectionId) {
  try {
    await http.delete(`/admin/sections/${sectionId}/`);
    ElMessage.success("已删除");
    await loadSections();
  } catch {
    ElMessage.error("删除板块失败");
  }
}

/* ============ 入社申请审批 ============ */
const requests = ref([]);
const loadingReq = ref(false);
const reqHint = ref("");

async function loadRequests() {
  if (!current.value?.id) return;
  loadingReq.value = true;
  reqHint.value = "";
  try {
    const res = await http.get(`/admin/clubs/${current.value.id}/requests/`);
    requests.value = (res.data || []).map((x) => ({ ...x, __loading: false }));
  } catch (e) {
    if (e?.response?.status === 403) reqHint.value = "你没有权限查看该社团的申请（需要 staff 或社团管理员）。";
    if (e?.response?.status === 404) reqHint.value = "后端未提供 admin requests 接口（/admin/clubs/<id>/requests/）。";
    requests.value = [];
  } finally {
    loadingReq.value = false;
  }
}

async function approve(row) {
  row.__loading = true;
  try {
    await http.post(`/requests/${row.id}/approve/`);
    ElMessage.success("已通过");
    await loadRequests();
  } catch {
    ElMessage.error("审批失败");
  } finally {
    row.__loading = false;
  }
}

async function reject(row) {
  row.__loading = true;
  try {
    await http.post(`/requests/${row.id}/reject/`);
    ElMessage.success("已拒绝");
    await loadRequests();
  } catch {
    ElMessage.error("审批失败");
  } finally {
    row.__loading = false;
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
.muted{ color: var(--muted); }

.drawer-wrap{ display:grid; gap: 12px; }
.row{ display:flex; justify-content: space-between; align-items:center; gap: 10px; flex-wrap: wrap; }
.kv{ margin: 6px 0; }

.tip{ margin-top: 10px; font-size: 12px; line-height: 1.5; }
</style>

<template>
  <el-container class="layout">
    <el-aside class="aside" :width="ui.collapsed ? '72px' : '260px'">
      <div class="aside__brand">
        <div class="brand__logo">📚</div>
        <div class="brand__text" v-if="!ui.collapsed">
          <div class="brand__title">书圈</div>
          <div class="brand__sub">管理后台</div>
        </div>
      </div>

      <el-scrollbar class="aside__scroll">
        <el-menu
          class="aside__menu"
          :default-active="active"
          router
          :collapse="ui.collapsed"
          background-color="transparent"
          text-color="var(--sidebar-text)"
          active-text-color="#fff"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>

          <el-menu-item index="/announcements">
            <el-icon><BellFilled /></el-icon>
            <span>公告管理</span>
          </el-menu-item>

          <el-menu-item index="/books">
            <el-icon><Collection /></el-icon>
            <span>书籍管理</span>
          </el-menu-item>

          <el-menu-item index="/chapters">
            <el-icon><Document /></el-icon>
            <span>章节管理</span>
          </el-menu-item>

          <el-menu-item index="/clubs">
            <el-icon><OfficeBuilding /></el-icon>
            <span>社团管理</span>
          </el-menu-item>

          <el-menu-item index="/activities">
            <el-icon><Calendar /></el-icon>
            <span>活动管理</span>
          </el-menu-item>

          <el-menu-item index="/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>

      <div class="aside__footer">
        <el-button class="aside__btn" text @click="ui.toggleCollapsed()">
          <el-icon><Fold v-if="!ui.collapsed" /><Expand v-else /></el-icon>
          <span v-if="!ui.collapsed">收起菜单</span>
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header__left">
          <el-button class="icon-btn" text @click="ui.toggleCollapsed()">
            <el-icon><Menu /></el-icon>
          </el-button>

          <div class="crumbs">
            <span class="crumbs__muted">管理后台</span>
            <span class="crumbs__sep" v-if="pageTitle">/</span>
            <span class="crumbs__title" v-if="pageTitle">{{ pageTitle }}</span>
          </div>
        </div>

        <div class="header__right">
          <el-tooltip content="切换主题" placement="bottom">
            <el-button class="icon-btn" text @click="ui.toggleTheme()">
              <el-icon><Moon v-if="ui.theme !== 'dark'" /><Sunny v-else /></el-icon>
            </el-button>
          </el-tooltip>

          <el-dropdown trigger="click">
            <span class="user-chip">
              <span class="user-avatar">{{ (auth.username || "管").charAt(0).toUpperCase() }}</span>
              <span class="user-name">{{ auth.username || "管理员" }}</span>
              <el-icon class="user-chev"><ArrowDown /></el-icon>
            </span>

            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  当前账号：{{ auth.username || "管理员" }}
                </el-dropdown-item>
                <el-dropdown-item divided @click="logout">
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useUiStore } from "../stores/ui";

import {
  Menu,
  HomeFilled,
  BellFilled,
  Collection,
  Document,
  UserFilled,
  OfficeBuilding,
  Calendar,
  Fold,
  Expand,
  Sunny,
  Moon,
  ArrowDown,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const ui = useUiStore();

const active = computed(() => route.path);
const pageTitle = computed(() => route.matched?.[route.matched.length - 1]?.meta?.title || "");

function logout() {
  if (!confirm("确定要退出登录吗？")) return;
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.layout{ height: 100vh; }

.aside{
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  display:flex;
  flex-direction: column;
}

.aside__brand{
  display:flex;
  align-items:center;
  gap: 10px;
  padding: 16px;
  color: #fff;
}
.brand__logo{
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display:grid;
  place-items:center;
  background: rgba(37,99,235,.18);
  border: 1px solid rgba(37,99,235,.25);
  user-select:none;
}
.brand__title{ font-weight: 1000; letter-spacing: .2px; }
.brand__sub{ margin-top: 2px; font-size: 12px; color: var(--sidebar-muted); font-weight: 900; }

.aside__scroll{ flex: 1; padding: 6px 10px 10px; }

.aside__menu :deep(.el-menu-item){
  border-radius: 12px;
  margin: 4px 0;
}
.aside__menu :deep(.el-menu-item.is-active){
  background: rgba(37,99,235,.18) !important;
}
.aside__menu :deep(.el-menu-item:hover){
  background: rgba(255,255,255,0.06);
}

.aside__footer{
  padding: 10px 12px 14px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.aside__btn{
  width: 100%;
  justify-content: flex-start;
  color: var(--sidebar-text);
  border-radius: 12px;
}

.header{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 12px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  height: 56px;
}

.header__left, .header__right{
  display:flex;
  align-items:center;
  gap: 10px;
}

.icon-btn{ border-radius: 12px; }

.crumbs{
  display:flex;
  align-items:center;
  gap: 8px;
  color: var(--muted);
  font-weight: 900;
}
.crumbs__title{ color: var(--text); }
.crumbs__sep{ opacity: .6; }

.user-chip{
  display:inline-flex;
  align-items:center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.55);
  cursor: pointer;
  user-select:none;
}
html.dark .user-chip{ background: rgba(17,24,39,0.60); }

.user-avatar{
  width: 30px;
  height: 30px;
  border-radius: 12px;
  display:grid;
  place-items:center;
  font-weight: 1000;
  color: #fff;
  background: linear-gradient(135deg, var(--brand-2), var(--brand));
}
.user-name{
  max-width: 140px;
  overflow:hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 1000;
}
.user-chev{ opacity: .6; }

.main{
  padding: 18px;
  background: var(--bg);
}
</style>

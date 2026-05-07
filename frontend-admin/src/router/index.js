import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import AdminLayout from "../layouts/AdminLayout.vue";
import Login from "../views/Login.vue";
import Dashboard from "../views/Dashboard.vue";
import Announcements from "../views/Announcements.vue";

import Books from "../views/Books.vue";
import Chapters from "../views/Chapters.vue";
import Users from "../views/Users.vue";
import Clubs from "../views/Clubs.vue";
import Activities from "../views/Activities.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      component: Login,
      meta: { title: "登录" },
    },
    {
      path: "/",
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          component: Dashboard,
          meta: { title: "仪表盘", requiresAuth: true },
        },
        {
          path: "announcements",
          component: Announcements,
          meta: { title: "公告管理", requiresAuth: true },
        },
        {
          path: "books",
          component: Books,
          meta: { title: "书籍管理", requiresAuth: true },
        },
        {
          path: "chapters",
          component: Chapters,
          meta: { title: "章节管理", requiresAuth: true },
        },
        {
          path: "users",
          component: Users,
          meta: { title: "用户管理", requiresAuth: true },
        },
        {
          path: "clubs",
          component: Clubs,
          meta: { title: "社团管理", requiresAuth: true },
        },
        {
          path: "activities",
          component: Activities,
          meta: { title: "活动管理", requiresAuth: true },
        },
      ],
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return "/login";
  }

  if (to.path === "/login" && auth.isLoggedIn) {
    return "/";
  }

  return true;
});

export default router;

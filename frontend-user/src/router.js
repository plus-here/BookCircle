import { createRouter, createWebHistory } from "vue-router";

import Home from "./views/Home.vue";
import BookDetail from "./views/BookDetail.vue";
import ReadChapter from "./views/ReadChapter.vue";
import Shelf from "./views/Shelf.vue";
import Login from "./views/Login.vue";
import Register from "./views/Register.vue";
import Profile from "./views/Profile.vue";

import Clubs from "./views/Clubs.vue";
import ClubDetail from "./views/ClubDetail.vue";
import ClubRequests from "./views/ClubRequests.vue";
import SectionPosts from "./views/SectionPosts.vue";
import PostDetail from "./views/PostDetail.vue";

import Groups from "./views/Groups.vue";
import GroupChat from "./views/GroupChat.vue";

import DMThreads from "./views/DMThreads.vue";
import DMChat from "./views/DMChat.vue";

import Activities from "./views/Activities.vue";
import ActivityDetail from "./views/ActivityDetail.vue";
import MyActivities from "./views/MyActivities.vue";

import Announcements from "./views/Announcements.vue";
import AnnouncementDetail from "./views/AnnouncementDetail.vue";


const authRequired = { requiresAuth: true };

const routes = [
  { path: "/", component: Home },
  { path: "/books/:id", component: BookDetail },
  { path: "/chapters/:id", component: ReadChapter },
  { path: "/shelf", component: Shelf, meta: authRequired },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/profile", component: Profile, meta: authRequired },

  { path: "/clubs", component: Clubs },
  { path: "/clubs/:id", component: ClubDetail },
  { path: "/clubs/:id/requests", component: ClubRequests, meta: authRequired },
  { path: "/sections/:id/posts", component: SectionPosts, meta: authRequired },
  { path: "/posts/:id", component: PostDetail },
  { path: "/groups", component: Groups, meta: authRequired },
  { path: "/groups/:id", component: GroupChat, meta: authRequired },

  { path: "/dm", component: DMThreads, meta: authRequired },
  { path: "/dm/:id", component: DMChat, meta: authRequired },
  { path: "/activities", component: Activities },
  { path: "/activities/:id", component: ActivityDetail },
  { path: "/my-activities", component: MyActivities, meta: authRequired },

  { path: "/announcements", component: Announcements },
  { path: "/announcements/:id", component: AnnouncementDetail },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (!to.meta?.requiresAuth) return true;
  if (localStorage.getItem("access")) return true;
  return {
    path: "/login",
    query: { redirect: to.fullPath },
  };
});

export default router;

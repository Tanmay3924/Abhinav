import { createRouter, createWebHistory } from "vue-router";
import Home from "./components/Home.vue";
import Login from "./components/Login.vue";
import Register from "./components/Register.vue";
import AdminDash from "./components/AdminDash.vue";
import UserDash from "./components/UserDash.vue";
import AdminLots from "./components/AdminLots.vue";
import AdminUsers from "./components/AdminUsers.vue";
import AdminReservations from "./components/AdminReservations.vue";
import AdminAnalytics from "./components/AdminAnalytics.vue";
import UserAnalytics from "./components/UserAnalytics.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/home", component: Home },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  {
    path: "/admin",
    component: AdminDash,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/admin/lots",
    component: AdminLots,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/user",
    component: UserDash,
    meta: { requiresAuth: true, role: "user" },
  },
  {
    path: "/admin/users",
    component: AdminUsers,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/admin/reservations",
    component: AdminReservations,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/admin/analytics",
    component: AdminAnalytics,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/user/analytics",
    component: UserAnalytics,
    meta: { requiresAuth: true, role: "user" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Simple guard: check token & stored user
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("pz_token");
  const userStr = localStorage.getItem("pz_user");
  let user = null;
  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch (e) {
      user = null;
    }
  }

  if (to.meta.requiresAuth) {
    if (!token || !user) return next("/login");
    if (to.meta.role && user.role !== to.meta.role) {
      return next(user.role === "admin" ? "/admin" : "/user");
    }
  }
  next();
});

export default router;

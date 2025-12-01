// frontend/src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import api, { setAuthToken } from "./api";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle"; // bootstrap JS (modals etc)

// If token exists in localStorage, set auth header on startup
const token = localStorage.getItem("pz_token");
if (token) setAuthToken(token);

const app = createApp(App);

// make axios available as this.$api in components
app.config.globalProperties.$api = api;
app.config.globalProperties.$axios = api;

app.use(router);
app.mount("#app");

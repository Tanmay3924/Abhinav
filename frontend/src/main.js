import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { setAuthToken } from "./api";
import "bootstrap/dist/css/bootstrap.min.css";

// If token exists in localStorage, set auth header on startup
const token = localStorage.getItem("pz_token");
if (token) setAuthToken(token);

const app = createApp(App);
app.use(router);
app.mount("#app");

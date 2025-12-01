<template>
  <div class="auth-page d-flex align-items-center">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-5 col-md-7">
          <div class="card login-card shadow-lg">
            <div class="card-body p-4">
              <h3 class="mb-3 text-center">Welcome back</h3>
              <p class="text-center text-muted small mb-4">Sign in to access your ParkZone dashboard</p>

              <div class="mb-3">
                <label class="form-label small">Email</label>
                <input v-model="email" type="email" class="form-control form-control-lg" placeholder="you@domain.com" />
              </div>

              <div class="mb-3">
                <label class="form-label small">Password</label>
                <input v-model="password" type="password" class="form-control form-control-lg" placeholder="Enter your password" />
              </div>

              <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <input type="checkbox" id="remember" v-model="remember" />
                  <label for="remember" class="small ms-1">Remember me</label>
                </div>
                <router-link to="/register" class="small">Create account</router-link>
              </div>

              <div class="d-grid mb-2">
                <button class="btn btn-primary btn-lg" @click="doLogin" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ loading ? "Signing in…" : "Sign In" }}
                </button>
              </div>

              <div v-if="msg" class="alert mt-3" :class="msgType">{{ msg }}</div>
            </div>
          </div>

          <div class="text-center mt-3 small text-muted">
            By signing in you agree to our <u>terms</u> & <u>privacy</u>.
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import api, { setAuthToken } from "../api";

export default {
  name: "Login",
  data() {
    return {
      email: "",
      password: "",
      remember: false,
      msg: null,
      msgType: "alert-info",
      loading: false
    };
  },
  methods: {
    async doLogin() {
      this.msg = null;
      if (!this.email || !this.password) {
        this.msg = "Please enter both email and password";
        this.msgType = "alert-warning";
        return;
      }
      this.loading = true;
      try {
        const res = await api.post("/auth/login", { email: this.email, password: this.password });
        const token = res.data.access_token;
        const user = res.data.user;

        // save token and user
        localStorage.setItem("pz_token", token);
        localStorage.setItem("pz_user", JSON.stringify(user));
        if (this.remember) localStorage.setItem("pz_remember", "1");
        else localStorage.removeItem("pz_remember");

        setAuthToken(token);

        // small success toast-like message then redirect
        this.msg = "Welcome back! Redirecting…";
        this.msgType = "alert-success";
        setTimeout(() => {
          if (user.role === "admin") this.$router.push("/admin");
          else this.$router.push("/user");
        }, 600);
      } catch (err) {
        this.msg = err.response?.data?.msg || "Invalid credentials or server unreachable";
        this.msgType = "alert-danger";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.auth-page { min-height: 78vh; display: flex; align-items: center; background: linear-gradient(180deg,#f1f5f9 0%, #ffffff 100%); }
.login-card { border-radius: 12px; overflow: hidden; }
.login-card .card-body { padding: 2rem; }
.spinner-border { vertical-align: middle; }
</style>

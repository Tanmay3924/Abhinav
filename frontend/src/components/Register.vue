<template>
  <div class="auth-page d-flex align-items-center">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-6 col-md-8">
          <div class="card register-card shadow-lg">
            <div class="card-body p-4">
              <h3 class="mb-3 text-center">Create your ParkZone account</h3>
              <p class="text-center text-muted small mb-4">Register to reserve parking and track your history.</p>

              <div class="mb-2">
                <label class="form-label small">Username</label>
                <input v-model="username" class="form-control" placeholder="e.g. john_doe" />
              </div>

              <div class="mb-2">
                <label class="form-label small">Email</label>
                <input v-model="email" type="email" class="form-control" placeholder="you@domain.com" />
              </div>

              <div class="mb-3">
                <label class="form-label small">Password</label>
                <input v-model="password" type="password" class="form-control" placeholder="At least 6 characters" />
              </div>

              <div class="d-grid">
                <button class="btn btn-success btn-lg" @click="doRegister" :disabled="loading">
                  {{ loading ? "Creating account…" : "Create Account" }}
                </button>
              </div>

              <div v-if="msg" class="alert mt-3" :class="msgType">{{ msg }}</div>

              <div class="text-center mt-3 small">
                Already have an account? <router-link to="/login">Sign in</router-link>
              </div>
            </div>
          </div>

          <div class="text-center mt-3 small text-muted">
            We never share your data. This is a demo app for your project submission.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";

export default {
  name: "Register",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      msg: null,
      msgType: "alert-info",
      loading: false
    };
  },
  methods: {
    async doRegister() {
      this.msg = null;

      if (!this.username || !this.email || !this.password) {
        this.msg = "Please fill all fields.";
        this.msgType = "alert-warning";
        return;
      }
      if (this.password.length < 6) {
        this.msg = "Password must be at least 6 characters.";
        this.msgType = "alert-warning";
        return;
      }

      this.loading = true;
      try {
        await api.post("/auth/register", { username: this.username, email: this.email, password: this.password });
        this.msg = "Account created! Redirecting to login…";
        this.msgType = "alert-success";
        setTimeout(() => this.$router.push("/login"), 900);
      } catch (err) {
        this.msg = err.response?.data?.msg || "Registration failed";
        this.msgType = "alert-danger";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.auth-page { min-height: 78vh; display: flex; align-items: center; background: linear-gradient(180deg,#ffffff 0%, #f7f9fc 100%); }
.register-card { border-radius: 12px; }
.register-card .card-body { padding: 2rem; }
</style>

<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
      <div class="container">
        <a class="navbar-brand" href="/">ParkZone 2.0</a>
        <div class="d-flex">
          <template v-if="user">
            <span class="me-3">Hi, {{ user.username }}</span>
            <button class="btn btn-outline-secondary btn-sm" @click="goDashboard">Dashboard</button>
            <button class="btn btn-danger btn-sm ms-2" @click="logout">Logout</button>
          </template>
          <template v-else>
            <router-link class="btn btn-outline-primary btn-sm me-2" to="/login">Login</router-link>
            <router-link class="btn btn-primary btn-sm" to="/register">Register</router-link>
          </template>
        </div>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script>
export default {
  name: "App",
  computed: {
    user() {
      const u = localStorage.getItem("pz_user");
      if (!u) return null;
      try { return JSON.parse(u); } catch(e) { return null; }
    }
  },
  methods: {
    logout() {
      localStorage.removeItem("pz_token");
      localStorage.removeItem("pz_user");
      // remove auth header
      import("./api").then(m => m.setAuthToken(null));
      this.$router.push("/login");
    },
    goDashboard() {
      const u = this.user;
      if (!u) return this.$router.push("/login");
      if (u.role === "admin") this.$router.push("/admin");
      else this.$router.push("/user");
    }
  }
};
</script>

<style>
body { background: #f8f9fa; }
</style>

<template>
  <div class="admin-container">
    <div class="container py-5">
      <h2 class="fw-bold text-white mb-2">Admin Dashboard</h2>
      <p class="text-light mb-4 opacity-75">Welcome, {{ adminName }}!</p>

      <div class="row g-4">
        <div class="col-md-4">
          <div class="card dash-card shadow">
            <div class="card-body text-center">
              <h5 class="card-title">Parking Lots</h5>
              <p class="card-text small">Create and manage parking lots.</p>
              <button class="btn btn-primary" @click="goTo('/admin/lots')">
                Manage Lots
              </button>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card dash-card shadow">
            <div class="card-body text-center">
              <h5 class="card-title">Users</h5>
              <p class="card-text small">View registered users.</p>
              <button class="btn btn-primary" @click="goTo('/admin/users')">
                View Users
              </button>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card dash-card shadow">
            <div class="card-body text-center">
              <h5 class="card-title">Reservations</h5>
              <p class="card-text small">View parking history.</p>
              <button
                class="btn btn-primary"
                @click="goTo('/admin/reservations')"
              >
                View Reservations
              </button>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card dash-card shadow">
            <div class="card-body text-center">
              <h5 class="card-title">Analytics</h5>
              <p class="card-text small">Charts & insights.</p>
              <button class="btn btn-primary" @click="goTo('/admin/analytics')">
                View Analytics
              </button>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card dash-card shadow">
            <div class="card-body text-center">
              <h5 class="card-title">CSV Export</h5>
              <p class="card-text small">Export parking records.</p>
              <button class="btn btn-primary" @click="exportCSV">
                Export CSV
              </button>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card dash-card shadow">
            <div class="card-body text-center">
              <h5 class="card-title">Logout</h5>
              <p class="card-text small">End your session.</p>
              <button class="btn btn-danger" @click="logout">Logout</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// --- FIX: Import must be inside the script tag ---
import api from "../api";

export default {
  name: "AdminDash",
  data() {
    return {
      adminName: "",
    };
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("pz_user") || "{}");
    this.adminName = user.username || "Admin";
  },
  methods: {
    goTo(path) {
      this.$router.push(path);
    },
    logout() {
      localStorage.removeItem("pz_token");
      localStorage.removeItem("pz_user");
      this.$router.push("/login");
    },
    async exportCSV() {
      if (!confirm("Generate and email CSV report?")) return;
      try {
        const res = await api.post("/admin/export-csv");
        alert(res.data.msg);
      } catch (err) {
        console.error(err);
        alert("Failed to start export job. Check backend logs.");
      }
    },
  },
};
</script>

<style scoped>
/* Background gradient like Home page */
.admin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #0b61a4 55%, #4f46e5 100%);
  padding-bottom: 50px;
}

/* Dashboard Cards */
.dash-card {
  border-radius: 14px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.dash-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.25);
}

.card-title {
  font-weight: 600;
}
</style>

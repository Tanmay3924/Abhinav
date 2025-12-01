<template>
  <div class="user-container">
    <div class="container py-5">
      <div class="d-flex align-items-center justify-content-between mb-4">
        <h2 class="fw-bold text-white mb-0">My Activity & Stats</h2>
        <button class="btn btn-light btn-sm" @click="$router.push('/user')">
          &larr; Back to Dashboard
        </button>
      </div>

      <div v-if="loading" class="text-white text-center mt-5">
        <div class="spinner-border text-light" role="status"></div>
        <p>Loading your stats...</p>
      </div>

      <div v-else>
        <div class="row g-4 mb-4">
          <div class="col-md-6">
            <div class="card shadow border-0">
              <div class="card-body text-center">
                <h6 class="text-muted text-uppercase">Total Spent</h6>
                <h3 class="fw-bold text-primary">${{ stats.total_spent }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow border-0">
              <div class="card-body text-center">
                <h6 class="text-muted text-uppercase">Total Parkings</h6>
                <h3 class="fw-bold text-success">{{ stats.total_parkings }}</h3>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow border-0" style="height: 400px">
          <div class="card-header bg-white fw-bold">
            My Spending Trend (Last 5 Visits)
          </div>
          <div class="card-body">
            <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
            <div v-else class="text-center text-muted mt-5">
              No recent parking history to display.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { Bar } from "vue-chartjs";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default {
  name: "UserAnalytics",
  components: { Bar },
  data() {
    return {
      loading: true,
      stats: null,
      chartData: null,
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true },
        },
      },
    };
  },
  async created() {
    try {
      const res = await api.get("/user/analytics");
      this.stats = res.data.stats;

      // Only setup chart if we have data points
      if (res.data.chart.labels.length > 0) {
        this.chartData = {
          labels: res.data.chart.labels,
          datasets: [
            {
              label: "Cost ($)",
              backgroundColor: "#0d6efd",
              data: res.data.chart.data,
            },
          ],
        };
      }
    } catch (err) {
      console.error(err);
      alert("Error loading stats");
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
/* Same gradient as User Dash for consistency */
.user-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  padding-bottom: 50px;
}
</style>

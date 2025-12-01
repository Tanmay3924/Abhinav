<template>
  <div class="admin-container">
    <div class="container py-5">
      <div class="d-flex align-items-center justify-content-between mb-4">
        <h2 class="fw-bold text-white mb-0">Analytics & Insights</h2>
        <button class="btn btn-light btn-sm" @click="$router.push('/admin')">
          &larr; Back to Dashboard
        </button>
      </div>

      <div v-if="loading" class="text-white text-center mt-5">
        <div class="spinner-border text-light" role="status"></div>
        <p class="mt-2">Loading data...</p>
      </div>

      <div v-else>
        <div class="row g-4 mb-4">
          <div class="col-md-4">
            <div class="card shadow border-0">
              <div class="card-body text-center">
                <h6 class="text-muted text-uppercase">Total Revenue</h6>
                <h3 class="fw-bold text-primary">
                  ${{ stats.revenue.total_lifetime }}
                </h3>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card shadow border-0">
              <div class="card-body text-center">
                <h6 class="text-muted text-uppercase">Available Spots</h6>
                <h3 class="fw-bold text-success">
                  {{ stats.occupancy.available }}
                </h3>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card shadow border-0">
              <div class="card-body text-center">
                <h6 class="text-muted text-uppercase">Occupied Spots</h6>
                <h3 class="fw-bold text-danger">
                  {{ stats.occupancy.occupied }}
                </h3>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-md-8">
            <div class="card shadow border-0 h-100">
              <div class="card-header bg-white fw-bold">
                Revenue (Last 7 Days)
              </div>
              <div class="card-body">
                <Bar v-if="barData" :data="barData" :options="chartOptions" />
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card shadow border-0 h-100">
              <div class="card-header bg-white fw-bold">Live Occupancy</div>
              <div
                class="card-body d-flex align-items-center justify-content-center"
              >
                <div style="position: relative; height: 250px; width: 100%">
                  <Doughnut
                    v-if="doughnutData"
                    :data="doughnutData"
                    :options="chartOptions"
                  />
                </div>
              </div>
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
  ArcElement,
} from "chart.js";
import { Bar, Doughnut } from "vue-chartjs";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default {
  name: "AdminAnalytics",
  components: { Bar, Doughnut },
  data() {
    return {
      loading: true,
      stats: null,
      barData: null,
      doughnutData: null,
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  async created() {
    await this.fetchAnalytics();
  },
  methods: {
    async fetchAnalytics() {
      try {
        const res = await api.get("/admin/analytics");
        this.stats = res.data;
        this.setupCharts();
      } catch (err) {
        console.error(err);
        alert("Failed to load analytics data.");
      } finally {
        this.loading = false;
      }
    },
    setupCharts() {
      // 1. Setup Bar Chart
      this.barData = {
        labels: this.stats.revenue.daily_labels,
        datasets: [
          {
            label: "Revenue ($)",
            backgroundColor: "#4f46e5",
            data: this.stats.revenue.daily_values,
          },
        ],
      };

      // 2. Setup Doughnut Chart
      this.doughnutData = {
        labels: ["Available", "Occupied"],
        datasets: [
          {
            backgroundColor: ["#198754", "#dc3545"],
            data: [
              this.stats.occupancy.available,
              this.stats.occupancy.occupied,
            ],
          },
        ],
      };
    },
  },
};
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #0b61a4 55%, #4f46e5 100%);
  padding-bottom: 50px;
}
</style>

<template>
  <div class="container mt-4">
    <h2>User Dashboard</h2>

    <div v-if="loading" class="text-center">Loading...</div>

    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="text-white">User Dashboard</h2>
        <div>
          <button
            class="btn btn-info text-white me-2"
            @click="$router.push('/user/analytics')"
          >
            📊 My Stats
          </button>
        </div>
      </div>
      <div v-if="activeReservation" class="card text-white bg-success mb-4">
        <div class="card-header">Current Status: <strong>OCCUPIED</strong></div>
        <div class="card-body">
          <h5 class="card-title">
            You are parked at: {{ activeReservation.lot_name }}
          </h5>
          <p class="card-text">
            <strong>Spot Number:</strong> {{ activeReservation.spot_number
            }}<br />
            <strong>Parked At:</strong>
            {{ formatDate(activeReservation.reservation.parked_at) }}<br />
            <strong>Rate:</strong> ₹{{ activeReservation.price_per_hour }}/hr
          </p>
          <button @click="releaseSpot" class="btn btn-danger">
            Release Spot & Pay
          </button>
        </div>
      </div>

      <div v-if="!activeReservation" class="mb-5">
        <h4>Available Parking Lots</h4>
        <div class="row">
          <div class="col-md-4 mb-3" v-for="lot in lots" :key="lot.id">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ lot.prime_location_name }}</h5>
                <p class="card-text">
                  {{ lot.address }}<br />
                  Price: ₹{{ lot.price_per_hour }}/hr<br />
                  <span
                    :class="
                      lot.available_spots > 0 ? 'text-success' : 'text-danger'
                    "
                  >
                    Available Spots: {{ lot.available_spots }}
                  </span>
                </p>
                <button
                  class="btn btn-primary w-100"
                  :disabled="lot.available_spots === 0"
                  @click="occupySpot(lot.id)"
                >
                  {{
                    lot.available_spots > 0 ? "Park Here (Auto-Alloc)" : "Full"
                  }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">Parking History</div>
        <div class="card-body">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Lot</th>
                <th>Spot</th>
                <th>In Time</th>
                <th>Out Time</th>
                <th>Cost</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="h in history" :key="h.id">
                <td>{{ h.lot_name }}</td>
                <td>{{ h.spot_number }}</td>
                <td>{{ formatDate(h.parked_at) }}</td>
                <td>{{ formatDate(h.left_at) }}</td>
                <td>₹{{ h.cost }}</td>
              </tr>
              <tr v-if="history.length === 0">
                <td colspan="5" class="text-center">No history found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";

export default {
  name: "UserDash",
  data() {
    return {
      lots: [],
      activeReservation: null,
      history: [],
      loading: true,
    };
  },
  async created() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        // 1. Check current status
        const statusRes = await api.get("/user/status");
        if (statusRes.data.has_active) {
          this.activeReservation = statusRes.data;
        } else {
          this.activeReservation = null;
        }

        // 2. Load lots (only needed if not parked, but good to have)
        const lotsRes = await api.get("/user/lots");
        this.lots = lotsRes.data.lots;

        // 3. Load History
        const histRes = await api.get("/user/history");
        this.history = histRes.data.history;
      } catch (err) {
        console.error(err);
        alert("Error fetching dashboard data");
      } finally {
        this.loading = false;
      }
    },
    async occupySpot(lotId) {
      if (
        !confirm(
          "Confirm parking at this lot? System will auto-allocate a spot."
        )
      )
        return;
      try {
        await api.post("/user/park", { lot_id: lotId });
        await this.fetchData(); // Refresh UI
      } catch (err) {
        alert(err.response?.data?.msg || "Error parking vehicle");
      }
    },
    async releaseSpot() {
      if (!confirm("Are you sure you want to release the spot and leave?"))
        return;
      try {
        const res = await api.post("/user/release");
        alert(`Spot Released! Cost: ₹${res.data.cost}`);
        await this.fetchData(); // Refresh UI
      } catch (err) {
        alert(err.response?.data?.msg || "Error releasing spot");
      }
    },
    formatDate(dateStr) {
      // 1. Safety Check
      if (!dateStr) return "-";

      // 2. Remove milliseconds if present (e.g., .123456)
      const cleanDate = dateStr.split(".")[0];

      // 3. Split into Date and Time (e.g., "2025-11-14" and "20:30:00")
      const [datePart, timePart] = cleanDate.split("T");
      if (!datePart || !timePart) return dateStr; // Fallback

      // 4. Split parts to format them manually
      const [year, month, day] = datePart.split("-");
      let [hour, minute] = timePart.split(":");

      // 5. Convert to 12-Hour Format (AM/PM) manually
      hour = parseInt(hour);
      const ampm = hour >= 12 ? "PM" : "AM";
      hour = hour % 12 || 12; // Convert 0 to 12

      // 6. Return the formatted string
      // Result: "14-11-2025, 8:30 PM" (Exactly what is in the DB)
      return `${day}-${month}-${year}, ${hour}:${minute} ${ampm}`;
    },
  },
};
</script>

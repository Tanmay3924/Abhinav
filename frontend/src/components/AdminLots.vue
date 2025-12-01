<template>
  <div class="container py-4">
    <h3 class="mb-4">Admin — Parking Lots</h3>

    <!-- Create Lot Form -->
    <div class="card mb-4 p-3 shadow-sm">
      <h5>Create Parking Lot</h5>
      <form @submit.prevent="createLot">

        <div class="mb-2">
          <input v-model="form.prime_location_name"
                 class="form-control"
                 placeholder="Prime Location Name"
                 required />
        </div>

        <div class="mb-2">
          <input v-model="form.address"
                 class="form-control"
                 placeholder="Address"
                 required />
        </div>

        <div class="mb-2">
          <input v-model="form.pin_code"
                 class="form-control"
                 placeholder="Pin Code"
                 required />
        </div>

        <div class="mb-2">
          <input v-model="form.price_per_hour"
                 type="number"
                 step="0.01"
                 class="form-control"
                 placeholder="Price Per Hour"
                 required />
        </div>

        <div class="mb-2">
          <input v-model="form.number_of_spots"
                 type="number"
                 class="form-control"
                 placeholder="Number of Spots"
                 required />
        </div>

        <button class="btn btn-primary mt-2" :disabled="creating">
          <span v-if="creating" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          <span v-else>Create Lot</span>
        </button>
      </form>
    </div>

    <!-- List of Lots -->
    <div class="card p-3 shadow-sm">
      <h5>Existing Lots</h5>

      <div v-if="loading" class="text-center py-2">
        <span class="spinner-border" role="status" aria-hidden="true"></span>
      </div>

      <div v-else>
        <div v-if="lots.length === 0" class="text-muted p-3">No lots yet.</div>

        <div v-for="lot in lots" :key="lot.id" class="border p-3 rounded mb-3">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>#{{ lot.id }}</strong> — {{ lot.prime_location_name }}
              <br />
              <small class="text-muted">{{ lot.address }}, {{ lot.pin_code }}</small>
              <br />
              <small class="badge bg-secondary">Spots: {{ lot.number_of_spots }}</small>
              <small class="badge bg-info ms-2">Rs {{ lot.price_per_hour }}/hr</small>
            </div>

            <div>
              <button class="btn btn-sm btn-outline-primary me-2"
                      @click="startEdit(lot)">
                Edit
              </button>

              <button class="btn btn-sm btn-outline-danger"
                      @click="deleteLot(lot.id)">
                Delete
              </button>
            </div>
          </div>

          <!-- Edit Form -->
          <div v-if="editingId === lot.id" class="mt-3 p-3 bg-light rounded">
            <h6>Edit Lot</h6>

            <input v-model="editForm.prime_location_name"
                   class="form-control mb-2"
                   placeholder="Prime Location Name" />

            <input v-model="editForm.address"
                   class="form-control mb-2"
                   placeholder="Address" />

            <input v-model="editForm.pin_code"
                   class="form-control mb-2"
                   placeholder="Pin Code" />

            <input v-model="editForm.price_per_hour"
                   type="number"
                   step="0.01"
                   class="form-control mb-2"
                   placeholder="Price Per Hour" />

            <input v-model="editForm.number_of_spots"
                   type="number"
                   class="form-control mb-2"
                   placeholder="Number of Spots" />

            <div class="mt-2">
              <button class="btn btn-success btn-sm me-2"
                      @click="saveEdit"
                      :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                <span v-else>Save</span>
              </button>

              <button class="btn btn-secondary btn-sm"
                      @click="cancelEdit">
                Cancel
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
/*
  AdminLots.vue
  - Uses centralized 'api' instance (frontend/src/api.js).
  - Expects token stored in localStorage under 'pz_token' (per your router.js).
  - Backend routes are mounted under /api (Flask create_app registers url_prefix "/api/admin").
*/

import api, { setAuthToken } from "../api"; // adjust path if your component location differs

export default {
  name: "AdminLots",
  data() {
    return {
      lots: [],
      loading: false,
      creating: false,
      saving: false,

      form: {
        prime_location_name: "",
        address: "",
        pin_code: "",
        price_per_hour: "",
        number_of_spots: ""
      },

      editingId: null,
      editForm: {}
    };
  },

  mounted() {
    // Set auth header if token exists (router stores token under 'pz_token')
    const token = localStorage.getItem("pz_token");
    if (token) setAuthToken(token);
    this.loadLots();
  },

  methods: {
    async loadLots() {
      try {
        this.loading = true;
        // api.baseURL already has /api, so this becomes http://127.0.0.1:5000/api/admin/lots
        const res = await api.get("/admin/lots?include_spots=1");
        this.lots = Array.isArray(res.data.lots) ? res.data.lots : [];
      } catch (err) {
        console.error("LOAD LOTS ERROR:", err);
        alert("Failed to load lots. Check console for details.");
      } finally {
        this.loading = false;
      }
    },

    async createLot() {
      try {
        this.creating = true;

        // ensure token header is present (useful if client set token after login)
        setAuthToken(localStorage.getItem("pz_token"));

        // prepare payload and ensure numeric types
        const payload = {
          prime_location_name: (this.form.prime_location_name || "").trim(),
          number_of_spots: Number.parseInt(this.form.number_of_spots || 0, 10),
          price_per_hour: Number.parseFloat(this.form.price_per_hour || 0),
          address: (this.form.address || "").trim(),
          pin_code: (this.form.pin_code || "").trim()
        };

        const res = await api.post("/admin/lots", payload);

        console.log("CREATE success:", res.data);
        alert("Lot created!");
        this.loadLots();

        // reset form
        this.form = {
          prime_location_name: "",
          address: "",
          pin_code: "",
          price_per_hour: "",
          number_of_spots: ""
        };
      } catch (err) {
        console.error("CREATE ERROR:", err);

        if (err.response) {
          // server responded with a status code outside 2xx
          const status = err.response.status;
          const serverMsg = err.response.data?.msg || JSON.stringify(err.response.data) || "";
          alert(`Failed to create lot.\nStatus: ${status}\nMessage: ${serverMsg}`);
        } else if (err.request) {
          // request was sent but no response (network/CORS)
          console.error("No response from server (request):", err.request);
          alert("Failed to create lot. No response from server. Check backend and CORS.");
        } else {
          // some other error
          alert("Failed to create lot: " + err.message);
        }
      } finally {
        this.creating = false;
      }
    },

    startEdit(lot) {
      this.editingId = lot.id;
      // clone to avoid mutating the list item directly while editing
      this.editForm = {
        prime_location_name: lot.prime_location_name || "",
        address: lot.address || "",
        pin_code: lot.pin_code || "",
        price_per_hour: lot.price_per_hour || 0,
        number_of_spots: lot.number_of_spots || 0
      };
    },

    cancelEdit() {
      this.editingId = null;
      this.editForm = {};
    },

    async saveEdit() {
      try {
        this.saving = true;
        setAuthToken(localStorage.getItem("pz_token"));

        const payload = {
          prime_location_name: (this.editForm.prime_location_name || "").trim(),
          price_per_hour: Number.parseFloat(this.editForm.price_per_hour || 0),
          address: (this.editForm.address || "").trim(),
          pin_code: (this.editForm.pin_code || "").trim(),
          number_of_spots: Number.parseInt(this.editForm.number_of_spots || 0, 10)
        };

        await api.put(`/admin/lots/${this.editingId}`, payload);

        alert("Lot updated!");
        this.loadLots();
        this.cancelEdit();
      } catch (err) {
        console.error("EDIT ERROR:", err);
        const serverMsg = err.response?.data?.msg || err.message;
        alert("Failed to update lot.\n" + serverMsg);
      } finally {
        this.saving = false;
      }
    },

    async deleteLot(id) {
      if (!confirm("Are you sure you want to delete this lot?")) return;

      try {
        setAuthToken(localStorage.getItem("pz_token"));
        await api.delete(`/admin/lots/${id}`);
        alert("Lot deleted!");
        this.loadLots();
      } catch (err) {
        console.error("DELETE ERROR:", err);
        const serverMsg = err.response?.data?.msg || err.message;
        alert("Failed to delete lot.\n" + serverMsg);
      }
    }
  }
};
</script>

<style scoped>
.card { border-radius: 10px; }
.border { font-size: 14px; }
.spinner-border { vertical-align: baseline; }
.bg-light { background: #f7fafc !important; }
</style>

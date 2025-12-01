<template>
  <div class="container py-4">
    <h3 class="mb-4">Admin — Reservations</h3>

    <div class="card mb-3 p-3 shadow-sm">
      <div class="d-flex gap-2 mb-2 align-items-center">
        <input
          v-model="q"
          @input="onSearch"
          class="form-control"
          placeholder="Search by user email, spot id or remarks"
        />
        <select v-model="filterStatus" class="form-select" style="width: 160px">
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="left">Left</option>
        </select>
        <button
          class="btn btn-outline-secondary"
          @click="fetchReservations"
          :disabled="loading"
        >
          <span
            v-if="loading"
            class="spinner-border spinner-border-sm me-2"
          ></span>
          Refresh
        </button>
      </div>

      <div v-if="msg" :class="['alert', msgType]">{{ msg }}</div>

      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th>#</th>
              <th>User</th>
              <th>Spot ID</th>
              <th>Parked At</th>
              <th>Left At</th>
              <th>Duration</th>
              <th>Cost</th>
              <th>Remarks</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length === 0">
              <td colspan="9" class="text-center text-muted">
                No reservations found.
              </td>
            </tr>

            <tr v-for="(r, idx) in paged" :key="r.id">
              <td>{{ startIndex + idx + 1 }}</td>
              <td>{{ r.user_email || r.user_id || "-" }}</td>
              <td>{{ r.spot_id }}</td>
              <td>{{ formatDate(r.parked_at) }}</td>
              <td>{{ r.left_at ? formatDate(r.left_at) : "—" }}</td>
              <td>
                {{
                  r.left_at ? formatDuration(r.parked_at, r.left_at) : "ongoing"
                }}
              </td>
              <td>{{ r.cost != null ? `₹${r.cost}` : "—" }}</td>
              <td class="text-truncate" style="max-width: 150px">
                {{ r.remarks || "" }}
              </td>
              <td class="text-end">
                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="openReservation(r)"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- pagination -->
      <div class="d-flex justify-content-between align-items-center mt-2">
        <div class="small text-muted">
          Showing {{ filtered.length }} reservations
        </div>
        <nav v-if="pages > 1" aria-label="reservations pagination">
          <ul class="pagination mb-0">
            <li :class="['page-item', { disabled: page === 1 }]">
              <a class="page-link" href="#" @click.prevent="page = page - 1"
                >Prev</a
              >
            </li>
            <li
              v-for="p in pages"
              :key="p"
              :class="['page-item', { active: p === page }]"
            >
              <a class="page-link" href="#" @click.prevent="page = p">{{
                p
              }}</a>
            </li>
            <li :class="['page-item', { disabled: page === pages }]">
              <a class="page-link" href="#" @click.prevent="page = page + 1"
                >Next</a
              >
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Reservation Modal -->
    <div class="modal fade" tabindex="-1" ref="resModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Reservation — {{ selected ? `#${selected.id}` : "" }}
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="closeModal"
            ></button>
          </div>
          <div class="modal-body">
            <div v-if="selected">
              <dl class="row">
                <dt class="col-sm-4">Reservation ID</dt>
                <dd class="col-sm-8">{{ selected.id }}</dd>
                <dt class="col-sm-4">User</dt>
                <dd class="col-sm-8">
                  {{ selected.user_email || selected.user_id }}
                </dd>
                <dt class="col-sm-4">Spot ID</dt>
                <dd class="col-sm-8">{{ selected.spot_id }}</dd>
                <dt class="col-sm-4">Parked At</dt>
                <dd class="col-sm-8">{{ formatDate(selected.parked_at) }}</dd>
                <dt class="col-sm-4">Left At</dt>
                <dd class="col-sm-8">
                  {{
                    selected.left_at
                      ? formatDate(selected.left_at)
                      : "— not left —"
                  }}
                </dd>
                <dt class="col-sm-4">Duration (sec)</dt>
                <dd class="col-sm-8">
                  {{ selected.left_at ? selected.duration_seconds : "—" }}
                </dd>
                <dt class="col-sm-4">Cost</dt>
                <dd class="col-sm-8">
                  {{ selected.cost != null ? `₹${selected.cost}` : "—" }}
                </dd>
                <dt class="col-sm-4">Remarks</dt>
                <dd class="col-sm-8">{{ selected.remarks || "—" }}</dd>
              </dl>

              <hr />
              <h6>Raw JSON</h6>
              <pre style="white-space: pre-wrap">{{ pretty(selected) }}</pre>
            </div>
            <div v-else class="text-muted">No reservation selected.</div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";

function showModal(el) {
  if (!el) return null;
  if (typeof bootstrap === "undefined" || !bootstrap.Modal) return null;
  const m = new bootstrap.Modal(el, { backdrop: "static" });
  m.show();
  return m;
}

export default {
  name: "AdminReservations",
  data() {
    return {
      reservations: [],
      loading: false,
      msg: null,
      msgType: "alert-info",
      q: "",
      filterStatus: "",
      page: 1,
      perPage: 12,
      selected: null,
      modalInstance: null,
    };
  },
  computed: {
    filtered() {
      let list = this.reservations || [];
      if (this.q) {
        const s = this.q.toLowerCase();
        list = list.filter(
          (r) =>
            (r.user_email || "").toLowerCase().includes(s) ||
            String(r.spot_id).includes(s) ||
            (r.remarks || "").toLowerCase().includes(s)
        );
      }
      if (this.filterStatus === "active") {
        list = list.filter((r) => !r.left_at);
      } else if (this.filterStatus === "left") {
        list = list.filter((r) => !!r.left_at);
      }
      return list;
    },
    pages() {
      return Math.max(1, Math.ceil(this.filtered.length / this.perPage));
    },
    paged() {
      const start = (this.page - 1) * this.perPage;
      return this.filtered.slice(start, start + this.perPage);
    },
    startIndex() {
      return (this.page - 1) * this.perPage;
    },
  },
  mounted() {
    this.fetchReservations();
  },
  methods: {
    pretty(obj) {
      try {
        return JSON.stringify(obj, null, 2);
      } catch (e) {
        return String(obj);
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return "-";

      // 1. Remove milliseconds if present
      const cleanDate = dateStr.split(".")[0];

      // 2. Split into Date and Time
      const [datePart, timePart] = cleanDate.split("T");
      if (!datePart || !timePart) return dateStr;

      // 3. Manual Format (DD-MM-YYYY, HH:MM AM/PM)
      const [year, month, day] = datePart.split("-");
      let [hour, minute] = timePart.split(":");

      hour = parseInt(hour);
      const ampm = hour >= 12 ? "PM" : "AM";
      hour = hour % 12 || 12;

      return `${day}-${month}-${year}, ${hour}:${minute} ${ampm}`;
    },
    formatDuration(start, end) {
      try {
        const s = new Date(start);
        const e = new Date(end);
        const secs = Math.round((e - s) / 1000);
        return `${secs} s`;
      } catch (e) {
        return "—";
      }
    },
    async fetchReservations() {
      this.loading = true;
      this.msg = null;
      try {
        const res = await api.get("/admin/reservations");
        // backend returns array "reservations"
        this.reservations =
          res.data && res.data.reservations
            ? res.data.reservations.map((r) => {
                // enrich with user_email if backend includes nested user info
                if (!r.user_email && r.user_id && r.user) {
                  r.user_email = r.user.email || r.user_id;
                }
                // helper: precompute duration_seconds for modal (if left_at present)
                if (r.left_at) {
                  try {
                    r.duration_seconds = Math.round(
                      (new Date(r.left_at) - new Date(r.parked_at)) / 1000
                    );
                  } catch {}
                }
                return r;
              })
            : [];
        this.msgType = "alert-info";
      } catch (err) {
        console.error("fetchReservations error:", err);
        const server = err?.response?.data;
        this.msg =
          server?.msg ??
          (typeof server === "string"
            ? server
            : "Failed to fetch reservations");
        this.msgType = "alert-danger";
      } finally {
        this.loading = false;
      }
    },
    onSearch() {
      this.page = 1;
    },
    openReservation(r) {
      this.selected = r;
      const el = this.$refs.resModal;
      if (this.modalInstance && this.modalInstance.hide)
        this.modalInstance.hide();
      this.modalInstance = showModal(el);
    },
    closeModal() {
      if (this.modalInstance && this.modalInstance.hide) {
        this.modalInstance.hide();
        this.modalInstance = null;
      }
      this.selected = null;
    },
  },
};
</script>

<style scoped>
.table-hover tbody tr:hover {
  background: rgba(0, 0, 0, 0.02);
}
pre {
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 6px;
}
</style>

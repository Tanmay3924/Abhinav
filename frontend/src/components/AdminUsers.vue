<template>
  <div class="container py-4">
    <h3 class="mb-4">Admin — Users</h3>

    <div class="card mb-4 p-3 shadow-sm">
      <div class="d-flex align-items-center gap-2 mb-2">
        <input v-model="q" @input="onSearch" class="form-control" placeholder="Search by username or email" />
        <button class="btn btn-outline-secondary" @click="fetchUsers" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Refresh
        </button>
      </div>

      <div v-if="msg" :class="['alert', msgType]">{{ msg }}</div>

      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th>#</th>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Registered</th>
              <th>Current Reservation</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length === 0">
              <td colspan="7" class="text-center text-muted">No users found.</td>
            </tr>

            <tr v-for="(u, idx) in paged" :key="u.id">
              <td>{{ startIndex + idx + 1 }}</td>
              <td>{{ u.username }}</td>
              <td>{{ u.email }}</td>
              <td><span class="badge bg-secondary">{{ u.role }}</span></td>
              <td class="small text-muted">{{ formatDate(u.created_at) }}</td>
              <td>
                <div v-if="u.current_reservation">
                  <div class="small">
                    Lot: <strong>{{ u.current_reservation.lot_name ?? u.current_reservation.lot_id }}</strong>
                  </div>
                  <div class="small">
                    Spot #: <strong>{{ u.current_reservation.spot_id }}</strong>
                  </div>
                  <div class="small text-muted">
                    Since {{ formatDate(u.current_reservation.parked_at) }}
                  </div>
                </div>
                <div v-else class="small text-muted">— none —</div>
              </td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary" @click="openUser(u)">View</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- pagination -->
      <div class="d-flex justify-content-between align-items-center mt-2">
        <div class="small text-muted">Showing {{ filtered.length }} users</div>
        <nav v-if="pages > 1" aria-label="users pagination">
          <ul class="pagination mb-0">
            <li :class="['page-item', {disabled: page === 1}]">
              <a class="page-link" href="#" @click.prevent="page = page - 1">Prev</a>
            </li>
            <li v-for="p in pages" :key="p" :class="['page-item', {active: p === page}]">
              <a class="page-link" href="#" @click.prevent="page = p">{{ p }}</a>
            </li>
            <li :class="['page-item', {disabled: page === pages}]">
              <a class="page-link" href="#" @click.prevent="page = page + 1">Next</a>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- User modal -->
    <div class="modal-body">

    <h6>Profile</h6>
    <dl class="row">
        <dt class="col-sm-3">Username</dt>
        <dd class="col-sm-9">{{ selected?.username }}</dd>

        <dt class="col-sm-3">Email</dt>
        <dd class="col-sm-9">{{ selected?.email }}</dd>

        <dt class="col-sm-3">Role</dt>
        <dd class="col-sm-9">{{ selected?.role }}</dd>

        <dt class="col-sm-3">Registered</dt>
        <dd class="col-sm-9">{{ formatDate(selected?.created_at) }}</dd>
    </dl>

    <hr />

    <h6>Current Reservation</h6>

    <div v-if="selected?.current_reservation">

        <div><strong>Spot ID:</strong> {{ selected.current_reservation.spot_id }}</div>
        <div><strong>Parked at:</strong> {{ formatDate(selected.current_reservation.parked_at) }}</div>
        <div><strong>Left at:</strong> 
        {{ selected.current_reservation.left_at ? formatDate(selected.current_reservation.left_at) : '— not left —' }}
        </div>
        <div><strong>Cost:</strong> {{ selected.current_reservation.cost ?? '—' }}</div>

        <div class="mt-2">
        <strong>Raw:</strong>
        <pre style="white-space: pre-wrap;">{{ pretty(selected.current_reservation) }}</pre>
        </div>

    </div>

    <div v-else class="text-muted">
        No active reservation.
    </div>

    </div>


  </div>
</template>

<script>
import api from "../api";

// simple helper to show bootstrap modal (no external libs)
function showModal(el) {
  if (!el) return;
  const m = new bootstrap.Modal(el, { backdrop: "static" });
  m.show();
  return m;
}

export default {
  name: "AdminUsers",
  data() {
    return {
      users: [],
      loading: false,
      msg: null,
      msgType: "alert-info",
      q: "",
      page: 1,
      perPage: 8,

      selected: null,
      modalInstance: null
    };
  },
  computed: {
    filtered() {
      if (!this.q) return this.users;
      const s = this.q.toLowerCase();
      return this.users.filter(u => (u.username||"").toLowerCase().includes(s) || (u.email||"").toLowerCase().includes(s));
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
    }
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    pretty(obj) {
      try { return JSON.stringify(obj, null, 2); } catch(e) { return String(obj); }
    },
    formatDate(dt) {
    if (!dt) return "—";
    try {
        return new Date(dt).toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
        });
    } catch (e) {
        return dt;
    }
    },

    async fetchUsers() {
      this.loading = true;
      this.msg = null;
      try {
        const res = await api.get("/admin/users");
        this.users = res.data.users || [];
        this.msgType = "alert-info";
      } catch (err) {
        console.error("fetchUsers error:", err);
        const server = err?.response?.data;
        this.msg = server?.msg ?? (typeof server === "string" ? server : "Failed to fetch users");
        this.msgType = "alert-danger";
      } finally {
        this.loading = false;
      }
    },
    onSearch() {
      this.page = 1;
    },
    openUser(u) {
      this.selected = u;
      // open bootstrap modal
      const el = this.$refs.userModal;
      if (this.modalInstance) this.modalInstance.hide();
      this.modalInstance = showModal(el);
    },
    closeModal() {
      if (this.modalInstance) {
        this.modalInstance.hide();
        this.modalInstance = null;
      }
      this.selected = null;
    }
  }
};
</script>

<style scoped>
.card { border-radius: 10px; }
.table-hover tbody tr:hover { background: rgba(0,0,0,0.02); }
pre { background: #f8f9fa; padding: .5rem; border-radius: 6px; }
</style>

<template>
  <div class="home-hero">
    <div class="overlay">
      <div class="container py-5 text-center text-white hero-content">
        <h1 class="display-5 fw-bold mb-3">ParkZone 2.0</h1>
        <p class="lead mb-4">
          Smart parking management for 4-wheelers — reserve, park, and manage with one intuitive app.
        </p>

        <div class="d-flex justify-content-center gap-2 mb-4">
          <router-link class="btn btn-lg btn-primary btn-cta" to="/register">Get Started</router-link>
          <router-link class="btn btn-lg btn-outline-light" to="/login">Sign In</router-link>
        </div>

        <div class="row features mt-5 text-start">
          <div class="col-md-4 mb-3">
            <div class="card h-100 feature-card">
              <div class="card-body">
                <h5 class="card-title">Fast Booking</h5>
                <p class="card-text small">Reserve a spot in seconds — the app auto-allocates the nearest available slot so you don’t waste time searching.</p>
              </div>
            </div>
          </div>

          <div class="col-md-4 mb-3">
            <div class="card h-100 feature-card">
              <div class="card-body">
                <h5 class="card-title">Real-time Availability</h5>
                <p class="card-text small">See live spot status and avoid surprises — know which lots are available before you arrive.</p>
              </div>
            </div>
          </div>

          <div class="col-md-4 mb-3">
            <div class="card h-100 feature-card">
              <div class="card-body">
                <h5 class="card-title">Insights & History</h5>
                <p class="card-text small">Track your parking history and view simple summaries — understand usage and costs with clear records.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Home"
};
</script>

<style scoped>
.home-hero {
  min-height: 78vh;
  background: linear-gradient(135deg,#0f172a 0%, #0b61a4 55%, #4f46e5 100%);
  display: flex;
  align-items: center;
}

.overlay {
  width: 100%;
  background: linear-gradient(rgba(6,11,26,0.45), rgba(6,11,26,0.45));
  padding: 4rem 0;
}

.hero-content { max-width: 960px; margin: 0 auto; }

.btn-cta {
  box-shadow: 0 8px 18px rgba(79,70,229,0.25);
  transform: translateY(0);
  transition: transform .18s ease, box-shadow .18s ease;
}
.btn-cta:hover { transform: translateY(-4px); box-shadow: 0 16px 30px rgba(79,70,229,0.28); }

.feature-card { border: none; border-radius: 12px; box-shadow: 0 6px 18px rgba(2,6,23,0.25); background: rgba(255,255,255,0.95); }
.feature-card .card-body { min-height: 120px; }

@media (max-width: 767px) {
  .home-hero { padding-top: 2rem; padding-bottom: 2rem; }
  .features { text-align: center; }
}
</style>

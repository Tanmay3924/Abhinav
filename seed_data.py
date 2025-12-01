from backend.app import create_app, db
from backend.app.models import ParkingLot, ParkingSpot, SPOT_AVAILABLE

app = create_app()

def seed_lots():
    with app.app_context():
        print("🌱 Seeding Parking Lots...")

        # 1. Create a Mall Parking Lot
        mall_lot = ParkingLot(
            prime_location_name="City Mall Plaza",
            address="123 Shopping Ave, Downtown",
            price_per_hour=5.0,
            number_of_spots=5,
            pin_code="10001"
        )

        # 2. Create a Beach Parking Lot
        beach_lot = ParkingLot(
            prime_location_name="Sunset Beach",
            address="45 Ocean Dr, Coastline",
            price_per_hour=8.5,
            number_of_spots=3,
            pin_code="20002"
        )

        db.session.add(mall_lot)
        db.session.add(beach_lot)
        db.session.commit()  # Commit to get IDs

        # 3. Create Spots for Mall (Lot ID will be generated)
        print(f"   Creating spots for {mall_lot.prime_location_name}...")
        for i in range(1, mall_lot.number_of_spots + 1):
            spot = ParkingSpot(lot_id=mall_lot.id, spot_number=i, status=SPOT_AVAILABLE)
            db.session.add(spot)

        # 4. Create Spots for Beach
        print(f"   Creating spots for {beach_lot.prime_location_name}...")
        for i in range(1, beach_lot.number_of_spots + 1):
            spot = ParkingSpot(lot_id=beach_lot.id, spot_number=i, status=SPOT_AVAILABLE)
            db.session.add(spot)

        db.session.commit()
        print("✅ Database populated successfully!")

if __name__ == "__main__":
    seed_lots()
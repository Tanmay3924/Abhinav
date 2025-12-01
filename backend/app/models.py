from . import db
from datetime import datetime,timedelta
from werkzeug.security import generate_password_hash, check_password_hash

def get_ist_time():
    """Returns current time in IST (UTC + 5:30)"""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

# Spot status constants
SPOT_AVAILABLE = "A"   # Available
SPOT_OCCUPIED  = "O"   # Occupied

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=get_ist_time)

    # relationships
    reservations = db.relationship("Reservation", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ParkingLot(db.Model):
    __tablename__ = "parking_lots"

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(200), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False, default=0.0)
    address = db.Column(db.String(300))
    pin_code = db.Column(db.String(20))
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=get_ist_time)

    # relationships
    spots = db.relationship("ParkingSpot", back_populates="lot", cascade="all, delete-orphan", order_by="ParkingSpot.spot_number")

    def as_dict(self, include_spots: bool=False):
        d = {
            "id": self.id,
            "prime_location_name": self.prime_location_name,
            "price_per_hour": self.price_per_hour,
            "address": self.address,
            "pin_code": self.pin_code,
            "number_of_spots": self.number_of_spots,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_spots:
            d["spots"] = [s.as_dict() for s in self.spots]
        return d

class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)  # number within lot (1..N)
    status = db.Column(db.String(1), nullable=False, default=SPOT_AVAILABLE)  # 'A' or 'O'
    vehicle_number = db.Column(db.String(50), nullable=True)  # optional last-known vehicle
    created_at = db.Column(db.DateTime, default=get_ist_time)

    # relationships
    lot = db.relationship("ParkingLot", back_populates="spots")
    reservations = db.relationship("Reservation", back_populates="spot", cascade="all, delete-orphan", order_by="Reservation.parked_at")

    __table_args__ = (
        db.UniqueConstraint('lot_id', 'spot_number', name='uq_lot_spotnumber'),
    )

    def as_dict(self, include_reservations: bool=False):
        d = {
            "id": self.id,
            "lot_id": self.lot_id,
            "spot_number": self.spot_number,
            "status": self.status,
            "vehicle_number": self.vehicle_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_reservations:
            d["reservations"] = [r.as_dict() for r in self.reservations]
        return d

class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spots.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parked_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    left_at = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=True)         # calculated when user leaves
    remarks = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)

    # relationships
    spot = db.relationship("ParkingSpot", back_populates="reservations")
    user = db.relationship("User", back_populates="reservations")

    def duration_seconds(self):
        if not self.left_at:
            return None
        return (self.left_at - self.parked_at).total_seconds()

    def as_dict(self):
        return {
            "id": self.id,
            "spot_id": self.spot_id,
            "user_id": self.user_id,
            # Add + "Z" here
            "parked_at": (self.parked_at.isoformat() + "Z") if self.parked_at else None,
            "left_at": (self.left_at.isoformat() + "Z") if self.left_at else None,
            "cost": self.cost,
            "remarks": self.remarks,
            "created_at": (self.created_at.isoformat() + "Z") if self.created_at else None
        }

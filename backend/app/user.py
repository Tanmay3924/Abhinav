from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from . import db
from .models import ParkingLot, ParkingSpot, Reservation, User, SPOT_AVAILABLE, SPOT_OCCUPIED
from . import db, cache

user_bp = Blueprint("user", __name__)

@user_bp.route("/lots", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60, key_prefix='user_view_lots')  # <--- CACHE THIS ROUTE
def view_lots():
    """View available parking lots with availability count."""
    # (Existing logic remains exactly the same)
    lots = ParkingLot.query.order_by(ParkingLot.id).all()
    output = []
    for lot in lots:
        available_count = ParkingSpot.query.filter_by(lot_id=lot.id, status=SPOT_AVAILABLE).count()
        data = lot.as_dict()
        data['available_spots'] = available_count
        output.append(data)
    
    print("--- FETCHING FROM DB (Cache Miss) ---") # Debug print to prove it works
    return jsonify({"lots": output}), 200

@user_bp.route("/status", methods=["GET"])
@jwt_required()
def current_status():
    """Check if user currently has an occupied spot."""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    # Find active reservation (where left_at is None)
    active_res = Reservation.query.filter_by(user_id=user.id, left_at=None).first()
    
    if active_res:
        spot = ParkingSpot.query.get(active_res.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        return jsonify({
            "has_active": True,
            "reservation": active_res.as_dict(),
            "spot_number": spot.spot_number,
            "lot_name": lot.prime_location_name,
            "price_per_hour": lot.price_per_hour
        }), 200
    
    return jsonify({"has_active": False}), 200

@user_bp.route("/park", methods=["POST"])
@jwt_required()
def park_vehicle():
    """
    Auto-allocation: User chooses Lot -> System picks first Available Spot.
    Updates status to Occupied (O).
    """
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    # Prevent double parking
    if Reservation.query.filter_by(user_id=user.id, left_at=None).first():
        return jsonify({"msg": "You already have an active parking spot."}), 400

    data = request.get_json()
    lot_id = data.get("lot_id")

    # 1. Find Lot
    lot = ParkingLot.query.get_or_404(lot_id)

    # 2. Find first available spot (Auto-allocation)
    spot = ParkingSpot.query.filter_by(lot_id=lot.id, status=SPOT_AVAILABLE)\
        .order_by(ParkingSpot.spot_number.asc()).first()

    if not spot:
        return jsonify({"msg": "No spots available in this lot."}), 400

    # 3. Occupy Spot
    spot.status = SPOT_OCCUPIED
    
    # 4. Create Reservation (Timestamp recorded via default=datetime.utcnow)
    new_res = Reservation(user_id=user.id, spot_id=spot.id)
    
    db.session.add(new_res)
    db.session.commit()
    cache.delete('user_view_lots')
    return jsonify({
        "msg": "Spot allocated and occupied successfully", 
        "spot_number": spot.spot_number,
        "reservation": new_res.as_dict()
    }), 201

@user_bp.route("/release", methods=["POST"])
@jwt_required()
def release_spot():
    """
    User releases the spot.
    Updates status to Available (A).
    Calculates cost.
    """
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    # Find active reservation
    reservation = Reservation.query.filter_by(user_id=user.id, left_at=None).first()
    if not reservation:
        return jsonify({"msg": "No active parking found."}), 404

    # 1. Update Reservation (Timestamp left_at)
    reservation.left_at = datetime.now()
    
    # 2. Calculate Cost
    spot = ParkingSpot.query.get(reservation.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)
    
    duration_hours = (reservation.left_at - reservation.parked_at).total_seconds() / 3600
    # Minimum 1 hour charge or exact calculation
    billable_hours = max(1, round(duration_hours, 2)) 
    cost = billable_hours * lot.price_per_hour
    
    reservation.cost = round(cost, 2)

    # 3. Release Spot
    spot.status = SPOT_AVAILABLE

    db.session.commit()
    cache.delete('user_view_lots')
    return jsonify({
        "msg": "Spot released successfully",
        "cost": reservation.cost,
        "duration_hours": billable_hours,
        "reservation": reservation.as_dict()
    }), 200

@user_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    """Track timestamps for reservation and View parking history."""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    reservations = Reservation.query.filter_by(user_id=user.id)\
        .filter(Reservation.left_at.is_not(None))\
        .order_by(Reservation.parked_at.desc()).all()
    
    output = []
    for r in reservations:
        spot = ParkingSpot.query.get(r.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        res_dict = r.as_dict()
        res_dict['lot_name'] = lot.prime_location_name
        res_dict['spot_number'] = spot.spot_number
        output.append(res_dict)

    return jsonify({"history": output}), 200

# ... existing imports ...
from sqlalchemy import func

@user_bp.route("/analytics", methods=["GET"])
@jwt_required()
def user_analytics():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    # 1. Total Stats
    total_spent = db.session.query(func.sum(Reservation.cost))\
        .filter(Reservation.user_id == user.id).scalar() or 0.0
    
    total_parkings = Reservation.query.filter_by(user_id=user.id).count()

    # 2. Chart Data: Last 5 Reservations (Cost Analysis)
    # Get last 5 completed reservations
    recent_reservations = Reservation.query.filter_by(user_id=user.id)\
        .filter(Reservation.left_at.is_not(None))\
        .order_by(Reservation.left_at.desc())\
        .limit(5).all()

    # Reverse them so the chart goes Left (Old) -> Right (New)
    recent_reservations = recent_reservations[::-1]

    labels = []
    data_points = []

    for res in recent_reservations:
        # Format date as "14 Nov"
        date_str = res.left_at.strftime("%d %b")
        labels.append(date_str)
        data_points.append(res.cost)

    return jsonify({
        "stats": {
            "total_spent": round(total_spent, 2),
            "total_parkings": total_parkings
        },
        "chart": {
            "labels": labels,
            "data": data_points
        }
    }), 200
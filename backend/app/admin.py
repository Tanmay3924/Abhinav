# backend/app/admin.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from . import db
from .models import ParkingLot, ParkingSpot, SPOT_AVAILABLE, SPOT_OCCUPIED
import traceback
from .models import User, Reservation
# ... existing imports ...
from sqlalchemy import func
from datetime import datetime, timedelta
from . import db, cache
from .tasks import export_reservations_csv

admin_bp = Blueprint("admin", __name__)


def admin_only():
    """
    Support both old tokens (identity was a dict) and new tokens
    (identity is string; role is in additional_claims).
    """
    identity = get_jwt_identity()
    role = None

    # If token identity used to be a dict, keep compatibility
    if isinstance(identity, dict):
        role = identity.get("role")
    else:
        claims = get_jwt() or {}
        # role might be in top-level claims or inside 'user' claim
        role = claims.get("role") or (claims.get("user") or {}).get("role")

    if not role or role != "admin":
        return jsonify({"msg": "Admins only"}), 403
    return None


# ----------------------------
#  CREATE A PARKING LOT
# ----------------------------
@admin_bp.route("/lots", methods=["POST"])
@jwt_required()
def create_lot():
    err = admin_only()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({"msg": "No JSON payload received"}), 400

    # --- Validation helpers ---
    def must_be_string(field_name, required=True):
        val = data.get(field_name)
        if val is None:
            if required:
                raise ValueError(f"{field_name} is required and must be a string")
            return None
        if isinstance(val, str):
            return val.strip()
        if isinstance(val, (int, float, bool)):
            return str(val)
        raise ValueError(f"{field_name} must be a string; got {type(val).__name__}: {val!r}")

    def must_be_int(field_name, required=True, minimum=None):
        val = data.get(field_name)
        if val is None:
            if required:
                raise ValueError(f"{field_name} is required and must be an integer")
            return None
        if isinstance(val, int):
            num = val
        elif isinstance(val, float):
            num = int(val)
        elif isinstance(val, str):
            if val.strip() == "":
                raise ValueError(f"{field_name} must be an integer")
            try:
                num = int(float(val))
            except Exception:
                raise ValueError(f"{field_name} must be an integer; got: {val!r}")
        else:
            raise ValueError(f"{field_name} must be an integer; got {type(val).__name__}")
        if minimum is not None and num < minimum:
            raise ValueError(f"{field_name} must be >= {minimum}")
        return num

    def must_be_float(field_name, required=True, minimum=None):
        val = data.get(field_name)
        if val is None:
            if required:
                raise ValueError(f"{field_name} is required and must be a number")
            return None
        if isinstance(val, (int, float)):
            num = float(val)
        elif isinstance(val, str):
            if val.strip() == "":
                raise ValueError(f"{field_name} must be a number")
            try:
                num = float(val)
            except Exception:
                raise ValueError(f"{field_name} must be a number; got: {val!r}")
        else:
            raise ValueError(f"{field_name} must be a number; got {type(val).__name__}")
        if minimum is not None and num < minimum:
            raise ValueError(f"{field_name} must be >= {minimum}")
        return num

    # --- Validate and coerce fields ---
    try:
        prime_location_name = must_be_string("prime_location_name")
        # optional fields
        address = must_be_string("address", required=False)
        pin_code = must_be_string("pin_code", required=False)
        number_of_spots = must_be_int("number_of_spots", minimum=1)
        price_per_hour = must_be_float("price_per_hour", minimum=0)
    except ValueError as ve:
        return jsonify({"msg": str(ve)}), 422

    # --- Create lot and spots in DB ---
    try:
        lot = ParkingLot(
            prime_location_name=prime_location_name,
            address=address,
            pin_code=pin_code,
            number_of_spots=number_of_spots,
            price_per_hour=price_per_hour,
        )

        db.session.add(lot)
        db.session.flush()  # ensures lot.id is available for spots

        # create spots numbered 1..N (note: models use 'spot_number')
        for i in range(1, number_of_spots + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=i,
                status=SPOT_AVAILABLE
            )
            db.session.add(spot)

        db.session.commit()

        # Return the created lot with spots
        return jsonify({"msg": "lot created", "lot": lot.as_dict(include_spots=True)}), 201

    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("Exception creating lot: %s\n%s", exc, traceback.format_exc())
        return jsonify({"msg": "Internal server error creating lot"}), 500


# ----------------------------
#  LIST LOTS
# ----------------------------
@admin_bp.route("/lots", methods=["GET"])
@jwt_required()
def list_lots():
    err = admin_only()
    if err:
        return err

    include = request.args.get("include_spots")
    include_spots = include == "1"

    lots = ParkingLot.query.order_by(ParkingLot.id.asc()).all()
    return jsonify({"lots": [lot.as_dict(include_spots=include_spots) for lot in lots]}), 200


# ----------------------------
#  UPDATE LOT
# ----------------------------
@admin_bp.route("/lots/<int:lot_id>", methods=["PUT"])
@jwt_required()
def update_lot(lot_id):
    err = admin_only()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    try:
        lot = ParkingLot.query.get_or_404(lot_id)

        if "prime_location_name" in data:
            lot.prime_location_name = str(data["prime_location_name"]).strip()

        if "address" in data:
            lot.address = str(data["address"]).strip()

        if "pin_code" in data:
            lot.pin_code = str(data["pin_code"]).strip()

        if "price_per_hour" in data:
            lot.price_per_hour = float(data["price_per_hour"])

        if "number_of_spots" in data:
            new_total = int(data["number_of_spots"])

            existing_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()

            if new_total > existing_spots:
                # add new spots
                for i in range(existing_spots + 1, new_total + 1):
                    db.session.add(ParkingSpot(
                        lot_id=lot.id,
                        spot_number=i,
                        status=SPOT_AVAILABLE
                    ))
            elif new_total < existing_spots:
                # find spots that would be removed (spot_number > new_total)
                to_remove = ParkingSpot.query.filter(
                    ParkingSpot.lot_id == lot.id,
                    ParkingSpot.spot_number > new_total
                ).order_by(ParkingSpot.spot_number.desc()).all()

                # if any of these are occupied, refuse the change
                occupied = [s for s in to_remove if s.status == SPOT_OCCUPIED]
                if occupied:
                    return jsonify({"msg": "Cannot reduce spots: some spots to remove are occupied"}), 400

                # safe to delete (delete rows one-by-one to keep ORM consistent)
                for s in to_remove:
                    db.session.delete(s)

            lot.number_of_spots = new_total

        db.session.commit()

        return jsonify({"msg": "lot updated", "lot": lot.as_dict(include_spots=True)}), 200

    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("ERROR updating lot: %s\n%s", exc, traceback.format_exc())
        return jsonify({"msg": "Internal Server Error"}), 500


# ----------------------------
#  DELETE LOT
# ----------------------------
@admin_bp.route("/lots/<int:lot_id>", methods=["DELETE"])
@jwt_required()
def delete_lot(lot_id):
    err = admin_only()
    if err:
        return err

    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        # check for any occupied spot
        occ = ParkingSpot.query.filter_by(lot_id=lot.id, status=SPOT_OCCUPIED).first()
        if occ:
            return jsonify({"msg": "Cannot delete lot: some spots are occupied"}), 400
        db.session.delete(lot)
        db.session.commit()
        return jsonify({"msg": "lot deleted"}), 200
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("ERROR deleting lot: %s\n%s", exc, traceback.format_exc())
        return jsonify({"msg":"Internal Server Error"}), 500

    
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    err = admin_only()
    if err:
        return err

    users = User.query.order_by(User.id).all()
    out = []
    for u in users:
        last = Reservation.query.filter_by(user_id=u.id).order_by(Reservation.parked_at.desc()).first()
        res_obj = last.as_dict() if last and not last.left_at else None
        out.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "current_reservation": res_obj
        })
    return jsonify({"users": out}), 200       

@admin_bp.route("/lots/<int:lot_id>", methods=["GET"])
@jwt_required()
def get_lot(lot_id):
    err = admin_only()
    if err:
        return err

    include = request.args.get("include_spots")
    include_spots = include == "1"

    lot = ParkingLot.query.get_or_404(lot_id)
    return jsonify({"lot": lot.as_dict(include_spots=include_spots)}), 200

@admin_bp.route("/lots/<int:lot_id>/spots", methods=["GET"])
@jwt_required()
def list_spots(lot_id):
    err = admin_only()
    if err:
        return err

    lot = ParkingLot.query.get_or_404(lot_id)
    return jsonify({"spots": [s.as_dict() for s in lot.spots]}), 200

@admin_bp.route("/reservations", methods=["GET"])
@jwt_required()
def list_reservations():
    err = admin_only()
    if err:
        return err

    try:
        rows = Reservation.query.order_by(Reservation.parked_at.desc()).limit(500).all()
        out = []
        for r in rows:
            obj = r.as_dict()
            # attach user email (if available)
            try:
                u = User.query.get(r.user_id)
                if u:
                    obj["user_email"] = u.email
            except Exception:
                pass
            # attach lot_name if possible
            try:
                sp = ParkingSpot.query.get(r.spot_id)
                if sp:
                    lot = ParkingLot.query.get(sp.lot_id)
                    if lot:
                        obj["lot_name"] = lot.prime_location_name
            except Exception:
                pass
            out.append(obj)
        return jsonify({"reservations": out}), 200
    except Exception:
        current_app.logger.exception("Error listing reservations")
        return jsonify({"msg": "Internal server error"}), 500

# ----------------------------
#  ANALYTICS DASHBOARD DATA
# ----------------------------
@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
@cache.cached(timeout=300, key_prefix='admin_stats')
def get_analytics():
    err = admin_only()
    if err: return err

    try:
        # 1. Current Occupancy Stats
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status=SPOT_OCCUPIED).count()
        available_spots = total_spots - occupied_spots

        # 2. Total Revenue (Lifetime)
        total_revenue = db.session.query(func.sum(Reservation.cost)).scalar() or 0.0

        # 3. Revenue Last 7 Days (Bar Chart Data)
        # We fetch data in Python to avoid SQLite date-string complexities
        today = datetime.now()
        seven_days_ago = today - timedelta(days=6) # 6 days ago + today = 7 days
        
        recent_reservations = Reservation.query.filter(
            Reservation.left_at >= seven_days_ago
        ).all()

        # Initialize dictionary for last 7 days: { "DD-MM": 0.0, ... }
        daily_revenue = {}
        for i in range(7):
            d = seven_days_ago + timedelta(days=i)
            key = d.strftime("%d-%m") # e.g., "14-11"
            daily_revenue[key] = 0.0

        # Fill with actual data
        for res in recent_reservations:
            if res.left_at and res.cost:
                key = res.left_at.strftime("%d-%m")
                if key in daily_revenue:
                    daily_revenue[key] += res.cost

        return jsonify({
            "occupancy": {
                "total": total_spots,
                "occupied": occupied_spots,
                "available": available_spots
            },
            "revenue": {
                "total_lifetime": round(total_revenue, 2),
                "daily_labels": list(daily_revenue.keys()),
                "daily_values": list(daily_revenue.values())
            }
        }), 200

    except Exception as exc:
        current_app.logger.error("Analytics Error: %s", exc)
        return jsonify({"msg": "Error fetching analytics"}), 500
@admin_bp.route("/export-csv", methods=["POST"])
@jwt_required()
def trigger_csv_export():
    try:
        err = admin_only()
        if err: 
            return err

        identity = get_jwt_identity()
        email = identity if isinstance(identity, str) else identity.get("email")

        # Debug print
        print("Export triggered by:", email)

        task = export_reservations_csv.delay(email)

        return jsonify({"msg": "CSV Export started!", "task_id": task.id}), 202

    except Exception as e:
        print("EXPORT CSV ERROR:", e)
        import traceback; traceback.print_exc()
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500

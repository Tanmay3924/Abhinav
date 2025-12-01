# backend/app/public.py
from flask import Blueprint, request, jsonify, current_app
from .models import ParkingLot
from . import db

public_bp = Blueprint("public", __name__)

@public_bp.route("/lots", methods=["GET"])
def list_lots_public():
    """Public endpoint for users to list parking lots.
       Query param: include_spots=1 to include spot list.
    """
    include = request.args.get("include_spots")
    include_spots = include == "1"
    try:
        lots = ParkingLot.query.order_by(ParkingLot.id.asc()).all()
        return jsonify({"lots": [l.as_dict(include_spots=include_spots) for l in lots]}), 200
    except Exception:
        current_app.logger.exception("Error listing lots (public)")
        return jsonify({"msg": "Internal server error"}), 500


@public_bp.route("/lots/<int:lot_id>", methods=["GET"])
def get_lot_public(lot_id):
    include = request.args.get("include_spots")
    include_spots = include == "1"
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        return jsonify({"lot": lot.as_dict(include_spots=include_spots)}), 200
    except Exception:
        current_app.logger.exception("Error getting lot (public)")
        return jsonify({"msg": "Internal server error"}), 500

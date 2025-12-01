# backend/app/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"msg": "username, email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "email already registered"}), 400

    user = User(username=username, email=email, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "user registered", "user": user.as_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "invalid credentials"}), 401

    # Use a string identity (sub) to avoid "Subject must be a string"
    # Put user metadata into additional_claims so server can read role/id later
    claims = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    access_token = create_access_token(identity=str(user.email), additional_claims=claims)

    identity_for_response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    return jsonify({"access_token": access_token, "user": identity_for_response}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    identity = get_jwt_identity()
    return jsonify({"user": identity}), 200

from flask import Blueprint, request, jsonify, make_response
from models.user import register_user, authenticate_user, verify_token, refresh_user_token
import config

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not (username and email and password):
        return jsonify({"error": "All fields are required"}), 400

    result = register_user(username, email, password)
    return jsonify(result), 201 if result.get("success") else 400

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not (email and password):
        return jsonify({"error": "Email and password are required"}), 400

    access_token, refresh_token = authenticate_user(email, password)
    if not access_token:
        return jsonify({"error": "Invalid credentials"}), 401

    # Set cookies with SameSite=None for cross-origin requests
    response = make_response(jsonify({"success": True, "message": "Login successful"}))
    response.set_cookie(config.COOKIE_NAME, access_token, httponly=True, secure=True, samesite="None")
    response.set_cookie(config.REFRESH_TOKEN_NAME, refresh_token, httponly=True, secure=True, samesite="None", max_age=60*60*24*int(config.REFRESH_EXPIRY_DAYS))
    return response

@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"success": True, "message": "Logged out successfully"}))
    response.delete_cookie(config.COOKIE_NAME, samesite="None", secure=True)
    response.delete_cookie(config.REFRESH_TOKEN_NAME, samesite="None", secure=True)
    return response

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    refresh_token = request.cookies.get(config.REFRESH_TOKEN_NAME)
    if not refresh_token:
        return jsonify({"error": "No refresh token provided"}), 401

    new_access_token, new_refresh_token = refresh_user_token(refresh_token)
    if not new_access_token:
        return jsonify({"error": "Invalid refresh token"}), 401

    # Set new tokens with SameSite=None for cross-origin requests
    response = make_response(jsonify({"success": True}))
    response.set_cookie(config.COOKIE_NAME, new_access_token, httponly=True, secure=True, samesite="None")
    response.set_cookie(config.REFRESH_TOKEN_NAME, new_refresh_token, httponly=True, secure=True, samesite="None", max_age=60*60*24*int(config.REFRESH_EXPIRY_DAYS))
    return response

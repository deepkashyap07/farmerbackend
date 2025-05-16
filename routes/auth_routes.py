from flask import Blueprint, request, jsonify, make_response
from models.user import register_user, authenticate_user, refresh_user_token
import config
import os

auth_bp = Blueprint("auth", __name__)

# Determine if the app is running in production

def set_auth_cookies(response, access_token, refresh_token):
    # Set access token cookie
    response.set_cookie(
        key=config.COOKIE_NAME,
        value=access_token,
        max_age=60 * 15,      # 15 minutes or your token expiry
        path='/',
         secure=True,          # REQUIRED for cross-origin cookies
        samesite="None"
    )
    # Set refresh token cookie
    response.set_cookie(
        key=config.REFRESH_TOKEN_NAME,
        value=refresh_token,
        max_age=60 * 60 * 24 *7,  # e.g., 7 days
        path='/',
        secure=True,          # REQUIRED for cross-origin cookies
        samesite="None"
        
    )
    return response

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not (username and email and password):
        return jsonify({"error": "All fields are required"}), 400

    result = register_user(username, email, password)
    if not result.get("success"):
        return jsonify(result), 400

    # Generate tokens after successful registration
    access_token, refresh_token = authenticate_user(email, password)
    response = make_response(jsonify({"success": True, "message": "Registration successful"}))
    response = set_auth_cookies(response, access_token, refresh_token)
    return response

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

    response = make_response(jsonify({"success": True, "message": "Login successful"}))
    response = set_auth_cookies(response, access_token, refresh_token)
    return response

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    refresh_token = request.cookies.get(config.REFRESH_TOKEN_NAME)

    if not refresh_token:
        return jsonify({"error": "No refresh token provided"}), 401


    new_access_token, new_refresh_token = refresh_user_token(refresh_token)
    if not new_access_token:
        return jsonify({"error": "Invalid refresh token"}), 401

    response = make_response(jsonify({"success": True, "message": "Token refreshed"}))
    response = set_auth_cookies(response, new_access_token, new_refresh_token)
    return response

@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"success": True, "message": "Logged out successfully"}))
    response.delete_cookie(config.COOKIE_NAME, samesite="None" , path='/')
    response.delete_cookie(config.REFRESH_TOKEN_NAME, samesite="None" , path='/')
    return response

from flask import request, jsonify
from functools import wraps
from models.user import verify_token
import config

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Extract token from the cookie
            token = request.cookies.get(config.COOKIE_NAME)
            if not token:
                return jsonify({"error": "Authentication token is missing"}), 401
            
            # Verify the token
            user_id = verify_token(token)
            if not user_id:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            # Attach the user ID to the request context for downstream use
            request.user_id = user_id
            
            return func(*args, **kwargs)
        
        except Exception as e:
            print(f"Authentication error: {e}")
            return jsonify({"error": "Authentication failed"}), 500
    
    return wrapper

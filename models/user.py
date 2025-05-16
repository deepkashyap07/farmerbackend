from database import db
from bcrypt import hashpw, gensalt, checkpw
from itsdangerous import URLSafeSerializer, BadSignature
from utils.validation import validate_email
from datetime import datetime, timedelta
import config
import uuid

serializer = URLSafeSerializer(config.SECRET_KEY)

def register_user(username, email, password):
    try:
        # Validate email
        if not validate_email(email):
            return {"error": "Invalid email address"}

        # Check if user already exists
        if db.users.find_one({"email": email}):
            return {"error": "User already exists"}

        # Hash password
        hashed_password = hashpw(password.encode("utf-8"), gensalt())

        # Generate initial refresh token
        refresh_token = str(uuid.uuid4())

        # Insert user
        user_id = db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password,
            "refresh_token": refresh_token
        }).inserted_id

        return {"success": True, "message": "User registered successfully", "user_id": str(user_id)}
    
    except Exception as e:
        print(f"Database error during registration: {e}")
        return {"error": "Database error"}

def authenticate_user(email, password):
    try:
        user = db.users.find_one({"email": email})
        if not user or not checkpw(password.encode("utf-8"), user["password"]):
            return None, None
        
        # Generate tokens
        access_token = generate_access_token(str(user["_id"]))
        refresh_token = user.get("refresh_token")
        
        # If refresh token is missing, generate a new one
        if not refresh_token:
            refresh_token = str(uuid.uuid4())
            db.users.update_one({"_id": user["_id"]}, {"$set": {"refresh_token": refresh_token}})
        
        return access_token, refresh_token
    
    except Exception as e:
        print(f"Database error during authentication: {e}")
        return None, None

def generate_access_token(user_id):
    try:
        expiry_time = datetime.utcnow() + timedelta(seconds=int(config.JWT_EXPIRY_SECONDS))
        token_data = {
            "user_id": user_id,
            "exp": expiry_time.timestamp()
        }
        return serializer.dumps(token_data)
    except Exception as e:
        print(f"Token generation error: {e}")
        return None

def verify_token(token):
    try:
        data = serializer.loads(token)
        if datetime.utcnow().timestamp() > data.get("exp"):
            return None  # Token expired
        return data.get("user_id")
    except BadSignature as e:
        print(f"Invalid token signature: {e}")
        return None

def refresh_user_token(refresh_token):
    try:
        user = db.users.find_one({"refresh_token": refresh_token})
        if not user:
            return None, None
        
        # Generate new tokens
        new_access_token = generate_access_token(str(user["_id"]))
        new_refresh_token = str(uuid.uuid4())
        
        # Update user with the new refresh token
        db.users.update_one({"_id": user["_id"]}, {"$set": {"refresh_token": new_refresh_token}})
        
        return new_access_token, new_refresh_token
    
    except Exception as e:
        print(f"Database error during refresh: {e}")
        return None, None

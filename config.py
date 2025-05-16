import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
COOKIE_NAME = os.getenv("COOKIE_NAME", "auth_token")
REFRESH_TOKEN_NAME = os.getenv("REFRESH_TOKEN_NAME", "refresh_token")
REFRESH_EXPIRY_DAYS = int(os.getenv("REFRESH_EXPIRY_DAYS", "7"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")
JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY_SECONDS", "3600"))



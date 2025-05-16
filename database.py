from pymongo import MongoClient
import dns
import config

print("MONGO_URI from config:", config.MONGO_URI)  # Debug print

try:
    client = MongoClient(config.MONGO_URI)
    db = client.get_database("crop_userdb")
    print(db)
    print("Connection successful:", db.list_collection_names())
except Exception as e:
    print("Connection failed:", e)
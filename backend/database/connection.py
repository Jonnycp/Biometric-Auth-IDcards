import os
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

_client = None

def getClient() -> MongoClient:
    global _client
    if _client is None:
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI non è impostato nel .env")
        
        _client = MongoClient(MONGODB_URI)
    return _client

def getDatabase() -> Database:
    client = getClient()
    return client.get_default_database()

def getUsersCollection() -> Collection:
    db = getDatabase()
    return db.get_collection("users")
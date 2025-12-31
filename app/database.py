from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client.get_database()
        print("✅ Connected to MongoDB successfully")
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("✅ Closed MongoDB connection")

def get_database():
    return db
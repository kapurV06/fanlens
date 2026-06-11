import os
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client["fanlens"]
    print("Connected to MongoDB Atlas")

async def close_db():
    global client
    if client:
        client.close()

def get_db():
    return db
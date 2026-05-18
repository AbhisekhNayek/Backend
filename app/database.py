from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Async MongoDB client setup
client = AsyncIOMotorClient(settings.mongo_uri)

# Retrieve the default database (e.g. Docton_App) specified in the URI
db = client.get_default_database()

async def connect_db():
    try:
        # Ping database to verify connection
        await client.admin.command('ping')
        print(f"[OK] MongoDB Connected: {client.nodes}")
    except Exception as e:
        print(f"[ERROR] MongoDB Connection Failed: {e}")
        raise e


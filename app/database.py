from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.logger import logger

# Async MongoDB client setup
client = AsyncIOMotorClient(settings.mongo_uri)

# Retrieve the default database (e.g. Docton_App) specified in the URI
db = client.get_default_database()

async def connect_db():
    try:
        # Ping database to verify connection
        database = client[settings.mongo_db_name]
        logger.info(f"MongoDB Connected: {client.nodes}")
        
        # Performance Optimization: Ensure background indexes on key collections
        await database.users.create_index("email", unique=True, background=True)
        await database.doctors.create_index("email", unique=True, background=True)
        await database.nurses.create_index("email", unique=True, background=True)
        
        # Ensure fast notifications retrieval by recipient and creation time
        await database.notifications.create_index([("recipientId", 1), ("createdAt", -1)], background=True)
        await database.notifications.create_index("recipientRole", background=True)
        
        logger.info("Database Indexes optimized and ensured successfully.")
    except Exception as e:
        logger.error(f"MongoDB Connection Failed or Index optimization failed: {e}")
        raise e

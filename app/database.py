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
        db = client[settings.mongo_db_name]
        logger.info(f"MongoDB Connected: {client.nodes}")
    except Exception as e:
        logger.error(f"MongoDB Connection Failed: {e}")
        raise e

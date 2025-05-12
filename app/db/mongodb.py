from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_to_database(cls):
        """Connect to MongoDB database"""
        if cls.client is None:
            try:
                cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
                logger.info("Connected to MongoDB")
            except ConnectionFailure as e:
                logger.error(f"Could not connect to MongoDB: {e}")
                raise e
    
    @classmethod
    async def close_database_connection(cls):
        """Close MongoDB connection"""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            logger.info("Closed connection with MongoDB")
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls.client is None:
            raise ConnectionError("MongoDB connection not established")
        return cls.client[settings.MONGODB_NAME]

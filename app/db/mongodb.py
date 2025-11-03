"""MongoDB async client and connection management."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoDB:
    """MongoDB connection manager with async support."""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_to_database(cls) -> None:
        """Establish connection to MongoDB database.

        Creates a connection pool and initializes the database client.
        """
        try:
            logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")

            cls.client = AsyncIOMotorClient(
                settings.mongodb_url,
                minPoolSize=settings.mongodb_min_pool_size,
                maxPoolSize=settings.mongodb_max_pool_size,
            )

            cls.database = cls.client[settings.mongodb_db_name]

            # Test the connection
            await cls.client.admin.command("ping")

            logger.info(
                f"Successfully connected to MongoDB database: {settings.mongodb_db_name}"
            )

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    @classmethod
    async def init_beanie_models(cls, document_models: list) -> None:
        """Initialize Beanie ODM with document models.

        Args:
            document_models: List of Beanie document model classes
        """
        try:
            if cls.database is None:
                raise RuntimeError("Database not connected. Call connect_to_database first.")

            await init_beanie(
                database=cls.database,
                document_models=document_models
            )

            logger.info(f"Initialized Beanie with {len(document_models)} document models")

        except Exception as e:
            logger.error(f"Failed to initialize Beanie models: {str(e)}")
            raise

    @classmethod
    async def close_database_connection(cls) -> None:
        """Close the database connection and cleanup resources."""
        try:
            if cls.client is not None:
                cls.client.close()
                logger.info("MongoDB connection closed successfully")

        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
            raise

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get the database instance.

        Returns:
            AsyncIOMotorDatabase instance

        Raises:
            RuntimeError: If database is not connected
        """
        if cls.database is None:
            raise RuntimeError("Database not connected. Call connect_to_database first.")

        return cls.database

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection from the database.

        Args:
            collection_name: Name of the collection

        Returns:
            AsyncIOMotorCollection instance
        """
        database = cls.get_database()
        return database[collection_name]


# Singleton instance
db = MongoDB()

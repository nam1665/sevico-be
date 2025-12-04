from pymongo import MongoClient
from pymongo.database import Database
from contextlib import asynccontextmanager
from typing import Optional
from app.config.settings import get_settings


class MongoDatabase:
    """MongoDB connection manager."""
    
    _instance: Optional['MongoDatabase'] = None
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDatabase, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Initialize MongoDB connection."""
        if self._client is None:
            settings = get_settings()
            
            # Build MongoDB URI with authentication
            if settings.mongodb_username and settings.mongodb_password:
                mongodb_uri = (
                    f"mongodb://{settings.mongodb_username}:{settings.mongodb_password}"
                    f"@{settings.mongodb_host}:{settings.mongodb_port}"
                    f"/?authSource={settings.mongodb_auth_source}"
                )
            else:
                mongodb_uri = f"mongodb://{settings.mongodb_host}:{settings.mongodb_port}"
            
            self._client = MongoClient(mongodb_uri)
            self._database = self._client[settings.mongodb_db_name]
            # Verify connection
            self._client.admin.command('ping')
            print(f"Connected to MongoDB: {settings.mongodb_db_name}")
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._database = None
            print("Disconnected from MongoDB")
    
    def get_database(self) -> Database:
        """Get the database instance."""
        if self._database is None:
            self.connect()
        return self._database
    
    def get_collection(self, collection_name: str):
        """Get a specific collection."""
        return self.get_database()[collection_name]


# Singleton instance
db = MongoDatabase()


def get_db() -> Database:
    """Dependency injection for database."""
    return db.get_database()

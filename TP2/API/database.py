import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

# MongoDB connection settings
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB2')
COLLECTION_NAME = 'cleaned'

# Global client variable
mongodb_client = None
database = None
collection = None


def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    global mongodb_client, database, collection
    
    try:
        if not MONGO_URI:
            raise ValueError("MONGO_URI not found in environment variables")
        
        if not DB_NAME:
            raise ValueError("DB2 (database name) not found in environment variables")
        
        print(f"🔄 Connecting to MongoDB Atlas...")
        mongodb_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        mongodb_client.admin.command('ping')
        
        # Get database and collection
        database = mongodb_client[DB_NAME]
        collection = database[COLLECTION_NAME]
        
        print(f"✅ Connected to MongoDB Atlas!")
        print(f"   Database: {DB_NAME}")
        print(f"   Collection: {COLLECTION_NAME}")
        
        return collection
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise


def close_mongodb_connection():
    """Close MongoDB connection"""
    global mongodb_client
    
    if mongodb_client:
        mongodb_client.close()
        print("✅ MongoDB connection closed")


def get_collection():
    """Get MongoDB collection instance"""
    global collection
    
    if collection is None:
        connect_to_mongodb()
    
    return collection

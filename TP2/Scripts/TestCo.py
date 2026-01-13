import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file
# Load from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        # Get connection string from environment variable
        mongo_uri = os.getenv('MONGO_URI')
        
        if not mongo_uri:
            print("❌ Error: MONGO_URI not found in .env file")
            return None
        
        print("🔄 Connecting to MongoDB Atlas...")
        
        # Create a MongoClient with a timeout
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Get database information
        db_names = client.list_database_names()
        print(f"\n📊 Available databases: {db_names}")
        
        return client
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        return None
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server selection timeout: {e}")
        print("   Check your connection string and network connection")
        return None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None

def main():
    """Test MongoDB connection"""
    print("=" * 50)
    print("    MongoDB Atlas Connection Test")
    print("=" * 50)
    
    client = connect_mongodb()
    
    if client:
        # Close the connection
        client.close()
        print("\n✅ Connection test successful!")
        print("   MongoDB connection closed.")
    else:
        print("\n❌ Connection test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

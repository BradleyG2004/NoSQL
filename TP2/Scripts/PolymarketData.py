import os
import sys
import requests
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

# Polymarket API URL
POLYMARKET_API_URL = os.getenv('POLYMARKET_API_URL')

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        mongo_uri = os.getenv('MONGO_URI')
        
        if not mongo_uri:
            print("❌ Error: MONGO_URI not found in .env file")
            return None
        
        print("🔄 Connecting to MongoDB Atlas...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        return client
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ Connection error: {e}")
        return None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None

def fetch_polymarket_data(limit=100):
    """
    Fetch data from Polymarket API
    
    Args:
        limit (int): Number of events to fetch (default: 100)
    """
    all_items = []
    
    print("\n📊 Starting to fetch data from Polymarket API...")
    print(f"   (Limit: {limit} events)")
    
    try:
        # Build URL with parameters
        params = {
            'limit': limit,
            'offset': 0
        }
        
        print(f"\n📄 Fetching events...")
        
        # Make the API request
        response = requests.get(POLYMARKET_API_URL, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Polymarket API returns a list of events directly
        if isinstance(data, list):
            all_items = data
            print(f"   ✓ Retrieved {len(all_items)} events")
        else:
            print(f"   ⚠️  Unexpected response format")
            return None
        
        print("\n✅ Data retrieval completed!")
                
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted by user! Collected {len(all_items)} items so far.")
        print("   Will proceed to insert what has been collected...")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching data from API: {e}")
        if all_items:
            print(f"   Will proceed with {len(all_items)} items already collected")
        else:
            return None
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if all_items:
            print(f"   Will proceed with {len(all_items)} items already collected")
        else:
            return None
    
    return all_items

def insert_to_mongodb(client, data, db_name=os.getenv('DB2'), collection_name='polymarket'):
    """Insert data into MongoDB collection"""
    try:
        # Get database and collection
        db = client[db_name]
        collection = db[collection_name]
        
        print(f"\n💾 Inserting data into '{db_name}.{collection_name}'...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        existing_count = collection.count_documents({})
        if existing_count > 0:
            print(f"   ⚠️  Collection already contains {existing_count} documents")
            choice = input("   Delete existing data? (y/n): ").lower()
            if choice == 'y':
                collection.delete_many({})
                print("   ✓ Existing data deleted")
        
        # Insert data in batches for better performance
        if data:
            batch_size = 1000
            total_inserted = 0
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                result = collection.insert_many(batch)
                total_inserted += len(result.inserted_ids)
                print(f"   ✓ Inserted batch {i//batch_size + 1}: {total_inserted}/{len(data)} documents")
            
            print(f"\n✅ Successfully inserted {total_inserted} documents!")
            
            # Show some stats
            print(f"\n📊 Collection stats:")
            print(f"   - Database: {db_name}")
            print(f"   - Collection: {collection_name}")
            print(f"   - Total documents: {collection.count_documents({})}")
            
        else:
            print("⚠️  No data to insert")
            
    except Exception as e:
        print(f"❌ Error inserting data: {e}")

def main():
    """Main function - Fetch and load Polymarket data"""
    print("=" * 50)
    print("    Polymarket Data Loader")
    print("=" * 50)
    
    # Connect to MongoDB
    client = connect_mongodb()
    
    if not client:
        print("\n❌ Cannot proceed without MongoDB connection")
        sys.exit(1)
    
    # Fetch 100 events
    limit = 100
    print(f"\n📌 Configured to fetch {limit} events")
    
    # Fetch data from Polymarket API
    data = fetch_polymarket_data(limit=limit)
    
    if data:
        # Insert data into MongoDB
        insert_to_mongodb(client, data)
    else:
        print("\n⚠️  No data retrieved from Polymarket API")
    
    # Close the connection
    client.close()
    print("\n✅ MongoDB connection closed")

if __name__ == "__main__":
    main()

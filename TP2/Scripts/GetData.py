
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

# Rijksmuseum Search API URL
RIJKSMUSEUM_API_URL = os.getenv('RIJKSMUSEUM_API_URL')

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

def fetch_rijksmuseum_data(max_pages=None):
    """
    Fetch data from Rijksmuseum Search API with pagination
    
    Args:
        max_pages (int, optional): Maximum number of pages to fetch. None = all pages
    """
    all_items = []
    current_url = RIJKSMUSEUM_API_URL
    page_count = 0
    
    print("\n🎨 Starting to fetch data from Rijksmuseum API...")
    if max_pages:
        print(f"   (Limited to {max_pages} pages = {max_pages * 100} items max)")
    
    try:
        while current_url:
            page_count += 1
            
            # Check if we've reached the limit
            if max_pages and page_count > max_pages:
                print(f"\n⚠️  Reached maximum page limit ({max_pages} pages)")
                break
            
            print(f"\n📄 Fetching page {page_count}...")
            
            # Make the API request
            response = requests.get(current_url, timeout=30)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract items from current page
            items = data.get('orderedItems', [])
            all_items.extend(items)
            
            # Get total items info
            total_items = data.get('partOf', {}).get('totalItems', 0)
            print(f"   ✓ Retrieved {len(items)} items (Total collected: {len(all_items)}/{total_items})")
            
            # Get next page URL
            next_page = data.get('next')
            if next_page:
                current_url = next_page.get('id')
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
            else:
                current_url = None
                print("\n✅ All pages retrieved!")
                
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

def insert_to_mongodb(client, data, db_name=os.getenv('DB'), collection_name='rijksmuseum'):
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
    """Main function - Fetch and load Rijksmuseum data"""
    print("=" * 50)
    print("    Rijksmuseum Data Loader")
    print("=" * 50)
    
    # Connect to MongoDB
    client = connect_mongodb()
    
    if not client:
        print("\n❌ Cannot proceed without MongoDB connection")
        sys.exit(1)
    
    # Fetch only 1 page (100 entries)
    max_pages = 1
    print(f"\n📌 Configured to fetch {max_pages} page(s) = {max_pages * 100} entries")
    
    # Fetch data from Rijksmuseum API
    data = fetch_rijksmuseum_data(max_pages=max_pages)
    
    if data:
        # Insert data into MongoDB
        insert_to_mongodb(client, data)
    else:
        print("\n⚠️  No data retrieved from Rijksmuseum API")
    
    # Close the connection
    client.close()
    print("\n✅ MongoDB connection closed")

if __name__ == "__main__":
    main()


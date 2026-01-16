"""
Graph Structure:
    - Market nodes: Main entities with properties (id, title, description, etc.)
    - Category nodes: Market categories
    - Series nodes: Market series
    - Relationships:
      * Market -[:BELONGS_TO]-> Category
      * Market -[:IN_SERIES]-> Series
"""

import os
import sys
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from neo4j import GraphDatabase
from dotenv import load_dotenv
from datetime import datetime

env_loaded = False
try:
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(parent_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path, override=False)  # Don't override existing env vars
        env_loaded = True
        print(f"📄 Loaded .env file from: {env_path}")
    else:
        # Also try loading from current directory
        if os.path.exists('.env'):
            load_dotenv('.env', override=False)
            env_loaded = True
            print("📄 Loaded .env file from current directory")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Check if running in Docker (environment variables are set by docker-compose)
if not env_loaded:
    print("📋 Using environment variables (from Docker or system)")


def check_environment_variables():
    """Check that required environment variables are set"""
    required_vars = {
        'MONGO_URI': 'MongoDB connection string',
        'DB2': 'MongoDB database name',
        'NEO4J_URI': 'Neo4j connection URI',
        'NEO4J_USER': 'Neo4j username',
        'NEO4J_PASSWORD': 'Neo4j password'
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"{var} ({description})")
        else:
            # Show that variable is set (but not the value for security)
            if 'PASSWORD' in var or 'URI' in var:
                # Show partial value for URIs, hide passwords
                if 'PASSWORD' in var:
                    print(f"   ✓ {var}: {'*' * len(value)}")
                else:
                    # Show first part of URI for verification
                    display_value = value[:30] + "..." if len(value) > 30 else value
                    print(f"   ✓ {var}: {display_value}")
            else:
                print(f"   ✓ {var}: {value}")
    
    if missing:
        print(f"\n❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    print("\n✅ All required environment variables are set")
    return True


def connect_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        mongo_uri = os.getenv('MONGO_URI')
        
        if not mongo_uri:
            print("❌ Error: MONGO_URI not found in environment variables")
            print("   Make sure MONGO_URI is set in .env file or as environment variable")
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


def connect_neo4j(max_retries=30, retry_delay=2):
    """Connect to Neo4j database with retry logic"""
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print("🔄 Connecting to Neo4j...")
    
    for attempt in range(1, max_retries + 1):
        try:
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            
            # Test connection
            with driver.session() as session:
                session.run("RETURN 1")
            
            print("✅ Successfully connected to Neo4j!")
            return driver
            
        except Exception as e:
            if attempt < max_retries:
                print(f"   ⏳ Attempt {attempt}/{max_retries} failed, retrying in {retry_delay}s... ({e})")
                time.sleep(retry_delay)
            else:
                print(f"❌ Neo4j connection error after {max_retries} attempts: {e}")
                print("   Make sure Neo4j is running and credentials are correct")
                return None
    
    return None


def clear_neo4j_graph(driver, auto_clear=False):
    """Clear existing graph data"""
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            
            if count > 0:
                print(f"\n⚠️  Neo4j database contains {count} nodes")
                if auto_clear:
                    print("   🗑️  Auto-clearing existing data (Docker mode)...")
                    session.run("MATCH (n) DETACH DELETE n")
                    print("   ✅ Graph cleared")
                else:
                    # Interactive mode (for local execution)
                    try:
                        choice = input("   Delete all existing data? (y/n): ").lower()
                        if choice == 'y':
                            print("   🗑️  Deleting all nodes and relationships...")
                            session.run("MATCH (n) DETACH DELETE n")
                            print("   ✅ Graph cleared")
                        else:
                            print("   ✓ Will append to existing data")
                    except EOFError:
                        # No input available (Docker mode), skip clearing
                        print("   ✓ Will append to existing data (non-interactive mode)")
    except Exception as e:
        print(f"❌ Error clearing graph: {e}")


def create_constraints(driver):
    """Create unique constraints and indexes for better performance"""
    try:
        with driver.session() as session:
            print("\n📋 Creating constraints and indexes...")
            
            # Create constraints for uniqueness
            constraints = [
                "CREATE CONSTRAINT market_id IF NOT EXISTS FOR (m:Market) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT series_slug IF NOT EXISTS FOR (s:Series) REQUIRE s.slug IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    # Constraint might already exist or syntax not supported, try without IF NOT EXISTS
                    constraint_alt = constraint.replace(" IF NOT EXISTS", "")
                    try:
                        session.run(constraint_alt)
                    except Exception:
                        # Constraint already exists, that's okay
                        pass
            
            print("   ✅ Constraints created")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not create constraints: {e}")


def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    
    # Try different date formats
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def create_market_node(driver, market_data):
    """Create a Market node in Neo4j"""
    with driver.session() as session:
        # Extract and prepare data
        # Handle different ID formats
        market_id = market_data.get('id', '')
        if not market_id:
            _id = market_data.get('_id', '')
            if isinstance(_id, dict) and '$oid' in _id:
                market_id = _id['$oid']
            elif isinstance(_id, str):
                market_id = _id
            else:
                market_id = str(_id) if _id else ''
        title = market_data.get('title', '')
        description = market_data.get('description', '')
        slug = market_data.get('slug', '')
        ticker = market_data.get('ticker', '')
        volume = market_data.get('volume', 0)
        if isinstance(volume, dict) and '$numberDouble' in volume:
            volume_str = volume['$numberDouble']
            if volume_str == 'Infinity':
                volume = float('inf')
            elif volume_str == '-Infinity':
                volume = float('-inf')
            elif volume_str == 'NaN':
                volume = float('nan')
            else:
                try:
                    volume = float(volume_str)
                except (ValueError, TypeError):
                    volume = 0
        comment_count = market_data.get('commentCount', 0)
        image = market_data.get('image', '')
        icon = market_data.get('icon', '')
        resolution_source = market_data.get('resolutionSource', '')
        published_at = market_data.get('published_at', '')
        updated_at = market_data.get('updatedAt', '')
        
        # Parse dates
        start_date = parse_date(market_data.get('startDate'))
        end_date = parse_date(market_data.get('endDate'))
        created_at = parse_date(market_data.get('createdAt') or market_data.get('creationDate'))
        closed_time = parse_date(market_data.get('closedTime'))
        
        # Create Market node
        query = """
        MERGE (m:Market {id: $id})
        SET m.title = $title,
            m.description = $description,
            m.slug = $slug,
            m.ticker = $ticker,
            m.volume = $volume,
            m.commentCount = $commentCount,
            m.image = $image,
            m.icon = $icon,
            m.resolutionSource = $resolutionSource,
            m.publishedAt = $publishedAt,
            m.updatedAt = $updatedAt,
            m.startDate = $startDate,
            m.endDate = $endDate,
            m.createdAt = $createdAt,
            m.closedTime = $closedTime
        RETURN m
        """
        
        session.run(query, 
                   id=market_id,
                   title=title,
                   description=description,
                   slug=slug,
                   ticker=ticker,
                   volume=float(volume) if volume else 0.0,
                   commentCount=int(comment_count) if comment_count else 0,
                   image=image,
                   icon=icon,
                   resolutionSource=resolution_source,
                   publishedAt=published_at,
                   updatedAt=updated_at,
                   startDate=start_date.isoformat() if start_date else None,
                   endDate=end_date.isoformat() if end_date else None,
                   createdAt=created_at.isoformat() if created_at else None,
                   closedTime=closed_time.isoformat() if closed_time else None)
        
        return market_id


def create_category_relationship(driver, market_id, category_name):
    """Create Category node and relationship with Market"""
    if not category_name:
        return
    
    with driver.session() as session:
        query = """
        MATCH (m:Market {id: $marketId})
        MERGE (c:Category {name: $categoryName})
        MERGE (m)-[:BELONGS_TO]->(c)
        """
        session.run(query, marketId=market_id, categoryName=category_name)


def create_series_relationship(driver, market_id, series_slug):
    """Create Series node and relationship with Market"""
    if not series_slug:
        return
    
    with driver.session() as session:
        query = """
        MATCH (m:Market {id: $marketId})
        MERGE (s:Series {slug: $seriesSlug})
        MERGE (m)-[:IN_SERIES]->(s)
        """
        session.run(query, marketId=market_id, seriesSlug=series_slug)


def import_markets_to_neo4j(mongo_client, neo4j_driver, db_name=None, batch_size=100):
    """Import markets from MongoDB to Neo4j"""
    try:
        if db_name is None:
            db_name = os.getenv('DB2')
        
        db = mongo_client[db_name]
        collection = db['cleaned']
        
        print(f"\n📊 Starting import from MongoDB to Neo4j...")
        print(f"   Database: {db_name}")
        print(f"   Collection: cleaned")
        
        # Count total documents
        total_docs = collection.count_documents({})
        print(f"\n📄 Total documents to import: {total_docs}")
        
        if total_docs == 0:
            print("⚠️  No documents found in 'cleaned' collection")
            return
        
        # Create constraints
        create_constraints(neo4j_driver)
        
        # Process documents in batches
        processed = 0
        markets_created = 0
        categories_created = 0
        series_created = 0
        
        print(f"\n🔄 Processing documents in batches of {batch_size}...")
        
        cursor = collection.find({})
        
        batch = []
        for doc in cursor:
            batch.append(doc)
            
            if len(batch) >= batch_size:
                # Process batch
                for market_data in batch:
                    try:
                        # Create market node
                        market_id = create_market_node(neo4j_driver, market_data)
                        markets_created += 1
                        
                        # Create category relationship
                        category = market_data.get('category')
                        if category:
                            create_category_relationship(neo4j_driver, market_id, category)
                            categories_created += 1
                        
                        # Create series relationship
                        series_slug = market_data.get('seriesSlug')
                        if series_slug:
                            create_series_relationship(neo4j_driver, market_id, series_slug)
                            series_created += 1
                        
                        processed += 1
                        
                    except Exception as e:
                        print(f"   ⚠️  Error processing document: {e}")
                        continue
                
                print(f"   ✓ Processed {processed}/{total_docs} documents")
                batch = []
        
        # Process remaining documents
        if batch:
            for market_data in batch:
                try:
                    market_id = create_market_node(neo4j_driver, market_data)
                    markets_created += 1
                    
                    category = market_data.get('category')
                    if category:
                        create_category_relationship(neo4j_driver, market_id, category)
                        categories_created += 1
                    
                    series_slug = market_data.get('seriesSlug')
                    if series_slug:
                        create_series_relationship(neo4j_driver, market_id, series_slug)
                        series_created += 1
                    
                    processed += 1
                except Exception as e:
                    print(f"   ⚠️  Error processing document: {e}")
                    continue
        
        # Get final statistics
        with neo4j_driver.session() as session:
            result = session.run("MATCH (m:Market) RETURN count(m) as count")
            market_count = result.single()["count"]
            
            result = session.run("MATCH (c:Category) RETURN count(c) as count")
            category_count = result.single()["count"]
            
            result = session.run("MATCH (s:Series) RETURN count(s) as count")
            series_count = result.single()["count"]
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            relationship_count = result.single()["count"]
        
        print(f"\n✅ Import completed!")
        print(f"\n📊 Neo4j Graph Statistics:")
        print(f"   - Market nodes: {market_count}")
        print(f"   - Category nodes: {category_count}")
        print(f"   - Series nodes: {series_count}")
        print(f"   - Total relationships: {relationship_count}")
        print(f"\n📊 Import Statistics:")
        print(f"   - Documents processed: {processed}/{total_docs}")
        print(f"   - Markets created: {markets_created}")
        print(f"   - Categories linked: {categories_created}")
        print(f"   - Series linked: {series_created}")
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function - Import MongoDB data to Neo4j"""
    print("=" * 60)
    print("    MongoDB to Neo4j Import Script")
    print("=" * 60)
    
    # Check environment variables
    print("\n🔍 Checking environment variables...")
    if not check_environment_variables():
        print("\n❌ Cannot proceed without required environment variables")
        sys.exit(1)
    
    # Connect to MongoDB
    mongo_client = connect_mongodb()
    if not mongo_client:
        print("\n❌ Cannot proceed without MongoDB connection")
        sys.exit(1)
    
    # Connect to Neo4j
    neo4j_driver = connect_neo4j()
    if not neo4j_driver:
        print("\n❌ Cannot proceed without Neo4j connection")
        mongo_client.close()
        sys.exit(1)
    
    try:
        # Check if running in Docker (non-interactive mode)
        is_docker = os.getenv('NEO4J_URI', '').startswith('bolt://neo4j:')
        
        # Clear existing graph (optional)
        # In Docker, auto-clear to avoid interactive prompts
        clear_neo4j_graph(neo4j_driver, auto_clear=is_docker)
        
        # Import data
        import_markets_to_neo4j(mongo_client, neo4j_driver)
        
    finally:
        # Close connections
        neo4j_driver.close()
        mongo_client.close()
        print("\n✅ Connections closed")
        print("=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to fetch Velib station data from API and insert into Cassandra
API: https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records?limit=20
"""

import requests
import time
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime
import sys

# Configuration
CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
KEYSPACE = 'mobility'
TABLE = 'velib_status'
VELIB_API_URL = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records?limit=20'

def connect_cassandra():
    """Connect to Cassandra cluster"""
    print("🔄 Connecting to Cassandra...")
    try:
        cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
        session = cluster.connect()
        print("✅ Connected to Cassandra!")
        return cluster, session
    except Exception as e:
        print(f"❌ Error connecting to Cassandra: {e}")
        sys.exit(1)

def fetch_velib_data():
    """Fetch data from Velib API"""
    print(f"\n📡 Fetching data from Velib API...")
    print(f"URL: {VELIB_API_URL}")
    
    try:
        response = requests.get(VELIB_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'results' not in data:
            print("❌ Unexpected API response format")
            return []
        
        stations = []
        for record in data['results']:
            if 'record' in record and 'fields' in record['record']:
                fields = record['record']['fields']
                station = {
                    'station_id': str(fields.get('stationcode', '')),
                    'station_name': fields.get('name', ''),
                    'latitude': float(fields.get('coordonnees_geo', {}).get('lat', 0)) if isinstance(fields.get('coordonnees_geo'), dict) else 0.0,
                    'longitude': float(fields.get('coordonnees_geo', {}).get('lon', 0)) if isinstance(fields.get('coordonnees_geo'), dict) else 0.0,
                    'available_bikes': int(fields.get('numbikesavailable', 0)),
                    'available_ebikes': int(fields.get('ebike', 0)),
                    'available_docks': int(fields.get('numdocksavailable', 0)),
                    'total_docks': int(fields.get('capacity', 0)),
                    'timestamp': datetime.now()
                }
                if station['station_id']:
                    stations.append(station)
        
        print(f"✅ Fetched {len(stations)} stations")
        return stations
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from API: {e}")
        return []
    except Exception as e:
        print(f"❌ Error processing API response: {e}")
        return []

def insert_data(session, stations):
    """Insert stations data into Cassandra"""
    if not stations:
        print("⚠️  No data to insert")
        return
    
    print(f"\n💾 Inserting {len(stations)} records into Cassandra...")
    
    # Prepare insert statement
    insert_query = f"""
        INSERT INTO {KEYSPACE}.{TABLE} 
        (station_id, timestamp, station_name, available_bikes, available_ebikes, 
         available_docks, total_docks, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    prepared = session.prepare(insert_query)
    
    inserted = 0
    for station in stations:
        try:
            session.execute(prepared, (
                station['station_id'],
                station['timestamp'],
                station['station_name'],
                station['available_bikes'],
                station['available_ebikes'],
                station['available_docks'],
                station['total_docks'],
                station['latitude'],
                station['longitude']
            ))
            inserted += 1
        except Exception as e:
            print(f"⚠️  Error inserting station {station['station_id']}: {e}")
    
    print(f"✅ Successfully inserted {inserted}/{len(stations)} records")

def main():
    """Main function"""
    print("=" * 60)
    print("  TP3 - Cassandra Velib Data Insertion")
    print("=" * 60)
    
    # Connect to Cassandra
    cluster, session = connect_cassandra()
    
    # Set keyspace
    try:
        session.set_keyspace(KEYSPACE)
        print(f"✅ Using keyspace: {KEYSPACE}")
    except Exception as e:
        print(f"❌ Error setting keyspace: {e}")
        cluster.shutdown()
        sys.exit(1)
    
    # Fetch data from API
    stations = fetch_velib_data()
    
    # Insert data
    insert_data(session, stations)
    
    # Display summary
    try:
        count_query = f"SELECT COUNT(*) FROM {KEYSPACE}.{TABLE}"
        result = session.execute(count_query)
        count = result.one()[0]
        print(f"\n📊 Total records in {KEYSPACE}.{TABLE}: {count}")
    except Exception as e:
        print(f"⚠️  Error counting records: {e}")
    
    # Close connection
    cluster.shutdown()
    print("\n✅ Data insertion completed!")

if __name__ == "__main__":
    main()

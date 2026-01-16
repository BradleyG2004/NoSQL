-- TP3 - Cassandra Schema Creation
-- Keyspace: mobility
-- Table: velib_status

-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS mobility
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- Use the keyspace
USE mobility;

-- Create table for Velib station status history
-- Partition key: station_id (to distribute data across nodes)
-- Clustering key: timestamp (to order by time within each partition)
CREATE TABLE IF NOT EXISTS velib_status (
    station_id text,
    timestamp timestamp,
    station_name text,
    available_bikes int,
    available_ebikes int,
    available_docks int,
    total_docks int,
    latitude double,
    longitude double,
    PRIMARY KEY (station_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Create an index for station_name (optional, for queries by name)
CREATE INDEX IF NOT EXISTS idx_station_name ON velib_status (station_name);

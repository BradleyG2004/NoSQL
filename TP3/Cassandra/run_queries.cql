-- TP3 - Cassandra Queries
-- These queries demonstrate the importance of partition keys in Cassandra

-- Query 1: Select all data for a specific station (using partition key)
-- This is the CORRECT way to query in Cassandra
SELECT * FROM mobility.velib_status 
WHERE station_id = '10001' 
ORDER BY timestamp DESC;

-- Query 2: Select data for multiple stations (using partition key IN clause)
SELECT * FROM mobility.velib_status 
WHERE station_id IN ('10001', '10002', '10003')
ORDER BY timestamp DESC;

-- Query 3: Count records for a specific station
SELECT COUNT(*) FROM mobility.velib_status 
WHERE station_id = '10001';

-- Query 4: Get latest status for a specific station
SELECT * FROM mobility.velib_status 
WHERE station_id = '10001' 
LIMIT 1;

-- Query 5: Get all stations (this will work but is inefficient for large datasets)
SELECT DISTINCT station_id, station_name FROM mobility.velib_status;

-- Query 6: Select by station name (using secondary index)
-- Note: Secondary indexes are less efficient than partition keys
SELECT * FROM mobility.velib_status 
WHERE station_name = 'Station Name Here'
ALLOW FILTERING;

-- Query 7: Get stations with available bikes > threshold for a specific station
SELECT * FROM mobility.velib_status 
WHERE station_id = '10001' 
AND available_bikes > 5
ALLOW FILTERING;

-- Query 8: Get all records (for small datasets only - not recommended for production)
SELECT * FROM mobility.velib_status LIMIT 100;

#!/bin/bash
set -e

echo "=========================================="
echo "  TP3 - Cassandra Setup"
echo "=========================================="

# Start Cassandra in background
echo "🚀 Starting Cassandra..."
# Start Cassandra with -R flag to allow running as root (acceptable in Docker container)
cassandra -R &
CASSANDRA_PID=$!

# Wait for Cassandra to be ready
echo "⏳ Waiting for Cassandra to be ready..."
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if cqlsh -e "DESCRIBE KEYSPACES" > /dev/null 2>&1; then
        echo "✅ Cassandra is ready!"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 5)) -eq 0 ]; then
        echo "   Attempt $attempt/$max_attempts..."
    fi
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Cassandra failed to start within timeout"
    exit 1
fi

# Create schema
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Creating schema..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f /docker-entrypoint-initdb.d/create_schema.cql ]; then
    cqlsh -f /docker-entrypoint-initdb.d/create_schema.cql
    echo "✅ Schema created!"
else
    echo "⚠️  Schema file not found"
fi

# Wait a bit for schema to be fully created
sleep 3

# Insert data from Velib API
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Inserting Velib data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 /usr/local/bin/insert_velib_data.py

# Display some sample queries
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Sample Queries:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To run queries, connect to cqlsh:"
echo "  docker exec -it <container-id> cqlsh"
echo ""
echo "Example queries (using partition key - CORRECT):"
echo "  SELECT * FROM mobility.velib_status WHERE station_id = '10001';"
echo ""
echo "Example queries (without partition key - WILL FAIL):"
echo "  SELECT * FROM mobility.velib_status WHERE timestamp > '2024-01-01';"
echo "  (This will fail because timestamp is not a partition key)"
echo ""

# Keep Cassandra running
echo "=========================================="
echo "Cassandra is running. Press Ctrl+C to stop."
echo "Connect using: cqlsh"
echo "=========================================="

# Wait for Cassandra process
wait $CASSANDRA_PID

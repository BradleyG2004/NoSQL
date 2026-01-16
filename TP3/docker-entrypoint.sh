#!/bin/bash
set -e

# Start Redis server in background
echo "🚀 Starting Redis server..."
redis-server /usr/local/etc/redis/redis.conf &
REDIS_PID=$!

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
until redis-cli ping > /dev/null 2>&1; do
  sleep 0.5
done
echo "✅ Redis is ready!"

# Run TP2 exercises
echo ""
/usr/local/bin/run_tp2_exercises.sh

# Keep Redis running in foreground
echo ""
echo "=========================================="
echo "Redis server is running. Press Ctrl+C to stop."
echo "You can connect using: redis-cli"
echo "=========================================="
wait $REDIS_PID

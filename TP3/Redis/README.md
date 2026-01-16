# TP2 - Redis Key-Value Exercises

This Docker setup automatically executes all TP2 Redis exercises when the container starts.

## Files Structure

```
TP3/
├── dockerfile              # Docker image definition
├── redis.conf             # Redis configuration file
├── docker-entrypoint.sh   # Entrypoint script (starts Redis + runs exercises)
├── run_tp2_exercises.sh   # Script with all TP2 exercises
└── README.md              # This file
```

## How to Use

### 1. Build the Docker Image

```bash
cd TP3
docker build -t redis-tp2 .
```

### 2. Run the Container

```bash
docker run -it redis-tp2
```

The container will:
1. Start Redis server
2. Automatically execute all TP2 exercises
3. Keep Redis running for interactive use

### 3. Interactive Use

After the exercises complete, Redis will continue running. You can:

- **Connect to Redis CLI** (in another terminal):
  ```bash
  docker exec -it <container-id> redis-cli
  ```

- **Run custom commands**:
  ```bash
  docker exec -it <container-id> redis-cli GET User:1
  ```

## Exercises Covered

The script automatically executes all 10 exercises from TP2:

1. ✅ Create and rename keys
2. ✅ Create multiple keys and list them
3. ✅ Get multiple values in one operation (MGET)
4. ✅ Append text to existing values
5. ✅ Create keys only if they don't exist (SETNX)
6. ✅ Temporary keys with TTL (expiration)
7. ✅ Simulate user with related keys
8. ✅ Atomic multi-key creation (MSETNX)
9. ✅ Hash structures for users
10. ✅ Lists and transactions

## Redis Configuration

The `redis.conf` file includes:
- Network binding on all interfaces (0.0.0.0)
- Port 6379
- No persistence (for testing purposes)
- No memory limits

## Customization

To modify exercises, edit `run_tp2_exercises.sh` and rebuild the image.

## Notes

- The container runs Redis in the foreground after completing exercises
- All data is stored in memory (no persistence)
- Press `Ctrl+C` to stop the container

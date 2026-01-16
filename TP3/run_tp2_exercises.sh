#!/bin/bash

# Script to execute TP2 Redis exercises
# This script will run all the exercises described in TP2

echo "=========================================="
echo "  TP2 - Redis Key-Value Exercises"
echo "=========================================="
echo ""

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 2

# Function to execute Redis command and display result
redis_exec() {
    local description="$1"
    shift
    echo ""
    echo "📌 Exercise: $description"
    echo "Command: redis-cli $@"
    redis-cli "$@"
    echo ""
}

# Exercise 1: Create a key User and rename it to User:1
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 1: Create and rename key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Create key 'User' with value 'John Doe'" SET User "John Doe"
redis_exec "Rename 'User' to 'User:1'" RENAME User User:1
redis_exec "Get value of User:1" GET User:1

# Exercise 2: Create multiple user keys and list them
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 2: Create multiple keys and list them"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Create User:2" SET User:2 "Jane Smith"
redis_exec "Create User:3" SET User:3 "Bob Johnson"
redis_exec "Create User:4" SET User:4 "Alice Williams"
redis_exec "List all keys" KEYS "*"
redis_exec "List keys starting with 'User'" KEYS "User*"

# Exercise 3: Display values of multiple keys in one operation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 3: Get multiple values in one operation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Get multiple values (MGET)" MGET User:1 User:2 User:3 User:4

# Exercise 4: Modify value by appending text
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 4: Append text to existing value"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Append ' - Updated' to User:1" APPEND User:1 " - Updated"
redis_exec "Get updated value" GET User:1

# Exercise 5: Create key only if it doesn't exist
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 5: Create key only if not exists (SETNX)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Try to create User:1 (should fail, already exists)" SETNX User:1 "New Value"
redis_exec "Try to create User:5 (should succeed)" SETNX User:5 "New User"
redis_exec "Get User:5" GET User:5

# Exercise 6: Create temporary key with TTL
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 6: Temporary key with expiration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Create User:Temp with 10 seconds TTL" SETEX User:Temp 10 "Temporary User"
redis_exec "Check TTL of User:Temp" TTL User:Temp
redis_exec "Get User:Temp" GET User:Temp
echo "⏳ Waiting 12 seconds for key to expire..."
sleep 12
redis_exec "Try to get User:Temp after expiration" GET User:Temp
redis_exec "Check if User:Temp exists" EXISTS User:Temp

# Exercise 7: Simulate user with related keys
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 7: Simulate user with related keys"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Create User:6" SET User:6 "Charlie Brown"
redis_exec "Create User:6:City" SET User:6:City "Paris"
redis_exec "Create User:6:Age with 30 seconds TTL" SETEX User:6:Age 30 "25"
redis_exec "Create User:6:Activity" SET User:6:Activity "Developer"
redis_exec "List all User:6 related keys" KEYS "User:6*"
redis_exec "Get all User:6 data" MGET User:6 User:6:City User:6:Age User:6:Activity

# Exercise 8: Atomic operation to create multiple keys only if none exist
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 8: Atomic multi-key creation (MSETNX)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Try MSETNX with new keys (should succeed)" MSETNX User:7 "User Seven" User:8 "User Eight"
redis_exec "Try MSETNX with one existing key (should fail)" MSETNX User:7 "Updated" User:9 "User Nine"
redis_exec "Check if User:9 was created (should not exist)" EXISTS User:9
redis_exec "List User:7 and User:8" MGET User:7 User:8

# Exercise 9: Create user using Hash structure
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 9: Hash structure for user"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Create user hash User:Hash:1" HSET User:Hash:1 name "David Lee" city "Lyon" age "30" email "david@example.com"
redis_exec "Get all fields and values (HGETALL)" HGETALL User:Hash:1
redis_exec "Get all field names (HKEYS)" HKEYS User:Hash:1
redis_exec "Get all values (HVALS)" HVALS User:Hash:1
redis_exec "Get specific field (HGET)" HGET User:Hash:1 name

# Exercise 10: Create Redis list and use transactions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Exercise 10: Redis List and Transactions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "Create list and push values (RPUSH)" RPUSH User:List:1 "Alice" "Bob" "Charlie"
redis_exec "Get all list elements (LRANGE)" LRANGE User:List:1 0 -1
redis_exec "Get list length (LLEN)" LLEN User:List:1
redis_exec "Pop from left (LPOP)" LPOP User:List:1
redis_exec "Pop from right (RPOP)" RPOP User:List:1
redis_exec "Get remaining list elements" LRANGE User:List:1 0 -1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Transaction Example:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting transaction (MULTI)..."
redis-cli <<EOF
MULTI
SET Transaction:Key1 Value1
SET Transaction:Key2 Value2
INCR Transaction:Counter
EXEC
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Final Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
redis_exec "All keys in database" KEYS "*"
redis_exec "Total number of keys" DBSIZE

echo ""
echo "=========================================="
echo "✅ All TP2 exercises completed!"
echo "=========================================="

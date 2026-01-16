FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the migration script
COPY MongoToNeo4j.py .

# Default command (will be overridden by docker-compose)
CMD ["python", "MongoToNeo4j.py"]

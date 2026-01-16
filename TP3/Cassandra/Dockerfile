FROM cassandra:latest

# Install Python and required packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Using --break-system-packages flag for Docker container (isolated environment)
RUN pip3 install --break-system-packages requests cassandra-driver

# Copy scripts
COPY create_schema.cql /docker-entrypoint-initdb.d/
COPY insert_velib_data.py /usr/local/bin/
COPY run_queries.cql /usr/local/bin/
COPY docker-entrypoint.sh /usr/local/bin/

# Make scripts executable
RUN chmod +x /usr/local/bin/insert_velib_data.py && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose Cassandra ports
EXPOSE 7000 7001 7199 9042 9160

# Use custom entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

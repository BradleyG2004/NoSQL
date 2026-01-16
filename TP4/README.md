# MongoDB to Neo4j Migration

This directory contains the Docker setup for migrating data from MongoDB to Neo4j.

## Prerequisites

- Docker and Docker Compose installed
- MongoDB connection string and database name configured in `.env` file

## Setup

1. Create a `.env` file in the project root (same directory as `TP2`, `TP3`, `TP4`) with the following variables:

```env
MONGO_URI=your_mongodb_connection_string
DB2=your_database_name
```

2. The Neo4j credentials are set in `docker-compose.yml`. Default values:
   - URI: `bolt://neo4j:7687` (internal Docker network)
   - User: `neo4j`
   - Password: `neo4jpassword`

## Usage

### Start the migration

From the `TP4` directory, run:

```bash
docker-compose up
```

This will:
1. Start the Neo4j container and wait for it to be healthy
2. Build and start the Python migration container
3. Execute the migration script automatically

### View logs

```bash
docker-compose logs -f
```

### Stop and clean up

```bash
docker-compose down
```

To also remove volumes (Neo4j data):

```bash
docker-compose down -v
```

## Access Neo4j Browser

Once Neo4j is running, you can access the Neo4j Browser at:
- **URL**: http://localhost:7474
- **Username**: `neo4j`
- **Password**: `neo4jpassword`

### Visualizing Your Graph

After the migration completes, you can visualize your graph data using Neo4j Browser. Here are some useful Cypher queries to explore your data:

#### View all Market nodes
```cypher
MATCH (m:Market)
RETURN m
LIMIT 25
```

#### View the graph structure
```cypher
MATCH (m:Market)-[r]->(n)
RETURN m, r, n
LIMIT 50
```

#### Count nodes by type
```cypher
MATCH (n)
RETURN labels(n) as NodeType, count(n) as Count
```

#### View Markets with their Categories
```cypher
MATCH (m:Market)-[:BELONGS_TO]->(c:Category)
RETURN m.title, c.name
LIMIT 20
```

#### View Markets with their Series
```cypher
MATCH (m:Market)-[:IN_SERIES]->(s:Series)
RETURN m.title, s.slug
LIMIT 20
```

#### Find Markets by Category
```cypher
MATCH (m:Market)-[:BELONGS_TO]->(c:Category {name: 'YourCategoryName'})
RETURN m
```

#### View the full graph (be careful with large datasets!)
```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 100
```

#### Statistics query
```cypher
MATCH (m:Market)
OPTIONAL MATCH (m)-[:BELONGS_TO]->(c:Category)
OPTIONAL MATCH (m)-[:IN_SERIES]->(s:Series)
RETURN 
  count(DISTINCT m) as TotalMarkets,
  count(DISTINCT c) as TotalCategories,
  count(DISTINCT s) as TotalSeries,
  count(DISTINCT (m)-[:BELONGS_TO]->(c)) as MarketCategoryRelations,
  count(DISTINCT (m)-[:IN_SERIES]->(s)) as MarketSeriesRelations
```

## Containers

- **neo4j**: Neo4j database server (ports 7474, 7687)
- **migration**: Python container that runs the migration script

The migration container will automatically wait for Neo4j to be ready before starting the import process.

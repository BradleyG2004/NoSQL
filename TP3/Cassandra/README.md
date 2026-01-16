# TP3 - Cassandra Velib Database

Ce setup Docker automatise la création d'une base de données Cassandra pour stocker l'historique de disponibilité des stations Vélib.

## 📋 Objectifs du TP3

- Comprendre le fonctionnement d'une base NoSQL distribuée orientée colonnes
- Manipuler le langage CQL (Cassandra Query Language)
- Créer un schéma de données simple
- Insérer et consulter des données
- Comprendre le rôle de la clé de partition dans la distribution des données

## 🏗️ Architecture

- **Keyspace**: `mobility`
- **Table**: `velib_status`
- **Partition Key**: `station_id` (distribue les données sur les nœuds)
- **Clustering Key**: `timestamp` (ordonne par temps dans chaque partition)

## 📂 Structure des fichiers

```
TP3/Cassandra/
├── Dockerfile              # Image Docker Cassandra
├── create_schema.cql       # Script de création du schéma
├── insert_velib_data.py   # Script Python pour récupérer et insérer les données
├── run_queries.cql         # Exemples de requêtes CQL
├── docker-entrypoint.sh   # Script d'initialisation
└── README.md               # Cette documentation
```

## 🚀 Utilisation

### 1. Construire l'image Docker

```bash
cd TP3/Cassandra
docker build -t cassandra-tp3 .
```

### 2. Lancer le conteneur

```bash
docker run -it -p 9042:9042 cassandra-tp3
```

Le conteneur va :
1. Démarrer Cassandra
2. Créer le keyspace `mobility`
3. Créer la table `velib_status`
4. Récupérer les données depuis l'API Vélib
5. Insérer les données dans Cassandra

### 3. Se connecter à Cassandra (dans un autre terminal)

```bash
docker exec -it <container-id> cqlsh
```

## 📊 Schéma de la table

```cql
CREATE TABLE velib_status (
    station_id text,           -- Clé de partition
    timestamp timestamp,        -- Clé de clustering
    station_name text,
    available_bikes int,
    available_ebikes int,
    available_docks int,
    total_docks int,
    latitude double,
    longitude double,
    PRIMARY KEY (station_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

## 🔍 Requêtes CQL

### ✅ Requêtes CORRECTES (avec clé de partition)

```cql
-- Requête par station_id (clé de partition)
SELECT * FROM mobility.velib_status 
WHERE station_id = '10001';

-- Requête avec plusieurs stations
SELECT * FROM mobility.velib_status 
WHERE station_id IN ('10001', '10002', '10003');
```

### ❌ Requêtes INCORRECTES (sans clé de partition)

```cql
-- Cette requête ÉCHOUERA car timestamp n'est pas une clé de partition
SELECT * FROM mobility.velib_status 
WHERE timestamp > '2024-01-01';

-- Cette requête nécessite ALLOW FILTERING (peu performant)
SELECT * FROM mobility.velib_status 
WHERE available_bikes > 5 
ALLOW FILTERING;
```

## 🎯 Points importants

### Clé de partition (`station_id`)

- **Rôle**: Distribue les données sur les nœuds du cluster
- **Contrainte**: Toutes les requêtes WHERE doivent inclure la clé de partition
- **Performance**: Les requêtes avec clé de partition sont très rapides

### Clé de clustering (`timestamp`)

- **Rôle**: Ordonne les données dans chaque partition
- **Utilisation**: Permet de trier et filtrer les données dans une partition

### Différences avec une base relationnelle

| Aspect | Base relationnelle | Cassandra |
|--------|-------------------|-----------|
| Requêtes | Flexibles (WHERE sur n'importe quelle colonne) | Doit inclure la clé de partition |
| Jointures | Supportées | Non supportées |
| Transactions ACID | Complètes | Limitées (au niveau de la partition) |
| Modèle | Normalisé | Dé-normalisé (optimisé pour les requêtes) |

## 📡 API Vélib

Les données sont récupérées depuis :
```
https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records?limit=20
```

## 🔧 Personnalisation

Pour modifier les exercices :
1. Éditez `create_schema.cql` pour changer le schéma
2. Éditez `insert_velib_data.py` pour modifier les données insérées
3. Éditez `run_queries.cql` pour ajouter des requêtes

## 📝 Notes

- Le conteneur garde Cassandra en cours d'exécution après l'initialisation
- Les données sont stockées en mémoire (pas de persistance configurée)
- Appuyez sur `Ctrl+C` pour arrêter le conteneur
- Pour des données persistantes, montez un volume Docker

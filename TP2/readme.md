# TP2 - Scripts MongoDB et Rijksmuseum

## Description
Suite de scripts Python pour tester la connexion MongoDB Atlas et récupérer/charger des données de l'API Rijksmuseum.

## Architecture des scripts

### 📂 Structure
```
TP2/
├── .env                          # Variables d'environnement
├── readme.md                     # Cette documentation
└── Scripts/
    ├── TestCo.py                 # Test de connexion MongoDB
    └── RijksmuseumData.py        # Récupération et chargement des données
```

### 🔍 TestCo.py - Test de connexion
**Objectif :** Tester uniquement la connexion à MongoDB Atlas

**Fonctionnalités :**
- ✅ Connexion à MongoDB Atlas via la chaîne de connexion du `.env`
- ✅ Test de connexion avec la commande `ping`
- ✅ Affichage des bases de données disponibles
- ✅ Gestion complète des erreurs de connexion
- ✅ Messages clairs et indicateurs visuels

### 🎨 RijksmuseumData.py - Chargement des données
**Objectif :** Récupérer et charger les données du Rijksmuseum dans MongoDB

**Fonctionnalités :**
- ✅ Connexion à MongoDB Atlas
- ✅ Récupération des données via l'API Rijksmuseum Search
- ✅ **Aucune clé API nécessaire**
- ✅ Pagination automatique (100 items par page)
- ✅ **Configuration : 1 page = 100 entrées**
- ✅ Gestion des interruptions (Ctrl+C)
- ✅ Délai de 0.5s entre requêtes pour ne pas surcharger l'API
- ✅ Insertion par lots de 1000 documents
- ✅ Option de suppression des données existantes
- ✅ Affichage de statistiques détaillées

**API utilisée :** `https://data.rijksmuseum.nl/search/collection`

**Stockage MongoDB :**
- Base de données : Définie dans `.env` (`DB`)
- Collection : `rijksmuseum`

## Configuration requise

### 📄 Fichier `.env`
Créer un fichier `.env` dans le répertoire `TP2/` avec :
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
RIJKSMUSEUM_API_URL=https://data.rijksmuseum.nl/search/collection
DB=sample_mflix
```

**Variables :**
- `MONGO_URI` : Chaîne de connexion MongoDB Atlas
- `RIJKSMUSEUM_API_URL` : URL de l'API Rijksmuseum
- `DB` : Nom de la base de données MongoDB à utiliser

### 📦 Dépendances Python
```bash
pip install pymongo python-dotenv requests
```

## 🚀 Utilisation

### 1. Tester la connexion MongoDB
```bash
cd TP2/Scripts
python TestCo.py
```

**Sortie attendue :**
```
==================================================
    MongoDB Atlas Connection Test
==================================================
🔄 Connecting to MongoDB Atlas...
✅ Successfully connected to MongoDB Atlas!

📊 Available databases: ['sample_mflix', 'admin', 'local']

✅ Connection test successful!
   MongoDB connection closed.
```

### 2. Récupérer et charger les données Rijksmuseum
```bash
cd TP2/Scripts
python RijksmuseumData.py
```

## 📋 Structure du code

### TestCo.py - Fonctions

#### `connect_mongodb()`
- Établit la connexion à MongoDB Atlas
- Teste la connexion avec la commande `ping`
- Affiche les bases de données disponibles
- **Retour :** Client MongoDB ou None en cas d'erreur

#### `main()`
- Fonction principale de test
- Affiche un en-tête formaté
- Appelle `connect_mongodb()`
- Ferme proprement la connexion
- **Exit code :** 0 si succès, 1 si échec

### RijksmuseumData.py - Fonctions

#### `connect_mongodb()`
- Établit la connexion à MongoDB Atlas
- Charge les variables depuis `.env` du répertoire parent
- **Retour :** Client MongoDB ou None en cas d'erreur

#### `fetch_rijksmuseum_data(max_pages=None)`
- Récupère les données de l'API Rijksmuseum avec pagination
- **Paramètres :**
  - `max_pages` (int, optional) : Nombre maximum de pages (None = toutes)
- Gère la pagination automatiquement via les tokens
- Gestion des interruptions (Ctrl+C)
- **Retour :** Liste d'objets (identifiants LOD)

#### `insert_to_mongodb(client, data, db_name, collection_name='rijksmuseum')`
- Insère les données dans MongoDB par lots
- **Paramètres :**
  - `client` : Client MongoDB
  - `data` : Liste des documents à insérer
  - `db_name` : Nom de la base (depuis `.env`)
  - `collection_name` : Nom de la collection (défaut: 'rijksmuseum')
- Demande confirmation avant de supprimer les données existantes
- Insertion par lots de 1000 pour optimiser les performances

#### `main()`
- Fonction principale orchestrant le workflow complet :
  1. Connexion à MongoDB
  2. Récupération de 100 entrées (1 page)
  3. Insertion dans MongoDB
  4. Fermeture de la connexion

## Format des données

Les données récupérées suivent le format **Linked Art Search** :
```📊 Exemples de sortie

### TestCo.py
```
==================================================
    MongoDB Atlas Connection Test
==================================================
🔄 Connecting to MongoDB Atlas...
✅ Successfully connected to MongoDB Atlas!

📊 Available databases: ['sample_mflix', 'admin', 'local']

✅ Connection test successful!
   MongoDB connection closed.
```

### RijksmuseumData.py
```
==================================================
    Rijksmuseum Data Loader
==================================================
🔄 Connecting to MongoDB Atlas...
✅ Successfully connected to MongoDB Atlas!

📌 Configured to fetch 1 page(s) = 100 entries

🎨 Starting to fetch data from Rijksmuseum API...
   (Limited to 1 pages = 100 items max)

📄 Fetching page 1...
   ✓ Retrieved 100 items (Total collected: 100/835887)

⚠️  Reached maximum page limit (1 pages)

💾 Inserting data into 'sample_mflix.rijksmuseum'...
   Delete existing data? (y/n): n
   ✓ Inserted batch 1: 100/100 documents

✅ Successfully inserted 100 documents!

📊 Collection stats:
   - Database: sample_mflix
   - Collection: rijksmuseum
   - Total documents: 100

✅ MongoDB connection closed
```

## 🔧 Personnalisation

### Modifier le nombre de pages récupérées
Dans `RijksmuseumData.py`, ligne ~180 :
```python
max_pages = 1  # Modifier cette valeur (1 page = 100 entrées)
```

### Supprimer l'interaction utilisateur
Pour éviter la question sur la suppression des données existantes, dans la fonction `insert_to_mongodb()` :
```python
# Remplacer ces lignes :
if existing_count > 0:
    print(f"   ⚠️  Collection already contains {existing_count} documents")
    choice = input("   Delete existing data? (y/n): ").lower()
    if choice == 'y':
        collection.delete_many({})

# Par :
if existing_count > 0:
    collection.delete_many({})
    print(f"   ✓ Deleted {existing_count} existing documents")
```

## 📝 Notes importantes

- **Collection totale :** ~836,000 objets (8,359 pages)
- **Configuration actuelle :** 100 entrées (1 page)
- **Format des données :** Linked Art Search (identifiants LOD)
- **Résolution des IDs :** Utiliser le Persistent Identifier Resolver du Rijksmuseum

## 👤 Fetching page 1...
   ✓ Retrieved 100 items (Total collected: 100/835887)

⚠️  Reached maximum page limit (1 pages)

💾 Inserting data into 'sample_mflix.rijksmuseum'...
   ✓ Inserted batch 1: 100/100 documents

✅ Successfully inserted 100 documents!

📊 Collection stats:
   - Database: sample_mflix
   - Collection: rijksmuseum
   - Total documents: 100

✅ MongoDB connection closed
```

## Auteur
TP2 - Manipulation de bases de données NoSQL
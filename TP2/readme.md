# ManipDB.py - Documentation

## Description
Script Python pour récupérer des données de l'API Rijksmuseum et les insérer dans une base MongoDB Atlas.

## Fonctionnalités

### 1. Connexion MongoDB Atlas
- Utilise une chaîne de connexion stockée dans le fichier `.env`
- Test automatique de la connexion avant toute opération
- Gestion des erreurs de connexion avec messages clairs

### 2. Récupération des données Rijksmuseum
- API utilisée : `https://data.rijksmuseum.nl/search/collection`
- **Aucune clé API nécessaire**
- Pagination automatique (100 items par page)
- **Configuration actuelle : 1 page = 100 entrées**
- Gestion des interruptions (Ctrl+C)
- Délai de 0.5s entre chaque requête pour ne pas surcharger l'API

### 3. Insertion dans MongoDB
- Base de données : `sample_mflix`
- Collection : `rijksmuseum`
- Insertion par lots de 1000 documents pour optimiser les performances
- Option de suppression des données existantes avant insertion
- Affichage de statistiques après insertion

## Configuration requise

### Fichier `.env`
Créer un fichier `.env` dans le même répertoire avec :
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
RIJKSMUSEUM_API_URL=https://data.rijksmuseum.nl/search/collection
```

### Dépendances Python
```bash
pip install pymongo python-dotenv requests
```

## Utilisation

```bash
python ManipDB.py
```

## Structure du code

### Fonctions principales

#### `connect_mongodb()`
- Établit la connexion à MongoDB Atlas
- Teste la connexion avec la commande `ping`
- Retourne le client MongoDB ou None en cas d'erreur

#### `fetch_rijksmuseum_data(max_pages=None)`
- Récupère les données de l'API Rijksmuseum
- **Paramètres :**
  - `max_pages` : Nombre maximum de pages à récupérer (None = toutes)
- Gère la pagination automatiquement via les tokens
- Retourne une liste d'objets (identifiants LOD)

#### `insert_to_mongodb(client, data, db_name, collection_name)`
- Insère les données dans MongoDB
- **Paramètres :**
  - `client` : Client MongoDB
  - `data` : Liste des documents à insérer
  - `db_name` : Nom de la base de données (défaut: 'sample_mflix')
  - `collection_name` : Nom de la collection (défaut: 'rijksmuseum')

#### `main()`
- Fonction principale qui orchestre le workflow :
  1. Connexion à MongoDB
  2. Récupération de 100 entrées (1 page)
  3. Insertion dans MongoDB
  4. Fermeture de la connexion

## Format des données

Les données récupérées suivent le format **Linked Art Search** :
```json
{
    "id": "https://id.rijksmuseum.nl/200100988",
    "type": "HumanMadeObject"
}
```

Chaque objet contient :
- `id` : Identifiant LOD (Linked Open Data) de l'objet
- `type` : Type de l'objet (généralement "HumanMadeObject")

## Notes importantes

- La collection Rijksmuseum complète contient ~836,000 objets (8,359 pages)
- Le script est actuellement configuré pour ne récupérer que **100 entrées** (1 page)
- Pour récupérer plus de données, modifier `max_pages = 1` dans la fonction `main()`
- Les identifiants LOD peuvent être résolus via le Persistent Identifier Resolver du Rijksmuseum pour obtenir des détails complets

## Exemple de sortie

```
🔄 Connecting to MongoDB Atlas...
✅ Successfully connected to MongoDB Atlas!

📌 Configured to fetch 1 page (100 entries)

🎨 Starting to fetch data from Rijksmuseum API...
   (Limited to 1 pages = 100 items max)

📄 Fetching page 1...
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
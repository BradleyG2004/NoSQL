# API Polymarket Cleaned Data

API REST avec FastAPI pour gérer la collection `cleaned` de Polymarket dans MongoDB.

## 🚀 Fonctionnalités

### CRUD complet:
- ✅ **CREATE** - Créer de nouveaux événements (ID auto-généré)
- ✅ **READ** - Lire les événements (pagination par page avec métadonnées)
- ✅ **UPDATE** - Mettre à jour des événements existants
- ✅ **DELETE** - Supprimer des événements

### Endpoints supplémentaires:
- 📊 Statistiques de la collection
- 🏷️ Liste des catégories
- 🔍 Recherche par slug
- 🔎 Recherche textuelle dans titre/description

### Caractéristiques:
- 🆔 **Génération automatique d'ID** (UUID v4)
- 📄 **Pagination intelligente** avec métadonnées (total_count, total_pages, has_next, has_prev)
- 🏷️ **Validation stricte des catégories** (Sports, Crypto, Pop-Culture uniquement)

## 📦 Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

Assurez-vous que votre fichier `.env` contient:
```env
MONGO_URI=mongodb+srv://...
DB2=nom_de_votre_base
```

## 🏃 Lancement

```bash
# Lancer le serveur
uvicorn main:app --reload

# Ou avec un port spécifique
uvicorn main:app --reload --port 8000
```

## 📖 Documentation API

Une fois le serveur lancé, accédez à:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 Endpoints

### Events

#### GET /events
Liste tous les événements avec pagination

**Paramètres de requête:**
- `page` (int, défaut=1): Numéro de la page (commence à 1)
- `per_page` (int, défaut=10, max=100): Nombre d'enregistrements par page
- `category` (string, optionnel): Filtrer par catégorie (Sports, Crypto ou Pop-Culture)
- `search` (string, optionnel): Rechercher dans titre/description

**Exemple:**
```bash
curl "http://localhost:8000/events?page=1&per_page=10&category=Sports"
```

**Réponse:**
```json
{
  "page": 1,
  "per_page": 10,
  "total_count": 100,
  "total_pages": 10,
  "has_next": true,
  "has_prev": false,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "id": "uuid-generated",
      "category": "Sports",
      "title": "Event Title",
      ...
    }
  ]
}
```

#### GET /events/{event_id}
Récupère un événement par son ID MongoDB

**Exemple:**
```bash
curl "http://localhost:8000/events/507f1f77bcf86cd799439011"
```

#### GET /events/slug/{slug}
Récupère un événement par son slug

**Exemple:**
```bash
curl "http://localhost:8000/events/slug/trump-2024-election"
```

#### POST /events
Crée un nouvel événement

**Notes importantes:**
- L'ID est **généré automatiquement** (UUID v4) - ne pas le fournir
- `category` doit être: **"Sports"**, **"Crypto"** ou **"Pop-Culture"**

**Exemple:**
```bash
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Sports",
    "closedTime": "2026-02-01T00:00:00Z",
    "commentCount": 42,
    "createdAt": "2026-01-01T00:00:00Z",
    "creationDate": "2026-01-01",
    "description": "Will X happen?",
    "endDate": "2026-02-01T00:00:00Z",
    "icon": "https://example.com/icon.png",
    "image": "https://example.com/image.png",
    "published_at": "2026-01-01T00:00:00Z",
    "resolutionSource": "Official Source",
    "seriesSlug": "series-name",
    "slug": "event-slug",
    "startDate": "2026-01-01T00:00:00Z",
    "ticker": "TICK",
    "title": "Event Title",
    "updatedAt": "2026-01-15T00:00:00Z",
    "volume": 1000000.50
  }'
```

#### PUT /events/{event_id}
Met à jour un événement (mise à jour partielle)

**Exemple:**
```bash
curl -X PUT "http://localhost:8000/events/507f1f77bcf86cd799439011" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nouveau titre",
    "commentCount": 100
  }'
```

#### DELETE /events/{event_id}
Supprime un événement

**Exemple:**
```bash
curl -X DELETE "http://localhost:8000/events/507f1f77bcf86cd799439011"
```

### Statistics

#### GET /stats
Récupère des statistiques globales

**Exemple:**
```bash
curl "http://localhost:8000/stats"
```

**Réponse:**
```json
{
  "total_events": 100,
  "categories": [
    {"_id": "politics", "count": 45},
    {"_id": "sports", "count": 30},
    {"_id": "crypto", "count": 25}
  ],
  "volume_statistics": {
    "total_volume": 50000000,
    "avg_volume": 500000,
    "min_volume": 1000,
    "max_volume": 5000000
  }
}
```

#### GET /categories
Liste toutes les catégories disponibles

**Exemple:**
```bash
curl "http://localhost:8000/categories"
```

## 📁 Structure du projet

```
API/
├── main.py           # Application FastAPI principale
├── models.py         # Modèles Pydantic
├── database.py       # Configuration MongoDB
├── requirements.txt  # Dépendances Python
└── README.md        # Documentation
```

## 🔒 Schéma des données

Chaque événement dans la collection `cleaned` contient:

- `_id` (ObjectId): ID MongoDB
- `id` (string): ID unique de l'événement (généré automatiquement - UUID v4)
- `category` (string): Catégorie de l'événement (**Sports**, **Crypto** ou **Pop-Culture**)
- `closedTime` (string): Heure de clôture
- `commentCount` (int): Nombre de commentaires
- `createdAt` (string): Date de création
- `creationDate` (string): Date de création
- `description` (string): Description de l'événement
- `endDate` (string): Date de fin
- `icon` (string): URL de l'icône
- `image` (string): URL de l'image
- `published_at` (string): Date de publication
- `resolutionSource` (string): Source de résolution
- `seriesSlug` (string): Slug de la série
- `slug` (string): Slug unique de l'événement
- `startDate` (string): Date de début
- `ticker` (string): Symbole ticker
- `title` (string): Titre de l'événement
- `updatedAt` (string): Dernière mise à jour
- `volume` (float): Volume de trading

## 🛠️ Technologies

- **FastAPI**: Framework web moderne et rapide
- **PyMongo**: Driver MongoDB pour Python
- **Pydantic**: Validation des données
- **Uvicorn**: Serveur ASGI

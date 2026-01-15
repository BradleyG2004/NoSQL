from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from bson.errors import InvalidId
import uuid

from models import (
    PolymarketEvent,
    PolymarketEventInDB,
    PolymarketEventUpdate,
    ResponseModel
)
from database import (
    connect_to_mongodb,
    close_mongodb_connection,
    get_collection
)

# Initialize FastAPI app
app = FastAPI(
    title="Polymarket Cleaned Data API",
    description="API CRUD pour la collection cleaned de Polymarket",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    try:
        connect_to_mongodb()
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    close_mongodb_connection()


# Helper function to serialize MongoDB document
def serialize_document(doc) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint"""
    return {
        "message": "Bienvenue sur l'API Polymarket Cleaned Data",
        "version": "1.0.0",
        "endpoints": {
            "GET /events": "Liste tous les événements",
            "GET /events/{event_id}": "Récupère un événement par ID MongoDB",
            "GET /events/slug/{slug}": "Récupère un événement par slug",
            "POST /events": "Crée un nouvel événement",
            "PUT /events/{event_id}": "Met à jour un événement",
            "DELETE /events/{event_id}": "Supprime un événement",
            "GET /stats": "Statistiques de la collection"
        }
    }


@app.get("/events", response_model=dict, tags=["Events"])
async def get_all_events(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Number of records per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title or description")
):
    """
    Récupère tous les événements avec pagination et filtres optionnels
    
    - **page**: Numéro de la page (commence à 1)
    - **per_page**: Nombre d'enregistrements par page (max 100)
    - **category**: Filtrer par catégorie
    - **search**: Recherche dans le titre ou la description
    """
    try:
        collection = get_collection()
        
        # Build filter query
        query = {}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Calculate pagination
        total_count = collection.count_documents(query)
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
        skip = (page - 1) * per_page
        
        # Get events with pagination
        events = list(collection.find(query).skip(skip).limit(per_page))
        
        # Serialize documents
        events = [serialize_document(event) for event in events]
        
        return {
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "data": events
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching events: {str(e)}"
        )


@app.get("/events/{event_id}", response_model=dict, tags=["Events"])
async def get_event_by_id(event_id: str):
    """
    Récupère un événement par son ID MongoDB
    
    - **event_id**: L'ID MongoDB de l'événement (format: 24 caractères hexadécimaux)
    """
    try:
        collection = get_collection()
        
        # Validate ObjectId
        try:
            object_id = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format. Must be a 24-character hex string."
            )
        
        # Find event
        event = collection.find_one({"_id": object_id})
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        return serialize_document(event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching event: {str(e)}"
        )


@app.get("/events/slug/{slug}", response_model=dict, tags=["Events"])
async def get_event_by_slug(slug: str):
    """
    Récupère un événement par son slug
    
    - **slug**: Le slug unique de l'événement
    """
    try:
        collection = get_collection()
        
        # Find event by slug
        event = collection.find_one({"slug": slug})
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with slug '{slug}' not found"
            )
        
        return serialize_document(event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching event: {str(e)}"
        )


@app.post("/events", response_model=ResponseModel, status_code=status.HTTP_201_CREATED, tags=["Events"])
async def create_event(event: PolymarketEvent):
    """
    Crée un nouvel événement
    
    Le corps de la requête doit contenir tous les champs obligatoires selon le schéma.
    L'ID est généré automatiquement.
    Category doit être: Sports, Crypto ou Pop-Culture
    """
    try:
        collection = get_collection()
        
        # Generate unique ID if not provided
        if not event.id:
            event.id = str(uuid.uuid4())
        
        # Check if event with same ID already exists
        existing = collection.find_one({"id": event.id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event with ID {event.id} already exists"
            )
        
        # Insert new event
        event_dict = event.model_dump()
        result = collection.insert_one(event_dict)
        
        return ResponseModel(
            success=True,
            message="Event created successfully",
            data={
                "_id": str(result.inserted_id),
                "id": event.id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating event: {str(e)}"
        )


@app.put("/events/{event_id}", response_model=ResponseModel, tags=["Events"])
async def update_event(event_id: str, event_update: PolymarketEventUpdate):
    """
    Met à jour un événement existant
    
    - **event_id**: L'ID MongoDB de l'événement à mettre à jour
    - Seuls les champs fournis dans le corps de la requête seront mis à jour
    """
    try:
        collection = get_collection()
        
        # Validate ObjectId
        try:
            object_id = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format. Must be a 24-character hex string."
            )
        
        # Check if event exists
        existing = collection.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Prepare update data (exclude None values)
        update_data = {k: v for k, v in event_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update event
        result = collection.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        return ResponseModel(
            success=True,
            message=f"Event updated successfully. {result.modified_count} field(s) modified.",
            data={
                "_id": event_id,
                "modified_count": result.modified_count
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating event: {str(e)}"
        )


@app.delete("/events/{event_id}", response_model=ResponseModel, tags=["Events"])
async def delete_event(event_id: str):
    """
    Supprime un événement
    
    - **event_id**: L'ID MongoDB de l'événement à supprimer
    """
    try:
        collection = get_collection()
        
        # Validate ObjectId
        try:
            object_id = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format. Must be a 24-character hex string."
            )
        
        # Delete event
        result = collection.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        return ResponseModel(
            success=True,
            message="Event deleted successfully",
            data={"_id": event_id, "deleted_count": result.deleted_count}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting event: {str(e)}"
        )


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """
    Récupère des statistiques sur la collection
    """
    try:
        collection = get_collection()
        
        # Count total documents
        total_events = collection.count_documents({})
        
        # Count by category
        categories = collection.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        categories_list = list(categories)
        
        # Get volume statistics
        volume_stats = collection.aggregate([
            {
                "$group": {
                    "_id": None,
                    "total_volume": {"$sum": "$volume"},
                    "avg_volume": {"$avg": "$volume"},
                    "min_volume": {"$min": "$volume"},
                    "max_volume": {"$max": "$volume"}
                }
            }
        ])
        volume_stats_list = list(volume_stats)
        
        return {
            "total_events": total_events,
            "categories": categories_list,
            "volume_statistics": volume_stats_list[0] if volume_stats_list else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )


@app.get("/categories", tags=["Statistics"])
async def get_categories():
    """
    Récupère la liste de toutes les catégories disponibles
    """
    try:
        collection = get_collection()
        
        # Get distinct categories
        categories = collection.distinct("category")
        
        return {
            "categories": sorted(categories),
            "count": len(categories)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )
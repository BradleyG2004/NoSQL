from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, Literal
from datetime import datetime
import uuid


class PolymarketEvent(BaseModel):
    """Model for Polymarket event in cleaned collection"""
    id: Optional[str] = Field(None, description="Event ID (auto-generated if not provided)")
    category: Literal["Sports", "Crypto", "Pop-Culture"] = Field(..., description="Event category")
    closedTime: str = Field(..., description="Time when event closed")
    commentCount: int = Field(..., description="Number of comments")
    createdAt: str = Field(..., description="Creation timestamp")
    creationDate: str = Field(..., description="Creation date")
    description: str = Field(..., description="Event description")
    endDate: str = Field(..., description="End date")
    icon: str = Field(..., description="Icon URL")
    image: str = Field(..., description="Image URL")
    published_at: str = Field(..., description="Publication timestamp")
    resolutionSource: str = Field(..., description="Resolution source")
    seriesSlug: str = Field(..., description="Series slug")
    slug: str = Field(..., description="Event slug")
    startDate: str = Field(..., description="Start date")
    ticker: str = Field(..., description="Ticker symbol")
    title: str = Field(..., description="Event title")
    updatedAt: str = Field(..., description="Last update timestamp")
    volume: float = Field(..., description="Trading volume")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "event123",
                "category": "politics",
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
            }
        }


class PolymarketEventInDB(PolymarketEvent):
    """Model for Polymarket event as stored in MongoDB"""
    mongodb_id: Optional[str] = Field(None, alias="_id", description="MongoDB ObjectId")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "id": "event123",
                "category": "politics",
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
            }
        }


class PolymarketEventUpdate(BaseModel):
    """Model for updating a Polymarket event (all fields optional)"""
    id: Optional[str] = None
    category: Optional[Literal["Sports", "Crypto", "Pop-Culture"]] = None
    closedTime: Optional[str] = None
    commentCount: Optional[int] = None
    createdAt: Optional[str] = None
    creationDate: Optional[str] = None
    description: Optional[str] = None
    endDate: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    published_at: Optional[str] = None
    resolutionSource: Optional[str] = None
    seriesSlug: Optional[str] = None
    slug: Optional[str] = None
    startDate: Optional[str] = None
    ticker: Optional[str] = None
    title: Optional[str] = None
    updatedAt: Optional[str] = None
    volume: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Event Title",
                "description": "Updated description",
                "commentCount": 50
            }
        }


class ResponseModel(BaseModel):
    """Standard response model"""
    success: bool
    message: str
    data: Optional[dict] = None

"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class ArticleBase(BaseModel):
    """Base article schema."""
    source: str
    title: str
    content: str
    category: Optional[str] = None
    url: str
    published_at: Optional[datetime] = None


class ArticleCreate(ArticleBase):
    """Schema for creating articles."""
    pass


class ArticleResponse(ArticleBase):
    """Schema for article responses."""
    id: int
    scraped_at: datetime
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    
    class Config:
        from_attributes = True


class ArticleFilter(BaseModel):
    """Schema for filtering articles."""
    source: Optional[str] = None
    category: Optional[str] = None
    sentiment_label: Optional[str] = None
    limit: int = 50
    offset: int = 0

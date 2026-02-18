"""FastAPI application for Maghrib News Aggregator."""
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger

from database import get_db, init_db
from models import Article
from schemas import ArticleResponse, ArticleFilter
from service import ScrapingService
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Maghrib News Aggregator",
    description="API pour agréger et normaliser les actualités marocaines",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraping service
scraping_service = ScrapingService(use_sentiment=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Maghrib News Aggregator API...")
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bienvenue à Maghrib News Aggregator API",
        "version": "1.0.0",
        "endpoints": {
            "articles": "/articles",
            "sources": "/sources",
            "categories": "/categories",
            "scrape": "/scrape",
            "stats": "/stats"
        }
    }


@app.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    source: Optional[str] = Query(None, description="Filtrer par source"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    sentiment: Optional[str] = Query(None, description="Filtrer par sentiment (Positif/Négatif/Neutre)"),
    limit: int = Query(50, ge=1, le=100, description="Nombre maximum d'articles"),
    offset: int = Query(0, ge=0, description="Offset pour pagination"),
    db: Session = Depends(get_db)
):
    """
    Récupérer les articles avec filtres optionnels.
    """
    query = db.query(Article)
    
    if source:
        query = query.filter(Article.source == source)
    
    if category:
        query = query.filter(Article.category == category)
    
    if sentiment:
        query = query.filter(Article.sentiment_label == sentiment)
    
    # Order by most recent first
    query = query.order_by(Article.scraped_at.desc())
    
    articles = query.offset(offset).limit(limit).all()
    return articles


@app.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Récupérer un article spécifique par ID.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article


@app.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    """
    Récupérer la liste des sources disponibles avec le nombre d'articles.
    """
    sources = db.query(
        Article.source,
        db.func.count(Article.id).label('count')
    ).group_by(Article.source).all()
    
    return [{"source": s[0], "count": s[1]} for s in sources]


@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """
    Récupérer la liste des catégories disponibles avec le nombre d'articles.
    """
    categories = db.query(
        Article.category,
        db.func.count(Article.id).label('count')
    ).filter(Article.category.isnot(None)).group_by(Article.category).all()
    
    return [{"category": c[0], "count": c[1]} for c in categories]


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Récupérer les statistiques globales.
    """
    total_articles = db.query(Article).count()
    
    # Articles by source
    by_source = db.query(
        Article.source,
        db.func.count(Article.id).label('count')
    ).group_by(Article.source).all()
    
    # Articles by sentiment
    by_sentiment = db.query(
        Article.sentiment_label,
        db.func.count(Article.id).label('count')
    ).filter(Article.sentiment_label.isnot(None)).group_by(Article.sentiment_label).all()
    
    # Recent articles (last 24h)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_count = db.query(Article).filter(Article.scraped_at >= yesterday).count()
    
    return {
        "total_articles": total_articles,
        "recent_articles_24h": recent_count,
        "by_source": {s[0]: s[1] for s in by_source},
        "by_sentiment": {s[0]: s[1] for s in by_sentiment if s[0]}
    }


@app.post("/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    source: Optional[str] = Query(None, description="Source spécifique à scraper"),
    max_articles: Optional[int] = Query(None, ge=1, le=100, description="Maximum d'articles par source"),
    db: Session = Depends(get_db)
):
    """
    Déclencher le scraping manuellement.
    """
    def scrape_task():
        if source:
            result = scraping_service.scrape_source(db, source, max_articles)
        else:
            result = scraping_service.scrape_all(db, max_articles)
        logger.info(f"Scraping task completed: {result}")
    
    background_tasks.add_task(scrape_task)
    
    return {
        "message": "Scraping démarré en arrière-plan",
        "source": source or "all",
        "status": "processing"
    }


@app.get("/search")
async def search_articles(
    q: str = Query(..., min_length=3, description="Terme de recherche"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Rechercher des articles par mot-clé.
    """
    articles = db.query(Article).filter(
        db.or_(
            Article.title.contains(q),
            Article.content.contains(q)
        )
    ).order_by(Article.scraped_at.desc()).limit(limit).all()
    
    return articles


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )

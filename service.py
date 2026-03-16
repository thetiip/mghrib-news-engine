"""Scraping service to orchestrate all spiders."""
from typing import List
from loguru import logger
from sqlalchemy.orm import Session
from spiders import (
    HespressSpider, Le360Spider, Medias24Spider,
    ElbotolaSpider, TelQuelSpider, YabiladiSpider,
)
from models import Article
from sentiment import SentimentAnalyzer, SimpleSentimentAnalyzer
from cleaner import ContentCleaner
from config import settings


class ScrapingService:
    """Service to manage scraping operations."""
    
    def __init__(self, use_sentiment: bool = True):
        """Initialize scraping service."""
        self.spiders = [
            HespressSpider(),
            Le360Spider(),
            Medias24Spider(),
            ElbotolaSpider(),
            TelQuelSpider(),
            YabiladiSpider(),
        ]
        self.use_sentiment = use_sentiment
        
        if use_sentiment:
            try:
                self.sentiment_analyzer = SentimentAnalyzer()
                self.sentiment_analyzer.initialize()
            except Exception as e:
                logger.warning(f"Failed to load advanced sentiment analyzer: {e}")
                logger.info("Using simple sentiment analyzer as fallback")
                self.sentiment_analyzer = SimpleSentimentAnalyzer()
        else:
            self.sentiment_analyzer = None
        
        self.cleaner = ContentCleaner()
    
    def scrape_all(self, db: Session, max_articles_per_source: int = None) -> dict:
        """
        Scrape all news sources.
        
        Args:
            db: Database session
            max_articles_per_source: Maximum articles per source
            
        Returns:
            Dictionary with scraping statistics
        """
        if max_articles_per_source is None:
            max_articles_per_source = settings.max_articles_per_source
        
        stats = {
            "total_scraped": 0,
            "total_saved": 0,
            "total_updated": 0,
            "by_source": {}
        }
        
        for spider in self.spiders:
            logger.info(f"Scraping {spider.source_name}...")
            
            try:
                articles = spider.scrape(max_articles=max_articles_per_source)
                scraped_count = len(articles)
                saved_count = 0
                updated_count = 0
                
                for article_data in articles:
                    # Add sentiment analysis if enabled
                    if self.sentiment_analyzer and article_data.get('content'):
                        sentiment = self.sentiment_analyzer.analyze(
                            article_data['title'] + ' ' + article_data['content'][:500]
                        )
                        if sentiment:
                            article_data['sentiment_score'] = sentiment['sentiment_score']
                            article_data['sentiment_label'] = sentiment['sentiment_label']
                    
                    # Check if article already exists
                    existing = db.query(Article).filter(Article.url == article_data['url']).first()
                    
                    if existing:
                        # Update existing article
                        for key, value in article_data.items():
                            setattr(existing, key, value)
                        updated_count += 1
                    else:
                        # Create new article
                        article = Article(**article_data)
                        db.add(article)
                        saved_count += 1
                
                db.commit()
                
                stats["by_source"][spider.source_name] = {
                    "scraped": scraped_count,
                    "saved": saved_count,
                    "updated": updated_count
                }
                stats["total_scraped"] += scraped_count
                stats["total_saved"] += saved_count
                stats["total_updated"] += updated_count
                
                logger.info(f"{spider.source_name}: {scraped_count} scraped, {saved_count} saved, {updated_count} updated")
            
            except Exception as e:
                logger.error(f"Error scraping {spider.source_name}: {str(e)}")
                stats["by_source"][spider.source_name] = {
                    "error": str(e)
                }
        
        logger.info(f"Scraping completed: {stats['total_scraped']} total articles, {stats['total_saved']} saved, {stats['total_updated']} updated")
        return stats
    
    def scrape_source(self, db: Session, source_name: str, max_articles: int = None) -> dict:
        """
        Scrape a specific source.
        
        Args:
            db: Database session
            source_name: Name of the source
            max_articles: Maximum articles to scrape
            
        Returns:
            Dictionary with scraping statistics
        """
        if max_articles is None:
            max_articles = settings.max_articles_per_source
        
        spider = None
        for s in self.spiders:
            if s.source_name.lower() == source_name.lower():
                spider = s
                break
        
        if not spider:
            raise ValueError(f"Unknown source: {source_name}")
        
        logger.info(f"Scraping {spider.source_name}...")
        articles = spider.scrape(max_articles=max_articles)
        
        saved_count = 0
        updated_count = 0
        
        for article_data in articles:
            # Add sentiment analysis if enabled
            if self.sentiment_analyzer and article_data.get('content'):
                sentiment = self.sentiment_analyzer.analyze(
                    article_data['title'] + ' ' + article_data['content'][:500]
                )
                if sentiment:
                    article_data['sentiment_score'] = sentiment['sentiment_score']
                    article_data['sentiment_label'] = sentiment['sentiment_label']
            
            # Check if article already exists
            existing = db.query(Article).filter(Article.url == article_data['url']).first()
            
            if existing:
                for key, value in article_data.items():
                    setattr(existing, key, value)
                updated_count += 1
            else:
                article = Article(**article_data)
                db.add(article)
                saved_count += 1
        
        db.commit()
        
        return {
            "source": spider.source_name,
            "scraped": len(articles),
            "saved": saved_count,
            "updated": updated_count
        }

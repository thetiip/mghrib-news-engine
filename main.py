"""Main entry point for the Maghrib News Aggregator."""
import sys
from loguru import logger
from database import init_db, SessionLocal
from service import ScrapingService
from config import settings

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level=settings.log_level
)


def main():
    """Main function to run the scraper."""
    logger.info("=== Maghrib News Aggregator ===")
    
    # Initialize database
    init_db()
    
    # Create scraping service
    scraping_service = ScrapingService(use_sentiment=True)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Run scraping
        logger.info("Starting scraping process...")
        stats = scraping_service.scrape_all(db)
        
        logger.info("=== Scraping Statistics ===")
        logger.info(f"Total articles scraped: {stats['total_scraped']}")
        logger.info(f"Total articles saved: {stats['total_saved']}")
        logger.info(f"Total articles updated: {stats['total_updated']}")
        
        for source, source_stats in stats['by_source'].items():
            if 'error' in source_stats:
                logger.error(f"{source}: Error - {source_stats['error']}")
            else:
                logger.info(f"{source}: {source_stats['scraped']} scraped, {source_stats['saved']} saved, {source_stats['updated']} updated")
        
        logger.info("Scraping completed successfully!")
    
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

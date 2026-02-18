"""Scheduled scraping task for continuous operation."""
import schedule
import time
from loguru import logger
from database import init_db, SessionLocal
from service import ScrapingService
from config import settings


def scrape_job():
    """Job to run scraping."""
    logger.info("Running scheduled scraping job...")
    
    db = SessionLocal()
    scraping_service = ScrapingService(use_sentiment=True)
    
    try:
        stats = scraping_service.scrape_all(db)
        logger.info(f"Scheduled scraping completed: {stats['total_scraped']} articles scraped")
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")
    finally:
        db.close()


def main():
    """Run the scheduler."""
    logger.info("Starting Maghrib News Aggregator Scheduler...")
    logger.info(f"Scraping interval: {settings.scraping_interval} seconds")
    
    # Initialize database
    init_db()
    
    # Schedule the job
    interval_minutes = settings.scraping_interval // 60
    schedule.every(interval_minutes).minutes.do(scrape_job)
    
    # Run immediately on startup
    scrape_job()
    
    # Run scheduler
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    main()

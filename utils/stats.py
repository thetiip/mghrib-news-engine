"""Statistics and reporting utilities."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Article
from loguru import logger


class StatsReporter:
    """Generate statistics and reports."""
    
    def __init__(self, db: Session):
        """Initialize stats reporter with database session."""
        self.db = db
    
    def get_daily_stats(self) -> dict:
        """Get statistics for the last 24 hours."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        total_today = self.db.query(Article).filter(
            Article.scraped_at >= yesterday
        ).count()
        
        by_source = {}
        sources = self.db.query(Article.source).distinct().all()
        
        for (source,) in sources:
            count = self.db.query(Article).filter(
                Article.source == source,
                Article.scraped_at >= yesterday
            ).count()
            by_source[source] = count
        
        return {
            "period": "24h",
            "total_articles": total_today,
            "by_source": by_source,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_sentiment_distribution(self) -> dict:
        """Get sentiment distribution across all articles."""
        sentiments = self.db.query(
            Article.sentiment_label,
            self.db.func.count(Article.id)
        ).filter(
            Article.sentiment_label.isnot(None)
        ).group_by(Article.sentiment_label).all()
        
        return {label: count for label, count in sentiments}
    
    def get_trending_categories(self, limit: int = 10) -> list:
        """Get trending categories."""
        categories = self.db.query(
            Article.category,
            self.db.func.count(Article.id).label('count')
        ).filter(
            Article.category.isnot(None)
        ).group_by(Article.category).order_by(
            self.db.text('count DESC')
        ).limit(limit).all()
        
        return [{"category": cat, "count": count} for cat, count in categories]
    
    def generate_daily_report(self) -> str:
        """Generate a daily report in text format."""
        stats = self.get_daily_stats()
        sentiment = self.get_sentiment_distribution()
        trending = self.get_trending_categories(5)
        
        report = f"""
=== RAPPORT QUOTIDIEN - Maghrib News Aggregator ===
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

📊 STATISTIQUES DES DERNIÈRES 24H:
- Total d'articles collectés: {stats['total_articles']}

Par source:
"""
        for source, count in stats['by_source'].items():
            report += f"  - {source}: {count} articles\n"
        
        report += f"""
😊 DISTRIBUTION DU SENTIMENT:
"""
        for label, count in sentiment.items():
            report += f"  - {label}: {count} articles\n"
        
        report += f"""
🔥 TOP 5 CATÉGORIES:
"""
        for item in trending:
            report += f"  - {item['category']}: {item['count']} articles\n"
        
        report += "\n" + "="*50
        
        return report
    
    def log_daily_report(self):
        """Log the daily report."""
        report = self.generate_daily_report()
        logger.info("\n" + report)
        return report


# Example usage:
# from database import SessionLocal
# db = SessionLocal()
# reporter = StatsReporter(db)
# report = reporter.generate_daily_report()
# print(report)

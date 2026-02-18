"""Quick demo script to test the aggregator."""
import sys
from loguru import logger
from database import init_db, SessionLocal
from spiders import HespressSpider
from service import ScrapingService

# Configure simple logging
logger.remove()
logger.add(sys.stderr, format="<level>{message}</level>", level="INFO")


def demo():
    """Run a quick demo of the aggregator."""
    print("=" * 60)
    print("🇲🇦 MAGHRIB NEWS AGGREGATOR - QUICK DEMO")
    print("=" * 60)
    print()
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    print("✅ Database ready\n")
    
    # Test single spider
    print("🕷️  Testing Hespress spider...")
    spider = HespressSpider()
    print(f"   Source: {spider.source_name}")
    print(f"   RSS URL: {spider.rss_url}")
    print()
    
    # Get a few article URLs
    print("🔍 Fetching article URLs...")
    urls = spider.get_article_urls(max_articles=3)
    print(f"✅ Found {len(urls)} articles\n")
    
    # Parse first article
    if urls:
        print("📰 Parsing first article...")
        article = spider.parse_article(urls[0])
        if article:
            print(f"   Title: {article['title'][:80]}...")
            print(f"   Category: {article.get('category', 'N/A')}")
            print(f"   Content length: {len(article['content'])} characters")
            print()
    
    # Test full scraping (limited)
    print("🚀 Running full scraping test (5 articles max per source)...")
    service = ScrapingService(use_sentiment=False)  # Skip sentiment for demo speed
    db = SessionLocal()
    
    try:
        stats = service.scrape_all(db, max_articles_per_source=5)
        print()
        print("=" * 60)
        print("📊 SCRAPING RESULTS")
        print("=" * 60)
        print(f"Total scraped: {stats['total_scraped']}")
        print(f"Total saved: {stats['total_saved']}")
        print(f"Total updated: {stats['total_updated']}")
        print()
        print("By source:")
        for source, source_stats in stats['by_source'].items():
            if 'error' in source_stats:
                print(f"  ❌ {source}: {source_stats['error']}")
            else:
                print(f"  ✅ {source}: {source_stats['scraped']} scraped, "
                      f"{source_stats['saved']} saved")
        print()
        
        # Show sample articles
        from models import Article
        articles = db.query(Article).limit(3).all()
        
        if articles:
            print("=" * 60)
            print("📰 SAMPLE ARTICLES")
            print("=" * 60)
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. [{article.source}] {article.title[:60]}...")
                print(f"   Category: {article.category or 'N/A'}")
                print(f"   URL: {article.url}")
        
        print()
        print("=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run 'python api.py' to start the API server")
        print("  2. Visit http://localhost:8000/docs for API documentation")
        print("  3. Run 'python main.py' for full scraping")
        print()
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    demo()

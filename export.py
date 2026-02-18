"""Export articles to JSON file."""
import json
from datetime import datetime
from database import SessionLocal
from models import Article
from loguru import logger


def export_to_json(output_file: str = "data/articles.json"):
    """
    Export all articles to JSON file.
    
    Args:
        output_file: Output file path
    """
    logger.info("Exporting articles to JSON...")
    
    db = SessionLocal()
    
    try:
        articles = db.query(Article).order_by(Article.scraped_at.desc()).all()
        
        articles_data = [article.to_dict() for article in articles]
        
        # Create output directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported {len(articles_data)} articles to {output_file}")
    
    except Exception as e:
        logger.error(f"Error exporting to JSON: {str(e)}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    export_to_json()

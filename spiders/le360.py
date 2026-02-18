"""Le360 news spider."""
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
from loguru import logger
from .base import BaseSpider


class Le360Spider(BaseSpider):
    """Spider for Le360 news site."""
    
    def __init__(self):
        """Initialize Le360 spider."""
        super().__init__("Le360")
        self.rss_url = "https://fr.le360.ma/rss"
        self.base_url = "https://fr.le360.ma"
    
    def get_article_urls(self, max_articles: int = 50) -> List[str]:
        """Get article URLs from RSS feed."""
        try:
            feed = feedparser.parse(self.rss_url)
            urls = [entry.link for entry in feed.entries[:max_articles]]
            return urls
        except Exception as e:
            logger.error(f"Error fetching Le360 RSS feed: {str(e)}")
            return []
    
    def get_category(self, article_soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract category from article."""
        # Try meta category
        meta_cat = article_soup.find('meta', property='article:section')
        if meta_cat and meta_cat.get('content'):
            return meta_cat['content']
        
        # Try from URL structure
        parts = url.split('/')
        for part in parts:
            if part in ['politique', 'economie', 'sport', 'tech', 'societe', 'culture']:
                return part.title()
        
        return "Actualité"
    
    def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a single Le360 article."""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # Extract title
            title_elem = soup.find('h1', class_='article-title') or soup.find('h1')
            if not title_elem:
                logger.warning(f"No title found for {url}")
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract content
            content_elem = soup.find('div', class_='article-body') or soup.find('div', class_='article-content')
            if not content_elem:
                # Try to find main content
                content_elem = soup.find('article') or soup.find('div', class_='content')
            
            if not content_elem:
                logger.warning(f"No content found for {url}")
                return None
            
            # Clean content
            for unwanted in content_elem.find_all(['script', 'style', 'iframe', 'ins', 'aside', 'figure']):
                unwanted.decompose()
            
            # Remove ads and related articles
            for ad_class in ['pub', 'publicite', 'advertisement', 'related-articles']:
                for ad in content_elem.find_all(class_=lambda x: x and ad_class in x.lower()):
                    ad.decompose()
            
            content = content_elem.get_text(separator='\n', strip=True)
            
            # Extract publish date
            date_elem = soup.find('time') or soup.find('meta', property='article:published_time')
            published_at = None
            
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get('content')
                if date_str:
                    try:
                        published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        pass
            
            # Get category
            category = self.get_category(soup, url)
            
            return self.normalize_article(
                title=title,
                content=content,
                url=url,
                category=category,
                published_at=published_at
            )
        
        except Exception as e:
            logger.error(f"Error parsing Le360 article {url}: {str(e)}")
            return None

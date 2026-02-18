"""Hespress news spider."""
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
from loguru import logger
from .base import BaseSpider


class HespressSpider(BaseSpider):
    """Spider for Hespress news site."""
    
    def __init__(self):
        """Initialize Hespress spider."""
        super().__init__("Hespress")
        self.rss_url = "https://www.hespress.com/feed"
        self.base_url = "https://www.hespress.com"
        self.rss_entries = {}  # Cache RSS entries
    
    def get_article_urls(self, max_articles: int = 50) -> List[str]:
        """Get article URLs from RSS feed."""
        try:
            feed = feedparser.parse(self.rss_url)
            # Store RSS entries for later use
            self.rss_entries = {entry.link: entry for entry in feed.entries[:max_articles]}
            urls = list(self.rss_entries.keys())
            return urls
        except Exception as e:
            logger.error(f"Error fetching Hespress RSS feed: {str(e)}")
            return []
    
    def get_category(self, article_soup: Optional[BeautifulSoup], url: str) -> Optional[str]:
        """Extract category from article."""
        if article_soup:
            # Try to get category from breadcrumb
            breadcrumb = article_soup.find('div', class_='breadcrumb')
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if len(links) > 1:
                    return links[1].get_text(strip=True)
        
        # Try to get from URL
        parts = url.split('/')
        if len(parts) > 3:
            category = parts[3]
            return category.replace('-', ' ').title()
        
        return "Général"
    
    def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a single Hespress article."""
        # Try to use RSS entry first
        if url in self.rss_entries:
            entry = self.rss_entries[url]
            try:
                title = entry.get('title', '').strip()
                # RSS sometimes has content or summary
                content = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
                
                if content:
                    # Clean HTML from RSS content
                    content_soup = BeautifulSoup(content, 'lxml')
                    content = content_soup.get_text(separator='\n', strip=True)
                
                # Get published date from RSS
                published_at = None
                if 'published_parsed' in entry and entry.published_parsed:
                    from time import mktime
                    published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
                
                # Extract category from RSS
                category = None
                if 'tags' in entry and entry.tags:
                    category = entry.tags[0].get('term', None)
                
                if not category:
                    category = self.get_category(None, url)
                
                # If we have title and content from RSS, return it
                if title and content and len(content) > 100:
                    return self.normalize_article(
                        title=title,
                        content=content,
                        url=url,
                        category=category,
                        published_at=published_at
                    )
            except Exception as e:
                logger.debug(f"Could not extract from RSS entry for {url}: {e}")
        
        # Fallback to regular scraping
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # Extract title
            title_elem = soup.find('h1', class_='post-title') or soup.find('h1')
            if not title_elem:
                logger.warning(f"No title found for {url}")
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract content
            content_elem = soup.find('div', class_='article-content') or soup.find('div', class_='entry-content')
            if not content_elem:
                logger.warning(f"No content found for {url}")
                return None
            
            # Clean content - remove scripts, styles, ads
            for unwanted in content_elem.find_all(['script', 'style', 'iframe', 'ins', 'aside']):
                unwanted.decompose()
            
            content = content_elem.get_text(separator='\n', strip=True)
            
            # Extract publish date
            date_elem = soup.find('time', class_='entry-date') or soup.find('time')
            published_at = None
            if date_elem and date_elem.get('datetime'):
                try:
                    published_at = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
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
            logger.error(f"Error parsing Hespress article {url}: {str(e)}")
            return None

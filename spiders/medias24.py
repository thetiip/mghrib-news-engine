"""Médias24 news spider."""
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
from loguru import logger
from .base import BaseSpider


class Medias24Spider(BaseSpider):
    """Spider for Médias24 news site."""
    
    def __init__(self):
        """Initialize Médias24 spider."""
        super().__init__("Médias24")
        self.rss_url = "https://www.medias24.com/rss"
        self.base_url = "https://www.medias24.com"
        self.rss_entries = {}  # Cache RSS entries to avoid re-fetching
    
    def get_article_urls(self, max_articles: int = 50) -> List[str]:
        """Get article URLs from RSS feed or homepage."""
        try:
            # Try RSS first - store entries for later use
            feed = feedparser.parse(self.rss_url)
            if feed.entries:
                # Store RSS entries for extracting content without hitting the site
                self.rss_entries = {entry.link: entry for entry in feed.entries[:max_articles]}
                urls = list(self.rss_entries.keys())
                return urls
            
            # Fallback to homepage scraping
            soup = self.fetch_page(self.base_url)
            if soup:
                links = soup.find_all('a', href=True)
                urls = []
                for link in links:
                    href = link['href']
                    if '/article/' in href or '/news/' in href:
                        if not href.startswith('http'):
                            href = self.base_url + href
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= max_articles:
                                break
                return urls
            
            return []
        except Exception as e:
            logger.error(f"Error fetching Médias24 URLs: {str(e)}")
            return []
    
    def get_category(self, article_soup: Optional[BeautifulSoup], url: str) -> Optional[str]:
        """Extract category from article."""
        if article_soup:
            # Try category tag
            cat_elem = article_soup.find('span', class_='category') or article_soup.find('a', class_='category')
            if cat_elem:
                return cat_elem.get_text(strip=True)
            
            # Try meta tags
            meta_cat = article_soup.find('meta', property='article:section')
            if meta_cat and meta_cat.get('content'):
                return meta_cat['content']
        
        # Try from URL
        if 'economie' in url.lower():
            return "Économie"
        elif 'politique' in url.lower():
            return "Politique"
        elif 'tech' in url.lower():
            return "Tech"
        elif 'finance' in url.lower():
            return "Finance"
        
        return "Économie"  # Default for Médias24
    
    def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a single Médias24 article."""
        # Try to use RSS entry first (avoids 403 errors)
        if url in self.rss_entries:
            entry = self.rss_entries[url]
            try:
                title = entry.get('title', '').strip()
                # RSS sometimes has content or summary
                content = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
                
                if not content:
                    # No content in RSS, we need to fetch the page
                    logger.debug(f"No content in RSS for {url}, fetching page...")
                else:
                    # Clean HTML from RSS content
                    from bs4 import BeautifulSoup
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
        
        # Fallback to regular scraping (may get 403)
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # Extract title
            title_elem = (soup.find('h1', class_='article-title') or 
                         soup.find('h1', class_='post-title') or 
                         soup.find('h1'))
            
            if not title_elem:
                logger.warning(f"No title found for {url}")
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract content
            content_elem = (soup.find('div', class_='article-content') or 
                           soup.find('div', class_='article-body') or
                           soup.find('div', class_='post-content') or
                           soup.find('article'))
            
            if not content_elem:
                logger.warning(f"No content found for {url}")
                return None
            
            # Clean content
            for unwanted in content_elem.find_all(['script', 'style', 'iframe', 'ins', 'aside']):
                unwanted.decompose()
            
            # Remove ads, social shares, related content
            for selector in ['.pub', '.publicite', '.social-share', '.related', '.newsletter']:
                for elem in content_elem.select(selector):
                    elem.decompose()
            
            content = content_elem.get_text(separator='\n', strip=True)
            
            # Extract publish date
            date_elem = (soup.find('time') or 
                        soup.find('span', class_='date') or
                        soup.find('meta', property='article:published_time'))
            
            published_at = None
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get('content') or date_elem.get_text()
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
            logger.error(f"Error parsing Médias24 article {url}: {str(e)}")
            return None

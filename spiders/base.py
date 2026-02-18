"""Base spider class for all news scrapers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import requests
from bs4 import BeautifulSoup


class BaseSpider(ABC):
    """Abstract base class for news spiders."""
    
    def __init__(self, source_name: str):
        """Initialize spider with source name."""
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    @abstractmethod
    def get_article_urls(self, max_articles: int = 50) -> List[str]:
        """
        Get list of article URLs from the source.
        
        Args:
            max_articles: Maximum number of articles to retrieve
            
        Returns:
            List of article URLs
        """
        pass
    
    @abstractmethod
    def parse_article(self, url: str) -> Optional[Dict]:
        """
        Parse a single article from URL.
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary with article data or None if parsing fails
        """
        pass
    
    @abstractmethod
    def get_category(self, article_soup: BeautifulSoup, url: str) -> Optional[str]:
        """
        Extract category from article.
        
        Args:
            article_soup: BeautifulSoup object of the article
            url: Article URL
            
        Returns:
            Category name or None
        """
        pass
    
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a page.
        
        Args:
            url: Page URL
            timeout: Request timeout in seconds
            
        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            # Add referer for better success rate
            headers = {}
            if 'medias24' in url.lower():
                headers['Referer'] = 'https://www.medias24.com/'
            
            response = self.session.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None
    
    def scrape(self, max_articles: int = 50) -> List[Dict]:
        """
        Main scraping method.
        
        Args:
            max_articles: Maximum number of articles to scrape
            
        Returns:
            List of article dictionaries
        """
        logger.info(f"Starting scraping for {self.source_name}...")
        articles = []
        
        try:
            urls = self.get_article_urls(max_articles)
            logger.info(f"Found {len(urls)} article URLs from {self.source_name}")
            
            for url in urls:
                try:
                    article = self.parse_article(url)
                    if article:
                        articles.append(article)
                        logger.debug(f"Successfully scraped: {article['title'][:50]}...")
                except Exception as e:
                    logger.error(f"Error parsing article {url}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} articles from {self.source_name}")
        except Exception as e:
            logger.error(f"Error during scraping {self.source_name}: {str(e)}")
        
        return articles
    
    def normalize_article(self, title: str, content: str, url: str, 
                         category: Optional[str] = None, 
                         published_at: Optional[datetime] = None) -> Dict:
        """
        Normalize article data to standard format.
        
        Args:
            title: Article title
            content: Article content
            url: Article URL
            category: Article category
            published_at: Publication datetime
            
        Returns:
            Normalized article dictionary
        """
        return {
            "source": self.source_name,
            "title": title.strip(),
            "content": content.strip(),
            "category": category,
            "url": url,
            "published_at": published_at
        }

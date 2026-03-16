"""TelQuel news spider."""
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
from loguru import logger
from .base import BaseSpider


class TelQuelSpider(BaseSpider):
    """Spider for TelQuel news site."""

    def __init__(self):
        """Initialize TelQuel spider."""
        super().__init__("TelQuel")
        self.rss_url = "https://telquel.ma/feed/"
        self.base_url = "https://telquel.ma"
        self.rss_entries = {}

    def get_article_urls(self, max_articles: int = 50) -> List[str]:
        """Get article URLs from RSS feed or homepage."""
        try:
            feed = feedparser.parse(self.rss_url)
            if feed.entries:
                self.rss_entries = {entry.link: entry for entry in feed.entries[:max_articles]}
                return list(self.rss_entries.keys())

            # Fallback to homepage scraping
            soup = self.fetch_page(self.base_url)
            if soup:
                urls = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if self.base_url in href and href != self.base_url and href.count('/') > 3:
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= max_articles:
                                break
                return urls

            return []
        except Exception as e:
            logger.error(f"Error fetching TelQuel URLs: {str(e)}")
            return []

    def get_category(self, article_soup: Optional[BeautifulSoup], url: str) -> Optional[str]:
        """Extract category from article."""
        if article_soup:
            meta_cat = article_soup.find('meta', property='article:section')
            if meta_cat and meta_cat.get('content'):
                return meta_cat['content']

            # WordPress-style category tags
            cat_elem = (
                article_soup.find('span', class_='cat-links')
                or article_soup.find('a', rel='category tag')
            )
            if cat_elem:
                return cat_elem.get_text(strip=True)

        # Try from URL structure
        url_lower = url.lower()
        if 'politique' in url_lower:
            return "Politique"
        elif 'economie' in url_lower or 'business' in url_lower:
            return "Économie"
        elif 'societe' in url_lower:
            return "Société"
        elif 'culture' in url_lower:
            return "Culture"
        elif 'sport' in url_lower:
            return "Sport"
        elif 'tech' in url_lower:
            return "Tech"

        return "Société"

    def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a single TelQuel article."""
        # Try RSS entry first
        if url in self.rss_entries:
            entry = self.rss_entries[url]
            try:
                title = entry.get('title', '').strip()
                content = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')

                if content:
                    content_soup = BeautifulSoup(content, 'lxml')
                    content = content_soup.get_text(separator='\n', strip=True)

                published_at = None
                if 'published_parsed' in entry and entry.published_parsed:
                    from time import mktime
                    published_at = datetime.fromtimestamp(mktime(entry.published_parsed))

                category = None
                if 'tags' in entry and entry.tags:
                    category = entry.tags[0].get('term', None)
                if not category:
                    category = self.get_category(None, url)

                if title and content and len(content) > 100:
                    return self.normalize_article(
                        title=title,
                        content=content,
                        url=url,
                        category=category,
                        published_at=published_at,
                    )
            except Exception as e:
                logger.debug(f"Could not extract from RSS entry for {url}: {e}")

        # Fallback to page scraping
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            title_elem = (
                soup.find('h1', class_='entry-title')
                or soup.find('h1', class_='article-title')
                or soup.find('h1', class_='post-title')
                or soup.find('h1')
            )
            if not title_elem:
                logger.warning(f"No title found for {url}")
                return None
            title = title_elem.get_text(strip=True)

            content_elem = (
                soup.find('div', class_='entry-content')
                or soup.find('div', class_='article-content')
                or soup.find('div', class_='post-content')
                or soup.find('article')
            )
            if not content_elem:
                logger.warning(f"No content found for {url}")
                return None

            for unwanted in content_elem.find_all(['script', 'style', 'iframe', 'ins', 'aside', 'figure']):
                unwanted.decompose()
            for ad_class in ['pub', 'publicite', 'advertisement', 'social-share', 'related', 'newsletter']:
                for elem in content_elem.find_all(class_=lambda x: x and ad_class in x.lower()):
                    elem.decompose()

            content = content_elem.get_text(separator='\n', strip=True)

            date_elem = soup.find('time', class_='entry-date') or soup.find('time') or soup.find('meta', property='article:published_time')
            published_at = None
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get('content')
                if date_str:
                    try:
                        published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        pass

            category = self.get_category(soup, url)

            return self.normalize_article(
                title=title,
                content=content,
                url=url,
                category=category,
                published_at=published_at,
            )
        except Exception as e:
            logger.error(f"Error parsing TelQuel article {url}: {str(e)}")
            return None

"""Content cleaner module for removing ads and extracting clean text."""
from typing import Optional
from newspaper import Article as NewspaperArticle
from loguru import logger


class ContentCleaner:
    """Clean and extract article content."""
    
    @staticmethod
    def clean_article(url: str, html_content: Optional[str] = None) -> Optional[dict]:
        """
        Clean article using newspaper3k library.
        
        Args:
            url: Article URL
            html_content: Optional HTML content (if already fetched)
            
        Returns:
            Dictionary with cleaned content or None
        """
        try:
            article = NewspaperArticle(url)
            
            if html_content:
                article.download(input_html=html_content)
            else:
                article.download()
            
            article.parse()
            
            return {
                'title': article.title,
                'content': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'keywords': article.keywords
            }
        except Exception as e:
            logger.error(f"Error cleaning article {url}: {str(e)}")
            return None
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra whitespace from text."""
        import re
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing HTML, extra whitespace, etc.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        text = ContentCleaner.remove_html_tags(text)
        text = ContentCleaner.remove_extra_whitespace(text)
        return text

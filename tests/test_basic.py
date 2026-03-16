"""Tests for Maghrib News Aggregator."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Article
from spiders import (
    HespressSpider, Le360Spider, Medias24Spider,
    ElbotolaSpider, TelQuelSpider, YabiladiSpider,
)
from sentiment import SimpleSentimentAnalyzer
from cleaner import ContentCleaner


# Test Database Setup
@pytest.fixture
def test_db():
    """Create a test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


# Test Models
def test_article_model(test_db):
    """Test Article model creation."""
    article = Article(
        source="Test Source",
        title="Test Title",
        content="Test Content",
        category="Test",
        url="https://test.com/article"
    )
    test_db.add(article)
    test_db.commit()
    
    retrieved = test_db.query(Article).first()
    assert retrieved.title == "Test Title"
    assert retrieved.source == "Test Source"


# Test Spiders
def test_hespress_spider_initialization():
    """Test Hespress spider initialization."""
    spider = HespressSpider()
    assert spider.source_name == "Hespress"
    assert spider.rss_url is not None


def test_le360_spider_initialization():
    """Test Le360 spider initialization."""
    spider = Le360Spider()
    assert spider.source_name == "Le360"
    assert spider.rss_url is not None


def test_medias24_spider_initialization():
    """Test Médias24 spider initialization."""
    spider = Medias24Spider()
    assert spider.source_name == "Médias24"


def test_elbotola_spider_initialization():
    """Test Elbotola spider initialization."""
    spider = ElbotolaSpider()
    assert spider.source_name == "Elbotola"
    assert spider.rss_url is not None


def test_telquel_spider_initialization():
    """Test TelQuel spider initialization."""
    spider = TelQuelSpider()
    assert spider.source_name == "TelQuel"
    assert spider.rss_url is not None


def test_yabiladi_spider_initialization():
    """Test Yabiladi spider initialization."""
    spider = YabiladiSpider()
    assert spider.source_name == "Yabiladi"
    assert spider.rss_url is not None


# Test Sentiment Analysis
def test_simple_sentiment_analyzer():
    """Test simple sentiment analyzer."""
    analyzer = SimpleSentimentAnalyzer()
    
    # Test positive text
    result = analyzer.analyze("excellent succès victoire")
    assert result['sentiment_label'] == "Positif"
    
    # Test negative text
    result = analyzer.analyze("échec crise problème")
    assert result['sentiment_label'] == "Négatif"
    
    # Test neutral text
    result = analyzer.analyze("article information")
    assert result['sentiment_label'] == "Neutre"


# Test Content Cleaner
def test_content_cleaner_remove_html():
    """Test HTML tag removal."""
    text = "<p>This is <strong>bold</strong> text</p>"
    clean = ContentCleaner.remove_html_tags(text)
    assert "<" not in clean
    assert ">" not in clean


def test_content_cleaner_whitespace():
    """Test whitespace removal."""
    text = "Too    many     spaces\n\n\n\nand newlines"
    clean = ContentCleaner.remove_extra_whitespace(text)
    assert "    " not in clean


# Test API (requires running server)
# def test_api_health_check():
#     """Test API health check endpoint."""
#     import requests
#     response = requests.get("http://localhost:8000/health")
#     assert response.status_code == 200
#     assert response.json()["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

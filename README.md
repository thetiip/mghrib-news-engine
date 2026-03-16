# Maghrib News Aggregator

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Intelligent Moroccan news aggregator with sentiment analysis**

[Features](#features) • [Installation](#installation) • [API](#api-endpoints) • [Roadmap](#roadmap)

</div>

---

## Overview

News in Morocco is fragmented across multiple sources (Hespress, Médias24, etc.), often cluttered with ads and difficult to track. 

**Maghrib News Aggregator** provides:
- Automated scraping from multiple news sources
- Clean JSON format normalization
- Content cleaning (no ads or tracking scripts)
- Arabic/French sentiment analysis
- Simple REST API for data access

---

## Features

### Modular Scraping
- Independent spider architecture
- Current support: **Hespress**, **Le360**, **Médias24**, **Elbotola**, **TelQuel**, **Yabiladi**
- RSS feeds and intelligent HTML parsing
- Easily extensible for new sources

### Content Cleaning
- Removes ads and tracking scripts
- Extracts main content using `newspaper3k`
- Clean, readable text output

### Sentiment Analysis
- Pre-trained BERT model for Arabic (CAMeL-Lab)
- Sentiment score: **-1 (Negative)** to **+1 (Positive)**
- Labels: Positive, Negative, Neutral
- Simple keyword-based fallback

### REST API
- FastAPI-based endpoints
- Filter by source, category, sentiment
- Interactive Swagger documentation
- CORS support for frontend integration

### Automation
- Periodic scraping scheduler (APScheduler)
- Docker Compose deployment (API + scraper)
- Automatic JSON export

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/maghrib-news-aggregator.git
cd maghrib-news-aggregator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env as needed

# 5. Run scraping
python main.py

# 6. Start API server
python api.py
```

The API will be available at `http://localhost:8000`  
Interactive documentation: `http://localhost:8000/docs`

---

## Usage

### Manual Scraping
```bash
# Scrape all sources
python main.py

# Or use scheduler (hourly scraping)
python scheduler.py
```

### JSON Export
```bash
# Export all articles to data/articles.json
python export.py
```

### Using the API

```python
import requests

# Get latest articles
response = requests.get("http://localhost:8000/articles?limit=10")
articles = response.json()

# Filter by source
hespress_news = requests.get("http://localhost:8000/articles?source=Hespress")

# Filter by sentiment
positive_news = requests.get("http://localhost:8000/articles?sentiment=Positif")

# Search by keyword
search = requests.get("http://localhost:8000/search?q=économie")
```

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/articles` | List articles (with filters) |
| `GET` | `/articles/{id}` | Get specific article |
| `GET` | `/sources` | List available sources |
| `GET` | `/categories` | List categories |
| `GET` | `/stats` | Global statistics |
| `GET` | `/search?q=...` | Search by keyword |
| `POST` | `/scrape` | Trigger manual scraping |
| `GET` | `/docs` | Interactive Swagger documentation |

### Example Responses

**`GET /articles?limit=2`**
```json
[
  {
    "id": 1,
    "source": "Hespress",
    "title": "Le Maroc annonce une nouvelle stratégie économique",
    "content": "Le gouvernement marocain a dévoilé...",
    "category": "Économie",
    "url": "https://hespress.com/...",
    "published_at": "2024-05-20T10:00:00",
    "scraped_at": "2024-05-20T11:30:00",
    "sentiment_score": 0.65,
    "sentiment_label": "Positif"
  }
]
```

**`GET /stats`**
```json
{
  "total_articles": 1234,
  "recent_articles_24h": 87,
  "by_source": {
    "Hespress": 456,
    "Le360": 321,
    "Médias24": 389,
    "Elbotola": 245,
    "TelQuel": 198,
    "Yabiladi": 267
  },
  "by_sentiment": {
    "Positif": 523,
    "Négatif": 234,
    "Neutre": 477
  }
}
```

---

## Architecture

```
maghrib-news-aggregator/
├── spiders/              # Modular scrapers
│   ├── base.py          # Abstract base class
│   ├── hespress.py      # Hespress spider
│   ├── le360.py         # Le360 spider
│   ├── medias24.py      # Médias24 spider
│   ├── elbotola.py      # Elbotola spider (sports)
│   ├── telquel.py       # TelQuel spider
│   └── yabiladi.py      # Yabiladi spider
├── api.py               # FastAPI application
├── main.py              # Main scraping script
├── scheduler.py         # Periodic scraping automation
├── service.py           # Business logic
├── sentiment.py         # Sentiment analysis
├── cleaner.py           # Content cleaning
├── models.py            # Database models
├── database.py          # SQLAlchemy configuration
├── schemas.py           # Pydantic schemas
├── config.py            # Configuration
├── export.py            # JSON export
└── requirements.txt     # Dependencies
```

---

## Roadmap

### Phase 1: MVP (Completed)
- [x] Modular spider architecture
- [x] Scrapers for Hespress, Médias24
- [x] JSON normalization
- [x] Content cleaning
- [x] Basic sentiment analysis
- [x] REST API
- [x] SQLite database

### Phase 2: Improvements (Completed)
- [x] Add Le360 (general news)
- [x] Add Elbotola (sports)
- [x] Add TelQuel (politics, society, culture)
- [x] Add Yabiladi (general news, diaspora)
- [ ] Add La Vie Éco (economy)
- [ ] Support for Arabic-only sites (Al-Massae, etc.)
- [ ] Improve sentiment analysis with Darija fine-tuning
- [ ] Redis caching system
- [ ] Unit and integration tests

### Phase 3: Expansion (Planned)
- [ ] Telegram bot for notifications
- [ ] WhatsApp bot
- [ ] React/Vue.js frontend
- [ ] Advanced filters (by region, date, author)
- [ ] Fake news detection
- [ ] Automatic summaries (LLM)
- [ ] Multilingual support (AR/FR/EN)

---

## Testing

```bash
# Run tests
pytest tests/

# Coverage
pytest --cov=. tests/
```

---

## Contributing

Contributions are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Adding a New Source

1. Create a file in `spiders/` (e.g., `elbotola.py`)
2. Inherit from `BaseSpider`
3. Implement `get_article_urls()`, `parse_article()`, `get_category()` methods
4. Add the spider to `spiders/__init__.py`
5. Add it to `service.py`

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Hespress](https://hespress.com) - News source
- [Le360](https://fr.le360.ma) - News source
- [Médias24](https://medias24.com) - News source
- [Elbotola](https://www.elbotola.com) - Sports news source
- [TelQuel](https://telquel.ma) - News source
- [Yabiladi](https://www.yabiladi.com) - News source
- [CAMeL Lab](https://github.com/CAMeL-Lab) - Arabic NLP models
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

---

## Contact

For questions or suggestions, open an issue on GitHub.

---

<div align="center">

**For the Moroccan Tech Community**

[Back to top](#maghrib-news-aggregator)

</div>

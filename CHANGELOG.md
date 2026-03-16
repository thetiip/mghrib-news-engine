# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-05-20

### Added

#### Core Features
- **Modular Spider Architecture**: Base spider class with extensible design
- **Source Scrapers**: 
  - Hespress spider with RSS feed support
  - Le360 spider with content extraction
  - Médias24 spider for economic news
- **Content Normalization**: Standardized JSON format for all articles
- **Content Cleaning**: Automatic removal of ads, tracking scripts, and unwanted content
- **Sentiment Analysis**: 
  - Advanced BERT-based analysis for Arabic text (CAMeL-Lab)
  - Simple keyword-based fallback analyzer
  - Sentiment scoring from -1 (negative) to +1 (positive)

#### API
- **FastAPI REST API** with comprehensive endpoints:
  - `GET /articles` - List articles with filtering
  - `GET /articles/{id}` - Get specific article
  - `GET /sources` - List available sources
  - `GET /categories` - List categories
  - `GET /stats` - Get statistics
  - `GET /search` - Search articles by keyword
  - `POST /scrape` - Trigger manual scraping
- **Interactive API Documentation** via Swagger UI
- **CORS Support** for frontend integration

#### Database
- **SQLite Database** with SQLAlchemy ORM
- **Article Model** with full metadata support
- **Automatic Schema Migrations**

#### Automation
- **Scheduler**: Periodic scraping with configurable intervals
- **Scheduler**: Periodic scraping via APScheduler
- **Export Functionality**: JSON export for data portability

#### Developer Experience
- **Setup Scripts**: Automated setup for Linux/Mac and Windows
- **Docker Support**: Full containerization with docker-compose
- **Makefile**: Common commands simplified
- **Comprehensive Documentation**: README, CONTRIBUTING, and inline docs
- **Demo Script**: Quick testing and validation
- **Jupyter Notebook**: Data exploration template

#### Testing
- **Unit Tests**: Basic test suite with pytest
- **Test Fixtures**: Reusable test utilities

#### Configuration
- **Environment Variables**: Flexible configuration via .env
- **Settings Management**: Centralized config with pydantic-settings
- **Logging**: Structured logging with loguru

### Documentation
- Professional README with badges, examples, and roadmap
- Contributing guidelines
- MIT License
- Change log (this file)
- API documentation (auto-generated)

### Infrastructure
- Docker and docker-compose configuration
- .gitignore for Python projects
- Requirements.txt with pinned versions

## [1.1.0] - 2026-03-16

### Added
- **New Source Scrapers**:
  - Le360 spider activated (was implemented but not registered)
  - Elbotola spider for Moroccan/African sports news
  - TelQuel spider for politics, society, and culture
  - Yabiladi spider for general and diaspora news
- **6 total news sources** now supported (up from 2 active)
- Unit tests for all new spider initializations

### Removed
- **GitHub Actions scraping workflow** (`scrape.yml`): data files should not be committed to git. Use `docker-compose up -d` or `python scheduler.py` for production scraping.

### Changed
- Updated documentation to reflect new sources and removal of GitHub Actions
- Added `data/articles.json` to `.gitignore`

## [Unreleased]

### Planned Features
- La Vie Éco scraper (economy)
- Arabic-only sources (Al-Massae, etc.)
- Telegram bot integration
- WhatsApp bot integration
- Enhanced sentiment analysis with Darija support
- Frontend (React/Vue.js)
- Redis caching
- PostgreSQL support
- Advanced filtering (by region, date range, author)
- Fake news detection
- Automatic summarization
- Multilingual support (AR/FR/EN)

---

## Version History

- **1.1.0** - Added Le360, Elbotola, TelQuel, Yabiladi sources; removed GitHub Actions pipeline
- **1.0.0** - Initial release with core functionality

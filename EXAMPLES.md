# Exemples d'Utilisation

Ce document présente différents exemples d'utilisation de Maghrib News Aggregator.

## 1. Usage Basique

### Scraper une seule fois

```bash
python main.py
```

### Lancer l'API

```bash
python api.py
# Ou avec auto-reload pour le développement
uvicorn api:app --reload
```

### Scraping périodique

```bash
python scheduler.py
```

## 2. Utilisation de l'API

### Avec curl

```bash
# Récupérer les derniers articles
curl http://localhost:8000/articles?limit=5

# Filtrer par source
curl http://localhost:8000/articles?source=Hespress

# Filtrer par catégorie
curl http://localhost:8000/articles?category=Économie

# Filtrer par sentiment
curl http://localhost:8000/articles?sentiment=Positif

# Recherche par mot-clé
curl http://localhost:8000/search?q=maroc

# Obtenir les statistiques
curl http://localhost:8000/stats

# Déclencher le scraping
curl -X POST http://localhost:8000/scrape
```

### Avec Python (requests)

```python
import requests

# Configuration de base
BASE_URL = "http://localhost:8000"

# 1. Récupérer tous les articles
response = requests.get(f"{BASE_URL}/articles")
articles = response.json()
print(f"Total articles: {len(articles)}")

# 2. Filtrer par source
hespress_articles = requests.get(
    f"{BASE_URL}/articles",
    params={"source": "Hespress", "limit": 10}
).json()

# 3. Recherche
search_results = requests.get(
    f"{BASE_URL}/search",
    params={"q": "économie", "limit": 20}
).json()

# 4. Statistiques
stats = requests.get(f"{BASE_URL}/stats").json()
print(f"Total articles: {stats['total_articles']}")
print(f"Sources: {stats['by_source']}")

# 5. Déclencher le scraping
response = requests.post(f"{BASE_URL}/scrape")
print(response.json())
```

### Avec Python (httpx - async)

```python
import httpx
import asyncio

async def get_articles():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/articles?limit=10")
        return response.json()

# Exécuter
articles = asyncio.run(get_articles())
```

### Avec JavaScript (fetch)

```javascript
// Récupérer les articles
fetch('http://localhost:8000/articles?limit=10')
  .then(response => response.json())
  .then(data => console.log(data));

// Recherche
fetch('http://localhost:8000/search?q=maroc')
  .then(response => response.json())
  .then(articles => {
    articles.forEach(article => {
      console.log(`${article.title} - ${article.source}`);
    });
  });

// Statistiques
fetch('http://localhost:8000/stats')
  .then(response => response.json())
  .then(stats => console.log('Stats:', stats));
```

## 3. Utilisation Programmatique

### Créer un Spider Personnalisé

```python
from spiders.base import BaseSpider
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class MonSiteSpider(BaseSpider):
    def __init__(self):
        super().__init__("MonSite")
        self.base_url = "https://monsite.ma"
    
    def get_article_urls(self, max_articles: int = 50) -> List[str]:
        """Récupérer les URLs des articles."""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []
        
        links = soup.find_all('a', class_='article-link')
        urls = [link['href'] for link in links[:max_articles]]
        return urls
    
    def parse_article(self, url: str) -> Optional[Dict]:
        """Parser un article."""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        title = soup.find('h1', class_='title').get_text(strip=True)
        content = soup.find('div', class_='content').get_text(strip=True)
        
        return self.normalize_article(
            title=title,
            content=content,
            url=url,
            category=self.get_category(soup, url)
        )
    
    def get_category(self, article_soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extraire la catégorie."""
        cat = article_soup.find('span', class_='category')
        return cat.get_text(strip=True) if cat else None

# Utilisation
spider = MonSiteSpider()
articles = spider.scrape(max_articles=10)
print(f"Scraped {len(articles)} articles")
```

### Utiliser le Service de Scraping

```python
from database import SessionLocal, init_db
from service import ScrapingService

# Initialiser la base de données
init_db()

# Créer une session
db = SessionLocal()

# Créer le service
service = ScrapingService(use_sentiment=True)

# Scraper toutes les sources
stats = service.scrape_all(db, max_articles_per_source=20)
print(stats)

# Scraper une source spécifique
stats = service.scrape_source(db, "Hespress", max_articles=30)
print(stats)

db.close()
```

### Analyse de Sentiment Personnalisée

```python
from sentiment import SentimentAnalyzer, SimpleSentimentAnalyzer

# Utiliser l'analyseur avancé
analyzer = SentimentAnalyzer()
analyzer.initialize()

text = "المغرب يحقق نجاحا كبيرا في الاقتصاد"
result = analyzer.analyze(text)
print(f"Score: {result['sentiment_score']}")
print(f"Label: {result['sentiment_label']}")

# Ou utiliser l'analyseur simple
simple = SimpleSentimentAnalyzer()
result = simple.analyze("Excellente nouvelle pour le Maroc")
print(result)
```

### Exporter les Données

```python
from export import export_to_json

# Exporter vers JSON
export_to_json("mon_export.json")

# Ou programmatiquement
from database import SessionLocal
from models import Article
import json

db = SessionLocal()
articles = db.query(Article).all()

data = [article.to_dict() for article in articles]

with open('export.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

db.close()
```

## 4. Utilisation avec Docker

### Lancer avec Docker Compose

```bash
# Build et démarrer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Rebuild après modification
docker-compose up -d --build
```

### Lancer individuellement

```bash
# Build l'image
docker build -t maghrib-news .

# Lancer l'API
docker run -p 8000:8000 -v $(pwd)/data:/app/data maghrib-news python api.py

# Lancer le scraper
docker run -v $(pwd)/data:/app/data maghrib-news python main.py
```

## 5. Automatisation avec le Scheduler

Le scheduler APScheduler peut être lancé en tant que service pour scraper automatiquement :

```bash
# Lancer le scheduler (scraping périodique, par défaut toutes les heures)
python scheduler.py

# Ou avec Docker Compose (API + scraper)
docker-compose up -d
```

Le scheduler exécutera le scraping de toutes les sources (Hespress, Le360, Médias24, Elbotola, TelQuel, Yabiladi) selon l'intervalle configuré dans `.env` (`SCRAPING_INTERVAL=3600`).

## 6. Intégrations Futures

### Telegram Bot (à venir)

```python
from integrations.telegram_bot import TelegramBot

# Configurer le bot
bot = TelegramBot(
    token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

# Envoyer un article
bot.send_article({
    'source': 'Hespress',
    'title': 'Titre de l\'article',
    'content': 'Contenu...',
    'category': 'Politique',
    'url': 'https://example.com',
    'sentiment_label': 'Positif'
})
```

## 7. Statistiques et Rapports

```python
from database import SessionLocal
from utils.stats import StatsReporter

db = SessionLocal()
reporter = StatsReporter(db)

# Rapport quotidien
report = reporter.generate_daily_report()
print(report)

# Statistiques spécifiques
daily_stats = reporter.get_daily_stats()
sentiment_dist = reporter.get_sentiment_distribution()
trending = reporter.get_trending_categories()

db.close()
```

## 8. Makefile

Utiliser les commandes Make pour simplifier :

```bash
# Voir toutes les commandes disponibles
make help

# Installer les dépendances
make install

# Lancer le scraper
make run

# Lancer l'API
make api

# Lancer les tests
make test

# Nettoyer les fichiers générés
make clean

# Exporter vers JSON
make export

# Voir les statistiques
make stats

# Docker
make docker-build
make docker-up
make docker-down
```

## 9. Développement et Tests

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dépendances de dev
pip install pytest pytest-cov

# Lancer les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=. --cov-report=html

# Lancer le demo rapide
python demo.py

# Mode développement avec auto-reload
make dev
# ou
uvicorn api:app --reload
```

---

Pour plus d'informations, consultez le [README.md](README.md) ou la [documentation de l'API](http://localhost:8000/docs).

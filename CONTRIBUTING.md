# Contributing to Maghrib News Aggregator

Merci de votre intérêt pour contribuer à ce projet ! 🎉

## Comment Contribuer

### Ajouter une Nouvelle Source

1. **Créer un nouveau spider**
   - Créez un fichier dans `spiders/` (ex: `elbotola.py`)
   - Héritez de `BaseSpider`
   - Implémentez les méthodes requises :
     - `get_article_urls()` - Récupérer les URLs des articles
     - `parse_article()` - Parser un article
     - `get_category()` - Extraire la catégorie

2. **Exemple de Spider**

```python
from .base import BaseSpider
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class ElBotolaSpider(BaseSpider):
    def __init__(self):
        super().__init__("ElBotola")
        self.base_url = "https://elbotola.com"
    
    def get_article_urls(self, max_articles: int = 50) -> List[str]:
        # Votre logique ici
        pass
    
    def parse_article(self, url: str) -> Optional[Dict]:
        # Votre logique ici
        pass
    
    def get_category(self, article_soup: BeautifulSoup, url: str) -> Optional[str]:
        # Votre logique ici
        pass
```

3. **Enregistrer le Spider**
   - Ajoutez l'import dans `spiders/__init__.py`
   - Ajoutez une instance dans `service.py`

### Améliorer l'Analyse de Sentiment

Si vous avez des connaissances en NLP pour l'arabe/darija :
- Proposez des modèles mieux adaptés
- Ajoutez des dictionnaires de mots pour le SimpleSentimentAnalyzer
- Créez des datasets de fine-tuning

### Tests

Avant de soumettre une PR :
- Testez votre code localement
- Assurez-vous que le scraping fonctionne
- Vérifiez que l'API retourne les bonnes données


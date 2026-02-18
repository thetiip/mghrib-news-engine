"""Sentiment analysis module for Arabic/Darija text."""
from typing import Dict, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from loguru import logger
from config import settings


class SentimentAnalyzer:
    """Sentiment analyzer for Arabic text."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.model_name = settings.sentiment_model
        self.device = "cuda" if settings.use_gpu and torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self._initialized = False
    
    def initialize(self):
        """Load the model and tokenizer."""
        if self._initialized:
            return
        
        try:
            logger.info(f"Loading sentiment model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self._initialized = True
            logger.info(f"Sentiment model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {str(e)}")
            logger.warning("Sentiment analysis will be disabled")
    
    def analyze(self, text: str) -> Optional[Dict]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment score and label, or None if analysis fails
        """
        if not self._initialized:
            self.initialize()
        
        if not self.model or not self.tokenizer:
            return None
        
        try:
            # Truncate text if too long (max 512 tokens for BERT models)
            inputs = self.tokenizer(
                text[:2000],  # Limit characters to avoid token overflow
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get predicted class and confidence
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = predictions[0][predicted_class].item()
            
            # Map to sentiment labels
            # Most Arabic sentiment models use: 0=negative, 1=neutral, 2=positive
            # Or: 0=negative, 1=positive
            sentiment_map = {
                0: "Négatif",
                1: "Neutre" if self.model.config.num_labels == 3 else "Positif",
                2: "Positif"
            }
            
            sentiment_label = sentiment_map.get(predicted_class, "Neutre")
            
            # Convert to score from -1 to +1
            if self.model.config.num_labels == 3:
                # 3-class: negative, neutral, positive
                sentiment_score = (predicted_class - 1) * confidence  # -1, 0, or +1 weighted by confidence
            else:
                # 2-class: negative, positive
                sentiment_score = (predicted_class * 2 - 1) * confidence  # -1 or +1 weighted by confidence
            
            return {
                "sentiment_score": float(sentiment_score),
                "sentiment_label": sentiment_label,
                "confidence": float(confidence)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None
    
    def analyze_batch(self, texts: list) -> list:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List of sentiment results
        """
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        return results


# Fallback simple sentiment analyzer using keyword matching
class SimpleSentimentAnalyzer:
    """Simple rule-based sentiment analyzer as fallback."""
    
    def __init__(self):
        """Initialize with sentiment word lists."""
        # Positive words in Arabic/French
        self.positive_words = [
            'جيد', 'ممتاز', 'رائع', 'إيجابي', 'نجاح', 'فوز', 'تقدم', 'نمو',
            'bon', 'excellent', 'réussite', 'succès', 'victoire', 'progrès', 'croissance'
        ]
        
        # Negative words in Arabic/French
        self.negative_words = [
            'سيء', 'فشل', 'خسارة', 'سلبي', 'انخفاض', 'أزمة', 'مشكلة',
            'mauvais', 'échec', 'perte', 'défaite', 'crise', 'problème', 'baisse'
        ]
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment using keyword matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment score and label
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        total = positive_count + negative_count
        
        if total == 0:
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "Neutre",
                "confidence": 0.5
            }
        
        score = (positive_count - negative_count) / total
        
        if score > 0.2:
            label = "Positif"
        elif score < -0.2:
            label = "Négatif"
        else:
            label = "Neutre"
        
        return {
            "sentiment_score": float(score),
            "sentiment_label": label,
            "confidence": min(abs(score) + 0.5, 1.0)
        }

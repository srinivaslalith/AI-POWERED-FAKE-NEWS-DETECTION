"""NLP engine for fake news detection using HuggingFace transformers."""

from transformers import pipeline, AutoTokenizer
from typing import Dict, List, Tuple, Optional, Any
import torch
import logging
import re

logger = logging.getLogger(__name__)


class FakeNewsDetector:
    """NLP engine for detecting fake news using transformer models."""
    
    def __init__(self, model_name: str, max_length: int = 512):
        self.model_name = model_name
        self.max_length = max_length
        self._pipeline = None
        self._tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self._pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict if text is fake news.
        
        Args:
            text: Article text to analyze
            
        Returns:
            Dict with prediction results
        """
        if not self._pipeline:
            raise RuntimeError("Model not loaded")
        
        # Truncate text if too long
        truncated_text = self._truncate_text(text)
        
        try:
            # Get prediction
            results = self._pipeline(truncated_text)
            
            # Process results - handle different model output formats
            if isinstance(results[0], list):
                scores = results[0]
            else:
                scores = results
            
            # Find the prediction with highest confidence
            best_prediction = max(scores, key=lambda x: x['score'])
            
            # Map labels to standardized format
            label = self._standardize_label(best_prediction['label'])
            confidence = best_prediction['score']
            
            return {
                'label': label,
                'confidence': confidence,
                'raw_scores': scores,
                'text_length': len(text),
                'truncated': len(text) > self.max_length
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'label': 'Unknown',
                'confidence': 0.0,
                'raw_scores': [],
                'text_length': len(text),
                'truncated': False,
                'error': str(e)
            }
    
    def analyze_sentences(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze individual sentences for suspiciousness.
        
        Args:
            text: Article text to analyze
            
        Returns:
            List of sentence analysis results
        """
        sentences = self._split_sentences(text)
        sentence_analyses = []
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
                
            try:
                prediction = self.predict(sentence)
                suspicion_score = 1.0 - prediction['confidence'] if prediction['label'] == 'Real' else prediction['confidence']
                
                sentence_analyses.append({
                    'sentence': sentence,
                    'suspicion_score': suspicion_score,
                    'position': i,
                    'label': prediction['label']
                })
            except Exception as e:
                logger.warning(f"Failed to analyze sentence {i}: {e}")
                sentence_analyses.append({
                    'sentence': sentence,
                    'suspicion_score': 0.5,  # Neutral score for failed analysis
                    'position': i,
                    'label': 'Unknown'
                })
        
        # Sort by suspicion score (highest first)
        sentence_analyses.sort(key=lambda x: x['suspicion_score'], reverse=True)
        
        return sentence_analyses
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit model's maximum input length."""
        if not self._tokenizer:
            # Fallback: simple character-based truncation
            return text[:self.max_length * 4]  # Rough estimate
        
        # Tokenize and truncate
        tokens = self._tokenizer.encode(text, truncation=True, max_length=self.max_length)
        return self._tokenizer.decode(tokens, skip_special_tokens=True)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple regex."""
        # Simple sentence splitting - could be improved with spaCy or NLTK
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _standardize_label(self, label: str) -> str:
        """Standardize model labels to common format."""
        label = label.lower()
        
        # Map various label formats to standard ones
        if label in ['fake', 'false', 'unreliable', 'fabricated']:
            return 'Fake'
        elif label in ['real', 'true', 'reliable', 'factual']:
            return 'Real'
        elif label in ['biased', 'opinion', 'misleading']:
            return 'Biased'
        elif label in ['satire', 'humor', 'comedy']:
            return 'Satire'
        else:
            return label.capitalize()
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the loaded model."""
        return {
            'model_name': self.model_name,
            'max_length': str(self.max_length),
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }
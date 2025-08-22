"""Mock NLP engine for testing without ML dependencies."""

from typing import Dict, List, Optional, Any
import logging
import re

logger = logging.getLogger(__name__)


class FakeNewsDetector:
    """Mock NLP engine for detecting fake news without requiring transformers."""
    
    def __init__(self, model_name: str, max_length: int = 512):
        self.model_name = model_name
        self.max_length = max_length
        logger.info(f"Mock model loaded: {model_name}")
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Mock prediction based on simple heuristics.
        
        Args:
            text: Article text to analyze
            
        Returns:
            Dict with prediction results
        """
        text_lower = text.lower()
        
        # Simple heuristics for fake news detection
        fake_indicators = [
            'miracle cure', 'shocking truth', 'they don\'t want you to know',
            'breaking:', 'scientists hate him', 'doctors shocked',
            'big pharma', 'leaked documents', 'government secret'
        ]
        
        real_indicators = [
            'federal reserve', 'announced today', 'according to',
            'research shows', 'study found', 'data indicates',
            'officials said', 'reported that'
        ]
        
        fake_score = sum(1 for indicator in fake_indicators if indicator in text_lower)
        real_score = sum(1 for indicator in real_indicators if indicator in text_lower)
        
        if fake_score > real_score:
            label = 'Fake'
            confidence = min(0.9, 0.6 + (fake_score * 0.1))
        elif real_score > fake_score:
            label = 'Real'
            confidence = min(0.9, 0.6 + (real_score * 0.1))
        else:
            label = 'Unknown'
            confidence = 0.5
        
        return {
            'label': label,
            'confidence': confidence,
            'raw_scores': [
                {'label': 'Real', 'score': 1.0 - confidence if label == 'Fake' else confidence},
                {'label': 'Fake', 'score': confidence if label == 'Fake' else 1.0 - confidence}
            ],
            'text_length': len(text),
            'truncated': len(text) > self.max_length
        }
    
    def analyze_sentences(self, text: str) -> List[Dict[str, Any]]:
        """
        Mock sentence analysis.
        
        Args:
            text: Article text to analyze
            
        Returns:
            List of sentence analysis results
        """
        sentences = self._split_sentences(text)
        sentence_analyses = []
        
        fake_indicators = [
            'miracle', 'shocking', 'secret', 'hidden', 'leaked',
            'breaking', 'exclusive', 'revealed'
        ]
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:
                continue
                
            sentence_lower = sentence.lower()
            suspicion_indicators = sum(1 for indicator in fake_indicators if indicator in sentence_lower)
            
            # Base suspicion score
            suspicion_score = min(0.9, 0.1 + (suspicion_indicators * 0.2))
            
            # Add some randomness for variety
            import random
            suspicion_score += random.uniform(-0.1, 0.1)
            suspicion_score = max(0.0, min(1.0, suspicion_score))
            
            label = 'Fake' if suspicion_score > 0.6 else 'Real'
            
            sentence_analyses.append({
                'sentence': sentence,
                'suspicion_score': suspicion_score,
                'position': i,
                'label': label
            })
        
        # Sort by suspicion score (highest first)
        sentence_analyses.sort(key=lambda x: x['suspicion_score'], reverse=True)
        
        return sentence_analyses
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple regex."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the mock model."""
        return {
            'model_name': f"{self.model_name} (MOCK)",
            'max_length': str(self.max_length),
            'device': 'cpu (mock)'
        }
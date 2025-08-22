"""Scoring module for calculating credibility scores."""

import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CredibilityScorer:
    """Calculator for credibility scores based on multiple factors."""
    
    def __init__(self, weights: Dict[str, float], domain_reputation_file: str):
        self.weights = weights
        self.domain_reputation = self._load_domain_reputation(domain_reputation_file)
    
    def _load_domain_reputation(self, file_path: str) -> Dict[str, float]:
        """Load domain reputation scores from JSON file."""
        try:
            reputation_file = Path(file_path)
            if reputation_file.exists():
                with open(reputation_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Domain reputation file not found: {file_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load domain reputation: {e}")
            return {}
    
    def calculate_credibility_score(
        self,
        model_prediction: Dict[str, any],
        fact_check_results: List[Dict[str, any]],
        domain: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Calculate overall credibility score.
        
        Args:
            model_prediction: Results from NLP model
            fact_check_results: Results from fact-checking
            domain: Source domain name
            
        Returns:
            Dict with credibility score and breakdown
        """
        # Model confidence component
        model_score = self._calculate_model_score(model_prediction)
        
        # Fact-check evidence component
        factcheck_score = self._calculate_factcheck_score(fact_check_results)
        
        # Source reputation component
        source_score = self._calculate_source_score(domain)
        
        # Weighted combination
        credibility_score = (
            model_score * self.weights.get('model_confidence', 0.5) +
            factcheck_score * self.weights.get('fact_check_evidence', 0.3) +
            source_score * self.weights.get('source_reputation', 0.2)
        ) * 100  # Scale to 0-100
        
        return {
            'credibility_score': round(credibility_score, 1),
            'breakdown': {
                'model_score': round(model_score * 100, 1),
                'factcheck_score': round(factcheck_score * 100, 1),
                'source_score': round(source_score * 100, 1)
            },
            'weights_used': self.weights,
            'source_reputation': source_score if domain else None
        }
    
    def _calculate_model_score(self, prediction: Dict[str, any]) -> float:
        """Calculate score from model prediction (0-1 scale)."""
        label = prediction.get('label', 'Unknown')
        confidence = prediction.get('confidence', 0.0)
        
        # Convert to credibility score
        if label == 'Real':
            return confidence  # High confidence in "Real" = high credibility
        elif label == 'Fake':
            return 1.0 - confidence  # High confidence in "Fake" = low credibility
        elif label == 'Biased':
            return 0.4  # Biased content gets moderate-low credibility
        elif label == 'Satire':
            return 0.2  # Satire gets low credibility for factual content
        else:
            return 0.5  # Unknown gets neutral score
    
    def _calculate_factcheck_score(self, fact_check_results: List[Dict[str, any]]) -> float:
        """Calculate score from fact-check results (0-1 scale)."""
        if not fact_check_results:
            return 0.5  # Neutral score when no fact-checks available
        
        # Check if any results are mocked (API unavailable)
        if any(result.get('mock', False) for result in fact_check_results):
            return 0.5  # Neutral score for mock results
        
        verdict_scores = []
        for result in fact_check_results:
            verdict = result.get('verdict', '').lower()
            
            # Map fact-check verdicts to credibility scores
            if verdict in ['true', 'correct', 'accurate', 'verified']:
                verdict_scores.append(1.0)
            elif verdict in ['false', 'incorrect', 'fabricated', 'fake']:
                verdict_scores.append(0.0)
            elif verdict in ['misleading', 'partly false', 'mixture']:
                verdict_scores.append(0.3)
            elif verdict in ['unproven', 'unsubstantiated', 'research in progress']:
                verdict_scores.append(0.4)
            else:
                verdict_scores.append(0.5)  # Unknown verdict
        
        # Average the scores
        return sum(verdict_scores) / len(verdict_scores) if verdict_scores else 0.5
    
    def _calculate_source_score(self, domain: Optional[str]) -> float:
        """Calculate score from source reputation (0-1 scale)."""
        if not domain:
            return 0.5  # Neutral score for unknown domain
        
        # Clean domain name
        domain = domain.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Look up in reputation database
        reputation = self.domain_reputation.get(domain)
        
        if reputation is not None:
            return reputation
        else:
            # Unknown domain gets neutral score
            return 0.5
    
    def get_scoring_explanation(self) -> Dict[str, any]:
        """Get explanation of scoring methodology."""
        return {
            'formula': 'credibility_score = (model_score * w1) + (factcheck_score * w2) + (source_score * w3)',
            'weights': self.weights,
            'scale': '0-100 (higher = more credible)',
            'components': {
                'model_score': 'Based on AI model confidence in Real vs Fake classification',
                'factcheck_score': 'Based on external fact-checking verdicts',
                'source_score': 'Based on historical source reputation'
            }
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Update scoring weights."""
        # Validate weights sum to 1.0
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total}, not 1.0. Normalizing...")
            new_weights = {k: v/total for k, v in new_weights.items()}
        
        self.weights.update(new_weights)
        logger.info(f"Updated weights: {self.weights}")
"""Fact-check adapter for integrating with external fact-checking APIs."""

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    
from typing import List, Dict, Optional, Any
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)


class FactCheckAdapter:
    """Adapter for fact-checking services."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        self.enabled = api_key is not None and REQUESTS_AVAILABLE
    
    def check_claims(self, text: str, max_claims: int = 5) -> List[Dict[str, Any]]:
        """
        Check claims in the text against fact-checking databases.
        
        Args:
            text: Text to fact-check
            max_claims: Maximum number of claims to return
            
        Returns:
            List of fact-check results
        """
        if not self.enabled:
            return self._mock_fact_check_response()
        
        try:
            # Extract key claims from text (simplified approach)
            claims = self._extract_claims(text)
            
            fact_check_results = []
            for claim in claims[:max_claims]:
                result = self._query_google_factcheck(claim)
                if result:
                    fact_check_results.extend(result)
            
            return fact_check_results[:max_claims]
            
        except Exception as e:
            logger.error(f"Fact-check query failed: {e}")
            return []
    
    def _extract_claims(self, text: str) -> List[str]:
        """
        Extract potential factual claims from text.
        
        This is a simplified implementation. In production, you might use
        more sophisticated NLP techniques to identify factual statements.
        """
        import re
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter for sentences that might contain factual claims
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for sentences with numbers, dates, names, or factual indicators
            if (len(sentence) > 20 and 
                (re.search(r'\d+', sentence) or  # Contains numbers
                 re.search(r'\b(said|reported|according|study|research|data)\b', sentence, re.IGNORECASE) or
                 re.search(r'\b(percent|million|billion|thousand)\b', sentence, re.IGNORECASE))):
                claims.append(sentence)
        
        return claims[:5]  # Limit to 5 claims
    
    def _query_google_factcheck(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Query Google Fact Check Tools API."""
        try:
            if not REQUESTS_AVAILABLE:
                return None
                
            params = {
                'key': self.api_key,
                'query': query,
                'languageCode': 'en'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            claims = data.get('claims', [])
            
            results = []
            for claim in claims:
                claim_review = claim.get('claimReview', [])
                if claim_review:
                    review = claim_review[0]  # Take first review
                    results.append({
                        'claim': claim.get('text', query),
                        'url': review.get('url', ''),
                        'verdict': review.get('textualRating', 'Unknown'),
                        'publisher': review.get('publisher', {}).get('name', 'Unknown'),
                        'review_date': review.get('reviewDate', '')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Google Fact Check API error: {e}")
            return None
    
    def _mock_fact_check_response(self) -> List[Dict[str, Any]]:
        """
        Return mock fact-check response when API is not available.
        
        This provides a consistent interface for testing and development.
        """
        return [
            {
                'claim': 'Fact-checking service unavailable',
                'url': '',
                'verdict': 'API key required',
                'publisher': 'System',
                'review_date': '',
                'mock': True
            }
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get fact-check adapter status."""
        return {
            'enabled': self.enabled,
            'api_key_set': self.api_key is not None,
            'service': 'Google Fact Check Tools API' if self.enabled else 'Mock service'
        }
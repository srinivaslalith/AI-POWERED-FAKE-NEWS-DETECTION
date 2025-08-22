"""Web scraper module for extracting article content from URLs."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Optional
import re


class ArticleScraper:
    """Scraper for extracting article content from web pages."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_article(self, url: str) -> Dict[str, Optional[str]]:
        """
        Extract article content from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dict containing 'text', 'title', 'domain', and 'error' keys
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'text': None,
                    'title': None,
                    'domain': None,
                    'error': 'Invalid URL format'
                }
            
            domain = parsed_url.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Fetch the page
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            text = self._extract_main_content(soup)
            
            if not text:
                return {
                    'text': None,
                    'title': title,
                    'domain': domain,
                    'error': 'Could not extract article content'
                }
            
            return {
                'text': text,
                'title': title,
                'domain': domain,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'text': None,
                'title': None,
                'domain': None,
                'error': f'Failed to fetch URL: {str(e)}'
            }
        except Exception as e:
            return {
                'text': None,
                'title': None,
                'domain': None,
                'error': f'Scraping error: {str(e)}'
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title from HTML."""
        # Try various title selectors
        title_selectors = [
            'h1',
            'title',
            '[property="og:title"]',
            '[name="twitter:title"]',
            '.article-title',
            '.post-title',
            '.entry-title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True) if hasattr(element, 'get_text') else element.get('content', '')
                if title and len(title) > 5:  # Basic validation
                    return title
        
        return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main article content from HTML."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            element.decompose()
        
        # Try common article content selectors
        content_selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            '.story-body',
            '.article-body',
            'main'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = self._clean_text(element.get_text())
                if text and len(text) > 100:  # Minimum content length
                    return text
        
        # Fallback: extract from body and filter by paragraph length
        body = soup.find('body')
        if body:
            paragraphs = body.find_all('p')
            article_text = []
            for p in paragraphs:
                text = self._clean_text(p.get_text())
                if len(text) > 50:  # Filter out short paragraphs
                    article_text.append(text)
            
            if article_text:
                return '\n\n'.join(article_text)
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
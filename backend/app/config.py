"""Configuration management for the fake news detector."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration class for loading and managing application settings."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file and environment variables."""
        # Load from YAML file - check both relative and absolute paths
        config_file = Path(self.config_path)
        if not config_file.is_absolute():
            # Try relative to current directory first
            if not config_file.exists():
                # Try relative to this file's directory
                config_file = Path(__file__).parent.parent / self.config_path
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = {}
        
        # Override with environment variables
        config.setdefault('model', {})
        config['model']['name'] = os.getenv('MODEL_NAME', config.get('model', {}).get('name', 'mrm8488/bert-tiny-finetuned-fake-news-detection'))
        config['model']['max_length'] = int(os.getenv('MODEL_MAX_LENGTH', config.get('model', {}).get('max_length', 512)))
        
        config.setdefault('factcheck', {})
        config['factcheck']['api_key'] = os.getenv('FACTCHECK_API_KEY', config.get('factcheck', {}).get('api_key'))
        config['factcheck']['enabled'] = config['factcheck']['api_key'] is not None
        
        config.setdefault('scoring', {})
        config['scoring'].setdefault('weights', {})
        weights = config['scoring']['weights']
        weights['model_confidence'] = float(os.getenv('WEIGHT_MODEL', weights.get('model_confidence', 0.5)))
        weights['fact_check_evidence'] = float(os.getenv('WEIGHT_FACTCHECK', weights.get('fact_check_evidence', 0.3)))
        weights['source_reputation'] = float(os.getenv('WEIGHT_SOURCE', weights.get('source_reputation', 0.2)))
        
        config.setdefault('domain_reputation', {})
        config['domain_reputation']['file'] = os.getenv('DOMAIN_REPUTATION_FILE', 
                                                       config.get('domain_reputation', {}).get('file', 'domain_reputation.json'))
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def model_name(self) -> str:
        return self.get('model.name')
    
    @property
    def model_max_length(self) -> int:
        return self.get('model.max_length')
    
    @property
    def factcheck_api_key(self) -> Optional[str]:
        return self.get('factcheck.api_key')
    
    @property
    def factcheck_enabled(self) -> bool:
        return self.get('factcheck.enabled', False)
    
    @property
    def scoring_weights(self) -> Dict[str, float]:
        return self.get('scoring.weights', {})
    
    @property
    def domain_reputation_file(self) -> str:
        return self.get('domain_reputation.file')


# Global config instance
config = Config()
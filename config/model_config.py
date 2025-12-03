"""
Model Configuration Module
===========================
Centralized configuration management for ML model parameters.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

class ModelConfig:
    """Configuration class for T5 model and training parameters."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    # Model Configuration
    @property
    def model_name(self) -> str:
        return self._config['model']['name']
    
    @property
    def pretrained_path(self) -> str:
        return self._config['model']['pretrained_path']
    
    @property
    def max_input_length(self) -> int:
        return self._config['model']['max_input_length']
    
    @property
    def max_output_length(self) -> int:
        return self._config['model']['max_output_length']
    
    @property
    def vocab_size(self) -> int:
        return self._config['model']['vocab_size']
    
    # Generation Parameters
    @property
    def num_beams(self) -> int:
        return self._config['model']['generation']['num_beams']
    
    @property
    def temperature(self) -> float:
        return self._config['model']['generation']['temperature']
    
    @property
    def top_p(self) -> float:
        return self._config['model']['generation']['top_p']
    
    @property
    def top_k(self) -> int:
        return self._config['model']['generation']['top_k']
    
    # Training Configuration
    @property
    def dataset_name(self) -> str:
        return self._config['training']['dataset']
    
    @property
    def batch_size(self) -> int:
        return self._config['training']['batch_size']
    
    @property
    def learning_rate(self) -> float:
        return self._config['training']['learning_rate']
    
    @property
    def num_epochs(self) -> int:
        return self._config['training']['num_epochs']
    
    @property
    def optimizer(self) -> str:
        return self._config['training']['optimizer']
    
    # Data Configuration
    @property
    def database_path(self) -> str:
        return self._config['data']['database_path']
    
    @property
    def chunk_size(self) -> int:
        return self._config['data']['chunk_size']
    
    @property
    def chunk_overlap(self) -> int:
        return self._config['data']['chunk_overlap']
    
    # Application Configuration
    @property
    def app_title(self) -> str:
        return self._config['app']['title']
    
    @property
    def app_port(self) -> int:
        return self._config['app']['port']
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get all model-related configuration."""
        return self._config['model']
    
    def get_training_config(self) -> Dict[str, Any]:
        """Get all training-related configuration."""
        return self._config['training']
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get all data-related configuration."""
        return self._config['data']
    
    def __repr__(self) -> str:
        return f"ModelConfig(config_path='{self.config_path}')"


# Global config instance
config = ModelConfig()


if __name__ == "__main__":
    # Test configuration loading
    cfg = ModelConfig()
    print(f"Model: {cfg.model_name}")
    print(f"Batch size: {cfg.batch_size}")
    print(f"Learning rate: {cfg.learning_rate}")
    print(f"Num beams: {cfg.num_beams}")
    print("\nFull model config:")
    print(cfg.get_model_config())

import os
import psutil
import sys
from pathlib import Path

# Fix Windows Unicode logging
if sys.platform == 'win32':
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        # Fallback for Windows systems without UTF-8 locale
        pass
from typing import Dict, Any

class Config:
    """Application configuration class"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MODELS_FOLDER = BASE_DIR / "models"
    LOGS_FOLDER = BASE_DIR / "logs"
    
    # Create necessary directories
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    MODELS_FOLDER.mkdir(exist_ok=True)
    LOGS_FOLDER.mkdir(exist_ok=True)
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB to accommodate larger files
    ALLOWED_EXTENSIONS = {'.csv', '.pdf'}
    UPLOAD_FOLDER = BASE_DIR / 'uploads'  # Make sure uploads folder exists
    UPLOAD_FOLDER.mkdir(exist_ok=True)  # Create if it doesn't exist
    
    # Processing settings optimized for CPU efficiency
    CHUNK_SIZE = 1000  # Process data in smaller chunks to prevent CPU overload
    MAX_ROWS = 10000   # Maximum number of rows to process (reduced for better performance)
    MAX_COLUMNS = 100  # Maximum number of columns to process (reduced for better performance)
    
    # Set number of workers based on CPU cores (conservative approach)
    NUM_WORKERS = max(1, min(4, psutil.cpu_count(logical=False)))  # Limit to max 4 workers to prevent CPU overload
    
    # Database settings (for future use)
    DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/financial_tracker.db')
    
    # ML Model settings
    MODEL_PATH = MODELS_FOLDER / "categorization_model.pkl"
    MIN_CONFIDENCE_SCORE = 0.5
    
    # Security settings
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.plot.ly https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data: https:;"
    }
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # Logging configuration
    LOG_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': str(LOGS_FOLDER / 'financial_tracker.log'),
                'formatter': 'detailed',
                'level': 'INFO'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file']
        }
    }
    
    # Chart configuration
    CHART_CONFIG = {
        'theme': 'plotly_white',
        'color_palette': [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD'
        ],
        'font_family': 'Arial, sans-serif'
    }
    
    # Budget defaults (as percentage of income)
    DEFAULT_BUDGET_PERCENTAGES = {
        'food': 0.15,        # 15%
        'transport': 0.10,    # 10%
        'entertainment': 0.05, # 5%
        'shopping': 0.10,     # 10%
        'utilities': 0.08,    # 8%
        'healthcare': 0.08,   # 8%
        'education': 0.05,    # 5%
        'travel': 0.05,       # 5%
        'insurance': 0.08,    # 8%
        'investment': 0.20,   # 20%
        'other': 0.06         # 6%
    }
    
    @classmethod
    def get_environment_config(cls) -> Dict[str, Any]:
        """Get configuration based on environment"""
        env = os.environ.get('FLASK_ENV', 'development')
        
        if env == 'production':
            return {
                'DEBUG': False,
                'TESTING': False,
                'LOG_LEVEL': 'INFO',
                'SECURITY_HEADERS_ENABLED': True
            }
        elif env == 'testing':
            return {
                'DEBUG': False,
                'TESTING': True,
                'LOG_LEVEL': 'WARNING',
                'SECURITY_HEADERS_ENABLED': False
            }
        else:  # development
            return {
                'DEBUG': True,
                'TESTING': False,
                'LOG_LEVEL': 'DEBUG',
                'SECURITY_HEADERS_ENABLED': False
            }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    return config_map.get(config_name, DevelopmentConfig)

"""
Centralized configuration management for the petrol price forecasting system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Database Configuration
class DatabaseConfig:
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'petrol_price_db')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    @classmethod
    def get_database_uri(cls):
        """Generate database URI based on DB_TYPE"""
        if cls.DB_TYPE == 'sqlite':
            db_path = BASE_DIR / 'petrol_price.db'
            return f'sqlite:///{db_path}'
        elif cls.DB_TYPE == 'mysql':
            return f'mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}'
        elif cls.DB_TYPE == 'postgresql':
            return f'postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}'
        else:
            raise ValueError(f"Unsupported database type: {cls.DB_TYPE}")

# Flask Configuration
class FlaskConfig:
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('FLASK_PORT', 5000))
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

# Path Configuration
class PathConfig:
    UPLOAD_FOLDER = BASE_DIR / os.getenv('UPLOAD_FOLDER', 'uploads')
    MODEL_FOLDER = BASE_DIR / os.getenv('MODEL_FOLDER', 'ml_pipeline/saved_models')
    REPORTS_FOLDER = BASE_DIR / os.getenv('REPORTS_FOLDER', 'reports')
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.MODEL_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)

# Scheduler Configuration
class SchedulerConfig:
    ENABLE_SCHEDULER = os.getenv('ENABLE_SCHEDULER', 'True').lower() == 'true'
    DATA_FETCH_HOUR = int(os.getenv('DATA_FETCH_HOUR', 9))
    RETRAIN_DAY = int(os.getenv('RETRAIN_DAY', 6))  # Sunday
    RETRAIN_HOUR = int(os.getenv('RETRAIN_HOUR', 2))

# Data Source Configuration
class DataSourceConfig:
    PETROL_PRICE_URL = os.getenv('PETROL_PRICE_URL', 'https://www.goodreturns.in/petrol-price.html')
    CRUDE_OIL_TICKER = os.getenv('CRUDE_OIL_TICKER', 'CL=F')
    INR_USD_TICKER = os.getenv('INR_USD_TICKER', 'INR=X')

# Model Configuration
class ModelConfig:
    MAX_TRIALS = int(os.getenv('MAX_TRIALS', 10))
    EPOCHS = int(os.getenv('EPOCHS', 50))
    VALIDATION_SPLIT = float(os.getenv('VALIDATION_SPLIT', 0.2))
    BATCH_SIZE = 32
    
    # Feature engineering parameters
    LAG_FEATURES = [1, 2, 7, 14]
    ROLLING_WINDOWS = [7]
    
    # Forecast horizons
    FORECAST_HORIZONS = [7, 14, 30]

# Initialize directories on import
PathConfig.ensure_directories()

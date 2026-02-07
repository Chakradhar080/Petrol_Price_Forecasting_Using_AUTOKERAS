"""
Scheduled jobs for automated data fetching, prediction, and retraining.
"""
from datetime import datetime
from scraper.data_ingestion_service import ingest_latest_data
from backend.services.prediction_service import predict
from backend.services.training_service import train_new_model
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/scheduler.log')

def daily_data_fetch_job():
    """
    Daily job to fetch latest petrol price and macro data
    Runs every day at configured time (default: 9 AM)
    """
    try:
        logger.info("=== Starting daily data fetch job ===")
        
        # Fetch and ingest latest data
        status = ingest_latest_data()
        
        if status['petrol_price'] or status['macro_data']:
            logger.info(f"Data fetch successful: {status}")
        else:
            logger.warning(f"Data fetch completed with issues: {status}")
        
        logger.info("=== Daily data fetch job complete ===")
        
    except Exception as e:
        logger.error(f"Error in daily_data_fetch_job: {str(e)}")

def daily_prediction_job():
    """
    Daily job to generate predictions using latest model
    Runs every day after data fetch
    """
    try:
        logger.info("=== Starting daily prediction job ===")
        
        # Generate 7-day forecast
        result = predict(horizon_days=7)
        
        if result.get('success'):
            logger.info(f"Prediction successful using {result['model_version']}")
        else:
            logger.error(f"Prediction failed: {result.get('error')}")
        
        logger.info("=== Daily prediction job complete ===")
        
    except Exception as e:
        logger.error(f"Error in daily_prediction_job: {str(e)}")

def weekly_retraining_job():
    """
    Weekly job to retrain model with updated data
    Runs once a week (default: Sunday 2 AM)
    """
    try:
        logger.info("=== Starting weekly retraining job ===")
        
        # Train new model
        result = train_new_model()
        
        if result.get('success'):
            logger.info(f"Retraining successful: {result['model_version']}")
            logger.info(f"Metrics - RMSE: {result['metrics']['rmse']}, "
                       f"MAE: {result['metrics']['mae']}, "
                       f"MAPE: {result['metrics']['mape']}%")
        else:
            logger.error(f"Retraining failed: {result.get('error')}")
        
        logger.info("=== Weekly retraining job complete ===")
        
    except Exception as e:
        logger.error(f"Error in weekly_retraining_job: {str(e)}")

def combined_daily_job():
    """
    Combined daily job: fetch data then generate prediction
    """
    daily_data_fetch_job()
    daily_prediction_job()

"""
Prediction orchestration service.
Handles prediction requests and logging.
"""
import json
from datetime import datetime
from ml_pipeline.predict import generate_forecast
from db.database import get_db_session
from db.models import PredictionLog
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/prediction_service.log')

class PredictionService:
    """Service for orchestrating predictions"""
    
    def __init__(self):
        pass
    
    def generate_prediction(self, horizon_days=7, model_version=None, end_date=None):
        """
        Generate prediction and log to database
        
        Args:
            horizon_days: Number of days to forecast
            model_version: Optional specific model version
            end_date: Optional end date string
        
        Returns:
            dict: Prediction results
        """
        try:
            logger.info(f"Generating forecast. Horizon: {horizon_days}, End Date: {end_date}")
            
            # Generate forecast
            result = generate_forecast(horizon_days, model_version, end_date)
            
            if not result.get('success'):
                return result
            
            # Log prediction
            self.log_prediction(
                horizon_days,
                result['model_version'],
                result['predictions']
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating prediction: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def log_prediction(self, horizon_days, model_version, predictions):
        """
        Log prediction to database
        
        Args:
            horizon_days: Forecast horizon
            model_version: Model version used
            predictions: List of predictions
        
        Returns:
            bool: Success status
        """
        try:
            with get_db_session() as session:
                log_entry = PredictionLog(
                    horizon_days=horizon_days,
                    model_version=model_version,
                    predictions_json=json.dumps(predictions)
                )
                session.add(log_entry)
            
            logger.info(f"Logged prediction for {horizon_days} days using {model_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging prediction: {str(e)}")
            return False
    
    def get_prediction_history(self, limit=10):
        """
        Get recent prediction history
        
        Args:
            limit: Number of recent predictions to fetch
        
        Returns:
            list: List of prediction logs
        """
        try:
            with get_db_session() as session:
                logs = session.query(PredictionLog).order_by(
                    PredictionLog.request_time.desc()
                ).limit(limit).all()
                
                return [log.to_dict() for log in logs]
                
        except Exception as e:
            logger.error(f"Error getting prediction history: {str(e)}")
            return []

# Convenience function
def predict(horizon_days=7, model_version=None, end_date=None):
    """Generate prediction"""
    service = PredictionService()
    return service.generate_prediction(horizon_days, model_version, end_date)

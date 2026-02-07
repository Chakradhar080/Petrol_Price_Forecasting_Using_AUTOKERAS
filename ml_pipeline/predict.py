"""
Prediction module for generating forecasts.
Updated to work with Keras models instead of Auto-Keras.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle
from tensorflow import keras
from db.database import get_db_session
from db.models import ProcessedFeature, ModelRegistry
from config import PathConfig
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/prediction.log')

def load_model_and_scaler(model_version=None):
    """
    Load trained model and scaler
    
    Args:
        model_version: Specific version to load, or None for latest
    
    Returns:
        tuple: (model, scaler, model_version, metrics)
    """
    try:
        with get_db_session() as session:
            if model_version:
                model_record = session.query(ModelRegistry).filter_by(
                    model_version=model_version
                ).first()
            else:
                model_record = session.query(ModelRegistry).order_by(
                    ModelRegistry.created_at.desc()
                ).first()
            
            if not model_record:
                logger.error("No trained model found")
                return None, None, None, None
            
            model_path = model_record.model_path
            scaler_path = model_path.replace('.h5', '_scaler.pkl')
            
            # Load Keras model
            model = keras.models.load_model(model_path)
            
            # Load scaler
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            
            metrics = {
                'rmse': model_record.rmse,
                'mae': model_record.mae,
                'mape': model_record.mape
            }
            
            logger.info(f"Loaded model {model_record.model_version}")
            
            return model, scaler, model_record.model_version, metrics
            
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None, None, None, None

def get_latest_features():
    """
    Get the most recent feature row from database
    
    Returns:
        dict: Latest features
    """
    try:
        with get_db_session() as session:
            latest = session.query(ProcessedFeature).order_by(
                ProcessedFeature.date.desc()
            ).first()
            
            if not latest:
                logger.error("No features found in database")
                return None
            
            return latest.to_dict()
            
    except Exception as e:
        logger.error(f"Error getting latest features: {str(e)}")
        return None

def generate_forecast(horizon_days=7, model_version=None, end_date=None):
    """
    Generate multi-day forecast using recursive prediction
    
    Args:
        horizon_days: Number of days to forecast (default 7)
        model_version: Optional specific model version to use
        end_date: Optional end date string (YYYY-MM-DD) to calculate horizon
    """
    try:
        logger.info(f"Generating forecast. Horizon: {horizon_days}, End Date: {end_date}")
        
        # Load model
        model, scaler, version, metrics = load_model_and_scaler(model_version)
        
        if model is None:
            return {'success': False, 'error': 'No trained model available'}
        
        # Get latest features
        latest = get_latest_features()
        
        if not latest:
            return {'success': False, 'error': 'No feature data available'}
        
        # Initialize predictions list
        predictions = []
        
        # Current feature state
        current_features = {
            'petrol_price': latest['petrol_price'],
            'lag_1': latest['lag_1'] if latest['lag_1'] else latest['petrol_price'],
            'lag_2': latest['lag_2'] if latest['lag_2'] else latest['petrol_price'],
            'lag_7': latest['lag_7'] if latest['lag_7'] else latest['petrol_price'],
            'lag_14': latest['lag_14'] if latest['lag_14'] else latest['petrol_price'],
            'rolling_7': latest['rolling_7'] if latest['rolling_7'] else latest['petrol_price'],
            'crude_oil_price': latest['crude_oil_price'] if latest['crude_oil_price'] else 80.0,
            'inr_usd': latest['inr_usd'] if latest['inr_usd'] else 83.0
        }
        
        # Use current system date for forecasting, not database date
        # This ensures forecasts always start from tomorrow regardless of when data was last updated
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Start from tomorrow (next day)
        current_date = current_date + timedelta(days=1)
        
        # If end_date is provided, calculate horizon_days
        if end_date:
            try:
                if isinstance(end_date, str):
                    target_date = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    target_date = datetime.combine(end_date, datetime.min.time())
                
                delta = target_date - current_date
                horizon_days = delta.days + 1
                
                if horizon_days <= 0:
                     return {'success': False, 'error': 'End date must be after latest data date'}
                     
                logger.info(f"Calculated horizon days from end date: {horizon_days}")
            except ValueError:
                return {'success': False, 'error': 'Invalid end date format'}
        
        # Recursive forecasting
        for day in range(horizon_days):
            # Prepare input
            X = np.array([[
                current_features['petrol_price'],
                current_features['lag_1'],
                current_features['lag_2'],
                current_features['lag_7'],
                current_features['lag_14'],
                current_features['rolling_7'],
                current_features['crude_oil_price'],
                current_features['inr_usd']
            ]])
            
            # Scale features
            X_scaled = scaler.transform(X)
            
            # Predict
            pred = model.predict(X_scaled, verbose=0)[0][0]
            
            # Ensure prediction is in reasonable range (petrol prices are typically 90-120)
            pred = max(90.0, min(150.0, float(pred)))
            
            # Store prediction
            predictions.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'predicted_price': round(pred, 2)
            })
            
            # Update features for next iteration
            current_features['lag_14'] = current_features['lag_7']
            current_features['lag_7'] = current_features['lag_2']
            current_features['lag_2'] = current_features['lag_1']
            current_features['lag_1'] = current_features['petrol_price']
            current_features['petrol_price'] = pred
            
            # Update rolling average (simplified)
            current_features['rolling_7'] = (current_features['rolling_7'] * 6 + pred) / 7
            
            # Move to next day
            current_date += timedelta(days=1)
        
        logger.info(f"Forecast generated successfully using {version}")
        
        return {
            'success': True,
            'model_version': version,
            'horizon_days': horizon_days,
            'predictions': predictions,
            'metrics': metrics
        }
        
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {'success': False, 'error': str(e)}


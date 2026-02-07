"""
Prediction routes for Flask API.
Handles forecast generation.
"""
from flask import Blueprint, request, jsonify
from backend.services.prediction_service import predict, PredictionService
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/api.log')

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/forecast', methods=['POST'])
def generate_forecast():
    """
    Generate petrol price forecast
    
    Request:
        {
            horizon_days: int (7, 14, or 30),
            model_version: str (optional)
        }
    
    Response:
        {
            success: bool,
            model_version: str,
            horizon_days: int,
            predictions: [
                {date: str, predicted_price: float},
                ...
            ],
            metrics: {
                rmse: float,
                mae: float,
                mape: float
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        horizon_days = data.get('horizon_days', 7)
        model_version = data.get('model_version')
        end_date = data.get('end_date')
        
        # Validate horizon only if end_date is not provided
        if not end_date and horizon_days <= 0:
            return jsonify({
                'success': False,
                'error': 'horizon_days must be positive'
            }), 400
        
        logger.info(f"Forecast request: {horizon_days} days, end_date: {end_date}, model: {model_version or 'latest'}")
        
        # Generate forecast
        result = predict(horizon_days, model_version, end_date)
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        logger.error(f"Error in generate_forecast: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@prediction_bp.route('/forecast/history', methods=['GET'])
def get_forecast_history():
    """
    Get recent prediction history
    
    Query params:
        - limit: Number of records (default: 10)
    
    Response:
        {
            success: bool,
            history: [...]
        }
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        service = PredictionService()
        history = service.get_prediction_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_forecast_history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

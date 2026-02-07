"""
Training routes for Flask API.
Handles model training and version management.
"""
from flask import Blueprint, request, jsonify
from backend.services.training_service import train_new_model
from ml_pipeline.model_registry import get_all_models, get_latest_model, get_best_model
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/api.log')

training_bp = Blueprint('training', __name__)

@training_bp.route('/train', methods=['POST'])
def train_model():
    """
    Trigger model training
    
    Request (optional):
        {
            start_date: "YYYY-MM-DD",
            end_date: "YYYY-MM-DD"
        }
    
    Response:
        {
            success: bool,
            model_version: str,
            metrics: {...},
            training_samples: int,
            validation_samples: int
        }
    """
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        logger.info(f"Training request received (start: {start_date}, end: {end_date})")
        
        # Train model
        result = train_new_model(start_date, end_date)
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        logger.error(f"Error in train_model: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/model/versions', methods=['GET'])
def get_model_versions():
    """
    Get all model versions
    
    Response:
        {
            success: bool,
            models: [...]
        }
    """
    try:
        models = get_all_models()
        
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_model_versions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/metrics/latest', methods=['GET'])
def get_latest_metrics():
    """
    Get metrics for latest model
    
    Response:
        {
            success: bool,
            model: {...}
        }
    """
    try:
        model = get_latest_model()
        
        if model:
            return jsonify({
                'success': True,
                'model': model
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No models found'
            }), 404
        
    except Exception as e:
        logger.error(f"Error in get_latest_metrics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/metrics/best', methods=['GET'])
def get_best_metrics():
    """
    Get best model by metric
    
    Query params:
        - metric: 'rmse', 'mae', or 'mape' (default: rmse)
    
    Response:
        {
            success: bool,
            model: {...}
        }
    """
    try:
        metric = request.args.get('metric', 'rmse')
        
        model = get_best_model(metric)
        
        if model:
            return jsonify({
                'success': True,
                'model': model,
                'metric_used': metric
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No models found'
            }), 404
        
    except Exception as e:
        logger.error(f"Error in get_best_metrics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

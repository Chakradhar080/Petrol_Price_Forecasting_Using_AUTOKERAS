"""
Main Flask application.
Initializes the API server and registers all routes.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.routes.data_routes import data_bp
from backend.routes.training_routes import training_bp
from backend.routes.prediction_routes import prediction_bp
from backend.routes.sync_routes import sync_bp
from backend.routes.prepare_routes import prepare_bp
from db.database import db_manager
from config import FlaskConfig
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/app.log')

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = FlaskConfig.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = FlaskConfig.MAX_CONTENT_LENGTH
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize database
    try:
        db_manager.create_all_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    # Register blueprints
    app.register_blueprint(data_bp, url_prefix='/api')
    app.register_blueprint(training_bp, url_prefix='/api')
    app.register_blueprint(prediction_bp, url_prefix='/api')
    app.register_blueprint(sync_bp, url_prefix='/api')
    app.register_blueprint(prepare_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'petrol-price-api'}), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'service': 'Petrol Price Forecasting API',
            'version': '1.0.0',
            'endpoints': {
                'data': '/api/upload-dataset, /api/data/raw, /api/data/processed, /api/data/latest',
                'training': '/api/train, /api/model/versions, /api/metrics/latest, /api/metrics/best',
                'prediction': '/api/forecast, /api/forecast/history'
            }
        }), 200
    
    logger.info("Flask application created successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=FlaskConfig.PORT,
        debug=FlaskConfig.DEBUG
    )

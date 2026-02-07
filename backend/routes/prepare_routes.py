"""
Data preparation routes for running ETL and feature engineering.
"""
from flask import Blueprint, jsonify, request
from ml_pipeline.preprocess import run_etl_pipeline
from ml_pipeline.feature_engineering import engineer_features, save_features
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/api.log')

prepare_bp = Blueprint('prepare', __name__)

@prepare_bp.route('/prepare-data', methods=['POST'])
def prepare_data():
    """
    Run ETL pipeline and feature engineering to prepare data for training
    
    Request body (optional):
    {
        "data_source": "combined" | "yahoo_finance" | "custom_csv"
    }
    
    Response:
        {
            success: bool,
            message: str,
            samples: int,
            data_source: str
        }
    """
    try:
        # Get data source from request (default: combined)
        data = request.get_json() or {}
        data_source = data.get('data_source', 'combined')
        
        logger.info(f"Starting data preparation (source: {data_source})...")
        
        # Step 1: ETL
        logger.info("Running ETL pipeline...")
        cleaned_df = run_etl_pipeline(source_filter=data_source)
        
        if cleaned_df.empty:
            return jsonify({
                'success': False,
                'message': f'ETL pipeline returned no data for source: {data_source}. Please upload data first.'
            }), 400
        
        logger.info(f"ETL complete: {len(cleaned_df)} records")
        
        # Step 2: Feature Engineering
        logger.info("Engineering features...")
        features_df = engineer_features(cleaned_df)
        
        if features_df.empty:
            return jsonify({
                'success': False,
                'message': 'Feature engineering returned no data'
            }), 400
        
        logger.info(f"Features engineered: {len(features_df)} samples")
        
        # Step 3: Save to database
        count = save_features(features_df)
        logger.info(f"Saved {count} processed features")
        
        return jsonify({
            'success': True,
            'message': f'Data prepared successfully! {count} training samples ready (source: {data_source}).',
            'samples': count,
            'data_source': data_source
        }), 200
        
    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

"""
Training orchestration service.
Coordinates ETL, feature engineering, model training, and evaluation.
"""
from datetime import datetime
from ml_pipeline.preprocess import run_etl_pipeline
from ml_pipeline.feature_engineering import engineer_features, save_features
from ml_pipeline.train import train_model
from ml_pipeline.evaluate import evaluate_model
from ml_pipeline.model_registry import register_model, get_next_model_version
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/training.log')

def train_new_model(start_date=None, end_date=None):
    """
    Complete training pipeline with automatic data fetching:
    0. Fetch latest data from Yahoo Finance
    1. Run ETL
    2. Engineer features
    3. Train model
    4. Evaluate model
    5. Register model
    
    Args:
        start_date: Optional start date for training data
        end_date: Optional end date for training data
    
    Returns:
        dict: Training results
    """
    try:
        logger.info("Starting full training pipeline...")
        
        # Step 0: Fetch latest data from Yahoo Finance (NEW!)
        logger.info("Step 0/5: Fetching latest data from Yahoo Finance...")
        try:
            from scraper.data_ingestion_service import ingest_latest_data
            fetch_status = ingest_latest_data()
            logger.info(f"✓ Data fetch complete: {fetch_status}")
        except Exception as e:
            logger.warning(f"⚠ Data fetch failed (continuing with existing data): {str(e)}")
        
        # Step 1: ETL
        logger.info("Step 1/5: Running ETL pipeline...")
        cleaned_df = run_etl_pipeline()
        
        if cleaned_df.empty:
            return {'success': False, 'message': 'ETL pipeline returned no data'}
        
        logger.info(f"✓ ETL complete: {len(cleaned_df)} records")
        
        # Step 2: Feature Engineering
        logger.info("Step 2/5: Engineering features...")
        features_df = engineer_features(cleaned_df)
        
        if features_df.empty:
            return {'success': False, 'message': 'Feature engineering returned no data'}
        
        logger.info(f"✓ Features engineered: {len(features_df)} samples")
        
        # Save features to database
        save_features(features_df)
        logger.info("✓ Features saved to database")
        
        # Step 3: Train Model
        logger.info("Step 3/5: Training model...")
        model_version = get_next_model_version()
        logger.info(f"Assigned model version: {model_version}")
        
        training_result = train_model(model_version, start_date, end_date)
        
        if not training_result.get('success'):
            return training_result
        
        logger.info(f"✓ Model trained: {model_version}")
        
        # Step 4: Evaluate Model
        logger.info("Step 4/5: Evaluating model...")
        eval_result = evaluate_model(
            training_result['y_val'],
            training_result['y_pred'],
            model_version,
            training_result['model_path'],
            training_result['training_samples']
        )
        
        if not eval_result.get('success'):
            return eval_result
        
        logger.info("✓ Model evaluation complete")
        
        # Step 5: Register Model
        logger.info("Step 5/5: Registering model...")
        register_model(
            model_version=model_version,
            model_path=training_result['model_path'],
            metrics=eval_result['metrics'],
            training_samples=training_result['training_samples'],
            data_source='combined'  # Track which data source trained this model
        )
        
        logger.info("🚀 Training pipeline complete!")
        
        return {
            'success': True,
            'model_version': model_version,
            'metrics': eval_result['metrics'],
            'training_samples': training_result['training_samples'],
            'validation_samples': training_result['validation_samples'],
            'data_source': 'combined',  # NEW: Track data source
            'data_auto_fetched': True  # NEW: Indicates data was fetched automatically
        }
        
    except Exception as e:
        logger.error(f"Error in training pipeline: {str(e)}")
        return {'success': False, 'message': str(e)}

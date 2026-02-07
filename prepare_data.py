"""
Complete data preparation script.
Runs ETL and feature engineering to prepare data for training.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ml_pipeline.preprocess import run_etl_pipeline
from ml_pipeline.feature_engineering import engineer_features, save_features
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/prepare_data.log')

def main():
    """Run ETL and feature engineering"""
    
    print("=" * 60)
    print("  Data Preparation - ETL & Feature Engineering")
    print("=" * 60)
    print()
    
    # Step 1: ETL
    print("[1/2] Running ETL pipeline...")
    try:
        cleaned_df = run_etl_pipeline()
        
        if cleaned_df.empty:
            print("✗ ETL pipeline returned no data")
            print("\nMake sure you have uploaded data first:")
            print("  python init_db.py")
            return
        
        print(f"✓ ETL complete: {len(cleaned_df)} records cleaned")
    except Exception as e:
        print(f"✗ ETL failed: {e}")
        return
    
    # Step 2: Feature Engineering
    print("\n[2/2] Engineering features...")
    try:
        features_df = engineer_features(cleaned_df)
        
        if features_df.empty:
            print("✗ Feature engineering returned no data")
            return
        
        print(f"✓ Features engineered: {len(features_df)} records")
        
        # Save to database
        save_features(features_df)
        print(f"✓ Features saved to database")
        
    except Exception as e:
        print(f"✗ Feature engineering failed: {e}")
        return
    
    print()
    print("=" * 60)
    print("  Data Preparation Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Go to 'Train Model' page and click 'Start Training'")
    print("2. After training, go to 'Forecast' page")
    print()
    print("Ready to train! 🚀")

if __name__ == '__main__':
    main()

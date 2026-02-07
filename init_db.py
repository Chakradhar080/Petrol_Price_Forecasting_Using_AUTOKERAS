"""
Quick start script to initialize the database and upload sample data.
Run this after installation to get started quickly.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from db.database import db_manager
from scraper.file_upload_handler import process_file_upload
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/init.log')

def main():
    """Initialize database and load sample data"""
    
    print("=" * 60)
    print("Petrol Price Forecasting System - Quick Start")
    print("=" * 60)
    
    # Step 1: Create database tables
    print("\n[1/3] Creating database tables...")
    try:
        db_manager.create_all_tables()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return
    
    # Step 2: Upload sample petrol data
    print("\n[2/3] Uploading sample petrol price data...")
    try:
        result = process_file_upload('sample_data_petrol.csv', 'petrol')
        if result['success']:
            print(f"✓ Uploaded {result['count']} petrol price records")
        else:
            print(f"✗ Error: {result['message']}")
    except Exception as e:
        print(f"✗ Error uploading petrol data: {e}")
    
    # Step 3: Upload sample macro data
    print("\n[3/3] Uploading sample macro data...")
    try:
        result = process_file_upload('sample_data_macro.csv', 'macro')
        if result['success']:
            print(f"✓ Uploaded {result['count']} macro data records")
        else:
            print(f"✗ Error: {result['message']}")
    except Exception as e:
        print(f"✗ Error uploading macro data: {e}")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start backend: python backend/app.py")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000")
    print("4. Go to 'Train Model' page and click 'Start Training'")
    print("5. After training, go to 'Forecast' page to generate predictions")
    print("\nHappy forecasting! 🚀")

if __name__ == '__main__':
    main()

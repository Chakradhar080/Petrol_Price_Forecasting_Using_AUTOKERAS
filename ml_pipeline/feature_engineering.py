"""
Feature engineering for time-series forecasting.
Creates lag features, rolling averages, and prepares target variable.
"""
import pandas as pd
import numpy as np
from db.database import get_db_session
from db.models import ProcessedFeature
from utils.logger import setup_logger
from config import ModelConfig

logger = setup_logger(__name__, 'logs/feature_engineering.log')

class FeatureEngineer:
    """Feature engineering for petrol price forecasting"""
    
    def __init__(self):
        self.lag_features = ModelConfig.LAG_FEATURES
        self.rolling_windows = ModelConfig.ROLLING_WINDOWS
    
    def create_lag_features(self, df, column='petrol_price', lags=None):
        """
        Create lag features for time series
        
        Args:
            df: Input DataFrame (must be sorted by date)
            column: Column to create lags for
            lags: List of lag periods (default: from config)
        
        Returns:
            DataFrame with lag features added
        """
        if lags is None:
            lags = self.lag_features
        
        for lag in lags:
            df[f'lag_{lag}'] = df[column].shift(lag)
        
        logger.info(f"Created lag features: {lags}")
        return df
    
    def create_rolling_features(self, df, column='petrol_price', windows=None):
        """
        Create rolling window features (moving averages)
        
        Args:
            df: Input DataFrame (must be sorted by date)
            column: Column to calculate rolling stats for
            windows: List of window sizes (default: from config)
        
        Returns:
            DataFrame with rolling features added
        """
        if windows is None:
            windows = self.rolling_windows
        
        for window in windows:
            df[f'rolling_{window}'] = df[column].rolling(window=window).mean()
        
        logger.info(f"Created rolling features: {windows}")
        return df
    
    def create_target_variable(self, df, column='petrol_price', horizon=1):
        """
        Create target variable (future price)
        
        Args:
            df: Input DataFrame
            column: Column to predict
            horizon: Prediction horizon (days ahead)
        
        Returns:
            DataFrame with target variable
        """
        df['target'] = df[column].shift(-horizon)
        
        logger.info(f"Created target variable with horizon={horizon}")
        return df
    
    def create_all_features(self, df):
        """
        Create all features for the dataset
        
        Args:
            df: Input DataFrame with columns: date, petrol_price, crude_oil_price, inr_usd
        
        Returns:
            DataFrame with all features
        """
        try:
            # Ensure data is sorted by date
            df = df.sort_values('date').reset_index(drop=True)
            
            # Create lag features
            df = self.create_lag_features(df, 'petrol_price')
            
            # Create rolling features
            df = self.create_rolling_features(df, 'petrol_price')
            
            # Create target variable (next day prediction)
            df = self.create_target_variable(df, 'petrol_price', horizon=1)
            
            # Remove rows with NaN values (due to lag/rolling/target creation)
            initial_count = len(df)
            df = df.dropna()
            removed_count = initial_count - len(df)
            
            logger.info(f"Feature engineering complete. Removed {removed_count} rows with NaN")
            logger.info(f"Final dataset: {len(df)} samples with {len(df.columns)} features")
            
            return df
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            return df
    
    def save_to_database(self, df):
        """
        Save processed features to database
        
        Args:
            df: DataFrame with processed features
        
        Returns:
            int: Number of records saved
        """
        try:
            count = 0
            
            # Convert date column to proper Python date objects for SQLite
            df_copy = df.copy()
            # Convert pandas Timestamp to Python date
            df_copy['date'] = pd.to_datetime(df_copy['date']).dt.date
            
            with get_db_session() as session:
                for _, row in df_copy.iterrows():
                    # Check if date already exists
                    existing = session.query(ProcessedFeature).filter_by(date=row['date']).first()
                    
                    if existing:
                        # Update existing record
                        existing.petrol_price = float(row['petrol_price'])
                        existing.lag_1 = float(row.get('lag_1')) if pd.notna(row.get('lag_1')) else None
                        existing.lag_2 = float(row.get('lag_2')) if pd.notna(row.get('lag_2')) else None
                        existing.lag_7 = float(row.get('lag_7')) if pd.notna(row.get('lag_7')) else None
                        existing.lag_14 = float(row.get('lag_14')) if pd.notna(row.get('lag_14')) else None
                        existing.rolling_7 = float(row.get('rolling_7')) if pd.notna(row.get('rolling_7')) else None
                        existing.crude_oil_price = float(row.get('crude_oil_price')) if pd.notna(row.get('crude_oil_price')) else None
                        existing.inr_usd = float(row.get('inr_usd')) if pd.notna(row.get('inr_usd')) else None
                        existing.target = float(row.get('target')) if pd.notna(row.get('target')) else None
                    else:
                        # Insert new record
                        new_record = ProcessedFeature(
                            date=row['date'],
                            petrol_price=float(row['petrol_price']),
                            lag_1=float(row.get('lag_1')) if pd.notna(row.get('lag_1')) else None,
                            lag_2=float(row.get('lag_2')) if pd.notna(row.get('lag_2')) else None,
                            lag_7=float(row.get('lag_7')) if pd.notna(row.get('lag_7')) else None,
                            lag_14=float(row.get('lag_14')) if pd.notna(row.get('lag_14')) else None,
                            rolling_7=float(row.get('rolling_7')) if pd.notna(row.get('rolling_7')) else None,
                            crude_oil_price=float(row.get('crude_oil_price')) if pd.notna(row.get('crude_oil_price')) else None,
                            inr_usd=float(row.get('inr_usd')) if pd.notna(row.get('inr_usd')) else None,
                            target=float(row.get('target')) if pd.notna(row.get('target')) else None
                        )
                        session.add(new_record)
                    
                    count += 1
                
                # Commit happens automatically when context exits successfully
            
            logger.info(f"Saved {count} processed feature records to database")
            return count
            
        except Exception as e:
            logger.error(f"Error saving features to database: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    def load_from_database(self, start_date=None, end_date=None):
        """
        Load processed features from database
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            DataFrame with processed features
        """
        try:
            with get_db_session() as session:
                query = session.query(ProcessedFeature)
                
                if start_date and end_date:
                    from sqlalchemy import and_
                    query = query.filter(
                        and_(
                            ProcessedFeature.date >= start_date,
                            ProcessedFeature.date <= end_date
                        )
                    )
                
                records = query.all()
                df = pd.DataFrame([r.to_dict() for r in records])
                
                if not df.empty:
                    df = df.sort_values('date').reset_index(drop=True)
                
                logger.info(f"Loaded {len(df)} processed feature records from database")
                return df
                
        except Exception as e:
            logger.error(f"Error loading features from database: {str(e)}")
            return pd.DataFrame()
    
    def prepare_ml_dataset(self, df):
        """
        Prepare dataset for machine learning (separate features and target)
        
        Args:
            df: DataFrame with all features and target
        
        Returns:
            tuple: (X, y, feature_names)
        """
        try:
            # Define feature columns (exclude date and target)
            feature_cols = [col for col in df.columns if col not in ['date', 'target', 'created_at', 'id']]
            
            X = df[feature_cols].values
            y = df['target'].values
            
            logger.info(f"Prepared ML dataset: X shape={X.shape}, y shape={y.shape}")
            return X, y, feature_cols
            
        except Exception as e:
            logger.error(f"Error preparing ML dataset: {str(e)}")
            return None, None, None

# Convenience functions
def engineer_features(df):
    """Engineer features from cleaned data"""
    engineer = FeatureEngineer()
    return engineer.create_all_features(df)

def save_features(df):
    """Save features to database"""
    engineer = FeatureEngineer()
    return engineer.save_to_database(df)

def load_features(start_date=None, end_date=None):
    """Load features from database"""
    engineer = FeatureEngineer()
    return engineer.load_from_database(start_date, end_date)

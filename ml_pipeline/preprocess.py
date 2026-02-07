"""
ETL (Extract, Transform, Load) pipeline for data preprocessing.
Handles data cleaning, deduplication, missing values, and outlier detection.
"""
import pandas as pd
from datetime import datetime
from sqlalchemy import and_
from db.database import get_db_session
from db.models import RawPetrolPrice, RawExogenousData
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/etl.log')

class ETLPipeline:
    """ETL pipeline for raw data preprocessing"""
    
    def __init__(self):
        pass
    
    def extract_raw_data(self, start_date=None, end_date=None, source_filter='combined'):
        """
        Extract raw data from database
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            source_filter: 'combined', 'yahoo_finance', or 'custom_csv'
        
        Returns:
            DataFrame with merged petrol and macro data
        """
        try:
            with get_db_session() as session:
                # Build query for petrol prices
                petrol_query = session.query(RawPetrolPrice)
                if start_date and end_date:
                    petrol_query = petrol_query.filter(
                        and_(
                            RawPetrolPrice.date >= start_date,
                            RawPetrolPrice.date <= end_date
                        )
                    )
                
                # Apply source filter for petrol prices
                if source_filter == 'yahoo_finance':
                    petrol_query = petrol_query.filter(RawPetrolPrice.source == 'yahoo_finance')
                elif source_filter == 'custom_csv':
                    petrol_query = petrol_query.filter(RawPetrolPrice.source.in_(['file_upload', 'manual', 'csv_upload']))
                
                # Build query for macro data
                macro_query = session.query(RawExogenousData)
                if start_date and end_date:
                    macro_query = macro_query.filter(
                        and_(
                            RawExogenousData.date >= start_date,
                            RawExogenousData.date <= end_date
                        )
                    )
                
                # Apply source filter for macro data
                if source_filter == 'yahoo_finance':
                    macro_query = macro_query.filter(RawExogenousData.source == 'yahoo_finance')
                elif source_filter == 'custom_csv':
                    macro_query = macro_query.filter(RawExogenousData.source.in_(['file_upload', 'manual', 'csv_upload']))
                
                # Convert to DataFrames
                petrol_df = pd.DataFrame([p.to_dict() for p in petrol_query.all()])
                macro_df = pd.DataFrame([m.to_dict() for m in macro_query.all()])
                
                if petrol_df.empty:
                    logger.warning(f"No petrol price data found for source: {source_filter}")
                    return pd.DataFrame()
                
                # Merge on date
                if not macro_df.empty:
                    merged_df = pd.merge(
                        petrol_df[['date', 'petrol_price', 'source']],
                        macro_df[['date', 'crude_oil_price', 'inr_usd']],
                        on='date',
                        how='left'
                    )
                else:
                    merged_df = petrol_df[['date', 'petrol_price', 'source']].copy()
                    merged_df['crude_oil_price'] = None
                    merged_df['inr_usd'] = None
                
                logger.info(f"Extracted {len(merged_df)} raw records (source: {source_filter})")
                return merged_df
                
        except Exception as e:
            logger.error(f"Error extracting raw data: {str(e)}")
            return pd.DataFrame()
    
    def remove_duplicates(self, df):
        """
        Remove duplicate records based on date
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame without duplicates
        """
        initial_count = len(df)
        df = df.drop_duplicates(subset=['date'], keep='first')
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate records")
        
        return df
    
    def standardize_dates(self, df):
        """
        Standardize date formats and sort chronologically
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with standardized dates
        """
        try:
            # Convert to datetime if not already
            if df['date'].dtype != 'datetime64[ns]':
                df['date'] = pd.to_datetime(df['date'])
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            logger.info("Dates standardized and sorted")
            return df
            
        except Exception as e:
            logger.error(f"Error standardizing dates: {str(e)}")
            return df
    
    def handle_missing_values(self, df, method='ffill'):
        """
        Handle missing values in the dataset
        
        Args:
            df: Input DataFrame
            method: 'ffill' (forward fill), 'bfill' (backward fill), or 'interpolate'
        
        Returns:
            DataFrame with missing values handled
        """
        try:
            initial_missing = df.isnull().sum().sum()
            
            if method == 'ffill':
                df = df.fillna(method='ffill')
            elif method == 'bfill':
                df = df.fillna(method='bfill')
            elif method == 'interpolate':
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
            
            # Fill any remaining NaNs with forward fill
            df = df.fillna(method='ffill')
            
            final_missing = df.isnull().sum().sum()
            filled_count = initial_missing - final_missing
            
            if filled_count > 0:
                logger.info(f"Filled {filled_count} missing values using {method}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            return df
    
    def detect_outliers(self, df, column='petrol_price', method='iqr', remove=False):
        """
        Detect (and optionally remove) outliers using IQR method
        
        Args:
            df: Input DataFrame
            column: Column to check for outliers
            method: 'iqr' or 'zscore'
            remove: Whether to remove outliers
        
        Returns:
            DataFrame (with outliers removed if remove=True)
        """
        try:
            if column not in df.columns:
                return df
            
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
                
            elif method == 'zscore':
                from scipy import stats
                z_scores = stats.zscore(df[column].dropna())
                outliers = abs(z_scores) > 3
            
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                logger.info(f"Detected {outlier_count} outliers in {column}")
                
                if remove:
                    df = df[~outliers]
                    logger.info(f"Removed {outlier_count} outliers")
            
            return df
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {str(e)}")
            return df
    
    def run_etl(self, start_date=None, end_date=None, remove_outliers=False, source_filter='combined'):
        """
        Run complete ETL pipeline
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            remove_outliers: Whether to remove outliers
            source_filter: 'combined', 'yahoo_finance', or 'custom_csv'
        
        Returns:
            Cleaned DataFrame
        """
        try:
            logger.info(f"Starting ETL pipeline (source: {source_filter})...")
            
            # Extract
            df = self.extract_raw_data(start_date, end_date, source_filter)
            
            if df.empty:
                logger.warning("No data to process")
                return df
            
            # Transform
            df = self.remove_duplicates(df)
            df = self.standardize_dates(df)
            df = self.handle_missing_values(df, method='ffill')
            
            if remove_outliers:
                df = self.detect_outliers(df, 'petrol_price', remove=True)
            
            logger.info(f"ETL pipeline complete. Output: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error in ETL pipeline: {str(e)}")
            return pd.DataFrame()

# Convenience function
def run_etl_pipeline(start_date=None, end_date=None, remove_outliers=False, source_filter='combined'):
    """Run ETL pipeline with optional source filtering"""
    pipeline = ETLPipeline()
    return pipeline.run_etl(start_date, end_date, remove_outliers, source_filter)

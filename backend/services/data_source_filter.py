"""
Data source filtering utility for separating training data by source.
"""
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/data_filter.log')

def filter_by_source(df, source_type='combined'):
    """
    Filter DataFrame by data source
    
    Args:
        df: DataFrame with 'source' column
        source_type: 'yahoo_finance', 'custom_csv', or 'combined'
    
    Returns:
        Filtered DataFrame
    """
    if source_type == 'combined':
        # Return all data
        return df
    
    elif source_type == 'yahoo_finance':
        # Only Yahoo Finance data
        filtered = df[df['source'] == 'yahoo_finance']
        logger.info(f"Filtered to Yahoo Finance only: {len(filtered)} records")
        return filtered
    
    elif source_type == 'custom_csv':
        # Only uploaded CSV data (file_upload, manual, etc.)
        filtered = df[df['source'].isin(['file_upload', 'manual', 'csv_upload'])]
        logger.info(f"Filtered to Custom CSV only: {len(filtered)} records")
        return filtered
    
    else:
        logger.warning(f"Unknown source type: {source_type}, returning all data")
        return df

def get_source_stats(df):
    """
    Get statistics about data sources in DataFrame
    
    Args:
        df: DataFrame with 'source' column
    
    Returns:
        dict: Source statistics
    """
    if 'source' not in df.columns:
        return {'total': len(df), 'sources': {}}
    
    stats = {
        'total': len(df),
        'sources': df['source'].value_counts().to_dict()
    }
    
    return stats

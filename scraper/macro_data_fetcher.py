"""
Fetch macro-economic data (crude oil prices, INR-USD exchange rates) from Yahoo Finance.
"""
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from utils.logger import setup_logger
from config import DataSourceConfig

logger = setup_logger(__name__, 'logs/scraper.log')

class MacroDataFetcher:
    """Fetch crude oil and currency data from Yahoo Finance"""
    
    def __init__(self):
        self.crude_ticker = DataSourceConfig.CRUDE_OIL_TICKER
        self.inr_usd_ticker = DataSourceConfig.INR_USD_TICKER
    
    def fetch_crude_oil_price(self, start_date=None, end_date=None):
        """
        Fetch crude oil prices from Yahoo Finance
        
        Args:
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: today)
        
        Returns:
            DataFrame with columns: date, crude_oil_price
        """
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Fetch data
            ticker = yf.Ticker(self.crude_ticker)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.warning(f"No crude oil data found for {start_date} to {end_date}")
                return pd.DataFrame()
            
            # Extract closing prices
            df = pd.DataFrame({
                'date': data.index.date,
                'crude_oil_price': data['Close'].values
            })
            
            logger.info(f"Fetched {len(df)} crude oil price records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching crude oil prices: {str(e)}")
            return pd.DataFrame()
    
    def fetch_inr_usd_rate(self, start_date=None, end_date=None):
        """
        Fetch INR-USD exchange rates from Yahoo Finance
        
        Args:
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: today)
        
        Returns:
            DataFrame with columns: date, inr_usd
        """
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Fetch data
            ticker = yf.Ticker(self.inr_usd_ticker)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.warning(f"No INR-USD data found for {start_date} to {end_date}")
                return pd.DataFrame()
            
            # Extract closing rates
            df = pd.DataFrame({
                'date': data.index.date,
                'inr_usd': data['Close'].values
            })
            
            logger.info(f"Fetched {len(df)} INR-USD rate records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching INR-USD rates: {str(e)}")
            return pd.DataFrame()
    
    def fetch_all_macro_data(self, start_date=None, end_date=None):
        """
        Fetch both crude oil and INR-USD data and merge them
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with columns: date, crude_oil_price, inr_usd
        """
        try:
            crude_df = self.fetch_crude_oil_price(start_date, end_date)
            inr_df = self.fetch_inr_usd_rate(start_date, end_date)
            
            if crude_df.empty and inr_df.empty:
                return pd.DataFrame()
            
            # Merge on date
            if not crude_df.empty and not inr_df.empty:
                merged_df = pd.merge(crude_df, inr_df, on='date', how='outer')
            elif not crude_df.empty:
                merged_df = crude_df
                merged_df['inr_usd'] = None
            else:
                merged_df = inr_df
                merged_df['crude_oil_price'] = None
            
            # Sort by date
            merged_df = merged_df.sort_values('date').reset_index(drop=True)
            
            logger.info(f"Fetched {len(merged_df)} macro data records")
            return merged_df
            
        except Exception as e:
            logger.error(f"Error fetching macro data: {str(e)}")
            return pd.DataFrame()
    
    def get_latest_data(self):
        """
        Get latest macro data (today's values)
        
        Returns:
            dict: {date, crude_oil_price, inr_usd}
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # Get last 7 days to ensure we have data
            
            df = self.fetch_all_macro_data(start_date, end_date)
            
            if df.empty:
                return None
            
            # Get most recent record
            latest = df.iloc[-1]
            
            return {
                'date': latest['date'],
                'crude_oil_price': latest['crude_oil_price'],
                'inr_usd': latest['inr_usd']
            }
            
        except Exception as e:
            logger.error(f"Error getting latest macro data: {str(e)}")
            return None

# Convenience functions
def fetch_macro_data(start_date=None, end_date=None):
    """Fetch macro data for date range"""
    fetcher = MacroDataFetcher()
    return fetcher.fetch_all_macro_data(start_date, end_date)

def fetch_latest_macro_data():
    """Fetch latest macro data"""
    fetcher = MacroDataFetcher()
    return fetcher.get_latest_data()

"""
Unified data ingestion service that coordinates petrol price and macro data collection.
Implements continuous update logic (fetch only missing dates) with deduplication.
"""
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import and_
from db.database import get_db_session
from db.models import RawPetrolPrice, RawExogenousData
from scraper.petrol_scraper import fetch_petrol_price
from scraper.macro_data_fetcher import fetch_macro_data, fetch_latest_macro_data
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/ingestion.log')

class DataIngestionService:
    """Service for continuous data ingestion with deduplication"""
    
    def __init__(self):
        pass
    
    def get_missing_dates(self, table_model, start_date, end_date):
        """
        Find dates missing from database within a date range
        
        Args:
            table_model: SQLAlchemy model (RawPetrolPrice or RawExogenousData)
            start_date: Start date
            end_date: End date
        
        Returns:
            list: List of missing dates
        """
        try:
            with get_db_session() as session:
                # Get all dates in database within range
                existing_dates = session.query(table_model.date).filter(
                    and_(
                        table_model.date >= start_date,
                        table_model.date <= end_date
                    )
                ).all()
                
                existing_dates_set = {date[0] for date in existing_dates}
                
                # Generate all dates in range
                all_dates = []
                current = start_date
                while current <= end_date:
                    all_dates.append(current)
                    current += timedelta(days=1)
                
                # Find missing dates
                missing_dates = [d for d in all_dates if d not in existing_dates_set]
                
                logger.info(f"Found {len(missing_dates)} missing dates in {table_model.__tablename__}")
                return missing_dates
                
        except Exception as e:
            logger.error(f"Error finding missing dates: {str(e)}")
            return []
    
    def ingest_petrol_price(self, date, price, source='web_scraper'):
        """
        Ingest a single petrol price record with deduplication
        
        Args:
            date: Date of the price
            price: Petrol price
            source: Data source
        
        Returns:
            bool: True if inserted, False if duplicate
        """
        try:
            with get_db_session() as session:
                # Check if date already exists
                existing = session.query(RawPetrolPrice).filter_by(date=date).first()
                
                if existing:
                    logger.debug(f"Petrol price for {date} already exists, skipping")
                    return False
                
                # Insert new record
                new_record = RawPetrolPrice(
                    date=date,
                    petrol_price=price,
                    source=source
                )
                session.add(new_record)
                
                logger.info(f"Inserted petrol price: {date} - ₹{price}")
                return True
                
        except Exception as e:
            logger.error(f"Error ingesting petrol price: {str(e)}")
            return False
    
    def ingest_macro_data(self, date, crude_oil_price=None, inr_usd=None, source='yahoo_finance'):
        """
        Ingest a single macro data record with deduplication
        
        Args:
            date: Date of the data
            crude_oil_price: Crude oil price
            inr_usd: INR-USD exchange rate
            source: Data source
        
        Returns:
            bool: True if inserted, False if duplicate
        """
        try:
            with get_db_session() as session:
                # Check if date already exists
                existing = session.query(RawExogenousData).filter_by(date=date).first()
                
                if existing:
                    logger.debug(f"Macro data for {date} already exists, skipping")
                    return False
                
                # Insert new record
                new_record = RawExogenousData(
                    date=date,
                    crude_oil_price=crude_oil_price,
                    inr_usd=inr_usd,
                    source=source
                )
                session.add(new_record)
                
                logger.info(f"Inserted macro data: {date} - Crude: ${crude_oil_price}, INR: {inr_usd}")
                return True
                
        except Exception as e:
            logger.error(f"Error ingesting macro data: {str(e)}")
            return False
    
    def fetch_and_ingest_latest_data(self):
        """
        Fetch and ingest today's petrol price and macro data
        
        Returns:
            dict: Status of ingestion
        """
        status = {
            'petrol_price': False,
            'macro_data': False,
            'errors': []
        }
        
        try:
            # Fetch petrol price
            petrol_data = fetch_petrol_price()
            if petrol_data:
                status['petrol_price'] = self.ingest_petrol_price(
                    petrol_data['date'],
                    petrol_data['price'],
                    petrol_data['source']
                )
            else:
                status['errors'].append("Failed to fetch petrol price")
            
            # Fetch macro data
            macro_data = fetch_latest_macro_data()
            if macro_data:
                status['macro_data'] = self.ingest_macro_data(
                    macro_data['date'],
                    macro_data['crude_oil_price'],
                    macro_data['inr_usd']
                )
            else:
                status['errors'].append("Failed to fetch macro data")
            
            logger.info(f"Latest data ingestion complete: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Error in fetch_and_ingest_latest_data: {str(e)}")
            status['errors'].append(str(e))
            return status
    
    def backfill_missing_data(self, start_date, end_date):
        """
        Backfill missing data for a date range
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            dict: Counts of inserted records
        """
        counts = {
            'petrol_price': 0,
            'macro_data': 0
        }
        
        try:
            # Find missing dates for macro data
            missing_macro_dates = self.get_missing_dates(RawExogenousData, start_date, end_date)
            
            if missing_macro_dates:
                # Fetch macro data for missing dates
                macro_df = fetch_macro_data(min(missing_macro_dates), max(missing_macro_dates))
                
                if not macro_df.empty:
                    for _, row in macro_df.iterrows():
                        if row['date'] in missing_macro_dates:
                            if self.ingest_macro_data(
                                row['date'],
                                row.get('crude_oil_price'),
                                row.get('inr_usd')
                            ):
                                counts['macro_data'] += 1
            
            logger.info(f"Backfill complete: {counts}")
            return counts
            
        except Exception as e:
            logger.error(f"Error in backfill_missing_data: {str(e)}")
            return counts
    
    def ingest_from_dataframe(self, df, data_type='petrol'):
        """
        Ingest data from a pandas DataFrame (used for file uploads)
        
        Args:
            df: DataFrame with appropriate columns
            data_type: 'petrol' or 'macro'
        
        Returns:
            dict: {inserted: int, duplicates: int, total: int, message: str}
        """
        inserted_count = 0
        duplicate_count = 0
        total_count = len(df)
        
        try:
            if data_type == 'petrol':
                for _, row in df.iterrows():
                    if self.ingest_petrol_price(
                        row['date'],
                        row['petrol_price'],
                        row.get('source', 'file_upload')
                    ):
                        inserted_count += 1
                    else:
                        duplicate_count += 1
            
            elif data_type == 'macro':
                for _, row in df.iterrows():
                    if self.ingest_macro_data(
                        row['date'],
                        row.get('crude_oil_price'),
                        row.get('inr_usd'),
                        row.get('source', 'file_upload')
                    ):
                        inserted_count += 1
                    else:
                        duplicate_count += 1
            
            message = f"Processed {total_count} records: {inserted_count} inserted, {duplicate_count} duplicates"
            logger.info(f"DataFrame ingestion ({data_type}): {message}")
            return {
                'inserted': inserted_count,
                'duplicates': duplicate_count,
                'total': total_count,
                'message': message
            }
            
        except Exception as e:
            logger.error(f"Error ingesting from DataFrame: {str(e)}")
            return count

# Convenience functions
def ingest_latest_data(start_date=None, end_date=None, period='1y'):
    """
    Fetch and ingest latest data with optional date range
    
    Args:
        start_date: Start date (YYYY-MM-DD) or None
        end_date: End date (YYYY-MM-DD) or None  
        period: Period string ('1mo', '3mo', '6mo', '1y', '5y', 'max') if dates not provided
    """
    service = DataIngestionService()
    # For now, just use the default behavior
    # TODO: Implement custom date range support in fetch_and_ingest_latest_data
    return service.fetch_and_ingest_latest_data()

def backfill_data(start_date, end_date):
    """Backfill missing data"""
    service = DataIngestionService()
    return service.backfill_missing_data(start_date, end_date)

"""
File upload handler for CSV/Excel files.
Validates schema, extracts data, and triggers ingestion.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from scraper.data_ingestion_service import DataIngestionService
from utils.logger import setup_logger
from config import PathConfig

logger = setup_logger(__name__, 'logs/upload.log')

class FileUploadHandler:
    """Handle file uploads and validation"""
    
    REQUIRED_PETROL_COLUMNS = ['date', 'petrol_price']
    REQUIRED_MACRO_COLUMNS = ['date']
    OPTIONAL_MACRO_COLUMNS = ['crude_oil_price', 'inr_usd']
    
    def __init__(self):
        self.upload_folder = PathConfig.UPLOAD_FOLDER
        self.ingestion_service = DataIngestionService()
    
    def validate_file_type(self, filename):
        """
        Validate file extension
        
        Args:
            filename: Name of uploaded file
        
        Returns:
            str: File type ('csv', 'excel', 'pdf', 'txt') or None
        """
        ext = Path(filename).suffix.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext in ['.xlsx', '.xls']:
            return 'excel'
        elif ext == '.pdf':
            return 'pdf'
        elif ext == '.txt':
            return 'txt'
        else:
            return None
    
    def read_file(self, filepath):
        """
        Read file into pandas DataFrame
        
        Args:
            filepath: Path to file
        
        Returns:
            DataFrame or None
        """
        try:
            file_type = self.validate_file_type(filepath)
            
            if file_type == 'csv':
                df = pd.read_csv(filepath)
            elif file_type == 'excel':
                df = pd.read_excel(filepath)
            elif file_type == 'txt':
                # Assume tab or comma separated
                df = pd.read_csv(filepath, sep=None, engine='python')
            else:
                logger.error(f"Unsupported file type: {file_type}")
                return None
            
            logger.info(f"Successfully read file: {filepath} ({len(df)} rows)")
            return df
            
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            return None
    
    def validate_date_column(self, df):
        """
        Validate and convert date column
        
        Args:
            df: DataFrame with 'date' column
        
        Returns:
            DataFrame with validated dates or None
        """
        try:
            if 'date' not in df.columns:
                logger.error("Missing 'date' column")
                return None
            
            # Try to parse dates
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Check for invalid dates
            invalid_count = df['date'].isna().sum()
            if invalid_count > 0:
                logger.warning(f"Found {invalid_count} invalid dates, removing them")
                df = df.dropna(subset=['date'])
            
            # Convert to date (remove time component)
            df['date'] = df['date'].dt.date
            
            return df
            
        except Exception as e:
            logger.error(f"Error validating dates: {str(e)}")
            return None
    
    def validate_petrol_data(self, df):
        """
        Validate petrol price data schema
        
        Args:
            df: DataFrame to validate
        
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Check required columns
        for col in self.REQUIRED_PETROL_COLUMNS:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        if errors:
            return False, errors
        
        # Validate date column
        df_validated = self.validate_date_column(df)
        if df_validated is None:
            errors.append("Invalid date format")
            return False, errors
        
        # Check for numeric petrol_price
        if not pd.api.types.is_numeric_dtype(df['petrol_price']):
            try:
                df['petrol_price'] = pd.to_numeric(df['petrol_price'], errors='coerce')
            except:
                errors.append("petrol_price column must be numeric")
                return False, errors
        
        # Check for negative prices
        if (df['petrol_price'] < 0).any():
            errors.append("Found negative petrol prices")
            return False, errors
        
        return True, []
    
    def validate_macro_data(self, df):
        """
        Validate macro data schema
        
        Args:
            df: DataFrame to validate
        
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Check required columns
        for col in self.REQUIRED_MACRO_COLUMNS:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        if errors:
            return False, errors
        
        # Validate date column
        df_validated = self.validate_date_column(df)
        if df_validated is None:
            errors.append("Invalid date format")
            return False, errors
        
        # Check for at least one optional column
        has_data = any(col in df.columns for col in self.OPTIONAL_MACRO_COLUMNS)
        if not has_data:
            errors.append(f"Must have at least one of: {', '.join(self.OPTIONAL_MACRO_COLUMNS)}")
            return False, errors
        
        return True, []
    
    def process_upload(self, filepath, data_type='auto'):
        """
        Process uploaded file and ingest data
        
        Args:
            filepath: Path to uploaded file
            data_type: 'petrol', 'macro', or 'auto' (auto-detect)
        
        Returns:
            dict: {success: bool, message: str, count: int}
        """
        try:
            # Read file
            df = self.read_file(filepath)
            if df is None:
                return {'success': False, 'message': 'Failed to read file', 'count': 0}
            
            # Auto-detect data type if needed
            if data_type == 'auto':
                if 'petrol_price' in df.columns:
                    data_type = 'petrol'
                elif 'crude_oil_price' in df.columns or 'inr_usd' in df.columns:
                    data_type = 'macro'
                else:
                    return {'success': False, 'message': 'Cannot determine data type', 'count': 0}
            
            # Validate based on type
            if data_type == 'petrol':
                is_valid, errors = self.validate_petrol_data(df)
                if not is_valid:
                    return {'success': False, 'message': '; '.join(errors), 'count': 0}
                
                # Validate dates
                df = self.validate_date_column(df)
                if df is None:
                    return {'success': False, 'message': 'Invalid date format', 'count': 0}
                
                # Ingest data
                count = self.ingestion_service.ingest_from_dataframe(df, 'petrol')
                
            elif data_type == 'macro':
                is_valid, errors = self.validate_macro_data(df)
                if not is_valid:
                    return {'success': False, 'message': '; '.join(errors), 'count': 0}
                
                # Validate dates
                df = self.validate_date_column(df)
                if df is None:
                    return {'success': False, 'message': 'Invalid date format', 'count': 0}
                
                # Ingest data
                count = self.ingestion_service.ingest_from_dataframe(df, 'macro')
            
            else:
                return {'success': False, 'message': f'Invalid data type: {data_type}', 'count': 0}
            
            message = f"Successfully ingested {count} records ({data_type} data)"
            logger.info(message)
            
            return {'success': True, 'message': message, 'count': count}
            
        except Exception as e:
            error_msg = f"Error processing upload: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg, 'count': 0}

# Convenience function
def process_file_upload(filepath, data_type='auto'):
    """Process file upload"""
    handler = FileUploadHandler()
    return handler.process_upload(filepath, data_type)

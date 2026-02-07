"""
Data management routes for Flask API.
Handles file uploads and data retrieval.
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from db.database import get_db_session
from db.models import RawPetrolPrice, RawExogenousData, ProcessedFeature
from scraper.file_upload_handler import process_file_upload
from config import PathConfig
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/api.log')

data_bp = Blueprint('data', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'txt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@data_bp.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    """
    Upload CSV/Excel file with petrol price or macro data
    
    Request:
        - file: File upload
        - data_type: 'petrol', 'macro', or 'auto' (optional, default: auto)
    
    Response:
        {success: bool, message: str, count: int}
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Get data type
        data_type = request.form.get('data_type', 'auto')
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = PathConfig.UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        logger.info(f"File uploaded: {filename}")
        
        # Process file
        result = process_file_upload(str(filepath), data_type)
        
        # Format response with detailed message
        if result['success']:
            response = {
                'success': True,
                'message': f"✓ {result['message']}",
                'inserted': result.get('inserted', 0),
                'duplicates': result.get('duplicates', 0),
                'total_processed': result.get('total', 0),
                'count': result.get('inserted', 0)
            }
        else:
            response = {
                'success': False,
                'message': f"✗ {result.get('message', 'Upload failed')}",
                'count': 0
            }
        
        return jsonify(response), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Error in upload_dataset: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@data_bp.route('/data/raw', methods=['GET'])
def get_raw_data():
    """
    Get raw petrol price and macro data
    
    Query params:
        - limit: Number of records (default: 100)
        - offset: Offset for pagination (default: 0)
    
    Response:
        {
            petrol_prices: [...],
            macro_data: [...],
            total_count: int
        }
    """
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        with get_db_session() as session:
            # Get petrol prices
            petrol_query = session.query(RawPetrolPrice).order_by(
                RawPetrolPrice.date.desc()
            ).limit(limit).offset(offset)
            
            petrol_prices = [p.to_dict() for p in petrol_query.all()]
            
            # Get macro data
            macro_query = session.query(RawExogenousData).order_by(
                RawExogenousData.date.desc()
            ).limit(limit).offset(offset)
            
            macro_data = [m.to_dict() for m in macro_query.all()]
            
            # Get total counts
            petrol_count = session.query(RawPetrolPrice).count()
            macro_count = session.query(RawExogenousData).count()
        
        return jsonify({
            'success': True,
            'petrol_prices': petrol_prices,
            'macro_data': macro_data,
            'counts': {
                'petrol': petrol_count,
                'macro': macro_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_raw_data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/data/processed', methods=['GET'])
def get_processed_data():
    """
    Get processed features
    
    Query params:
        - limit: Number of records (default: 100)
        - offset: Offset for pagination (default: 0)
    
    Response:
        {
            features: [...],
            total_count: int
        }
    """
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        with get_db_session() as session:
            # Get processed features
            query = session.query(ProcessedFeature).order_by(
                ProcessedFeature.date.desc()
            ).limit(limit).offset(offset)
            
            features = [f.to_dict() for f in query.all()]
            
            # Get total count
            total_count = session.query(ProcessedFeature).count()
        
        return jsonify({
            'success': True,
            'features': features,
            'total_count': total_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_processed_data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/data/latest', methods=['GET'])
def get_latest_data():
    """
    Get latest petrol price and macro data
    
    Response:
        {
            latest_petrol: {...},
            latest_macro: {...}
        }
    """
    try:
        with get_db_session() as session:
            # Get latest petrol price
            latest_petrol = session.query(RawPetrolPrice).order_by(
                RawPetrolPrice.date.desc()
            ).first()
            
            # Get latest macro data
            latest_macro = session.query(RawExogenousData).order_by(
                RawExogenousData.date.desc()
            ).first()
            
            # Convert to dicts WITHIN the session to avoid detached instance errors
            petrol_dict = latest_petrol.to_dict() if latest_petrol else None
            macro_dict = latest_macro.to_dict() if latest_macro else None
            
            # Get recent 30 days for dashboard chart
            recent_prices = session.query(RawPetrolPrice).order_by(
                RawPetrolPrice.date.desc()
            ).limit(30).all()
            recent_prices_list = [p.to_dict() for p in reversed(recent_prices)]
        
        # Combine data for dashboard
        result = {
            'date': petrol_dict['date'] if petrol_dict else None,
            'petrol_price': petrol_dict['petrol_price'] if petrol_dict else None,
            'crude_oil_price': macro_dict['crude_oil_price'] if macro_dict else None,
            'inr_usd': macro_dict['inr_usd'] if macro_dict else None,
            'recent_prices': recent_prices_list
        }
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_latest_data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
@data_bp.route('/data/ingestion-status', methods=['GET'])
def get_ingestion_status():
    """
    Get latest data ingestion status and statistics
    
    Response:
        {
            last_ingestion_date: date,
            total_records: int,
            petrol_records: int,
            macro_records: int,
            last_petrol_price: float,
            last_macro_data: dict
        }
    """
    try:
        from datetime import datetime
        
        with get_db_session() as session:
            today = datetime.now().date()
            
            # Get latest petrol price record (up to today only)
            latest_petrol = session.query(RawPetrolPrice).filter(
                RawPetrolPrice.date <= today
            ).order_by(
                RawPetrolPrice.date.desc()
            ).first()
            
            # Get latest macro data record (up to today only)
            latest_macro = session.query(RawExogenousData).filter(
                RawExogenousData.date <= today
            ).order_by(
                RawExogenousData.date.desc()
            ).first()
            
            # Get counts (only up to today)
            petrol_count = session.query(RawPetrolPrice).filter(
                RawPetrolPrice.date <= today
            ).count()
            macro_count = session.query(RawExogenousData).filter(
                RawExogenousData.date <= today
            ).count()
            
            # Determine last ingestion date (most recent of both)
            last_date = None
            if latest_petrol and latest_macro:
                last_date = max(latest_petrol.date, latest_macro.date)
            elif latest_petrol:
                last_date = latest_petrol.date
            elif latest_macro:
                last_date = latest_macro.date
            
            result = {
                'last_ingestion_date': str(last_date) if last_date else None,
                'total_records': petrol_count + macro_count,
                'petrol_records': petrol_count,
                'macro_records': macro_count,
                'last_petrol_price': float(latest_petrol.petrol_price) if latest_petrol else None,
                'last_macro_data': latest_macro.to_dict() if latest_macro else None,
                'status': 'active' if latest_petrol else 'no_data'
            }
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_ingestion_status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
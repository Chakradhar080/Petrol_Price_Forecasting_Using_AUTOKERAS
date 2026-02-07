"""
Data sync routes for fetching live data from Yahoo Finance.
"""
from flask import Blueprint, jsonify, request
from scraper.data_ingestion_service import ingest_latest_data
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/api.log')

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync/fetch-live-data', methods=['POST'])
def fetch_live_data():
    """
    Fetch latest data from Yahoo Finance (crude oil, INR-USD)
    
    Request body (optional):
    {
        "period": "1mo" | "3mo" | "6mo" | "1y" | "5y" | "max",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD"
    }
    
    Response:
        {
            success: bool,
            message: str,
            data: {
                crude_oil_records: int,
                inr_usd_records: int
            }
        }
    """
    try:
        # Get parameters from request
        data = request.get_json() or {}
        period = data.get('period', '1y')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        logger.info(f"Manual data sync triggered (period: {period}, start: {start_date}, end: {end_date})")
        
        # Fetch data from Yahoo Finance with custom parameters
        status = ingest_latest_data(start_date=start_date, end_date=end_date, period=period)
        
        return jsonify({
            'success': True,
            'message': f'Live data fetched successfully from Yahoo Finance',
            'data': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching live data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

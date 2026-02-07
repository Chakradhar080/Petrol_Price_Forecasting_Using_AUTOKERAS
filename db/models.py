"""
SQLAlchemy ORM models for all database tables.
"""
from sqlalchemy import Column, Integer, String, Date, DECIMAL, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class RawPetrolPrice(Base):
    """Raw petrol price data from web scraping or file upload"""
    __tablename__ = 'raw_petrol_prices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    petrol_price = Column(DECIMAL(10, 2), nullable=False)
    source = Column(String(100), default='web_scraper')
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<RawPetrolPrice(date={self.date}, price={self.petrol_price})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': str(self.date),
            'petrol_price': float(self.petrol_price),
            'source': self.source,
            'created_at': str(self.created_at)
        }

class RawExogenousData(Base):
    """Raw exogenous data (crude oil, INR-USD) from Yahoo Finance"""
    __tablename__ = 'raw_exogenous_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    crude_oil_price = Column(DECIMAL(10, 2))
    inr_usd = Column(DECIMAL(10, 4))
    source = Column(String(100), default='yahoo_finance')
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<RawExogenousData(date={self.date}, crude={self.crude_oil_price}, inr_usd={self.inr_usd})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': str(self.date),
            'crude_oil_price': float(self.crude_oil_price) if self.crude_oil_price else None,
            'inr_usd': float(self.inr_usd) if self.inr_usd else None,
            'source': self.source,
            'created_at': str(self.created_at)
        }

class ProcessedFeature(Base):
    """Processed features for machine learning"""
    __tablename__ = 'processed_features'
    
    date = Column(Date, primary_key=True)
    petrol_price = Column(DECIMAL(10, 2), nullable=False)
    lag_1 = Column(DECIMAL(10, 2))
    lag_2 = Column(DECIMAL(10, 2))
    lag_7 = Column(DECIMAL(10, 2))
    lag_14 = Column(DECIMAL(10, 2))
    rolling_7 = Column(DECIMAL(10, 2))
    crude_oil_price = Column(DECIMAL(10, 2))
    inr_usd = Column(DECIMAL(10, 4))
    target = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ProcessedFeature(date={self.date}, price={self.petrol_price})>"
    
    def to_dict(self):
        return {
            'date': str(self.date),
            'petrol_price': float(self.petrol_price),
            'lag_1': float(self.lag_1) if self.lag_1 else None,
            'lag_2': float(self.lag_2) if self.lag_2 else None,
            'lag_7': float(self.lag_7) if self.lag_7 else None,
            'lag_14': float(self.lag_14) if self.lag_14 else None,
            'rolling_7': float(self.rolling_7) if self.rolling_7 else None,
            'crude_oil_price': float(self.crude_oil_price) if self.crude_oil_price else None,
            'inr_usd': float(self.inr_usd) if self.inr_usd else None,
            'target': float(self.target) if self.target else None,
            'created_at': str(self.created_at)
        }

class ModelRegistry(Base):
    """Model version registry with performance metrics"""
    __tablename__ = 'model_registry'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(50), nullable=False, unique=True, index=True)
    rmse = Column(DECIMAL(10, 4))
    mae = Column(DECIMAL(10, 4))
    mape = Column(DECIMAL(10, 4))
    r2 = Column(DECIMAL(10, 4))
    model_path = Column(String(255), nullable=False)
    training_samples = Column(Integer)
    data_source = Column(String(100), default='combined')  # Track which data source was used
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ModelRegistry(version={self.model_version}, r2={self.r2}, source={self.data_source})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_version': self.model_version,
            'rmse': float(self.rmse) if self.rmse else None,
            'mae': float(self.mae) if self.mae else None,
            'mape': float(self.mape) if self.mape else None,
            'r2': float(self.r2) if self.r2 else None,
            'model_path': self.model_path,
            'training_samples': self.training_samples,
            'data_source': self.data_source,
            'created_at': str(self.created_at)
        }

class PredictionLog(Base):
    """Log of all prediction requests"""
    __tablename__ = 'prediction_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_time = Column(DateTime, server_default=func.now(), index=True)
    horizon_days = Column(Integer, nullable=False)
    model_version = Column(String(50), ForeignKey('model_registry.model_version'), nullable=False)
    predictions_json = Column(Text, nullable=False)
    
    def __repr__(self):
        return f"<PredictionLog(time={self.request_time}, horizon={self.horizon_days})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_time': str(self.request_time),
            'horizon_days': self.horizon_days,
            'model_version': self.model_version,
            'predictions_json': self.predictions_json
        }

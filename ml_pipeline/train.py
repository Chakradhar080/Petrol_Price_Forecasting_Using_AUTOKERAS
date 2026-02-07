"""
Model training module using TensorFlow/Keras.
Replaces Auto-Keras with a simple but effective neural network.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from db.database import get_db_session
from db.models import ProcessedFeature
from config import PathConfig, ModelConfig
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/training.log')

def load_training_data(start_date=None, end_date=None):
    """
    Load processed features from database for training
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        pd.DataFrame: Training data
    """
    try:
        with get_db_session() as session:
            query = session.query(ProcessedFeature)
            
            if start_date:
                query = query.filter(ProcessedFeature.date >= start_date)
            if end_date:
                query = query.filter(ProcessedFeature.date <= end_date)
            
            query = query.order_by(ProcessedFeature.date)
            
            features = [f.to_dict() for f in query.all()]
            
            if not features:
                logger.error("No training data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(features)
            logger.info(f"Loaded {len(df)} training samples")
            
            return df
            
    except Exception as e:
        logger.error(f"Error loading training data: {str(e)}")
        return pd.DataFrame()

def prepare_data(df):
    """
    Prepare data for training
    
    Args:
        df: DataFrame with features
    
    Returns:
        tuple: (X_train, X_val, y_train, y_val, scaler)
    """
    # Drop rows with missing target
    df = df.dropna(subset=['target'])
    
    # Feature columns
    feature_cols = ['petrol_price', 'lag_1', 'lag_2', 'lag_7', 'lag_14', 
                    'rolling_7', 'crude_oil_price', 'inr_usd']
    
    # Remove rows with any missing features
    df = df.dropna(subset=feature_cols)
    
    X = df[feature_cols].values
    y = df['target'].values
    
    # Time-based split (80% train, 20% validation)
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    # Standardize features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    
    logger.info(f"Training samples: {len(X_train)}, Validation samples: {len(X_val)}")
    
    return X_train, X_val, y_train, y_val, scaler

def build_model(input_dim):
    """
    Build an improved neural network for price prediction
    
    Args:
        input_dim: Number of input features
    
    Returns:
        keras.Model: Compiled model
    """
    model = Sequential([
        Dense(128, activation='relu', input_dim=input_dim),
        BatchNormalization(),
        Dropout(0.3),
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(32, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dropout(0.1),
        Dense(1)  # Output layer for regression
    ])
    
    # Use a lower learning rate for better convergence
    optimizer = keras.optimizers.Adam(learning_rate=0.001)
    model.compile(
        optimizer=optimizer,
        loss='mse',
        metrics=['mae']
    )
    
    return model

def train_model(model_version, start_date=None, end_date=None):
    """
    Train a new model
    
    Args:
        model_version: Version string for the model
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        dict: Training results
    """
    try:
        logger.info(f"Starting training for {model_version}")
        
        # Load data
        df = load_training_data(start_date, end_date)
        
        if df.empty:
            return {'success': False, 'error': 'No training data available'}
        
        # Prepare data
        X_train, X_val, y_train, y_val, scaler = prepare_data(df)
        
        if len(X_train) < 10:
            return {'success': False, 'error': 'Insufficient training data (need at least 10 samples)'}
        
        # Build model
        model = build_model(X_train.shape[1])
        
        # Callbacks for better training
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            min_delta=0.0001
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=0
        )
        
        # Train model
        logger.info("Training neural network...")
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=min(ModelConfig.EPOCHS, 200),  # Cap at 200 epochs
            batch_size=16,  # Smaller batch size for better convergence
            callbacks=[early_stop, reduce_lr],
            verbose=0
        )
        
        # Make predictions on validation set
        y_pred = model.predict(X_val, verbose=0).flatten()
        
        # Calculate R² score
        r2 = r2_score(y_val, y_pred)
        logger.info(f"Model R² Score: {r2:.4f}")
        
        # Save model
        model_path = PathConfig.MODEL_FOLDER / f"{model_version}.h5"
        model.save(str(model_path))
        
        # Save scaler
        scaler_path = PathConfig.MODEL_FOLDER / f"{model_version}_scaler.pkl"
        import pickle
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        logger.info(f"Model saved to {model_path}")
        
        return {
            'success': True,
            'model_version': model_version,
            'model_path': str(model_path),
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'y_val': y_val,
            'y_pred': y_pred,
            'r2_score': r2
        }
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return {'success': False, 'error': str(e)}

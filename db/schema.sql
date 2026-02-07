-- Petrol Price Forecasting System Database Schema
-- SQLite Version (for local development)

-- Table 1: Raw Petrol Prices
CREATE TABLE IF NOT EXISTS raw_petrol_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    petrol_price REAL NOT NULL,
    source TEXT DEFAULT 'web_scraper',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_petrol_date ON raw_petrol_prices(date);

-- Table 2: Raw Exogenous Data (Crude Oil & INR-USD)
CREATE TABLE IF NOT EXISTS raw_exogenous_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    crude_oil_price REAL,
    inr_usd REAL,
    source TEXT DEFAULT 'yahoo_finance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exogenous_date ON raw_exogenous_data(date);

-- Table 3: Processed Features (for ML)
CREATE TABLE IF NOT EXISTS processed_features (
    date DATE PRIMARY KEY,
    petrol_price REAL NOT NULL,
    lag_1 REAL,
    lag_2 REAL,
    lag_7 REAL,
    lag_14 REAL,
    rolling_7 REAL,
    crude_oil_price REAL,
    inr_usd REAL,
    target REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: Model Registry
CREATE TABLE IF NOT EXISTS model_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_version TEXT NOT NULL UNIQUE,
    rmse REAL,
    mae REAL,
    mape REAL,
    model_path TEXT NOT NULL,
    training_samples INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_model_version ON model_registry(model_version);

-- Table 5: Prediction Logs
CREATE TABLE IF NOT EXISTS prediction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    horizon_days INTEGER NOT NULL,
    model_version TEXT NOT NULL,
    predictions_json TEXT NOT NULL,
    FOREIGN KEY (model_version) REFERENCES model_registry(model_version)
);

CREATE INDEX IF NOT EXISTS idx_prediction_time ON prediction_logs(request_time);

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Data APIs
export const uploadDataset = (formData) => {
    return api.post('/upload-dataset', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};

// Alias for uploadDataset (for compatibility)
export const uploadFile = uploadDataset;

export const getRawData = (limit = 100, offset = 0) => {
    return api.get(`/data/raw?limit=${limit}&offset=${offset}`);
};

export const getProcessedData = (limit = 100, offset = 0) => {
    return api.get(`/data/processed?limit=${limit}&offset=${offset}`);
};

export const getLatestData = () => {
    return api.get('/data/latest');
};

export const getIngestionStatus = () => {
    return api.get('/data/ingestion-status');
};

// Sync APIs (NEW - Live Data Fetching)
export const fetchLiveData = (config = {}) => {
    return api.post('/sync/fetch-live-data', config);
};

// Prepare Data API (NEW - ETL + Feature Engineering)
export const prepareData = (dataSource = 'combined') => {
    return api.post('/prepare-data', { data_source: dataSource });
};

// Training APIs
export const trainModel = (data = {}) => {
    return api.post('/train', data);
};

export const getModelVersions = () => {
    return api.get('/model/versions');
};

// Alias for getModelVersions (for compatibility)
export const getModelHistory = getModelVersions;

export const getLatestMetrics = () => {
    return api.get('/metrics/latest');
};

export const getBestMetrics = (metric = 'rmse') => {
    return api.get(`/metrics/best?metric=${metric}`);
};

// Prediction APIs
export const generateForecast = (horizonDays, modelVersion = null, endDate = null) => {
    return api.post('/forecast', {
        horizon_days: horizonDays,
        model_version: modelVersion,
        end_date: endDate,
    });
};

export const getForecastHistory = (limit = 10) => {
    return api.get(`/forecast/history?limit=${limit}`);
};

export default api;

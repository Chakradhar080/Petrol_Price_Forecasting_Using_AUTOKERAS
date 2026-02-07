import React, { useState } from 'react';
import { uploadFile, fetchLiveData } from '../services/api';
import { Upload, Download, Database, CheckCircle, AlertCircle, Calendar } from 'lucide-react';

function UploadData() {
    const [file, setFile] = useState(null);
    const [dataType, setDataType] = useState('auto');
    const [uploading, setUploading] = useState(false);
    const [fetching, setFetching] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    // Yahoo Finance customization
    const [period, setPeriod] = useState('1y');
    const [useCustomDates, setUseCustomDates] = useState(false);
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setError(null);
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select a file');
            return;
        }

        try {
            setUploading(true);
            setError(null);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('data_type', dataType);

            const response = await uploadFile(formData);

            if (response.data.success) {
                setResult(response.data);
                setFile(null);
                setError(null);
            } else {
                setError(response.data.message || 'Upload failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || err.message);
        } finally {
            setUploading(false);
        }
    };

    const handleFetchLive = async () => {
        try {
            setFetching(true);
            setError(null);

            const config = useCustomDates && startDate && endDate
                ? { start_date: startDate, end_date: endDate }
                : { period };

            const response = await fetchLiveData(config);

            if (response.data.success) {
                setResult(response.data);
                setError(null);
            } else {
                setError(response.data.message || 'Fetch failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || err.message);
        } finally {
            setFetching(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-secondary-900">Upload Data</h1>
                <p className="text-secondary-600 mt-1">Import datasets from CSV files or fetch live data from Yahoo Finance</p>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <h3 className="text-sm font-semibold text-red-800">Error</h3>
                        <p className="text-sm text-red-700 mt-1">{error}</p>
                    </div>
                </div>
            )}

            {/* Success Alert */}
            {result && result.success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <h3 className="text-sm font-semibold text-green-800">Success</h3>
                        <p className="text-sm text-green-700 mt-1">{result.message}</p>
                        {result.data && (
                            <div className="text-xs text-green-600 mt-2">
                                Records imported: {result.data.records || result.data.crude_oil_records + result.data.inr_usd_records || 0}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Upload CSV File */}
            <div className="card">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="bg-primary-100 p-2 rounded-lg">
                        <Upload className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-secondary-900">Upload CSV File</h2>
                        <p className="text-sm text-secondary-600">Import petrol prices or macro data from CSV/Excel files</p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-semibold text-secondary-700 mb-2">
                            Data Type
                        </label>
                        <select
                            className="input max-w-xs"
                            value={dataType}
                            onChange={(e) => setDataType(e.target.value)}
                        >
                            <option value="auto">Auto-detect</option>
                            <option value="petrol">Petrol Prices</option>
                            <option value="macro">Macro Data (Crude Oil, INR-USD)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-secondary-700 mb-2">
                            Choose File
                        </label>
                        <input
                            type="file"
                            accept=".csv,.xlsx,.xls"
                            onChange={handleFileChange}
                            className="block w-full text-sm text-secondary-600
                                file:mr-4 file:py-2 file:px-4
                                file:rounded-lg file:border-0
                                file:text-sm file:font-semibold
                                file:bg-primary-50 file:text-primary-700
                                hover:file:bg-primary-100
                                cursor-pointer"
                        />
                        {file && (
                            <p className="text-sm text-secondary-600 mt-2">
                                Selected: {file.name}
                            </p>
                        )}
                    </div>

                    <button
                        onClick={handleUpload}
                        disabled={uploading || !file}
                        className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {uploading ? (
                            <span className="flex items-center space-x-2">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                <span>Uploading...</span>
                            </span>
                        ) : (
                            <span className="flex items-center space-x-2">
                                <Upload className="w-4 h-4" />
                                <span>Upload File</span>
                            </span>
                        )}
                    </button>
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="text-sm font-semibold text-blue-900 mb-2">CSV Format Requirements</h4>
                    <div className="text-xs text-blue-800 space-y-1">
                        <p><strong>Petrol Prices:</strong> date, petrol_price</p>
                        <p><strong>Macro Data:</strong> date, crude_oil_price, inr_usd</p>
                        <p><strong>Date Format:</strong> YYYY-MM-DD</p>
                    </div>
                </div>
            </div>

            {/* Fetch Live Data with Customization */}
            <div className="card">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="bg-accent-100 p-2 rounded-lg">
                        <Download className="w-5 h-5 text-accent-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-secondary-900">Fetch Live Data</h2>
                        <p className="text-sm text-secondary-600">Download crude oil and INR-USD data from Yahoo Finance</p>
                    </div>
                </div>

                <div className="space-y-4">
                    {/* Date Range Toggle */}
                    <div className="flex items-center space-x-3">
                        <input
                            type="checkbox"
                            id="useCustomDates"
                            checked={useCustomDates}
                            onChange={(e) => setUseCustomDates(e.target.checked)}
                            className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                        />
                        <label htmlFor="useCustomDates" className="text-sm font-medium text-secondary-700">
                            Use custom date range
                        </label>
                    </div>

                    {useCustomDates ? (
                        /* Custom Date Range */
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-semibold text-secondary-700 mb-2">
                                    <Calendar className="w-4 h-4 inline mr-1" />
                                    Start Date
                                </label>
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="input"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-secondary-700 mb-2">
                                    <Calendar className="w-4 h-4 inline mr-1" />
                                    End Date
                                </label>
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="input"
                                />
                            </div>
                        </div>
                    ) : (
                        /* Period Selection */
                        <div>
                            <label className="block text-sm font-semibold text-secondary-700 mb-2">
                                Period
                            </label>
                            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                                {['1mo', '3mo', '6mo', '1y', '5y', 'max'].map((p) => (
                                    <button
                                        key={p}
                                        onClick={() => setPeriod(p)}
                                        className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${period === p
                                                ? 'bg-primary-600 text-white'
                                                : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
                                            }`}
                                    >
                                        {p === '1mo' ? '1M' : p === '3mo' ? '3M' : p === '6mo' ? '6M' :
                                            p === '1y' ? '1Y' : p === '5y' ? '5Y' : 'Max'}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    <button
                        onClick={handleFetchLive}
                        disabled={fetching || (useCustomDates && (!startDate || !endDate))}
                        className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {fetching ? (
                            <span className="flex items-center space-x-2">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                <span>Fetching Data...</span>
                            </span>
                        ) : (
                            <span className="flex items-center space-x-2">
                                <Download className="w-4 h-4" />
                                <span>Fetch Live Data</span>
                            </span>
                        )}
                    </button>
                </div>

                <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <h4 className="text-sm font-semibold text-purple-900 mb-2">Data Sources</h4>
                    <div className="text-xs text-purple-800 space-y-1">
                        <p><strong>Crude Oil:</strong> WTI Crude (CL=F)</p>
                        <p><strong>Exchange Rate:</strong> INR-USD (INR=X)</p>
                        <p><strong>Provider:</strong> Yahoo Finance API</p>
                    </div>
                </div>
            </div>

            {/* Kaggle Import */}
            <div className="card bg-secondary-50 border-2 border-dashed border-secondary-300">
                <div className="flex items-center space-x-3 mb-4">
                    <div className="bg-secondary-200 p-2 rounded-lg">
                        <Database className="w-5 h-5 text-secondary-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-secondary-900">Kaggle Datasets</h2>
                        <p className="text-sm text-secondary-600">Quick import from Kaggle datasets (Coming Soon)</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <button disabled className="btn btn-secondary opacity-50 cursor-not-allowed">
                        Import Fuel Prices (India)
                    </button>
                    <button disabled className="btn btn-secondary opacity-50 cursor-not-allowed">
                        Import Crude Oil Prices
                    </button>
                </div>
            </div>
        </div>
    );
}

export default UploadData;

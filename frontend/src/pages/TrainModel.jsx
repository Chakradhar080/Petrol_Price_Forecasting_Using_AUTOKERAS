import React, { useState } from 'react';
import { prepareData, trainModel } from '../services/api';
import { Database, Zap, Settings, CheckCircle, AlertCircle } from 'lucide-react';

function TrainModel() {
    const [preparing, setPreparing] = useState(false);
    const [training, setTraining] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [dataSource, setDataSource] = useState('combined');

    const handlePrepareData = async () => {
        try {
            setPreparing(true);
            setError(null);

            const response = await prepareData(dataSource);

            if (response.data.success) {
                setError(null);
                setResult({
                    success: true,
                    message: response.data.message,
                    isPrepared: true,
                    data_source: response.data.data_source
                });
            } else {
                setError(response.data.message || 'Data preparation failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || err.message);
        } finally {
            setPreparing(false);
        }
    };

    const handleTrain = async () => {
        try {
            setTraining(true);
            setError(null);

            // Auto-prepare data if not already prepared
            if (!result?.isPrepared) {
                console.log('Data not prepared yet, preparing now...');
                const prepareResponse = await prepareData(dataSource);
                if (!prepareResponse.data.success) {
                    setError(prepareResponse.data.message || 'Data preparation failed');
                    setTraining(false);
                    return;
                }
                // Update result with preparation status
                setResult({
                    ...result,
                    success: true,
                    message: prepareResponse.data.message,
                    isPrepared: true,
                    data_source: prepareResponse.data.data_source
                });
            }

            const response = await trainModel({ data_source: dataSource });

            if (response.data.success) {
                setResult(response.data);
                setError(null);
            } else {
                setError(response.data.message || 'Training failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || err.message);
        } finally {
            setTraining(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-secondary-900">Train Model</h1>
                <p className="text-secondary-600 mt-1">Prepare data and train forecasting models with customizable options</p>
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
                    </div>
                </div>
            )}

            {/* Step 1: Data Source Selection */}
            <div className="card">
                <div className="flex items-center space-x-3 mb-4">
                    <div className="bg-primary-100 p-2 rounded-lg">
                        <Database className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-secondary-900">Step 1: Select Data Source</h2>
                        <p className="text-sm text-secondary-600">Choose which data to use for training</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Combined Option */}
                    <button
                        onClick={() => setDataSource('combined')}
                        className={`p-4 rounded-lg border-2 transition-all ${dataSource === 'combined'
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-secondary-200 hover:border-secondary-300'
                            }`}
                    >
                        <div className="text-center">
                            <div className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center mb-3 ${dataSource === 'combined' ? 'bg-primary-500' : 'bg-secondary-200'
                                }`}>
                                <Database className={`w-6 h-6 ${dataSource === 'combined' ? 'text-white' : 'text-secondary-600'
                                    }`} />
                            </div>
                            <h3 className="font-semibold text-secondary-900">Combined</h3>
                            <p className="text-xs text-secondary-600 mt-1">Yahoo Finance + Custom CSV</p>
                        </div>
                    </button>

                    {/* Yahoo Finance Only */}
                    <button
                        onClick={() => setDataSource('yahoo_finance')}
                        className={`p-4 rounded-lg border-2 transition-all ${dataSource === 'yahoo_finance'
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-secondary-200 hover:border-secondary-300'
                            }`}
                    >
                        <div className="text-center">
                            <div className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center mb-3 ${dataSource === 'yahoo_finance' ? 'bg-primary-500' : 'bg-secondary-200'
                                }`}>
                                <Zap className={`w-6 h-6 ${dataSource === 'yahoo_finance' ? 'text-white' : 'text-secondary-600'
                                    }`} />
                            </div>
                            <h3 className="font-semibold text-secondary-900">Yahoo Finance</h3>
                            <p className="text-xs text-secondary-600 mt-1">Live market data only</p>
                        </div>
                    </button>

                    {/* Custom CSV Only */}
                    <button
                        onClick={() => setDataSource('custom_csv')}
                        className={`p-4 rounded-lg border-2 transition-all ${dataSource === 'custom_csv'
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-secondary-200 hover:border-secondary-300'
                            }`}
                    >
                        <div className="text-center">
                            <div className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center mb-3 ${dataSource === 'custom_csv' ? 'bg-primary-500' : 'bg-secondary-200'
                                }`}>
                                <Settings className={`w-6 h-6 ${dataSource === 'custom_csv' ? 'text-white' : 'text-secondary-600'
                                    }`} />
                            </div>
                            <h3 className="font-semibold text-secondary-900">Custom CSV</h3>
                            <p className="text-xs text-secondary-600 mt-1">Uploaded datasets only</p>
                        </div>
                    </button>
                </div>

                <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-800">
                        <strong>Selected:</strong> {
                            dataSource === 'combined' ? 'Combined (Yahoo Finance + Custom CSV)' :
                                dataSource === 'yahoo_finance' ? 'Yahoo Finance Only' :
                                    'Custom CSV Only'
                        }
                    </p>
                </div>
            </div>

            {/* Step 2: Prepare Data */}
            <div className="card">
                <div className="flex items-center space-x-3 mb-4">
                    <div className="bg-accent-100 p-2 rounded-lg">
                        <Settings className="w-5 h-5 text-accent-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-secondary-900">Step 2: Prepare Data</h2>
                        <p className="text-sm text-secondary-600">Run ETL pipeline and feature engineering</p>
                    </div>
                </div>

                <button
                    onClick={handlePrepareData}
                    disabled={preparing}
                    className="btn btn-primary w-full md:w-auto"
                >
                    {preparing ? (
                        <span className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Preparing Data...</span>
                        </span>
                    ) : (
                        'Prepare Data'
                    )}
                </button>

                {result?.isPrepared && (
                    <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                        <p className="text-sm text-green-800">Data preparation complete! Ready for training.</p>
                    </div>
                )}
            </div>

            {/* Step 3: Train Model */}
            <div className="card">
                <div className="flex items-center space-x-3 mb-4">
                    <div className="bg-success/10 p-2 rounded-lg">
                        <Zap className="w-5 h-5 text-success" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-secondary-900">Step 3: Start Training</h2>
                        <p className="text-sm text-secondary-600">Train neural network model</p>
                    </div>
                </div>

                <button
                    onClick={handleTrain}
                    disabled={training}
                    className="btn btn-success w-full md:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {training ? (
                        <span className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Training Model...</span>
                        </span>
                    ) : (
                        'Start Training'
                    )}
                </button>

                {!result?.isPrepared && !training && (
                    <p className="text-sm text-secondary-500 mt-2">Data will be prepared automatically when training starts</p>
                )}
            </div>

            {/* Training Results */}
            {result?.metrics && (
                <div className="card bg-white shadow-lg border border-gray-200">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Training Results</h2>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                            <div className="text-sm text-blue-700">RMSE</div>
                            <div className="text-2xl font-bold text-blue-900 mt-1">
                                {result.metrics.rmse ? Number(result.metrics.rmse).toFixed(4) : 'N/A'}
                            </div>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                            <div className="text-sm text-green-700">MAE</div>
                            <div className="text-2xl font-bold text-green-900 mt-1">
                                {result.metrics.mae ? Number(result.metrics.mae).toFixed(4) : 'N/A'}
                            </div>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                            <div className="text-sm text-purple-700">MAPE</div>
                            <div className="text-2xl font-bold text-purple-900 mt-1">
                                {result.metrics.mape ? Number(result.metrics.mape).toFixed(2) + '%' : 'N/A'}
                            </div>
                        </div>
                        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                            <div className="text-sm text-orange-700">R² Score</div>
                            <div className="text-2xl font-bold text-orange-900 mt-1">
                                {result.metrics.r2 ? Number(result.metrics.r2).toFixed(4) : 'N/A'}
                            </div>
                        </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
                            <div>
                                <span className="text-gray-600">Model Version:</span>
                                <span className="font-semibold ml-2 text-gray-900">{result.model_version}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">Training Samples:</span>
                                <span className="font-semibold ml-2 text-gray-900">{result.training_samples}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">Validation Samples:</span>
                                <span className="font-semibold ml-2 text-gray-900">{result.validation_samples}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">Data Source:</span>
                                <span className="font-semibold ml-2 text-gray-900 capitalize">{dataSource.replace('_', ' ')}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default TrainModel;

import React, { useState, useEffect } from 'react';
import { generateForecast, getModelHistory, getLatestData } from '../services/api';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, Calendar, AlertCircle, ArrowRight } from 'lucide-react';

function Forecast() {
    const [models, setModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState(null);
    const [horizon, setHorizon] = useState(7);
    const [customDate, setCustomDate] = useState('');
    const [useCustomDate, setUseCustomDate] = useState(false);
    const [loading, setLoading] = useState(false);
    const [forecast, setForecast] = useState(null);
    const [error, setError] = useState(null);

    // Fetch available models on component mount
    useEffect(() => {
        fetchModels();
    }, []);

    const fetchModels = async () => {
        try {
            const response = await getModelHistory();
            if (response.data.success) {
                setModels(response.data.models || []);
                // Auto-select the first (latest) model
                if (response.data.models && response.data.models.length > 0) {
                    setSelectedModel(response.data.models[0].model_version);
                }
            }
        } catch (error) {
            console.error('Error fetching models:', error);
        }
    };

    const handleForecast = async () => {
        try {
            setLoading(true);
            setError(null);

            // If using custom date, pass it as end_date, horizon is ignored/calculated by backend
            const endDate = useCustomDate ? customDate : null;
            const targetHorizon = useCustomDate ? 0 : horizon; // if custom date, horizon is calculated by backend

            const response = await generateForecast(targetHorizon, selectedModel, endDate);

            if (response.data.success) {
                // Get the latest actual data to include today's value
                const historicalResponse = await getLatestData();
                
                let combinedData = [];
                
                // Add today's actual data if available
                if (historicalResponse.data.success && historicalResponse.data.data.petrol_price) {
                    const today = new Date();
                    const todayStr = today.toISOString().split('T')[0]; // Format as YYYY-MM-DD
                    
                    combinedData.push({
                        date: todayStr,
                        actual_price: historicalResponse.data.data.petrol_price,
                        isForecast: false,
                        dataType: 'actual'
                    });
                }
                
                // Add forecast data - starts from tomorrow onwards
                const formattedForecastData = response.data.predictions.map(pred => ({
                    date: pred.date,
                    forecast_price: pred.predicted_price,
                    isForecast: true,
                    dataType: 'forecast'
                }));

                // Combine today's actual data with forecast
                combinedData = [...combinedData, ...formattedForecastData];

                // Create a combined result that includes both actual and forecast data
                const combinedResult = {
                    ...response.data,
                    combinedData: combinedData
                };
                
                setForecast(combinedResult);
            } else {
                setError(response.data.message || response.data.error || 'Forecast generation failed');
            }
        } catch (err) {
            setError(err.response?.data?.message || err.response?.data?.error || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="card">
                <h1 className="header-title text-2xl">Price Forecast</h1>
                <p className="text-secondary-600 mt-1">Generate multi-day price predictions using trained models</p>
            </div>

            {/* Controls Card */}
            <div className="card">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="bg-primary-50 p-2 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Forecast Configuration</h2>
                        <p className="text-sm text-secondary-600">Select model, forecast horizon or target date</p>
                    </div>
                </div>

                {/* Model Selection */}
                <div className="mb-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <label className="block text-sm font-semibold text-gray-700 mb-3">Select Model Version</label>
                    <div className="relative">
                        {models.length > 0 ? (
                            <div className="relative">
                                <select
                                    value={selectedModel || ''}
                                    onChange={(e) => setSelectedModel(e.target.value)}
                                    className="w-full p-3 rounded-lg border-2 border-gray-300 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none pr-10"
                                >
                                    {models.map((model) => (
                                        <option key={model.model_version} value={model.model_version}>
                                            {model.model_version} | R²: {model.r2 ? Number(model.r2).toFixed(4) : 'N/A'} | RMSE: {model.rmse ? Number(model.rmse).toFixed(2) : 'N/A'}
                                        </option>
                                    ))}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                        ) : (
                            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded text-center">
                                <p className="text-sm text-yellow-800">No models available. Please train a model first.</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Horizon Selection */}
                    <div className="space-y-4">
                        <label className="block text-sm font-medium text-gray-700">Forecast Horizon (Days)</label>
                        <div className="flex space-x-3">
                            {[7, 14, 30, 60].map((days) => (
                                <button
                                    key={days}
                                    onClick={() => {
                                        setHorizon(days);
                                        setUseCustomDate(false);
                                    }}
                                    className={`btn ${horizon === days && !useCustomDate ? 'btn-primary' : 'btn-secondary'} flex-1 justify-center`}
                                    disabled={loading}
                                >
                                    {days} Days
                                </button>
                            ))}
                        </div>
                        <div className="flex items-center">
                            <input
                                type="number"
                                value={horizon}
                                onChange={(e) => setHorizon(parseInt(e.target.value) || 7)}
                                className="input w-24 mr-2"
                                min="1"
                                max="365"
                            />
                            <span className="text-sm text-secondary-600">Custom days</span>
                        </div>
                    </div>

                    {/* OR Separator */}
                    <div className="hidden md:flex flex-col justify-center items-center">
                        <div className="h-full w-px bg-gray-200"></div>
                        <span className="bg-white py-2 text-xs font-bold text-gray-400 uppercase tracking-widest absolute">OR</span>
                    </div>

                    {/* Target Date Selection */}
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <label className="block text-sm font-medium text-gray-700">Target End Date</label>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="useCustomDate"
                                    checked={useCustomDate}
                                    onChange={(e) => setUseCustomDate(e.target.checked)}
                                    className="mr-2 h-4 w-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                                />
                                <label htmlFor="useCustomDate" className="text-sm text-gray-600 cursor-pointer">Enable Date</label>
                            </div>
                        </div>
                        <div className={`transition-opacity ${!useCustomDate ? 'opacity-50 pointer-events-none' : ''}`}>
                            <div className="relative">
                                <input
                                    type="date"
                                    value={customDate}
                                    onChange={(e) => setCustomDate(e.target.value)}
                                    className="input pl-10"
                                    min={new Date().toISOString().split('T')[0]}
                                />
                                <Calendar className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                            </div>
                            <p className="text-xs text-secondary-500 mt-2">
                                Forecast from tomorrow until selected date
                            </p>
                        </div>
                    </div>
                </div>

                <div className="mt-8 flex justify-end">
                    <button
                        onClick={handleForecast}
                        disabled={loading || (useCustomDate && !customDate) || !selectedModel}
                        className="btn btn-primary px-8 py-3"
                    >
                        {loading ? (
                            <>
                                <span className="animate-spin mr-2">⟳</span>
                                Generating...
                            </>
                        ) : (
                            <>
                                Generate Forecast
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </>
                        )}
                    </button>
                </div>

                {error && (
                    <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
                        <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-red-800">{error}</p>
                    </div>
                )}
            </div>

            {/* Results */}
            {forecast && (
                <div className="space-y-6 animate-fade-in">
                    {/* Forecast Summary Card */}
                    <div className="card">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Forecast Results</h2>
                                <p className="text-secondary-600 text-sm mt-1">
                                    Model: {forecast.model_version} • Horizon: {forecast.horizon_days} Days
                                </p>
                            </div>
                        </div>

                        {/* Key Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                                <div className="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-2">Start Price</div>
                                <div className="text-3xl font-bold text-blue-900">
                                    ₹{forecast.predictions[0]?.predicted_price.toFixed(2)}
                                </div>
                                <div className="text-xs text-blue-600 mt-2">Day 1</div>
                            </div>

                            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                                <div className="text-xs font-semibold text-green-700 uppercase tracking-wide mb-2">End Price</div>
                                <div className="text-3xl font-bold text-green-900">
                                    ₹{forecast.predictions[forecast.predictions.length - 1]?.predicted_price.toFixed(2)}
                                </div>
                                <div className="text-xs text-green-600 mt-2">Day {forecast.horizon_days}</div>
                            </div>

                            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                                <div className="text-xs font-semibold text-purple-700 uppercase tracking-wide mb-2">Price Change</div>
                                <div className="text-3xl font-bold text-purple-900">
                                    ₹{(forecast.predictions[forecast.predictions.length - 1]?.predicted_price - forecast.predictions[0]?.predicted_price).toFixed(2)}
                                </div>
                                <div className={`text-xs mt-2 ${(forecast.predictions[forecast.predictions.length - 1]?.predicted_price - forecast.predictions[0]?.predicted_price) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {(forecast.predictions[forecast.predictions.length - 1]?.predicted_price - forecast.predictions[0]?.predicted_price) >= 0 ? '↗ Uptrend' : '↘ Downtrend'}
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
                                <div className="text-xs font-semibold text-orange-700 uppercase tracking-wide mb-2">Avg Price</div>
                                <div className="text-3xl font-bold text-orange-900">
                                    ₹{(forecast.predictions.reduce((sum, p) => sum + p.predicted_price, 0) / forecast.predictions.length).toFixed(2)}
                                </div>
                                <div className="text-xs text-orange-600 mt-2">Over {forecast.horizon_days} days</div>
                            </div>
                        </div>
                    </div>

                    {/* Main Forecast Chart */}
                    <div className="card">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Price Trend Forecast</h3>
                        <div style={{ width: '100%', height: '400px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart
                                    data={forecast.combinedData || forecast.predictions.map(p => ({...p, dataType: 'forecast'}))}
                                    margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#64748B"
                                        style={{ fontSize: '0.75rem' }}
                                        tick={{ fill: '#64748B' }}
                                        tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                        interval="preserveStartEnd"
                                    />
                                    <YAxis
                                        stroke="#64748B"
                                        style={{ fontSize: '0.75rem' }}
                                        tick={{ fill: '#64748B' }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'white',
                                            border: '1px solid #E2E8F0',
                                            borderRadius: '8px',
                                            fontSize: '0.875rem',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                            padding: '8px'
                                        }}
                                        formatter={(value, name, props) => {
                                            const isActual = props.payload.dataType === 'actual';
                                            return [
                                                `₹${value.toFixed(2)}`,
                                                isActual ? 'Actual Price (₹)' : 'Forecasted Price (₹)'
                                            ];
                                        }}
                                    />
                                    <Legend />
                                    {/* Actual data line */}
                                    <Line
                                        type="monotone"
                                        dataKey="actual_price"
                                        name="Actual Price (₹)"
                                        stroke="#6B7280"
                                        strokeWidth={2}
                                        dot={true}
                                        activeDot={{ r: 6 }}
                                        isAnimationActive={true}
                                    />
                                    {/* Forecast data line */}
                                    <Line
                                        type="monotone"
                                        dataKey="forecast_price"
                                        name="Forecasted Price (₹)"
                                        stroke="#2563EB"
                                        strokeWidth={3}
                                        strokeDasharray="5 5" /* Dashed line for forecast */
                                        dot={{ fill: '#2563EB', r: 4 }}
                                        activeDot={{ r: 6 }}
                                        isAnimationActive={true}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Area Chart - Price Distribution */}
                    <div className="card">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Price Distribution Over Time</h3>
                        <div style={{ width: '100%', height: '350px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart
                                    data={forecast.combinedData || forecast.predictions.map(p => ({...p, dataType: 'forecast'}))}
                                    margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                                >
                                    <defs>
                                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                                            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                                        </linearGradient>
                                        <linearGradient id="colorHistorical" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6B7280" stopOpacity={0.8}/>
                                            <stop offset="95%" stopColor="#6B7280" stopOpacity={0.1}/>
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#64748B"
                                        style={{ fontSize: '0.75rem' }}
                                        tick={{ fill: '#64748B' }}
                                        tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                        interval="preserveStartEnd"
                                    />
                                    <YAxis
                                        stroke="#64748B"
                                        style={{ fontSize: '0.75rem' }}
                                        tick={{ fill: '#64748B' }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'white',
                                            border: '1px solid #E2E8F0',
                                            borderRadius: '8px',
                                            fontSize: '0.875rem',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                            padding: '8px'
                                        }}
                                        formatter={(value, name, props) => {
                                            const isActual = props.payload.dataType === 'actual';
                                            return [
                                                `₹${value.toFixed(2)}`,
                                                isActual ? 'Actual Price (₹)' : 'Forecasted Price (₹)'
                                            ];
                                        }}
                                    />
                                    <Legend />
                                    {/* Actual data area */}
                                    <Area
                                        type="monotone"
                                        dataKey="actual_price"
                                        stroke="#6B7280"
                                        strokeWidth={2}
                                        fillOpacity={0.3}
                                        fill="url(#colorHistorical)"
                                        name="Actual Price (₹)"
                                        isAnimationActive={true}
                                    />
                                    {/* Forecast data area */}
                                    <Area
                                        type="monotone"
                                        dataKey="forecast_price"
                                        stroke="#2563EB"
                                        strokeWidth={2}
                                        fillOpacity={0.6}
                                        fill="url(#colorPrice)"
                                        name="Forecasted Price (₹)"
                                        isAnimationActive={true}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Daily Changes Bar Chart */}
                    <div className="card">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Daily Price Changes</h3>
                        <div style={{ width: '100%', height: '350px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={
                                        forecast.combinedData 
                                        ? forecast.combinedData.map((item, index, arr) => {
                                            // Calculate change from previous day
                                            let change = 0;
                                            if (index > 0) {
                                                const prevItem = arr[index - 1];
                                                const prevValue = prevItem.dataType === 'forecast' ? prevItem.forecast_price : prevItem.actual_price;
                                                const currentValue = item.dataType === 'forecast' ? item.forecast_price : item.actual_price;
                                                change = currentValue - prevValue;
                                            }
                                            return {
                                                date: item.date,
                                                change: change,
                                                dataType: item.dataType
                                            };
                                          })
                                        : forecast.predictions.map((pred, index) => ({
                                            date: pred.date,
                                            change: index > 0 ? pred.predicted_price - forecast.predictions[index - 1].predicted_price : 0,
                                            dataType: 'forecast'
                                        }))
                                    }
                                    margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#64748B"
                                        style={{ fontSize: '0.75rem' }}
                                        tick={{ fill: '#64748B' }}
                                        tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                        interval="preserveStartEnd"
                                    />
                                    <YAxis
                                        stroke="#64748B"
                                        style={{ fontSize: '0.75rem' }}
                                        tick={{ fill: '#64748B' }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'white',
                                            border: '1px solid #E2E8F0',
                                            borderRadius: '8px',
                                            fontSize: '0.875rem',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                            padding: '8px'
                                        }}
                                        formatter={(value) => [`₹${value.toFixed(2)}`, 'Daily Change']}
                                        labelFormatter={(label) => `Date: ${label}`}
                                    />
                                    <Bar
                                        dataKey="change"
                                        fill="#8B5CF6"
                                        radius={[8, 8, 0, 0]}
                                        name="Daily Change (₹)"
                                        isAnimationActive={true}
                                    />
                                    <Legend />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Price Statistics */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Min/Max Price */}
                        <div className="card">
                            <h3 className="text-lg font-bold text-gray-900 mb-4">Price Range Analysis</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-200">
                                    <span className="text-sm font-semibold text-red-700">Minimum Price</span>
                                    <span className="text-xl font-bold text-red-900">
                                        ₹{Math.min(...forecast.predictions.map(p => p.predicted_price)).toFixed(2)}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg border border-green-200">
                                    <span className="text-sm font-semibold text-green-700">Maximum Price</span>
                                    <span className="text-xl font-bold text-green-900">
                                        ₹{Math.max(...forecast.predictions.map(p => p.predicted_price)).toFixed(2)}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                                    <span className="text-sm font-semibold text-blue-700">Price Volatility</span>
                                    <span className="text-xl font-bold text-blue-900">
                                        ₹{(Math.max(...forecast.predictions.map(p => p.predicted_price)) - Math.min(...forecast.predictions.map(p => p.predicted_price))).toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Daily Changes */}
                        <div className="card">
                            <h3 className="text-lg font-bold text-gray-900 mb-4">Daily Change Statistics</h3>
                            <div className="space-y-4">
                                {(() => {
                                    const dataToUse = forecast.combinedData || forecast.predictions;
                                    const changes = [];
                                    
                                    for (let i = 1; i < dataToUse.length; i++) {
                                        const currentValue = dataToUse[i].forecast_price || dataToUse[i].predicted_price;
                                        const prevValue = dataToUse[i - 1].forecast_price || dataToUse[i - 1].predicted_price || dataToUse[i - 1].actual_price;
                                        
                                        changes.push(currentValue - prevValue);
                                    }
                                    
                                    const avgChange = changes.length > 0 ? changes.reduce((a, b) => a + b, 0) / changes.length : 0;
                                    const maxIncrease = changes.length > 0 ? Math.max(...changes) : 0;
                                    const maxDecrease = changes.length > 0 ? Math.min(...changes) : 0;

                                    return (
                                        <>
                                            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                                                <span className="text-sm font-semibold text-blue-700">Avg Daily Change</span>
                                                <span className={`text-xl font-bold ${avgChange >= 0 ? 'text-green-900' : 'text-red-900'}`}>
                                                    {avgChange >= 0 ? '+' : ''}₹{avgChange.toFixed(2)}
                                                </span>
                                            </div>
                                            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg border border-green-200">
                                                <span className="text-sm font-semibold text-green-700">Max Daily Increase</span>
                                                <span className="text-xl font-bold text-green-900">+₹{maxIncrease.toFixed(2)}</span>
                                            </div>
                                            <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-200">
                                                <span className="text-sm font-semibold text-red-700">Max Daily Decrease</span>
                                                <span className="text-xl font-bold text-red-900">-₹{Math.abs(maxDecrease).toFixed(2)}</span>
                                            </div>
                                        </>
                                    );
                                })()}
                            </div>
                        </div>
                    </div>

                    {/* Detailed Forecast Table */}
                    <div className="card">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Day-by-Day Forecast Details</h3>
                        <div className="overflow-x-auto">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Price</th>
                                        <th>Type</th>
                                        <th>Trend</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(forecast.combinedData || forecast.predictions).map((item, index, arr) => {
                                        const currentValue = item.dataType === 'forecast' ? item.forecast_price : (item.actual_price || item.predicted_price);
                                        const prevItem = index > 0 ? arr[index - 1] : null;
                                        const prevValue = prevItem 
                                            ? (prevItem.dataType === 'forecast' ? prevItem.forecast_price : (prevItem.actual_price || prevItem.predicted_price))
                                            : currentValue;
                                        const change = currentValue - prevValue;

                                        return (
                                            <tr key={`${item.date}-${index}`}>
                                                <td className="font-medium text-gray-900">{item.date}</td>
                                                <td className={`font-bold ${item.dataType === 'forecast' ? 'text-blue-600' : 'text-gray-900'}`}>₹{currentValue.toFixed(2)}</td>
                                                <td>
                                                    <span className={`badge ${item.dataType === 'forecast' ? 'badge-info' : 'badge-secondary'}`}>
                                                        {item.dataType === 'forecast' ? 'Forecast' : 'Actual'}
                                                    </span>
                                                </td>
                                                <td>
                                                    <span className={`badge ${change >= 0 ? 'badge-success' : 'badge-primary'}`}>
                                                        {change >= 0 ? '↗' : '↘'} {Math.abs(change).toFixed(2)}
                                                    </span>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Forecast;

import React, { useState, useEffect } from 'react';
import { getLatestData, getIngestionStatus, getModelHistory, generateForecast } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, ArrowUp, Info } from 'lucide-react';

function Dashboard() {
    const [latestData, setLatestData] = useState(null);
    const [ingestionStatus, setIngestionStatus] = useState(null);
    const [latestModel, setLatestModel] = useState(null);
    const [forecastData, setForecastData] = useState([]);
    const [forecastPredictions, setForecastPredictions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            
            // Fetch latest data
            const dataResponse = await getLatestData();
            if (dataResponse.data.success) {
                setLatestData(dataResponse.data.data);
            }
            
            // Fetch ingestion status
            const statusResponse = await getIngestionStatus();
            if (statusResponse.data.success) {
                setIngestionStatus(statusResponse.data.data);
            }
            
            // Fetch latest model info
            const modelResponse = await getModelHistory();
            if (modelResponse.data.success && modelResponse.data.models && modelResponse.data.models.length > 0) {
                setLatestModel(modelResponse.data.models[0]);
                
                // Generate 7-day forecast with the latest model
                try {
                    const forecastResponse = await generateForecast(7, modelResponse.data.models[0].model_version);
                    if (forecastResponse.data.success && forecastResponse.data.predictions) {
                        // Prepare combined chart data: today's actual + forecast
                        let chartData = [];
                        
                        // Add today's actual data
                        if (dataResponse.data.success && dataResponse.data.data.petrol_price) {
                            const today = new Date();
                            const todayStr = today.toISOString().split('T')[0];
                            chartData.push({
                                date: todayStr,
                                actual_price: dataResponse.data.data.petrol_price,
                                forecast_price: null,
                                type: 'actual'
                            });
                        }
                        
                        // Add forecast data
                        chartData = chartData.concat(forecastResponse.data.predictions.map((pred, idx) => ({
                            date: pred.date,
                            actual_price: null,
                            forecast_price: pred.predicted_price,
                            type: 'forecast'
                        })));
                        
                        setForecastData(chartData);
                        // Also store the full predictions for the table
                        setForecastPredictions(forecastResponse.data.predictions);
                    }
                } catch (forecastError) {
                    console.error('Error generating forecast:', forecastError);
                    // Use empty array if forecast fails
                    setForecastData([]);
                    setForecastPredictions([]);
                }
            }
            
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Key Metrics */}
            <div className="metrics-grid">
                <div className="metric-card">
                    <div className="metric-label">Current Petrol Price</div>
                    <div className="metric-value">
                        ₹{loading ? '...' : (latestData?.petrol_price?.toFixed(2) || '104.85')}
                    </div>
                    <div className="metric-change positive">
                        <ArrowUp className="w-4 h-4" />
                        +2.3% vs last month
                    </div>
                </div>

                <div className="metric-card accent-purple">
                    <div className="metric-label">Crude Oil (WTI)</div>
                    <div className="metric-value">
                        ${loading ? '...' : (latestData?.crude_oil_price?.toFixed(2) || '66.39')}
                    </div>
                    <div className="metric-change positive">
                        <ArrowUp className="w-4 h-4" />
                        +1.8% from last week
                    </div>
                </div>

                <div className="metric-card accent-green">
                    <div className="metric-label">INR-USD Rate</div>
                    <div className="metric-value">
                        ₹{loading ? '...' : (latestData?.inr_usd?.toFixed(2) || '91.88')}
                    </div>
                    <div className="metric-change">
                        Updated today
                    </div>
                </div>
            </div>

            {/* System Status Strip */}
            <div className="status-strip">
                <div className="status-item">
                    Last Ingestion: <strong>{ingestionStatus?.last_ingestion_date ? new Date(ingestionStatus.last_ingestion_date).toLocaleDateString() : 'N/A'}</strong>
                </div>
                <div className="status-item">
                    Records Ingested: <strong>{ingestionStatus?.total_records || 0}</strong>
                </div>
                <div className="status-item">
                    Active Model: <strong>{latestModel?.model_version || 'N/A'}</strong>
                </div>
                <div className="status-item">
                    R²: <strong>{latestModel?.r2 ? Number(latestModel.r2).toFixed(4) : 'N/A'}</strong>
                </div>
                <div className="status-item">
                    RMSE: <strong>{latestModel?.rmse ? Number(latestModel.rmse).toFixed(2) : 'N/A'}</strong>
                </div>
                <div className="status-item">
                    MAE: <strong>{latestModel?.mae ? Number(latestModel.mae).toFixed(2) : 'N/A'}</strong>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 gap-6">
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Forecast (Next 7 Days)</h2>
                        <p className="card-subtitle">Predicted price movement from today onwards</p>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={forecastData && forecastData.length > 0 ? forecastData : []}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#64748B"
                                    style={{ fontSize: '0.75rem' }}
                                    tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                    interval="preserveStartEnd"
                                />
                                <YAxis
                                    stroke="#64748B"
                                    style={{ fontSize: '0.75rem' }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'white',
                                        border: '1px solid #E2E8F0',
                                        borderRadius: '8px',
                                        fontSize: '0.875rem'
                                    }}
                                    formatter={(value, name) => {
                                        if (value === null) return null;
                                        return [`₹${value.toFixed(2)}`, name];
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="actual_price"
                                    stroke="#6B7280"
                                    strokeWidth={2}
                                    dot={true}
                                    activeDot={{ r: 6 }}
                                    name="Actual Price (₹)"
                                    isAnimationActive={true}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="forecast_price"
                                    stroke="#10B981"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    dot={{ fill: '#10B981', r: 4 }}
                                    activeDot={{ r: 6 }}
                                    name="Forecasted Price (₹)"
                                    isAnimationActive={true}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* System Info Card */}
            <div className="card bg-blue-50 border border-blue-200">
                <div className="flex items-start space-x-3">
                    <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 className="font-semibold text-blue-900">System Information</h3>
                        <div className="text-sm text-blue-800 mt-2 space-y-1">
                            <p><strong>Data Source:</strong> {latestModel?.data_source ? latestModel.data_source.replace(/_/g, ' ') : 'Combined (Yahoo Finance + Custom CSV)'}</p>
                            <p><strong>Forecasts Use:</strong> The latest trained model ({latestModel?.model_version || 'v1'}) with {ingestionStatus?.total_records || 'all'} ingested records</p>
                            <p><strong>Last Training:</strong> {latestModel?.created_at ? new Date(latestModel.created_at).toLocaleDateString() : 'Not yet trained'}</p>
                            <p><strong>Model Quality (R²):</strong> {latestModel?.r2 ? Number(latestModel.r2).toFixed(4) : 'N/A'} - Indicates how well the model fits the training data</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Prediction Table */}
            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">Upcoming Predictions</h2>
                    <p className="card-subtitle">Next 7-day forecast details</p>
                </div>
                <table className="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Predicted Price</th>
                            <th>Confidence</th>
                            <th>Change</th>
                        </tr>
                    </thead>
                    <tbody>
                        {forecastPredictions && forecastPredictions.length > 0 ? (
                            forecastPredictions.map((pred, idx) => {
                                const change = idx === 0 ? 0 : pred.predicted_price - forecastPredictions[idx - 1].predicted_price;
                                const changePercent = idx === 0 ? 0 : ((change / forecastPredictions[idx - 1].predicted_price) * 100).toFixed(2);
                                return (
                                    <tr key={idx}>
                                        <td>{new Date(pred.date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</td>
                                        <td>₹{pred.predicted_price.toFixed(2)}</td>
                                        <td><span className="badge badge-success">High</span></td>
                                        <td className={change >= 0 ? 'text-success' : 'text-danger'}>
                                            {change >= 0 ? '+' : ''}{change.toFixed(2)} ({changePercent}%)
                                        </td>
                                    </tr>
                                );
                            })
                        ) : (
                            <tr>
                                <td colSpan="4" className="text-center text-secondary-600">
                                    No forecast data available
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Dashboard;

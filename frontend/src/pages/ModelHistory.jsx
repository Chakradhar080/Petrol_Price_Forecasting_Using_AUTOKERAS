import React, { useState, useEffect } from 'react';
import { getModelHistory } from '../services/api';
import { History, Award, TrendingUp, Calendar } from 'lucide-react';

function ModelHistory() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await getModelHistory();
            if (response.data.success) {
                setModels(response.data.models);
            }
        } catch (error) {
            console.error('Error fetching model history:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-secondary-900">Model History</h1>
                    <p className="text-secondary-600 mt-1">View and compare all trained model versions</p>
                </div>
                <button onClick={fetchHistory} className="btn btn-primary">
                    Refresh
                </button>
            </div>

            {/* Models Grid */}
            {models && models.length > 0 ? (
                <div className="grid grid-cols-1 gap-6">
                    {models.map((model, idx) => (
                        <div key={idx} className="card hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    {idx === 0 ? (
                                        <div className="bg-success/10 p-2 rounded-lg">
                                            <Award className="w-5 h-5 text-success" />
                                        </div>
                                    ) : (
                                        <div className="bg-secondary-100 p-2 rounded-lg">
                                            <History className="w-5 h-5 text-secondary-600" />
                                        </div>
                                    )}
                                    <div>
                                        <h3 className="text-lg font-bold text-secondary-900">
                                            {model.model_version}
                                        </h3>
                                        {idx === 0 && (
                                            <span className="badge badge-success text-xs mt-1">Latest Model</span>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center space-x-2 text-sm text-secondary-600">
                                    <Calendar className="w-4 h-4" />
                                    <span>{new Date(model.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>

                            {/* Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                                <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
                                    <div className="text-xs font-semibold text-primary-700 uppercase tracking-wide">RMSE</div>
                                    <div className="text-2xl font-bold text-primary-900 mt-1">
                                        {model.rmse ? Number(model.rmse).toFixed(4) : 'N/A'}
                                    </div>
                                </div>
                                <div className="bg-accent-50 rounded-lg p-4 border border-accent-200">
                                    <div className="text-xs font-semibold text-accent-700 uppercase tracking-wide">MAE</div>
                                    <div className="text-2xl font-bold text-accent-900 mt-1">
                                        {model.mae ? Number(model.mae).toFixed(4) : 'N/A'}
                                    </div>
                                </div>
                                <div className="bg-success/10 rounded-lg p-4 border border-success/30">
                                    <div className="text-xs font-semibold text-green-700 uppercase tracking-wide">MAPE</div>
                                    <div className="text-2xl font-bold text-green-900 mt-1">
                                        {model.mape ? Number(model.mape).toFixed(2) + '%' : 'N/A'}
                                    </div>
                                </div>
                                <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
                                    <div className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">R² Score</div>
                                    <div className="text-2xl font-bold text-indigo-900 mt-1">
                                        {model.r2 ? Number(model.r2).toFixed(4) : 'N/A'}
                                    </div>
                                </div>
                            </div>

                            {/* Details */}
                            <div className="border-t border-secondary-200 pt-4">
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                    <div>
                                        <div className="text-secondary-600">Training Samples</div>
                                        <div className="font-semibold text-secondary-900 mt-1">
                                            {model.training_samples || 'N/A'}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-secondary-600">Validation Samples</div>
                                        <div className="font-semibold text-secondary-900 mt-1">
                                            {model.validation_samples || 'N/A'}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-secondary-600">Status</div>
                                        <div className="mt-1">
                                            <span className="badge badge-success">Active</span>
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-secondary-600">Model Path</div>
                                        <div className="font-mono text-xs text-secondary-900 mt-1 truncate">
                                            {model.model_path?.split('/').pop() || 'N/A'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="card text-center py-12">
                    <div className="bg-secondary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                        <TrendingUp className="w-8 h-8 text-secondary-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Models Found</h3>
                    <p className="text-secondary-600">Train your first model to see it here</p>
                </div>
            )}
        </div>
    );
}

export default ModelHistory;

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Upload, Zap, TrendingUp, History } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import UploadData from './pages/UploadData';
import TrainModel from './pages/TrainModel';
import Forecast from './pages/Forecast';
import ModelHistory from './pages/ModelHistory';

function Sidebar() {
    const location = useLocation();
    const isActive = (path) => location.pathname === path;

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/upload', label: 'Upload Data', icon: Upload },
        { path: '/train', label: 'Train Model', icon: Zap },
        { path: '/forecast', label: 'Forecast', icon: TrendingUp },
        { path: '/history', label: 'Model History', icon: History },
    ];

    return (
        <div className="sidebar">
            <div className="sidebar-logo">
                Petrol Price AI
            </div>
            <ul className="sidebar-nav">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <li key={item.path} className="sidebar-nav-item">
                            <Link
                                to={item.path}
                                className={`sidebar-nav-link ${isActive(item.path) ? 'active' : ''}`}
                            >
                                <Icon className="w-5 h-5" />
                                <span>{item.label}</span>
                            </Link>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}

function Header() {
    return (
        <div className="header">
            <h1 className="header-title">Dashboard</h1>
            <div className="header-status">
                <div className="status-badge">
                    <span className="status-badge-dot"></span>
                    Data: Updated Today
                </div>
                <div className="status-badge">
                    Model: v3 (Active)
                </div>
            </div>
        </div>
    );
}

function App() {
    return (
        <Router>
            <div className="app-layout">
                <Sidebar />
                <div className="main-content">
                    <Header />
                    <div className="content-area">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/upload" element={<UploadData />} />
                            <Route path="/train" element={<TrainModel />} />
                            <Route path="/forecast" element={<Forecast />} />
                            <Route path="/history" element={<ModelHistory />} />
                        </Routes>
                    </div>
                </div>
            </div>
        </Router>
    );
}

export default App;

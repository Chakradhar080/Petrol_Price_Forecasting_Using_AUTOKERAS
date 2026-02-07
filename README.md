# Petrol Price Forecasting System

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-green)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/react-18%2B-61dafb)](https://reactjs.org/)

An advanced machine learning system that predicts petrol prices using AutoML technology. This project combines automated data collection, neural network modeling, and an interactive dashboard to provide accurate forecasts of petrol prices.

## 🎯 Features

- **Automated Machine Learning**: Uses Auto-Keras for automated neural network architecture selection
- **Interactive Dashboard**: React-based web interface for visualizing predictions and trends
- **Data Management**: Supports automatic data scraping and manual CSV/Excel uploads
- **Model Tracking**: Maintains multiple model versions with performance metrics (RMSE, MAE, MAPE)
- **Scheduled Updates**: Automatic daily data collection and weekly model retraining via APScheduler
- **Multi-horizon Forecasting**: Generate predictions for 7, 14, or 30-day periods
- **REST API**: Full-featured API for programmatic access to predictions and model management

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14+ and npm
- Git
- SQLite3 (or MySQL/PostgreSQL for production)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/petrol-price-forecasting.git
   cd petrol-price-forecasting
   ```

2. **Set up Python Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   ```bash
   python init_db.py
   ```

5. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

6. **Prepare Initial Data (Optional)**
   ```bash
   python prepare_data.py
   ```

## 🏁 Quick Start

The fastest way to run the project locally:

```bash
# Terminal 1: Start Backend API
python backend/app.py
# API available at http://localhost:5000

# Terminal 2: Start Frontend
cd frontend
npm start
# Dashboard available at http://localhost:3000

# Terminal 3 (Optional): Start Scheduler for automated tasks
python scheduler/scheduler_app.py
```

Once running, navigate to `http://localhost:3000` to access the dashboard.

## 📁 Project Structure

```
.
├── backend/                      # Flask REST API server
│   ├── app.py                   # Main Flask application
│   ├── routes/                  # API endpoint definitions
│   │   ├── data_routes.py       
│   │   ├── prediction_routes.py 
│   │   ├── training_routes.py   
│   │   ├── prepare_routes.py    
│   │   └── sync_routes.py
│   ├── services/                # Business logic layer
│   │   ├── data_source_filter.py
│   │   ├── prediction_service.py
│   │   └── training_service.py
│   └── logs/                    # API server logs
├── frontend/                     # React dashboard application
│   ├── public/
│   │   └── index.html           # HTML entry point
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── pages/               # Dashboard pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Forecast.jsx
│   │   │   ├── ModelHistory.jsx
│   │   │   ├── TrainModel.jsx
│   │   │   └── UploadData.jsx
│   │   └── services/            # API client services
│   │       └── api.js
│   └── package.json             # Frontend dependencies
├── ml_pipeline/                 # Machine learning components
│   ├── train.py                 # Model training logic
│   ├── predict.py               # Inference functions
│   ├── evaluate.py              # Performance metrics
│   ├── feature_engineering.py   # Feature creation
│   ├── preprocess.py            # Data preprocessing
│   ├── model_registry.py        # Model versioning
│   └── saved_models/            # Trained model files
├── db/                          # Database layer
│   ├── database.py              # SQLAlchemy setup
│   ├── models.py                # Database models
│   └── schema.sql               # Database schema
├── scheduler/                   # Task scheduling (APScheduler)
│   ├── scheduler_app.py
│   └── jobs.py                  # Scheduled job definitions
├── scraper/                     # Data collection components
│   ├── petrol_scraper.py        # Petrol price scraper
│   ├── macro_data_fetcher.py    # Macroeconomic data
│   ├── data_ingestion_service.py
│   └── file_upload_handler.py
├── utils/                       # Utility functions
│   └── logger.py                # Logging configuration
├── uploads/                     # User uploaded datasets
├── logs/                        # Application logs
├── config.py                    # Configuration settings
├── init_db.py                   # Database initialization
├── prepare_data.py              # Data preparation script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🌐 API Documentation

### Core Endpoints

#### Data Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-dataset` | Upload CSV/Excel dataset |
| GET | `/api/data/raw` | Retrieve raw petrol and macro data |
| GET | `/api/data/processed` | Get processed features |
| GET | `/api/data/latest` | Get most recent data points |

#### Model Training & Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/train` | Start model training process |
| GET | `/api/model/versions` | List all trained model versions |
| GET | `/api/metrics/latest` | Get latest model metrics |
| GET | `/api/metrics/best?metric=rmse` | Get best model by metric |

#### Forecasting
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/forecast` | Generate forecast predictions |
| GET | `/api/forecast/history` | Retrieve historical forecasts |

**Example Forecast Request:**
```json
POST /api/forecast
{
  "horizon_days": 7,
  "model_version": "latest"
}
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following settings:

```env
# Database Configuration
DB_TYPE=sqlite
DB_NAME=petrol_price.db
# For MySQL/PostgreSQL:
# DB_HOST=localhost
# DB_USER=username
# DB_PASSWORD=password

# Scheduler Configuration
DATA_FETCH_HOUR=9          # Hour to fetch data (0-23)
RETRAIN_DAY=6              # Day to retrain (0=Monday, 6=Sunday)
RETRAIN_HOUR=2             # Hour to retrain (0-23)

# Model Training
MAX_TRIALS=10              # AutoML trials
EPOCHS=50                  # Training epochs
VALIDATION_SPLIT=0.2       # Validation data ratio
BATCH_SIZE=32

# API Server
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Data Processing
MIN_DATA_POINTS=60         # Minimum historical records needed
FORECAST_HORIZONS=[7,14,30]
```

### Application Configuration

Edit `config.py` to customize:
- Model hyperparameters
- Feature engineering settings
- Data processing parameters
- API response limits

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Database errors** | Verify `.env` credentials, ensure database server is running |
| **Training failures** | Check you have ≥60 days of historical data; review logs in `logs/` |
| **Frontend won't load** | Confirm backend API is running; check browser console for errors |
| **Data scraping fails** | Check internet connection; verify data source hasn't changed structure |
| **Model predictions are inaccurate** | Increase data quality; retrain with more recent data; adjust hyperparameters |

### Useful Commands

```bash
# View logs
tail -f logs/app.log

# Reset database (development only)
python -c "from db.database import Base, engine; Base.metadata.drop_all(engine)"
python init_db.py

# Test API connectivity
curl http://localhost:5000/api/data/latest

# Check scheduler status
python -c "from scheduler.scheduler_app import scheduler; print(scheduler.get_jobs())"
```

## 📚 Tech Stack

### Backend
- **Python 3.8+** - Core language
- **Flask** - Web framework & REST API
- **SQLAlchemy** - Database ORM
- **Auto-Keras** - Automated machine learning
- **TensorFlow** - Deep learning framework
- **APScheduler** - Job scheduling

### Frontend
- **React 18+** - UI framework
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Bootstrap** - Responsive styling

### Data Processing
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-learn** - Machine learning utilities
- **yfinance** - Financial data retrieval

### Database
- **SQLite** - Default (development)
- **MySQL/PostgreSQL** - Production-ready options

### Deployment Ready
- **Gunicorn** - WSGI server
- **Nginx** - Reverse proxy (optional)
- **Docker** - Containerization (optional)

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit changes: `git commit -m 'Add your feature description'`
4. Push to branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- Changes are tested locally
- PR description clearly explains the changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Auto-Keras team for the AutoML framework
- Flask and React communities
- All contributors and users who help improve this project

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in the repo
- Review API documentation in this README

---

**Last Updated:** February 2026  
**Version:** 1.0.0

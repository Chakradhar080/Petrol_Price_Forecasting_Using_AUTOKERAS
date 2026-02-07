"""
Model registry management.
Handles model versioning, retrieval, and comparison.
"""
from db.database import get_db_session
from db.models import ModelRegistry
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/model_registry.log')

class ModelRegistryManager:
    """Manager for model registry operations"""
    
    def __init__(self):
        pass
    
    def get_next_version(self):
        """
        Get next model version number
        
        Returns:
            str: Next version (e.g., 'v1', 'v2', 'v3')
        """
        try:
            with get_db_session() as session:
                # Get all existing versions
                versions = session.query(ModelRegistry.model_version).all()
                
                if not versions:
                    return 'v1'
                
                # Extract version numbers
                version_numbers = []
                for (version,) in versions:
                    try:
                        num = int(version.replace('v', ''))
                        version_numbers.append(num)
                    except:
                        continue
                
                if not version_numbers:
                    return 'v1'
                
                next_num = max(version_numbers) + 1
                return f'v{next_num}'
                
        except Exception as e:
            logger.error(f"Error getting next version: {str(e)}")
            return 'v1'
    
    def get_all_models(self):
        """
        Get all registered models
        
        Returns:
            list: List of model dictionaries
        """
        try:
            with get_db_session() as session:
                models = session.query(ModelRegistry).order_by(
                    ModelRegistry.created_at.desc()
                ).all()
                
                return [m.to_dict() for m in models]
                
        except Exception as e:
            logger.error(f"Error getting all models: {str(e)}")
            return []
    
    def get_model_by_version(self, model_version):
        """
        Get model details by version
        
        Args:
            model_version: Version identifier
        
        Returns:
            dict: Model details or None
        """
        try:
            with get_db_session() as session:
                model = session.query(ModelRegistry).filter_by(
                    model_version=model_version
                ).first()
                
                if model:
                    return model.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"Error getting model {model_version}: {str(e)}")
            return None
    
    def get_latest_model(self):
        """
        Get latest model details
        
        Returns:
            dict: Latest model details or None
        """
        try:
            with get_db_session() as session:
                model = session.query(ModelRegistry).order_by(
                    ModelRegistry.created_at.desc()
                ).first()
                
                if model:
                    return model.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"Error getting latest model: {str(e)}")
            return None
    
    def get_best_model(self, metric='rmse'):
        """
        Get best model based on a metric
        
        Args:
            metric: 'rmse', 'mae', or 'mape'
        
        Returns:
            dict: Best model details or None
        """
        try:
            with get_db_session() as session:
                if metric == 'rmse':
                    model = session.query(ModelRegistry).order_by(
                        ModelRegistry.rmse.asc()
                    ).first()
                elif metric == 'mae':
                    model = session.query(ModelRegistry).order_by(
                        ModelRegistry.mae.asc()
                    ).first()
                elif metric == 'mape':
                    model = session.query(ModelRegistry).order_by(
                        ModelRegistry.mape.asc()
                    ).first()
                else:
                    logger.error(f"Invalid metric: {metric}")
                    return None
                
                if model:
                    logger.info(f"Best model by {metric}: {model.model_version}")
                    return model.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"Error getting best model: {str(e)}")
            return None
    
    def compare_models(self):
        """
        Compare all models by metrics
        
        Returns:
            list: List of models sorted by RMSE
        """
        try:
            with get_db_session() as session:
                models = session.query(ModelRegistry).order_by(
                    ModelRegistry.rmse.asc()
                ).all()
                
                comparison = []
                for model in models:
                    comparison.append({
                        'model_version': model.model_version,
                        'rmse': float(model.rmse) if model.rmse else None,
                        'mae': float(model.mae) if model.mae else None,
                        'mape': float(model.mape) if model.mape else None,
                        'training_samples': model.training_samples,
                        'created_at': str(model.created_at)
                    })
                
                return comparison
                
        except Exception as e:
            logger.error(f"Error comparing models: {str(e)}")
            return []
    
    def delete_model(self, model_version):
        """
        Delete a model from registry (use with caution!)
        
        Args:
            model_version: Version to delete
        
        Returns:
            bool: Success status
        """
        try:
            with get_db_session() as session:
                model = session.query(ModelRegistry).filter_by(
                    model_version=model_version
                ).first()
                
                if model:
                    session.delete(model)
                    logger.warning(f"Deleted model {model_version} from registry")
                    return True
                else:
                    logger.error(f"Model {model_version} not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting model: {str(e)}")
            return False

# Convenience functions
def get_next_model_version():
    """Get next model version"""
    manager = ModelRegistryManager()
    return manager.get_next_version()

def get_all_models():
    """Get all models"""
    manager = ModelRegistryManager()
    return manager.get_all_models()

def get_latest_model():
    """Get latest model"""
    manager = ModelRegistryManager()
    return manager.get_latest_model()

def get_best_model(metric='rmse'):
    """Get best model by metric"""
    manager = ModelRegistryManager()
    return manager.get_best_model(metric)

def register_model(model_version, model_path, metrics, training_samples=None, data_source='combined'):
    """
    Register a new model in the registry
    
    Args:
        model_version: Model version identifier
        model_path: Path to saved model file
        metrics: Dict with rmse, mae, mape, r2
        training_samples: Number of training samples
        data_source: Source of training data (e.g., 'combined', 'file_upload', 'yahoo_finance')
    
    Returns:
        bool: Success status
    """
    try:
        with get_db_session() as session:
            new_model = ModelRegistry(
                model_version=model_version,
                model_path=model_path,
                rmse=metrics.get('rmse'),
                mae=metrics.get('mae'),
                mape=metrics.get('mape'),
                r2=metrics.get('r2'),
                training_samples=training_samples,
                data_source=data_source
            )
            session.add(new_model)
            logger.info(f"Registered model {model_version} in registry (R²: {metrics.get('r2')}, Source: {data_source})")
            return True
    except Exception as e:
        logger.error(f"Error registering model: {str(e)}")
        return False


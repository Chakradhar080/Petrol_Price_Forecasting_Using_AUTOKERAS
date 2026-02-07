"""
Model evaluation module.
Calculates RMSE, MAE, MAPE, R² and generates visualizations.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from db.database import get_db_session
from db.models import ModelRegistry
from utils.logger import setup_logger
from config import PathConfig

logger = setup_logger(__name__, 'logs/evaluation.log')

class ModelEvaluator:
    """Model evaluation and metrics calculation"""
    
    def __init__(self):
        self.reports_folder = PathConfig.REPORTS_FOLDER
    
    def calculate_rmse(self, y_true, y_pred):
        """Calculate Root Mean Squared Error"""
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    def calculate_mae(self, y_true, y_pred):
        """Calculate Mean Absolute Error"""
        return mean_absolute_error(y_true, y_pred)
    
    def calculate_mape(self, y_true, y_pred):
        """Calculate Mean Absolute Percentage Error"""
        # Avoid division by zero
        mask = y_true != 0
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    def calculate_r2(self, y_true, y_pred):
        """Calculate R² (Coefficient of Determination)"""
        return r2_score(y_true, y_pred)
    
    def calculate_all_metrics(self, y_true, y_pred):
        """
        Calculate all evaluation metrics
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            dict: All metrics
        """
        metrics = {
            'rmse': round(self.calculate_rmse(y_true, y_pred), 4),
            'mae': round(self.calculate_mae(y_true, y_pred), 4),
            'mape': round(self.calculate_mape(y_true, y_pred), 4),
            'r2': round(self.calculate_r2(y_true, y_pred), 4)
        }
        
        logger.info(f"Metrics - RMSE: {metrics['rmse']}, MAE: {metrics['mae']}, MAPE: {metrics['mape']}%, R²: {metrics['r2']}")
        return metrics
    
    def plot_actual_vs_predicted(self, y_true, y_pred, model_version, save=True):
        """
        Plot actual vs predicted values
        
        Args:
            y_true: True values
            y_pred: Predicted values
            model_version: Model version identifier
            save: Whether to save the plot
        
        Returns:
            str: Path to saved plot (if save=True)
        """
        try:
            plt.figure(figsize=(12, 6))
            
            # Plot actual vs predicted
            plt.plot(y_true, label='Actual', marker='o', markersize=3, alpha=0.7)
            plt.plot(y_pred, label='Predicted', marker='x', markersize=3, alpha=0.7)
            
            plt.title(f'Actual vs Predicted Petrol Prices - {model_version}')
            plt.xlabel('Sample Index')
            plt.ylabel('Petrol Price (₹)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if save:
                plot_path = self.reports_folder / f'actual_vs_predicted_{model_version}.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                logger.info(f"Plot saved to {plot_path}")
                plt.close()
                return str(plot_path)
            else:
                plt.show()
                return None
                
        except Exception as e:
            logger.error(f"Error creating plot: {str(e)}")
            return None
    
    def plot_error_distribution(self, y_true, y_pred, model_version, save=True):
        """
        Plot error distribution
        
        Args:
            y_true: True values
            y_pred: Predicted values
            model_version: Model version identifier
            save: Whether to save the plot
        
        Returns:
            str: Path to saved plot (if save=True)
        """
        try:
            errors = y_true - y_pred
            
            plt.figure(figsize=(10, 6))
            
            # Histogram
            plt.subplot(1, 2, 1)
            plt.hist(errors, bins=30, edgecolor='black', alpha=0.7)
            plt.title('Error Distribution')
            plt.xlabel('Prediction Error (₹)')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            
            # Box plot
            plt.subplot(1, 2, 2)
            plt.boxplot(errors, vert=True)
            plt.title('Error Box Plot')
            plt.ylabel('Prediction Error (₹)')
            plt.grid(True, alpha=0.3)
            
            plt.suptitle(f'Error Analysis - {model_version}')
            plt.tight_layout()
            
            if save:
                plot_path = self.reports_folder / f'error_distribution_{model_version}.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                logger.info(f"Error plot saved to {plot_path}")
                plt.close()
                return str(plot_path)
            else:
                plt.show()
                return None
                
        except Exception as e:
            logger.error(f"Error creating error plot: {str(e)}")
            return None
    
    def save_metrics_to_database(self, model_version, metrics, model_path, training_samples):
        """
        Save model metrics to database
        
        Args:
            model_version: Model version identifier
            metrics: Dictionary of metrics
            model_path: Path to saved model
            training_samples: Number of training samples
        
        Returns:
            bool: Success status
        """
        try:
            with get_db_session() as session:
                # Check if version already exists
                existing = session.query(ModelRegistry).filter_by(model_version=model_version).first()
                
                if existing:
                    # Update existing record
                    existing.rmse = metrics['rmse']
                    existing.mae = metrics['mae']
                    existing.mape = metrics['mape']
                    existing.r2 = metrics['r2']  # FIXED: Was missing
                    existing.model_path = model_path
                    existing.training_samples = training_samples
                    logger.info(f"Updated metrics for {model_version}")
                else:
                    # Insert new record
                    new_record = ModelRegistry(
                        model_version=model_version,
                        rmse=metrics['rmse'],
                        mae=metrics['mae'],
                        mape=metrics['mape'],
                        r2=metrics['r2'],  # FIXED: Was missing
                        model_path=model_path,
                        training_samples=training_samples
                    )
                    session.add(new_record)
                    logger.info(f"Saved metrics for {model_version}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving metrics to database: {str(e)}")
            return False
    
    def evaluate_and_save(self, y_true, y_pred, model_version, model_path, training_samples):
        """
        Complete evaluation pipeline
        
        Args:
            y_true: True values
            y_pred: Predicted values
            model_version: Model version identifier
            model_path: Path to saved model
            training_samples: Number of training samples
        
        Returns:
            dict: Evaluation results
        """
        try:
            # Calculate metrics
            metrics = self.calculate_all_metrics(y_true, y_pred)
            
            # Create visualizations
            actual_vs_pred_plot = self.plot_actual_vs_predicted(y_true, y_pred, model_version)
            error_plot = self.plot_error_distribution(y_true, y_pred, model_version)
            
            # Save to database
            db_success = self.save_metrics_to_database(
                model_version,
                metrics,
                model_path,
                training_samples
            )
            
            return {
                'success': True,
                'metrics': metrics,
                'plots': {
                    'actual_vs_predicted': actual_vs_pred_plot,
                    'error_distribution': error_plot
                },
                'database_saved': db_success
            }
            
        except Exception as e:
            logger.error(f"Error in evaluate_and_save: {str(e)}")
            return {'success': False, 'error': str(e)}

# Convenience function
def evaluate_model(y_true, y_pred, model_version, model_path, training_samples):
    """Evaluate model and save metrics"""
    evaluator = ModelEvaluator()
    return evaluator.evaluate_and_save(y_true, y_pred, model_version, model_path, training_samples)

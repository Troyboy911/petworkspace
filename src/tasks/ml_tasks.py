"""
Celery tasks for machine learning operations
"""

from celery import shared_task
from src.ml.ml_optimizer import MLOptimizer
from config.config import Config
from src.models import create_database, create_session

@shared_task(name='tasks.train_models')
def train_models(model_type='all'):
    """
    Task to train machine learning models
    
    Args:
        model_type: Type of model to train ('roi_prediction', 'trend_forecasting', 'all')
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        ml_optimizer = MLOptimizer(config)
        results = {}
        
        # Train ROI prediction model
        if model_type in ['roi_prediction', 'all']:
            roi_result = ml_optimizer.train_roi_prediction_model(session)
            results['roi_prediction'] = roi_result
        
        # Train trend forecasting model
        if model_type in ['trend_forecasting', 'all']:
            trend_result = ml_optimizer.train_trend_forecasting_model(session)
            results['trend_forecasting'] = trend_result
        
        # Generate trend forecasts
        if model_type in ['trend_forecasting', 'all']:
            forecasts = ml_optimizer.forecast_trending_keywords(days_ahead=7)
            results['forecasts'] = {
                'count': len(forecasts),
                'top_keywords': [f['keyword'] for f in forecasts[:5]] if forecasts else []
            }
        
        return {
            'status': 'success',
            'results': results
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()
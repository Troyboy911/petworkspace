"""
Celery application for background tasks
"""

from celery import Celery
from config.config import Config

# Initialize Celery app
celery_app = Celery('pet_automation',
                  broker=Config.CELERY_BROKER_URL,
                  backend=Config.CELERY_RESULT_BACKEND)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
)

# Import tasks to register them
from src.tasks import trend_tasks, content_tasks, social_tasks, affiliate_tasks, dropshipping_tasks, ml_tasks

# Register tasks
celery_app.tasks.register(trend_tasks.scrape_trends)
celery_app.tasks.register(content_tasks.generate_content)
celery_app.tasks.register(social_tasks.post_content)
celery_app.tasks.register(affiliate_tasks.generate_affiliate_links)
celery_app.tasks.register(affiliate_tasks.track_commissions)
celery_app.tasks.register(dropshipping_tasks.process_orders)
celery_app.tasks.register(dropshipping_tasks.update_inventory)
celery_app.tasks.register(ml_tasks.train_models)
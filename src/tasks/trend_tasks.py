"""
Celery tasks for trend scraping
"""

from celery import shared_task
from src.scrapers.trend_scraper import TrendScraper
from config.config import Config
from src.models import create_database, create_session

@shared_task(name='tasks.scrape_trends')
def scrape_trends():
    """
    Task to scrape trends from various platforms
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        scraper = TrendScraper(config)
        trends = scraper.run_full_trend_analysis(session)
        
        return {
            'status': 'success',
            'trends_count': len(trends),
            'platforms': list(set([t.get('platform') for t in trends]))
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()
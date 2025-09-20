import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///pet_automation.db')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    MONGODB_URL = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017/pet_automation')
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Social Media APIs
    TWITTER_CONFIG = {
        'api_key': os.environ.get('TWITTER_API_KEY'),
        'api_secret': os.environ.get('TWITTER_API_SECRET'),
        'access_token': os.environ.get('TWITTER_ACCESS_TOKEN'),
        'access_secret': os.environ.get('TWITTER_ACCESS_SECRET')
    }
    
    REDDIT_CONFIG = {
        'client_id': os.environ.get('REDDIT_CLIENT_ID'),
        'client_secret': os.environ.get('REDDIT_CLIENT_SECRET'),
        'user_agent': os.environ.get('REDDIT_USER_AGENT', 'pet_automation_bot')
    }
    
    INSTAGRAM_CONFIG = {
        'username': os.environ.get('INSTAGRAM_USERNAME'),
        'password': os.environ.get('INSTAGRAM_PASSWORD')
    }
    
    TIKTOK_CONFIG = {
        'api_key': os.environ.get('TIKTOK_API_KEY')
    }
    
    # E-commerce APIs
    SHOPIFY_CONFIG = {
        'api_key': os.environ.get('SHOPIFY_API_KEY'),
        'password': os.environ.get('SHOPIFY_PASSWORD'),
        'store_url': os.environ.get('SHOPIFY_STORE_URL')
    }
    
    AMAZON_CONFIG = {
        'associate_id': os.environ.get('AMAZON_ASSOCIATE_ID'),
        'access_key': os.environ.get('AMAZON_ACCESS_KEY'),
        'secret_key': os.environ.get('AMAZON_SECRET_KEY')
    }
    
    CLICKBANK_CONFIG = {
        'api_key': os.environ.get('CLICKBANK_API_KEY')
    }
    
    ALIEXPRESS_CONFIG = {
        'api_key': os.environ.get('ALIEXPRESS_API_KEY')
    }
    
    # Security Configuration
    PROXY_ROTATION_ENABLED = os.environ.get('PROXY_ROTATION_ENABLED', 'true').lower() == 'true'
    CAPTCHA_SERVICE = os.environ.get('CAPTCHA_SERVICE', '2captcha')
    CAPTCHA_API_KEY = os.environ.get('CAPTCHA_API_KEY')
    USER_AGENT_ROTATION = os.environ.get('USER_AGENT_ROTATION', 'true').lower() == 'true'
    REQUEST_DELAY_MIN = int(os.environ.get('REQUEST_DELAY_MIN', 2))
    REQUEST_DELAY_MAX = int(os.environ.get('REQUEST_DELAY_MAX', 5))
    
    # Scaling Configuration
    MAX_POSTS_PER_DAY = int(os.environ.get('MAX_POSTS_PER_DAY', 1000))
    MAX_ACCOUNTS_PER_PLATFORM = int(os.environ.get('MAX_ACCOUNTS_PER_PLATFORM', 50))
    WORKER_PROCESSES = int(os.environ.get('WORKER_PROCESSES', 4))
    THREAD_POOL_SIZE = int(os.environ.get('THREAD_POOL_SIZE', 20))
    
    # Monetization Targets
    TARGET_MONTHLY_REVENUE = float(os.environ.get('TARGET_MONTHLY_REVENUE', 10000))
    MIN_PROFIT_MARGIN = float(os.environ.get('MIN_PROFIT_MARGIN', 5.0))
    MAX_AD_SPEND_PERCENT = float(os.environ.get('MAX_AD_SPEND_PERCENT', 20))
    
    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Pet Supplies Keywords and Niches
    PET_KEYWORDS = [
        'dog toys', 'cat toys', 'pet supplies', 'dog food', 'cat food',
        'pet grooming', 'dog training', 'cat training', 'pet health',
        'dog accessories', 'cat accessories', 'pet beds', 'pet carriers',
        'dog treats', 'cat treats', 'pet vitamins', 'dog clothes',
        'cat litter', 'pet toys', 'dog leash', 'cat collar'
    ]
    
    PET_NICHES = [
        'organic pet food', 'smart pet devices', 'luxury pet accessories',
        'pet health supplements', 'eco-friendly pet products',
        'pet training tools', 'pet travel accessories', 'senior pet care',
        'puppy training supplies', 'kitten care products'
    ]
    
    # Content Templates
    CONTENT_TEMPLATES = {
        'viral_post': [
            "🔥 {pet_owners} are going CRAZY over this {product}! ",
            "Your {pet_type} will thank you for this {product} 🐕",
            "I couldn't believe what happened when I gave my {pet_type} this {product}..."
        ],
        'product_description': [
            "Give your {pet_type} the {benefit} they deserve with our {product}. ",
            "Transform your {pet_type}'s {aspect} with this amazing {product}. "
        ],
        'email_campaign': [
            "Subject: Your {pet_type} needs this {product} 🐾\n\nHi {name},",
            "Don't let your {pet_type} miss out on {benefit}..."
        ]
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
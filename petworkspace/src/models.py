from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Trend(Base):
    __tablename__ = 'trends'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=False)  # twitter, reddit, google
    volume = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)
    sentiment_score = Column(Float, default=0.0)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0.0)
    cost_price = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    affiliate_link = Column(String(1000))
    product_url = Column(String(1000))
    image_url = Column(String(1000))
    category = Column(String(200))
    tags = Column(JSON)
    supplier = Column(String(200))
    platform = Column(String(100))  # amazon, clickbank, aliexpress
    commission_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SocialMediaAccount(Base):
    __tablename__ = 'social_media_accounts'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # twitter, reddit, instagram, tiktok
    username = Column(String(100), nullable=False)
    password = Column(String(200))
    api_key = Column(String(500))
    api_secret = Column(String(500))
    access_token = Column(String(500))
    is_active = Column(Boolean, default=True)
    posts_today = Column(Integer, default=0)
    last_post_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Content(Base):
    __tablename__ = 'content'
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50), nullable=False)  # post, email, description
    platform = Column(String(50))  # twitter, reddit, instagram, tiktok
    title = Column(String(500))
    content = Column(Text, nullable=False)
    hashtags = Column(JSON)
    image_url = Column(String(1000))
    product_id = Column(Integer, ForeignKey('products.id'))
    trend_id = Column(Integer, ForeignKey('trends.id'))
    is_posted = Column(Boolean, default=False)
    posting_time = Column(DateTime)
    engagement_score = Column(Float, default=0.0)
    performance_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", backref="content")
    trend = relationship("Trend", backref="content")

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('content.id'))
    account_id = Column(Integer, ForeignKey('social_media_accounts.id'))
    platform_post_id = Column(String(200))
    post_url = Column(String(1000))
    status = Column(String(50), default='pending')  # pending, posted, failed
    posted_at = Column(DateTime)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    content = relationship("Content", backref="posts")
    account = relationship("SocialMediaAccount", backref="posts")

class AffiliateLink(Base):
    __tablename__ = 'affiliate_links'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    platform = Column(String(100), nullable=False)  # amazon, clickbank, shopee
    affiliate_url = Column(String(1000), nullable=False)
    original_url = Column(String(1000))
    commission_rate = Column(Float, default=0.0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", backref="affiliate_links")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(100), unique=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_address = Column(Text)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, default=0.0)
    cost_price = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    status = Column(String(50), default='pending')  # pending, processing, shipped, delivered
    supplier_order_id = Column(String(100))
    tracking_number = Column(String(200))
    order_date = Column(DateTime, default=datetime.utcnow)
    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)
    
    product = relationship("Product", backref="orders")

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    platform = Column(String(50))  # overall, twitter, reddit, instagram, tiktok
    metric_type = Column(String(100), nullable=False)  # revenue, clicks, conversions, engagement
    value = Column(Float, default=0.0)
    category = Column(String(100))  # pet_supplies, dog_toys, cat_food, etc.
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ABTest(Base):
    __tablename__ = 'ab_tests'
    
    id = Column(Integer, primary_key=True)
    test_name = Column(String(200), nullable=False)
    variant_a = Column(JSON, nullable=False)
    variant_b = Column(JSON, nullable=False)
    platform = Column(String(50), nullable=False)
    metric = Column(String(100), nullable=False)  # clicks, conversions, engagement
    results = Column(JSON)
    winner = Column(String(10))  # A, B, or tie
    confidence_level = Column(Float, default=0.0)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

class MLModel(Base):
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(200), nullable=False)
    model_type = Column(String(100), nullable=False)  # roi_prediction, trend_forecasting, etc.
    accuracy = Column(Float, default=0.0)
    parameters = Column(JSON)
    training_data_size = Column(Integer, default=0)
    last_trained = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    performance_metrics = Column(JSON)

# Database setup function
def create_database(engine_url):
    engine = create_engine(engine_url)
    Base.metadata.create_all(engine)
    return engine

# Session factory
def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
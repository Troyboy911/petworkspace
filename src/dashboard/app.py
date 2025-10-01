from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import json
import logging
from config.config import Config
from src.models import db, Product, Order, Analytics, Trend, SocialMediaAccount, Content, Post
from src.ml.ml_optimizer import MLOptimizer, AnalyticsEngine
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ML components
ml_optimizer = MLOptimizer(Config())
analytics_engine = AnalyticsEngine(Config())

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Get key metrics
        metrics = get_dashboard_metrics()
        
        # Get recent activity
        recent_activity = get_recent_activity()
        
        # Get performance charts data
        charts_data = get_charts_data()
        
        return render_template('dashboard.html', 
                             metrics=metrics, 
                             recent_activity=recent_activity,
                             charts_data=charts_data)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for dashboard metrics"""
    try:
        metrics = get_dashboard_metrics()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"API metrics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/revenue')
def api_revenue():
    """API endpoint for revenue data"""
    try:
        # Get revenue data for charts
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        revenue_data = db.session.query(
            Analytics.date,
            Analytics.value
        ).filter(
            Analytics.metric_type == 'revenue',
            Analytics.date >= start_date,
            Analytics.date <= end_date
        ).order_by(Analytics.date).all()
        
        data = [{
            'date': item.date.strftime('%Y-%m-%d'),
            'revenue': float(item.value)
        } for item in revenue_data]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"API revenue error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products')
def api_products():
    """API endpoint for products data"""
    try:
        products = db.session.query(Product).filter_by(is_active=True).all()
        
        products_data = [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'cost_price': p.cost_price,
            'profit_margin': p.profit_margin,
            'category': p.category,
            'commission_rate': p.commission_rate,
            'is_active': p.is_active,
            'created_at': p.created_at.strftime('%Y-%m-%d')
        } for p in products]
        
        return jsonify(products_data)
    except Exception as e:
        logger.error(f"API products error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders')
def api_orders():
    """API endpoint for orders data"""
    try:
        orders = db.session.query(Order).order_by(Order.order_date.desc()).limit(100).all()
        
        orders_data = [{
            'id': o.id,
            'order_id': o.order_id,
            'product_name': o.product.name if o.product else 'Unknown',
            'customer_name': o.customer_name,
            'total_price': o.total_price,
            'profit': o.profit,
            'status': o.status,
            'order_date': o.order_date.strftime('%Y-%m-%d %H:%M:%S')
        } for o in orders]
        
        return jsonify(orders_data)
    except Exception as e:
        logger.error(f"API orders error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social-media')
def api_social_media():
    """API endpoint for social media metrics"""
    try:
        # Get social media accounts
        accounts = db.session.query(SocialMediaAccount).filter_by(is_active=True).all()
        
        social_data = []
        for account in accounts:
            # Get recent posts
            recent_posts = db.session.query(Post).filter_by(
                account_id=account.id
            ).order_by(Post.posted_at.desc()).limit(10).all()
            
            total_engagement = sum(
                (post.likes + post.comments + post.shares) 
                for post in recent_posts if post.posted_at
            )
            
            avg_engagement = total_engagement / len(recent_posts) if recent_posts else 0
            
            social_data.append({
                'platform': account.platform,
                'username': account.username,
                'posts_today': account.posts_today,
                'total_engagement': total_engagement,
                'avg_engagement': avg_engagement,
                'last_post_time': account.last_post_time.strftime('%Y-%m-%d %H:%M:%S') if account.last_post_time else None
            })
        
        return jsonify(social_data)
    except Exception as e:
        logger.error(f"API social media error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trends')
def api_trends():
    """API endpoint for trending keywords"""
    try:
        # Get recent trends
        trends = db.session.query(Trend).filter(
            Trend.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(Trend.growth_rate.desc()).limit(20).all()
        
        trends_data = [{
            'keyword': t.keyword,
            'platform': t.platform,
            'volume': t.volume,
            'growth_rate': t.growth_rate,
            'sentiment_score': t.sentiment_score,
            'category': t.category,
            'created_at': t.created_at.strftime('%Y-%m-%d')
        } for t in trends]
        
        return jsonify(trends_data)
    except Exception as e:
        logger.error(f"API trends error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/products')
def products_page():
    """Products management page"""
    try:
        products = db.session.query(Product).filter_by(is_active=True).all()
        return render_template('products.html', products=products)
    except Exception as e:
        logger.error(f"Products page error: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/orders')
def orders_page():
    """Orders management page"""
    try:
        orders = db.session.query(Order).order_by(Order.order_date.desc()).limit(100).all()
        return render_template('orders.html', orders=orders)
    except Exception as e:
        logger.error(f"Orders page error: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/analytics')
def analytics_page():
    """Analytics and insights page"""
    try:
        # Get analytics data
        analytics_data = get_analytics_data()
        
        # Generate ML insights
        ml_insights = generate_ml_insights()
        
        return render_template('analytics.html', 
                             analytics_data=analytics_data,
                             ml_insights=ml_insights)
    except Exception as e:
        logger.error(f"Analytics page error: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/social-media')
def social_media_page():
    """Social media management page"""
    try:
        accounts = db.session.query(SocialMediaAccount).filter_by(is_active=True).all()
        recent_posts = db.session.query(Post).order_by(Post.posted_at.desc()).limit(50).all()
        
        return render_template('social_media.html', 
                             accounts=accounts, 
                             recent_posts=recent_posts)
    except Exception as e:
        logger.error(f"Social media page error: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/settings')
def settings_page():
    """Settings and configuration page"""
    try:
        config_data = {
            'max_posts_per_day': Config.MAX_POSTS_PER_DAY,
            'target_monthly_revenue': Config.TARGET_MONTHLY_REVENUE,
            'min_profit_margin': Config.MIN_PROFIT_MARGIN,
            'max_ad_spend_percent': Config.MAX_AD_SPEND_PERCENT,
            'proxy_rotation_enabled': Config.PROXY_ROTATION_ENABLED,
            'user_agent_rotation': Config.USER_AGENT_ROTATION
        }
        
        return render_template('settings.html', config=config_data)
    except Exception as e:
        logger.error(f"Settings page error: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/train-ml-model', methods=['POST'])
def train_ml_model():
    """API endpoint to train ML models"""
    try:
        model_type = request.json.get('model_type', 'roi_prediction')
        
        if model_type == 'roi_prediction':
            result = ml_optimizer.train_roi_prediction_model(db.session)
        elif model_type == 'trend_forecasting':
            result = ml_optimizer.train_trend_forecasting_model(db.session)
        else:
            return jsonify({'success': False, 'error': 'Unknown model type'})
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"ML model training error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predict-roi', methods=['POST'])
def predict_roi():
    """API endpoint to predict ROI for products"""
    try:
        product_data = request.json.get('product_data')
        
        prediction = ml_optimizer.predict_product_roi(product_data)
        
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"ROI prediction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/forecast-trends', methods=['GET'])
def forecast_trends():
    """API endpoint to forecast trending keywords"""
    try:
        days_ahead = request.args.get('days', 7, type=int)
        
        forecasts = ml_optimizer.forecast_trending_keywords(days_ahead)
        
        return jsonify(forecasts)
    except Exception as e:
        logger.error(f"Trend forecasting error: {e}")
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_dashboard_metrics():
    """Get key dashboard metrics"""
    try:
        # Revenue metrics
        total_revenue = db.session.query(db.func.sum(Analytics.value)).filter(
            Analytics.metric_type == 'revenue',
            Analytics.date >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        # Order metrics
        total_orders = db.session.query(Order).filter(
            Order.order_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Profit metrics
        total_profit = db.session.query(db.func.sum(Order.profit)).filter(
            Order.order_date >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        # Social media metrics
        total_posts = db.session.query(Post).filter(
            Post.posted_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        total_engagement = db.session.query(db.func.sum(Post.likes + Post.comments + Post.shares)).filter(
            Post.posted_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        # Product metrics
        total_products = db.session.query(Product).filter_by(is_active=True).count()
        
        # Calculate conversion rates
        conversion_rate = (total_orders / max(total_posts, 1)) * 100 if total_posts > 0 else 0
        
        return {
            'total_revenue': float(total_revenue),
            'total_profit': float(total_profit),
            'total_orders': total_orders,
            'total_posts': total_posts,
            'total_engagement': int(total_engagement),
            'total_products': total_products,
            'conversion_rate': round(conversion_rate, 2),
            'avg_profit_per_order': round(total_profit / max(total_orders, 1), 2) if total_orders > 0 else 0,
            'avg_engagement_per_post': round(total_engagement / max(total_posts, 1), 2) if total_posts > 0 else 0
        }
    except Exception as e:
        logger.error(f"Dashboard metrics error: {e}")
        return {}

def get_recent_activity():
    """Get recent activity data"""
    try:
        # Recent orders
        recent_orders = db.session.query(Order).order_by(Order.order_date.desc()).limit(5).all()
        
        # Recent posts
        recent_posts = db.session.query(Post).order_by(Post.posted_at.desc()).limit(5).all()
        
        # Recent trends
        recent_trends = db.session.query(Trend).order_by(Trend.created_at.desc()).limit(5).all()
        
        activity = {
            'orders': [{
                'id': o.id,
                'product_name': o.product.name if o.product else 'Unknown',
                'profit': o.profit,
                'date': o.order_date.strftime('%Y-%m-%d %H:%M:%S')
            } for o in recent_orders],
            'posts': [{
                'id': p.id,
                'platform': p.content.platform if p.content else 'Unknown',
                'engagement': p.likes + p.comments + p.shares,
                'date': p.posted_at.strftime('%Y-%m-%d %H:%M:%S') if p.posted_at else None
            } for p in recent_posts],
            'trends': [{
                'keyword': t.keyword,
                'growth_rate': t.growth_rate,
                'platform': t.platform,
                'date': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for t in recent_trends]
        }
        
        return activity
    except Exception as e:
        logger.error(f"Recent activity error: {e}")
        return {}

def get_charts_data():
    """Get data for charts"""
    try:
        # Revenue chart data (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        revenue_data = db.session.query(
            Analytics.date,
            db.func.sum(Analytics.value).label('revenue')
        ).filter(
            Analytics.metric_type == 'revenue',
            Analytics.date >= start_date,
            Analytics.date <= end_date
        ).group_by(Analytics.date).order_by(Analytics.date).all()
        
        # Engagement chart data
        engagement_data = db.session.query(
            Post.platform,
            db.func.avg(Post.likes + Post.comments + Post.shares).label('avg_engagement')
        ).filter(
            Post.posted_at >= start_date
        ).group_by(Post.platform).all()
        
        # Product performance data
        product_performance = db.session.query(
            Product.category,
            db.func.sum(Order.profit).label('total_profit')
        ).join(Order).filter(
            Order.order_date >= start_date
        ).group_by(Product.category).all()
        
        charts_data = {
            'revenue_timeline': [{
                'date': item.date.strftime('%Y-%m-%d'),
                'revenue': float(item.revenue)
            } for item in revenue_data],
            'engagement_by_platform': [{
                'platform': item.platform,
                'engagement': float(item.avg_engagement or 0)
            } for item in engagement_data],
            'profit_by_category': [{
                'category': item.category,
                'profit': float(item.total_profit or 0)
            } for item in product_performance]
        }
        
        return charts_data
    except Exception as e:
        logger.error(f"Charts data error: {e}")
        return {}

def get_analytics_data():
    """Get comprehensive analytics data"""
    try:
        # Get data for the last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Revenue analytics
        revenue_by_day = db.session.query(
            db.func.date(Analytics.date).label('date'),
            db.func.sum(Analytics.value).label('revenue')
        ).filter(
            Analytics.metric_type == 'revenue',
            Analytics.date >= start_date
        ).group_by(db.func.date(Analytics.date)).all()
        
        # Platform performance
        platform_performance = db.session.query(
            Analytics.platform,
            db.func.sum(Analytics.value).label('total_value')
        ).filter(
            Analytics.metric_type.in_(['revenue', 'engagement']),
            Analytics.date >= start_date
        ).group_by(Analytics.platform).all()
        
        # Category performance
        category_performance = db.session.query(
            Product.category,
            db.func.sum(Order.profit).label('total_profit'),
            db.func.count(Order.id).label('order_count')
        ).join(Order).filter(
            Order.order_date >= start_date
        ).group_by(Product.category).all()
        
        analytics_data = {
            'revenue_by_day': [{
                'date': str(item.date),
                'revenue': float(item.revenue)
            } for item in revenue_by_day],
            'platform_performance': [{
                'platform': item.platform,
                'total_value': float(item.total_value)
            } for item in platform_performance],
            'category_performance': [{
                'category': item.category,
                'total_profit': float(item.total_profit),
                'order_count': item.order_count
            } for item in category_performance]
        }
        
        return analytics_data
    except Exception as e:
        logger.error(f"Analytics data error: {e}")
        return {}

def generate_ml_insights():
    """Generate ML-powered insights"""
    try:
        # Get recent analytics data
        analytics_data = get_analytics_data()
        
        # Convert to format for ML analysis
        performance_data = []
        
        for item in analytics_data.get('category_performance', []):
            performance_data.append({
                'category': item['category'],
                'revenue': item['total_profit'],
                'order_count': item['order_count'],
                'engagement_rate': random.uniform(0.02, 0.08),  # Simulated
                'content_length': random.randint(100, 300),  # Simulated
                'content_type': random.choice(['post', 'video', 'image']),
                'posting_time': random.choice([9, 12, 15, 18, 21]),  # Simulated
                'hashtags': ['#pet', '#pets', '#petcare']  # Simulated
            })
        
        # Generate insights using ML
        insights = analytics_engine.generate_performance_insights(performance_data)
        
        return insights
    except Exception as e:
        logger.error(f"ML insights generation error: {e}")
        return {}

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        return render_template('health.html', 
                             environment=app.config['FLASK_ENV'],
                             timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
#!/usr/bin/env python3
"""
Pet Automation Suite - Main Orchestrator
This is the main entry point that coordinates all automation services
"""

import logging
import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, List
from config.config import Config
from src.models import create_database, create_session, Product, Trend, Content, Post, Order
from src.scrapers.trend_scraper import TrendScraper
from src.ai.content_generator import AIContentGenerator
from src.social.auto_poster import SocialMediaAutoPoster
from src.affiliate.affiliate_manager import AffiliateManager
from src.dropshipping.dropshipping_manager import DropshippingManager
from src.ml.ml_optimizer import MLOptimizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PetAutomationSuite:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.trend_scraper = TrendScraper(config)
        self.content_generator = AIContentGenerator(config)
        self.social_poster = SocialMediaAutoPoster(config)
        self.affiliate_manager = AffiliateManager(config)
        self.dropshipping_manager = DropshippingManager(config)
        self.ml_optimizer = MLOptimizer(config)
        
        # Database session
        self.engine = create_database(config.DATABASE_URL)
        self.session = create_session(self.engine)
        
        # State tracking
        self.is_running = False
        self.services = {}
        
    def start_services(self):
        """Start all automation services"""
        self.logger.info("Starting Pet Automation Suite services...")
        
        try:
            # Start trend scraping service
            self.start_trend_service()
            
            # Start content generation service
            self.start_content_service()
            
            # Start social media service
            self.start_social_service()
            
            # Start affiliate service
            self.start_affiliate_service()
            
            # Start dropshipping service
            self.start_dropshipping_service()
            
            # Start ML optimization service
            self.start_ml_service()
            
            self.is_running = True
            self.logger.info("All services started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start services: {e}")
            raise
    
    def start_trend_service(self):
        """Start trend scraping service"""
        self.logger.info("Starting trend scraping service...")
        
        def trend_job():
            try:
                self.logger.info("Running trend analysis...")
                trends = self.trend_scraper.run_full_trend_analysis(self.session)
                
                # Get trending keywords
                trending_keywords = self.trend_scraper.get_trending_keywords(self.session)
                
                self.logger.info(f"Found {len(trends)} trends, {len(trending_keywords)} trending keywords")
                
            except Exception as e:
                self.logger.error(f"Trend analysis failed: {e}")
        
        # Schedule trend analysis every 2 hours
        schedule.every(2).hours.do(trend_job)
        
        # Run immediately
        trend_job()
        
        self.services['trend'] = True
        self.logger.info("Trend service started")
    
    def start_content_service(self):
        """Start content generation service"""
        self.logger.info("Starting content generation service...")
        
        def content_job():
            try:
                self.logger.info("Generating content...")
                
                # Get trending products
                trending_products = self.session.query(Product).filter_by(is_active=True).all()
                
                if not trending_products:
                    self.logger.warning("No active products found for content generation")
                    return
                
                # Generate content for each product
                for product in trending_products[:10]:  # Limit to 10 products
                    try:
                        # Generate viral post
                        viral_content = self.content_generator.generate_viral_post(
                            product=product,
                            platform='twitter'
                        )
                        
                        # Save content to database
                        content = Content(
                            content_type='viral_post',
                            platform='twitter',
                            content=viral_content['content'],
                            hashtags=viral_content['hashtags'],
                            product_id=product.id
                        )
                        self.session.add(content)
                        
                        self.logger.info(f"Generated content for product: {product.name}")
                        
                    except Exception as e:
                        self.logger.error(f"Content generation failed for product {product.name}: {e}")
                        continue
                
                self.session.commit()
                self.logger.info(f"Generated content for {len(trending_products)} products")
                
            except Exception as e:
                self.logger.error(f"Content generation job failed: {e}")
                self.session.rollback()
        
        # Schedule content generation every 4 hours
        schedule.every(4).hours.do(content_job)
        
        # Run immediately
        content_job()
        
        self.services['content'] = True
        self.logger.info("Content service started")
    
    def start_social_service(self):
        """Start social media posting service"""
        self.logger.info("Starting social media service...")
        
        def social_job():
            try:
                self.logger.info("Executing social media posting...")
                
                # Get pending content
                pending_content = self.session.query(Content).filter_by(
                    is_posted=False
                ).limit(20).all()
                
                if not pending_content:
                    self.logger.info("No pending content to post")
                    return
                
                # Post content
                posted_count = 0
                
                for content in pending_content:
                    try:
                        # Get available accounts
                        accounts = self.session.query(SocialMediaAccount).filter_by(
                            platform=content.platform,
                            is_active=True
                        ).all()
                        
                        if not accounts:
                            self.logger.warning(f"No active accounts for platform: {content.platform}")
                            continue
                        
                        # Select account (rotate for variety)
                        account = accounts[posted_count % len(accounts)]
                        
                        # Post content
                        result = self.social_poster.post_to_platform(content, account)
                        
                        if result:
                            # Update content status
                            content.is_posted = True
                            content.posting_time = datetime.utcnow()
                            
                            # Create post record
                            post = Post(
                                content_id=content.id,
                                account_id=account.id,
                                platform_post_id=result.get('platform_post_id'),
                                post_url=result.get('post_url'),
                                status=result['status'],
                                posted_at=result['posted_at']
                            )
                            self.session.add(post)
                            
                            posted_count += 1
                            self.logger.info(f"Posted content to {content.platform}")
                        
                    except Exception as e:
                        self.logger.error(f"Social posting failed for content {content.id}: {e}")
                        continue
                
                self.session.commit()
                self.logger.info(f"Posted {posted_count} pieces of content")
                
            except Exception as e:
                self.logger.error(f"Social media job failed: {e}")
                self.session.rollback()
        
        # Schedule social posting every hour
        schedule.every().hour.do(social_job)
        
        # Run immediately
        social_job()
        
        self.services['social'] = True
        self.logger.info("Social media service started")
    
    def start_affiliate_service(self):
        """Start affiliate link management service"""
        self.logger.info("Starting affiliate service...")
        
        def affiliate_job():
            try:
                self.logger.info("Running affiliate link management...")
                
                # Get products without affiliate links
                products_without_links = self.session.query(Product).filter(
                    Product.affiliate_links == None
                ).limit(20).all()
                
                if products_without_links:
                    # Generate affiliate links
                    for product in products_without_links:
                        try:
                            if product.platform == 'amazon':
                                affiliate_link = self.affiliate_manager.generate_amazon_affiliate_link(
                                    product.product_url
                                )
                            elif product.platform == 'clickbank':
                                affiliate_link = self.affiliate_manager.generate_clickbank_affiliate_link(
                                    product.product_url
                                )
                            else:
                                continue
                            
                            if affiliate_link:
                                # Save affiliate link
                                from src.models import AffiliateLink
                                link = AffiliateLink(
                                    product_id=product.id,
                                    platform=product.platform,
                                    affiliate_url=affiliate_link,
                                    original_url=product.product_url,
                                    commission_rate=product.commission_rate
                                )
                                self.session.add(link)
                                
                                self.logger.info(f"Generated affiliate link for {product.name}")
                        
                        except Exception as e:
                            self.logger.error(f"Affiliate link generation failed for {product.name}: {e}")
                            continue
                    
                    self.session.commit()
                
                # Track commissions
                commission_data = self.affiliate_manager.track_commissions(self.session)
                
                self.logger.info(f"Affiliate service completed. Total commissions: ${commission_data.get('total_commissions', 0)}")
                
            except Exception as e:
                self.logger.error(f"Affiliate service job failed: {e}")
                self.session.rollback()
        
        # Schedule affiliate management every 3 hours
        schedule.every(3).hours.do(affiliate_job)
        
        # Run immediately
        affiliate_job()
        
        self.services['affiliate'] = True
        self.logger.info("Affiliate service started")
    
    def start_dropshipping_service(self):
        """Start dropshipping automation service"""
        self.logger.info("Starting dropshipping service...")
        
        def dropshipping_job():
            try:
                self.logger.info("Running dropshipping automation...")
                
                # Monitor inventory levels
                inventory_alerts = self.dropshipping_manager.monitor_inventory_levels(self.session)
                
                if inventory_alerts:
                    self.logger.warning(f"Found {len(inventory_alerts)} inventory alerts")
                    for alert in inventory_alerts:
                        self.logger.info(f"Low inventory: {alert['product_name']} - {alert['current_stock']} units remaining")
                
                # Process pending orders
                pending_orders = self.session.query(Order).filter_by(
                    status='pending'
                ).limit(10).all()
                
                if pending_orders:
                    for order in pending_orders:
                        try:
                            success = self.dropshipping_manager.auto_fulfill_order(order)
                            
                            if success:
                                self.logger.info(f"Order {order.order_id} fulfilled successfully")
                            else:
                                self.logger.error(f"Order fulfillment failed for {order.order_id}")
                        
                        except Exception as e:
                            self.logger.error(f"Order processing failed for {order.order_id}: {e}")
                            continue
                
                # Dynamic pricing adjustment
                pricing_updates = self.dropshipping_manager.dynamic_pricing_adjustment(self.session)
                
                if pricing_updates:
                    self.logger.info(f"Updated pricing for {len(pricing_updates)} products")
                
                self.logger.info("Dropshipping service completed")
                
            except Exception as e:
                self.logger.error(f"Dropshipping service job failed: {e}")
                self.session.rollback()
        
        # Schedule dropshipping tasks every 30 minutes
        schedule.every(30).minutes.do(dropshipping_job)
        
        # Run immediately
        dropshipping_job()
        
        self.services['dropshipping'] = True
        self.logger.info("Dropshipping service started")
    
    def start_ml_service(self):
        """Start machine learning optimization service"""
        self.logger.info("Starting ML optimization service...")
        
        def ml_job():
            try:
                self.logger.info("Running ML optimization...")
                
                # Train ROI prediction model (daily)
                roi_result = self.ml_optimizer.train_roi_prediction_model(self.session)
                
                if roi_result['success']:
                    self.logger.info(f"ROI model trained with accuracy: {roi_result['accuracy']:.2f}")
                
                # Train trend forecasting model (daily)
                trend_result = self.ml_optimizer.train_trend_forecasting_model(self.session)
                
                if trend_result['success']:
                    self.logger.info(f"Trend forecasting model trained with accuracy: {trend_result['accuracy']:.2f}")
                
                # Generate trend forecasts
                forecasts = self.ml_optimizer.forecast_trending_keywords(days_ahead=7)
                
                if forecasts:
                    self.logger.info(f"Generated {len(forecasts)} trend forecasts")
                
                self.logger.info("ML optimization completed")
                
            except Exception as e:
                self.logger.error(f"ML service job failed: {e}")
        
        # Schedule ML tasks daily at 2 AM
        schedule.every().day.at("02:00").do(ml_job)
        
        # Run immediately
        ml_job()
        
        self.services['ml'] = True
        self.logger.info("ML service started")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.logger.info("Starting scheduler loop...")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.logger.info("Scheduler interrupted by user")
                self.stop_services()
                break
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def stop_services(self):
        """Stop all services"""
        self.logger.info("Stopping Pet Automation Suite services...")
        
        self.is_running = False
        
        # Clear scheduled jobs
        schedule.clear()
        
        self.logger.info("All services stopped")
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            'running': self.is_running,
            'services': self.services,
            'uptime': datetime.utcnow().isoformat()
        }
    
    def generate_report(self) -> Dict:
        """Generate performance report"""
        try:
            # Get metrics for the last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Revenue metrics
            total_revenue = self.session.query(Analytics).filter(
                Analytics.metric_type == 'revenue',
                Analytics.date >= start_date
            ).with_entities(Analytics.value).all()
            
            total_revenue = sum(item[0] for item in total_revenue) if total_revenue else 0
            
            # Order metrics
            total_orders = self.session.query(Order).filter(
                Order.order_date >= start_date
            ).count()
            
            # Social media metrics
            total_posts = self.session.query(Post).filter(
                Post.posted_at >= start_date
            ).count()
            
            total_engagement = self.session.query(Post).filter(
                Post.posted_at >= start_date
            ).with_entities(
                (Post.likes + Post.comments + Post.shares).label('engagement')
            ).all()
            
            total_engagement = sum(item[0] for item in total_engagement) if total_engagement else 0
            
            # Product metrics
            total_products = self.session.query(Product).filter_by(is_active=True).count()
            
            report = {
                'period': f"{start_date.date()} to {end_date.date()}",
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'total_posts': total_posts,
                'total_engagement': total_engagement,
                'total_products': total_products,
                'avg_engagement_per_post': total_engagement / max(total_posts, 1),
                'conversion_rate': (total_orders / max(total_posts, 1)) * 100,
                'services_status': self.services,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return {'error': str(e)}

def main():
    """Main entry point"""
    # Initialize configuration
    config = Config()
    
    # Create automation suite
    suite = PetAutomationSuite(config)
    
    try:
        # Start services
        suite.start_services()
        
        # Run scheduler
        suite.run_scheduler()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Pet Automation Suite...")
        suite.stop_services()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        suite.stop_services()
        raise

if __name__ == "__main__":
    main()
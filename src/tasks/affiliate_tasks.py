"""
Celery tasks for affiliate link management
"""

from celery import shared_task
from src.affiliate.affiliate_manager import AffiliateManager
from config.config import Config
from src.models import create_database, create_session, Product, AffiliateLink

@shared_task(name='tasks.generate_affiliate_links')
def generate_affiliate_links(product_id=None):
    """
    Task to generate affiliate links for products
    
    Args:
        product_id: Optional specific product ID to generate links for
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        affiliate_manager = AffiliateManager(config)
        
        # Get products without affiliate links
        if product_id:
            products = session.query(Product).filter_by(id=product_id).all()
        else:
            products = session.query(Product).filter(
                Product.affiliate_link == None
            ).limit(20).all()
        
        if not products:
            return {
                'status': 'warning',
                'message': 'No products found needing affiliate links'
            }
        
        generated_links = []
        
        # Generate affiliate links for each product
        for product in products:
            try:
                if product.platform == 'amazon':
                    affiliate_link = affiliate_manager.generate_amazon_affiliate_link(
                        product.product_url
                    )
                elif product.platform == 'clickbank':
                    affiliate_link = affiliate_manager.generate_clickbank_affiliate_link(
                        product.product_url
                    )
                elif product.platform == 'shopee':
                    affiliate_link = affiliate_manager.generate_shopee_affiliate_link(
                        product.product_url
                    )
                else:
                    continue
                
                if affiliate_link:
                    # Save affiliate link
                    link = AffiliateLink(
                        product_id=product.id,
                        platform=product.platform,
                        affiliate_url=affiliate_link,
                        original_url=product.product_url,
                        commission_rate=product.commission_rate
                    )
                    session.add(link)
                    
                    # Update product with affiliate link
                    product.affiliate_link = affiliate_link
                    
                    generated_links.append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'platform': product.platform
                    })
            
            except Exception as e:
                continue
        
        session.commit()
        
        return {
            'status': 'success',
            'generated_count': len(generated_links),
            'links': generated_links
        }
        
    except Exception as e:
        session.rollback()
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()

@shared_task(name='tasks.track_commissions')
def track_commissions():
    """
    Task to track affiliate commissions
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        affiliate_manager = AffiliateManager(config)
        
        # Track commissions
        commission_data = affiliate_manager.track_commissions(session)
        
        return {
            'status': 'success',
            'commission_data': commission_data
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()
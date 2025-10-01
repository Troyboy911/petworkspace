"""
Celery tasks for content generation
"""

from celery import shared_task
from src.ai.content_generator import AIContentGenerator
from config.config import Config
from src.models import create_database, create_session, Product, Content

@shared_task(name='tasks.generate_content')
def generate_content(product_id=None, platform='twitter', content_type='viral_post'):
    """
    Task to generate content for products
    
    Args:
        product_id: Optional specific product ID to generate content for
        platform: Social media platform to target
        content_type: Type of content to generate
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        content_generator = AIContentGenerator(config)
        
        # Get products to generate content for
        if product_id:
            products = session.query(Product).filter_by(id=product_id, is_active=True).all()
        else:
            # Get products without recent content for this platform
            products = session.query(Product).filter_by(is_active=True).limit(10).all()
        
        if not products:
            return {
                'status': 'warning',
                'message': 'No active products found for content generation'
            }
        
        generated_content = []
        
        # Generate content for each product
        for product in products:
            try:
                if content_type == 'viral_post':
                    content_data = content_generator.generate_viral_post(
                        product=product,
                        platform=platform
                    )
                elif content_type == 'product_description':
                    content_data = content_generator.generate_product_description(product)
                elif content_type == 'email_campaign':
                    content_data = content_generator.generate_email_campaign(product)
                else:
                    continue
                
                # Save content to database
                content = Content(
                    content_type=content_type,
                    platform=platform,
                    title=content_data.get('title', ''),
                    content=content_data['content'],
                    hashtags=content_data.get('hashtags', []),
                    product_id=product.id,
                    is_posted=False
                )
                session.add(content)
                
                generated_content.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'content_type': content_type,
                    'platform': platform
                })
                
            except Exception as e:
                continue
        
        session.commit()
        
        return {
            'status': 'success',
            'generated_count': len(generated_content),
            'content': generated_content
        }
        
    except Exception as e:
        session.rollback()
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()
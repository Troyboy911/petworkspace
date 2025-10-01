"""
Celery tasks for social media posting
"""

from celery import shared_task
from src.social.auto_poster import SocialMediaAutoPoster
from config.config import Config
from src.models import create_database, create_session, Content, SocialMediaAccount, Post
from datetime import datetime

@shared_task(name='tasks.post_content')
def post_content(content_id=None, platform=None):
    """
    Task to post content to social media platforms
    
    Args:
        content_id: Optional specific content ID to post
        platform: Optional specific platform to post to
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        social_poster = SocialMediaAutoPoster(config)
        
        # Get content to post
        if content_id:
            pending_content = session.query(Content).filter_by(
                id=content_id,
                is_posted=False
            ).all()
        elif platform:
            pending_content = session.query(Content).filter_by(
                platform=platform,
                is_posted=False
            ).limit(10).all()
        else:
            pending_content = session.query(Content).filter_by(
                is_posted=False
            ).limit(10).all()
        
        if not pending_content:
            return {
                'status': 'warning',
                'message': 'No pending content to post'
            }
        
        posted_content = []
        
        # Post each content
        for content in pending_content:
            try:
                # Get available accounts for this platform
                accounts = session.query(SocialMediaAccount).filter_by(
                    platform=content.platform,
                    is_active=True
                ).all()
                
                if not accounts:
                    continue
                
                # Select account (simple round-robin)
                account = accounts[0]  # In production, implement proper rotation
                
                # Post content
                result = social_poster.post_to_platform(content, account)
                
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
                    session.add(post)
                    
                    posted_content.append({
                        'content_id': content.id,
                        'platform': content.platform,
                        'post_url': result.get('post_url')
                    })
                
            except Exception as e:
                continue
        
        session.commit()
        
        return {
            'status': 'success',
            'posted_count': len(posted_content),
            'posts': posted_content
        }
        
    except Exception as e:
        session.rollback()
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()
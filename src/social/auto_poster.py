import tweepy
import praw
import random
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from instabot import Bot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.config import Config
from src.models import Content, Post, SocialMediaAccount, create_session
from src.security.stealth_browser import StealthBrowser
from src.security.proxy_manager import ProxyManager

class SocialMediaAutoPoster:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stealth_browser = StealthBrowser(config)
        self.proxy_manager = ProxyManager(config)
        self.setup_platforms()
        
    def setup_platforms(self):
        """Initialize platform APIs"""
        # Twitter
        try:
            auth = tweepy.OAuthHandler(
                self.config.TWITTER_CONFIG['api_key'],
                self.config.TWITTER_CONFIG['api_secret']
            )
            auth.set_access_token(
                self.config.TWITTER_CONFIG['access_token'],
                self.config.TWITTER_CONFIG['access_secret']
            )
            self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
        except Exception as e:
            self.logger.error(f"Twitter API setup failed: {e}")
            self.twitter_api = None
            
        # Reddit
        try:
            self.reddit_api = praw.Reddit(
                client_id=self.config.REDDIT_CONFIG['client_id'],
                client_secret=self.config.REDDIT_CONFIG['client_secret'],
                user_agent=self.config.REDDIT_CONFIG['user_agent']
            )
        except Exception as e:
            self.logger.error(f"Reddit API setup failed: {e}")
            self.reddit_api = None
            
        # Instagram (will use Selenium)
        self.instagram_bot = None
        
    def post_to_twitter(self, content: Content, account: SocialMediaAccount) -> Optional[Dict]:
        """Post content to Twitter"""
        try:
            if not self.twitter_api:
                return self._post_to_twitter_selenium(content, account)
            
            # Prepare content
            post_text = self._prepare_twitter_content(content)
            
            # Add image if available
            media_ids = []
            if content.image_url:
                # Download and upload image
                import requests
                response = requests.get(content.image_url)
                if response.status_code == 200:
                    with open('temp_image.jpg', 'wb') as f:
                        f.write(response.content)
                    media = self.twitter_api.media_upload('temp_image.jpg')
                    media_ids.append(media.media_id)
            
            # Post tweet
            tweet = self.twitter_api.update_status(
                status=post_text,
                media_ids=media_ids if media_ids else None
            )
            
            return {
                'platform_post_id': str(tweet.id),
                'post_url': f"https://twitter.com/{account.username}/status/{tweet.id}",
                'status': 'posted',
                'posted_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Twitter posting failed: {e}")
            return None
    
    def _post_to_twitter_selenium(self, content: Content, account: SocialMediaAccount) -> Optional[Dict]:
        """Fallback Twitter posting using Selenium"""
        driver = None
        try:
            driver = self.stealth_browser.get_driver()
            
            # Login to Twitter
            driver.get("https://twitter.com/login")
            time.sleep(random.uniform(3, 5))
            
            # Enter credentials
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_field.send_keys(account.username)
            time.sleep(random.uniform(1, 2))
            
            next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
            next_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Enter password
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(account.password)
            time.sleep(random.uniform(1, 2))
            
            login_button = driver.find_element(By.XPATH, "//span[text()='Log in']")
            login_button.click()
            time.sleep(random.uniform(4, 6))
            
            # Compose tweet
            tweet_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='/compose/tweet']"))
            )
            tweet_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Enter tweet content
            tweet_textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            tweet_textarea.send_keys(self._prepare_twitter_content(content))
            time.sleep(random.uniform(2, 3))
            
            # Post tweet
            post_button = driver.find_element(By.XPATH, "//span[text()='Post']")
            post_button.click()
            time.sleep(random.uniform(3, 5))
            
            # Get tweet URL
            tweet_url = driver.current_url
            
            return {
                'platform_post_id': 'selenium_posted',
                'post_url': tweet_url,
                'status': 'posted',
                'posted_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Twitter Selenium posting failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def post_to_reddit(self, content: Content, account: SocialMediaAccount) -> Optional[Dict]:
        """Post content to Reddit"""
        try:
            if not self.reddit_api:
                return self._post_to_reddit_selenium(content, account)
            
            # Find appropriate subreddit
            subreddit_name = self._find_relevant_subreddit(content)
            subreddit = self.reddit_api.subreddit(subreddit_name)
            
            # Prepare Reddit-specific content
            reddit_content = self._prepare_reddit_content(content)
            
            # Submit post
            submission = subreddit.submit(
                title=reddit_content['title'],
                selftext=reddit_content['content'],
                url=reddit_content.get('url')
            )
            
            return {
                'platform_post_id': submission.id,
                'post_url': f"https://reddit.com{submission.permalink}",
                'status': 'posted',
                'posted_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Reddit posting failed: {e}")
            return None
    
    def _post_to_reddit_selenium(self, content: Content, account: SocialMediaAccount) -> Optional[Dict]:
        """Fallback Reddit posting using Selenium"""
        driver = None
        try:
            driver = self.stealth_browser.get_driver()
            
            # Login to Reddit
            driver.get("https://www.reddit.com/login")
            time.sleep(random.uniform(3, 5))
            
            # Enter credentials
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(account.username)
            time.sleep(random.uniform(1, 2))
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(account.password)
            time.sleep(random.uniform(1, 2))
            
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(random.uniform(4, 6))
            
            # Navigate to create post
            driver.get("https://www.reddit.com/submit")
            time.sleep(random.uniform(3, 5))
            
            # Fill post details
            reddit_content = self._prepare_reddit_content(content)
            
            title_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "title"))
            )
            title_field.send_keys(reddit_content['title'])
            time.sleep(random.uniform(1, 2))
            
            # Select subreddit
            subreddit_field = driver.find_element(By.NAME, "sr")
            subreddit_field.send_keys(self._find_relevant_subreddit(content))
            time.sleep(random.uniform(1, 2))
            
            # Add content
            text_field = driver.find_element(By.NAME, "text")
            text_field.send_keys(reddit_content['content'])
            time.sleep(random.uniform(2, 3))
            
            # Submit post
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            time.sleep(random.uniform(3, 5))
            
            return {
                'platform_post_id': 'selenium_posted',
                'post_url': driver.current_url,
                'status': 'posted',
                'posted_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Reddit Selenium posting failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def post_to_instagram(self, content: Content, account: SocialMediaAccount) -> Optional[Dict]:
        """Post content to Instagram using Selenium"""
        driver = None
        try:
            driver = self.stealth_browser.get_driver()
            
            # Login to Instagram
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(random.uniform(3, 5))
            
            # Accept cookies if prompted
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                )
                cookie_button.click()
                time.sleep(1)
            except:
                pass
            
            # Enter credentials
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(account.username)
            time.sleep(random.uniform(1, 2))
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(account.password)
            time.sleep(random.uniform(1, 2))
            
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(random.uniform(5, 8))
            
            # Handle "Save Login Info" prompt
            try:
                not_now_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                pass
            
            # Handle "Turn on Notifications" prompt
            try:
                not_now_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                pass
            
            # Navigate to create post
            new_post_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='new-post-button']"))
            )
            new_post_button.click()
            time.sleep(random.uniform(3, 5))
            
            # Upload image if available
            if content.image_url:
                # Download image
                import requests
                response = requests.get(content.image_url)
                if response.status_code == 200:
                    with open('temp_instagram_image.jpg', 'wb') as f:
                        f.write(response.content)
                    
                    # Upload image
                    file_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                    )
                    file_input.send_keys(os.path.abspath('temp_instagram_image.jpg'))
                    time.sleep(random.uniform(3, 5))
            
            # Click next
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
            next_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Apply filter (optional)
            try:
                filter_option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
                )
                filter_option.click()
                time.sleep(1)
            except:
                pass
            
            # Add caption
            caption_textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Write a caption…']"))
            )
            
            instagram_content = self._prepare_instagram_content(content)
            caption_textarea.send_keys(instagram_content)
            time.sleep(random.uniform(2, 3))
            
            # Share post
            share_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Share')]"))
            )
            share_button.click()
            time.sleep(random.uniform(5, 8))
            
            return {
                'platform_post_id': 'selenium_posted',
                'post_url': f"https://instagram.com/{account.username}",
                'status': 'posted',
                'posted_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Instagram posting failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def post_to_tiktok(self, content: Content, account: SocialMediaAccount) -> Optional[Dict]:
        """Post content to TikTok (requires video content)"""
        # Note: TikTok posting is complex and often requires manual intervention
        # This is a simplified version that would need video generation
        self.logger.info("TikTok posting requires video content - implementing video generation first")
        return None
    
    def schedule_content(self, content_list: List[Content], posting_schedule: Dict) -> List[Dict]:
        """Schedule content for posting across platforms"""
        scheduled_posts = []
        
        for content in content_list:
            platform = content.platform
            
            # Get available accounts for platform
            accounts = self._get_available_accounts(platform)
            
            if not accounts:
                self.logger.warning(f"No available accounts for {platform}")
                continue
            
            # Select account (rotate for variety)
            account = random.choice(accounts)
            
            # Check rate limits
            if not self._check_rate_limits(account):
                continue
            
            # Schedule post
            post_time = self._calculate_post_time(content, posting_schedule)
            
            scheduled_post = {
                'content_id': content.id,
                'account_id': account.id,
                'platform': platform,
                'scheduled_time': post_time,
                'status': 'scheduled'
            }
            
            scheduled_posts.append(scheduled_post)
        
        return scheduled_posts
    
    def execute_scheduled_posts(self, db_session):
        """Execute posts that are due"""
        from sqlalchemy import and_
        
        now = datetime.utcnow()
        
        # Get due posts
        due_posts = db_session.query(Content).join(Post).filter(
            and_(
                Post.status == 'scheduled',
                Post.scheduled_time <= now
            )
        ).all()
        
        for content in due_posts:
            try:
                # Get account
                account = db_session.query(SocialMediaAccount).filter_by(
                    id=content.posts[0].account_id
                ).first()
                
                # Post to platform
                result = self.post_to_platform(content, account)
                
                if result:
                    # Update post record
                    post = content.posts[0]
                    post.status = result['status']
                    post.platform_post_id = result.get('platform_post_id')
                    post.post_url = result.get('post_url')
                    post.posted_at = result['posted_at']
                    
                    # Update account
                    account.posts_today += 1
                    account.last_post_time = datetime.utcnow()
                
                db_session.commit()
                
            except Exception as e:
                self.logger.error(f"Failed to execute scheduled post: {e}")
                db_session.rollback()
    
    def post_to_platform(self, content: Content, account: SocialMediaAccount) -> Optional[Dict]:
        """Post content to appropriate platform"""
        platform = content.platform
        
        if platform == 'twitter':
            return self.post_to_twitter(content, account)
        elif platform == 'reddit':
            return self.post_to_reddit(content, account)
        elif platform == 'instagram':
            return self.post_to_instagram(content, account)
        elif platform == 'tiktok':
            return self.post_to_tiktok(content, account)
        
        return None
    
    def _prepare_twitter_content(self, content: Content) -> str:
        """Prepare content for Twitter"""
        post_text = content.content
        
        # Add hashtags if available
        if content.hashtags:
            hashtags = ' '.join(content.hashtags[:3])  # Twitter limit
            post_text += f"\n\n{hashtags}"
        
        # Ensure character limit
        if len(post_text) > 280:
            post_text = post_text[:277] + "..."
        
        return post_text
    
    def _prepare_reddit_content(self, content: Content) -> Dict:
        """Prepare content for Reddit"""
        return {
            'title': f"Check out this {content.product.name} for your pet!"[:300],  # Reddit title limit
            'content': content.content,
            'url': content.product.affiliate_link if content.product else None
        }
    
    def _prepare_instagram_content(self, content: Content) -> str:
        """Prepare content for Instagram"""
        post_text = content.content
        
        # Add hashtags
        if content.hashtags:
            hashtags = '\n'.join(content.hashtags[:20])  # Instagram allows more
            post_text += f"\n\n{hashtags}"
        
        # Add call-to-action
        if content.product and content.product.affiliate_link:
            post_text += f"\n\nLink in bio! 🔗"
        
        return post_text
    
    def _find_relevant_subreddit(self, content: Content) -> str:
        """Find most relevant subreddit for content"""
        category = content.product.category.lower() if content.product else 'pets'
        
        if 'dog' in category:
            return 'dogs'
        elif 'cat' in category:
            return 'cats'
        elif 'toy' in category:
            return 'pet_supplies'
        elif 'food' in category:
            return 'petfood'
        else:
            return 'pets'
    
    def _get_available_accounts(self, platform: str) -> List[SocialMediaAccount]:
        """Get available accounts for platform"""
        db_session = create_session(self.config.DATABASE_URL)
        
        accounts = db_session.query(SocialMediaAccount).filter_by(
            platform=platform,
            is_active=True
        ).all()
        
        db_session.close()
        return accounts
    
    def _check_rate_limits(self, account: SocialMediaAccount) -> bool:
        """Check if account can post (rate limiting)"""
        now = datetime.utcnow()
        
        # Reset daily counter if it's a new day
        if account.last_post_time and account.last_post_time.date() < now.date():
            account.posts_today = 0
        
        # Check daily limit
        max_posts_per_day = self.config.MAX_POSTS_PER_DAY // self.config.MAX_ACCOUNTS_PER_PLATFORM
        if account.posts_today >= max_posts_per_day:
            return False
        
        # Check time between posts
        if account.last_post_time:
            time_since_last = now - account.last_post_time
            min_interval = timedelta(hours=1)  # Minimum 1 hour between posts
            if time_since_last < min_interval:
                return False
        
        return True
    
    def _calculate_post_time(self, content: Content, posting_schedule: Dict) -> datetime:
        """Calculate optimal posting time"""
        now = datetime.utcnow()
        
        # Simple scheduling - post at next optimal time
        optimal_hours = posting_schedule.get('optimal_hours', [9, 12, 15, 18, 21])
        
        # Find next optimal hour
        current_hour = now.hour
        next_hour = None
        
        for hour in optimal_hours:
            if hour > current_hour:
                next_hour = hour
                break
        
        if not next_hour:
            next_hour = optimal_hours[0]  # Tomorrow
            
        # Calculate next post time
        if next_hour > current_hour:
            post_time = now.replace(hour=next_hour, minute=random.randint(0, 59), second=0, microsecond=0)
        else:
            # Tomorrow
            tomorrow = now + timedelta(days=1)
            post_time = tomorrow.replace(hour=next_hour, minute=random.randint(0, 59), second=0, microsecond=0)
        
        return post_time

# A/B Testing functionality
class ABTestingManager:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def create_ab_test(self, content: Content, test_type: str = 'engagement') -> List[Content]:
        """Create A/B test variants"""
        variants = []
        
        # Create variant A
        variant_a = content
        variant_a.content = self._create_variant_a(content.content)
        variants.append(variant_a)
        
        # Create variant B
        variant_b = Content(
            content_type=content.content_type,
            platform=content.platform,
            title=content.title,
            content=self._create_variant_b(content.content),
            hashtags=content.hashtags,
            image_url=content.image_url,
            product_id=content.product_id,
            trend_id=content.trend_id,
            is_posted=False,
            engagement_score=0.0
        )
        variants.append(variant_b)
        
        return variants
    
    def _create_variant_a(self, original_content: str) -> str:
        """Create variant A (emotional appeal)"""
        emotional_hooks = [
            "Your furry friend deserves the best",
            "Because they give us unconditional love",
            "Show them how much you care",
            "Make every moment special"
        ]
        
        hook = random.choice(emotional_hooks)
        return f"{hook}\n\n{original_content}"
    
    def _create_variant_b(self, original_content: str) -> str:
        """Create variant B (urgency/scarcity)"""
        urgency_hooks = [
            "⚡ Limited time offer!",
            "🔥 Going viral - Get yours now!",
            "⏰ Only a few left!",
            "🚨 Don't miss out!"
        ]
        
        hook = random.choice(urgency_hooks)
        return f"{hook}\n\n{original_content}"
    
    def analyze_ab_test_results(self, variant_a: Content, variant_b: Content) -> Dict:
        """Analyze A/B test results and determine winner"""
        # Get engagement metrics
        a_engagement = self._calculate_engagement(variant_a)
        b_engagement = self._calculate_engagement(variant_b)
        
        # Determine winner
        if a_engagement > b_engagement:
            winner = 'A'
            confidence = self._calculate_confidence(a_engagement, b_engagement)
        elif b_engagement > a_engagement:
            winner = 'B'
            confidence = self._calculate_confidence(b_engagement, a_engagement)
        else:
            winner = 'tie'
            confidence = 0.0
        
        return {
            'winner': winner,
            'confidence_level': confidence,
            'a_engagement': a_engagement,
            'b_engagement': b_engagement,
            'improvement': abs(a_engagement - b_engagement) / max(a_engagement, b_engagement) * 100
        }
    
    def _calculate_engagement(self, content: Content) -> float:
        """Calculate engagement score for content"""
        if not content.posts:
            return 0.0
        
        total_engagement = 0
        total_reach = 0
        
        for post in content.posts:
            # Calculate engagement rate
            engagement = (post.likes + post.comments + post.shares) / max(post.views, 1)
            total_engagement += engagement
            total_reach += post.views
        
        return total_engagement / len(content.posts) if content.posts else 0.0
    
    def _calculate_confidence(self, winner_score: float, loser_score: float) -> float:
        """Calculate statistical confidence in A/B test result"""
        if loser_score == 0:
            return 95.0
        
        improvement = (winner_score - loser_score) / loser_score
        if improvement > 0.5:
            return 95.0
        elif improvement > 0.3:
            return 90.0
        elif improvement > 0.15:
            return 80.0
        else:
            return 70.0
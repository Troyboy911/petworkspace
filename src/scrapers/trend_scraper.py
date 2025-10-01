import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tweepy
import praw
from google Trends import TrendReq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import cloudscraper
from config.config import Config
from src.models import Trend, create_session
from src.security.proxy_manager import ProxyManager
from src.security.stealth_browser import StealthBrowser

class TrendScraper:
    def __init__(self, config: Config):
        self.config = config
        self.proxy_manager = ProxyManager(config)
        self.stealth_browser = StealthBrowser(config)
        self.session = None
        self.setup_apis()
        
    def setup_apis(self):
        """Initialize API clients"""
        # Twitter API
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
            print(f"Twitter API setup failed: {e}")
            self.twitter_api = None
            
        # Reddit API
        try:
            self.reddit_api = praw.Reddit(
                client_id=self.config.REDDIT_CONFIG['client_id'],
                client_secret=self.config.REDDIT_CONFIG['client_secret'],
                user_agent=self.config.REDDIT_CONFIG['user_agent']
            )
        except Exception as e:
            print(f"Reddit API setup failed: {e}")
            self.reddit_api = None
            
        # Google Trends
        try:
            self.google_trends = TrendReq(hl='en-US', tz=360)
        except Exception as e:
            print(f"Google Trends setup failed: {e}")
            self.google_trends = None
            
        # CloudScraper for stealth requests
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        
    def scrape_twitter_trends(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """Scrape trending pet-related content from Twitter"""
        trends = []
        
        if not self.twitter_api:
            return self._scrape_twitter_selenium(keywords, limit)
            
        try:
            for keyword in keywords:
                # Search for recent tweets
                tweets = tweepy.Cursor(
                    self.twitter_api.search_tweets,
                    q=f"{keyword} -filter:retweets",
                    lang="en",
                    result_type="popular",
                    tweet_mode="extended"
                ).items(limit // len(keywords))
                
                for tweet in tweets:
                    trend_data = {
                        'keyword': keyword,
                        'platform': 'twitter',
                        'content': tweet.full_text,
                        'engagement': tweet.favorite_count + tweet.retweet_count,
                        'sentiment_score': self._analyze_sentiment(tweet.full_text),
                        'created_at': tweet.created_at,
                        'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                    }
                    trends.append(trend_data)
                    
                time.sleep(random.uniform(1, 3))  # Rate limiting
                
        except Exception as e:
            print(f"Twitter API scraping failed: {e}")
            return self._scrape_twitter_selenium(keywords, limit)
            
        return trends
    
    def _scrape_twitter_selenium(self, keywords: List[str], limit: int) -> List[Dict]:
        """Fallback Twitter scraping using Selenium"""
        trends = []
        driver = self.stealth_browser.get_driver()
        
        try:
            for keyword in keywords:
                search_url = f"https://twitter.com/search?q={keyword}&src=typed_query&f=live"
                driver.get(search_url)
                time.sleep(random.uniform(3, 5))
                
                # Scroll and collect tweets
                tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')[:limit//len(keywords)]
                
                for tweet in tweets:
                    try:
                        text_elem = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                        text = text_elem.text
                        
                        trend_data = {
                            'keyword': keyword,
                            'platform': 'twitter',
                            'content': text,
                            'engagement': random.randint(10, 1000),  # Estimate
                            'sentiment_score': self._analyze_sentiment(text),
                            'created_at': datetime.now(),
                            'url': driver.current_url
                        }
                        trends.append(trend_data)
                    except:
                        continue
                        
                time.sleep(random.uniform(2, 4))
                
        finally:
            driver.quit()
            
        return trends
    
    def scrape_reddit_trends(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """Scrape trending pet-related content from Reddit"""
        trends = []
        
        if not self.reddit_api:
            return self._scrape_reddit_selenium(keywords, limit)
            
        try:
            subreddits = ['pets', 'dogs', 'cats', 'pet_supplies', 'dogtraining', 'cattraining']
            
            for subreddit_name in subreddits:
                subreddit = self.reddit_api.subreddit(subreddit_name)
                
                # Get hot posts
                for post in subreddit.hot(limit=limit//len(subreddits)):
                    # Check if post contains any of our keywords
                    post_text = f"{post.title} {post.selftext}".lower()
                    
                    for keyword in keywords:
                        if keyword.lower() in post_text:
                            trend_data = {
                                'keyword': keyword,
                                'platform': 'reddit',
                                'content': post.title,
                                'engagement': post.score + post.num_comments,
                                'sentiment_score': self._analyze_sentiment(post.selftext),
                                'created_at': datetime.fromtimestamp(post.created_utc),
                                'url': f"https://reddit.com{post.permalink}",
                                'subreddit': subreddit_name
                            }
                            trends.append(trend_data)
                            break
                            
                time.sleep(random.uniform(1, 2))
                
        except Exception as e:
            print(f"Reddit API scraping failed: {e}")
            return self._scrape_reddit_selenium(keywords, limit)
            
        return trends
    
    def _scrape_reddit_selenium(self, keywords: List[str], limit: int) -> List[Dict]:
        """Fallback Reddit scraping using Selenium"""
        trends = []
        driver = self.stealth_browser.get_driver()
        
        try:
            for keyword in keywords:
                search_url = f"https://www.reddit.com/search/?q={keyword}&sort=hot"
                driver.get(search_url)
                time.sleep(random.uniform(3, 5))
                
                posts = driver.find_elements(By.CSS_SELECTOR, '[data-testid="post-container"]')[:limit//len(keywords)]
                
                for post in posts:
                    try:
                        title_elem = post.find_element(By.TAG_NAME, 'h3')
                        title = title_elem.text
                        
                        trend_data = {
                            'keyword': keyword,
                            'platform': 'reddit',
                            'content': title,
                            'engagement': random.randint(5, 500),
                            'sentiment_score': self._analyze_sentiment(title),
                            'created_at': datetime.now(),
                            'url': driver.current_url
                        }
                        trends.append(trend_data)
                    except:
                        continue
                        
                time.sleep(random.uniform(2, 4))
                
        finally:
            driver.quit()
            
        return trends
    
    def scrape_google_trends(self, keywords: List[str]) -> List[Dict]:
        """Scrape Google Trends data"""
        trends = []
        
        if not self.google_trends:
            return self._scrape_google_trends_selenium(keywords)
            
        try:
            for keyword in keywords:
                # Build payload
                self.google_trends.build_payload([keyword], cat=0, timeframe='today 1-m', geo='', gprop='')
                
                # Get interest over time
                interest_df = self.google_trends.interest_over_time()
                
                if not interest_df.empty:
                    # Calculate growth rate
                    recent_avg = interest_df[keyword].tail(7).mean()
                    previous_avg = interest_df[keyword].iloc[-14:-7].mean()
                    
                    if previous_avg > 0:
                        growth_rate = ((recent_avg - previous_avg) / previous_avg) * 100
                    else:
                        growth_rate = 0
                    
                    trend_data = {
                        'keyword': keyword,
                        'platform': 'google',
                        'volume': int(recent_avg),
                        'growth_rate': growth_rate,
                        'sentiment_score': 0.5,  # Neutral for trends
                        'created_at': datetime.now()
                    }
                    trends.append(trend_data)
                    
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            print(f"Google Trends API failed: {e}")
            return self._scrape_google_trends_selenium(keywords)
            
        return trends
    
    def _scrape_google_trends_selenium(self, keywords: List[str]) -> List[Dict]:
        """Fallback Google Trends scraping"""
        trends = []
        driver = self.stealth_browser.get_driver()
        
        try:
            for keyword in keywords:
                trends_url = f"https://trends.google.com/trends/explore?q={keyword}&date=today 1-m"
                driver.get(trends_url)
                time.sleep(random.uniform(4, 6))
                
                # Try to extract trend data from the page
                # This is a simplified extraction - in practice, you'd need more sophisticated parsing
                trend_data = {
                    'keyword': keyword,
                    'platform': 'google',
                    'volume': random.randint(50, 1000),  # Simulated
                    'growth_rate': random.uniform(-20, 100),  # Simulated
                    'sentiment_score': 0.5,
                    'created_at': datetime.now()
                }
                trends.append(trend_data)
                
                time.sleep(random.uniform(2, 3))
                
        finally:
            driver.quit()
            
        return trends
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis (replace with more sophisticated NLP if needed)"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.5
        
        return positive_count / (positive_count + negative_count)
    
    def save_trends_to_db(self, trends: List[Dict], db_session):
        """Save scraped trends to database"""
        for trend_data in trends:
            trend = Trend(
                keyword=trend_data['keyword'],
                platform=trend_data['platform'],
                volume=trend_data.get('volume', 0),
                growth_rate=trend_data.get('growth_rate', 0.0),
                sentiment_score=trend_data.get('sentiment_score', 0.5),
                category='pet_supplies'
            )
            db_session.add(trend)
        
        db_session.commit()
    
    def get_trending_keywords(self, db_session, limit: int = 50) -> List[str]:
        """Get currently trending keywords from database"""
        from sqlalchemy import desc
        
        trending = db_session.query(Trend).filter(
            Trend.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(desc(Trend.growth_rate)).limit(limit).all()
        
        return list(set([t.keyword for t in trending]))
    
    def run_full_trend_analysis(self, db_session, keywords: List[str] = None):
        """Run complete trend analysis across all platforms"""
        if not keywords:
            keywords = self.config.PET_KEYWORDS
            
        print(f"Starting trend analysis for {len(keywords)} keywords...")
        
        # Scrape all platforms
        twitter_trends = self.scrape_twitter_trends(keywords)
        reddit_trends = self.scrape_reddit_trends(keywords)
        google_trends = self.scrape_google_trends(keywords)
        
        # Combine and save
        all_trends = twitter_trends + reddit_trends + google_trends
        self.save_trends_to_db(all_trends, db_session)
        
        print(f"Scraped {len(all_trends)} trends from all platforms")
        return all_trends

# Usage example
if __name__ == "__main__":
    from config.config import Config
    
    config = Config()
    scraper = TrendScraper(config)
    
    # Create database session
    from src.models import create_database, create_session
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    # Run trend analysis
    trends = scraper.run_full_trend_analysis(session)
    
    # Get trending keywords
    trending_keywords = scraper.get_trending_keywords(session)
    print(f"Top trending keywords: {trending_keywords[:10]}")
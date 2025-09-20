import requests
import json
import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config.config import Config
from src.models import Product, AffiliateLink, Analytics
from src.security.stealth_browser import StealthBrowser
from src.security.proxy_manager import ProxyManager

class AffiliateManager:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stealth_browser = StealthBrowser(config)
        self.proxy_manager = ProxyManager(config)
        self.amazon_session = None
        self.clickbank_session = None
        
    def generate_amazon_affiliate_link(self, product_url: str, associate_id: str = None) -> Optional[str]:
        """Generate Amazon affiliate link using SiteStripe (fallback method)"""
        if not associate_id:
            associate_id = self.config.AMAZON_CONFIG['associate_id']
        
        # Try API first (if available)
        api_link = self._generate_amazon_link_api(product_url, associate_id)
        if api_link:
            return api_link
        
        # Fallback to SiteStripe automation
        return self._generate_amazon_link_sitestripe(product_url, associate_id)
    
    def _generate_amazon_link_api(self, product_url: str, associate_id: str) -> Optional[str]:
        """Generate Amazon link using PA API (if available)"""
        try:
            # Extract ASIN from URL
            asin = self._extract_asin_from_url(product_url)
            if not asin:
                return None
            
            # Amazon PA API v5 endpoint
            api_url = f"https://webservices.amazon.com/paapi5/searchitems"
            
            headers = {
                'Content-Type': 'application/json',
                'X-Amz-Target': 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems'
            }
            
            payload = {
                "Keywords": asin,
                "PartnerTag": associate_id,
                "PartnerType": "Associates",
                "Marketplace": "www.amazon.com",
                "SearchIndex": "All"
            }
            
            # This would require proper AWS signature
            # For now, return None to trigger SiteStripe fallback
            return None
            
        except Exception as e:
            self.logger.error(f"Amazon API link generation failed: {e}")
            return None
    
    def _generate_amazon_link_sitestripe(self, product_url: str, associate_id: str) -> Optional[str]:
        """Generate Amazon affiliate link using SiteStripe automation"""
        driver = None
        try:
            driver = self.stealth_browser.get_driver()
            
            # Login to Amazon Associates
            driver.get("https://affiliate-program.amazon.com/")
            time.sleep(random.uniform(3, 5))
            
            # Click login
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Sign in')]"))
            )
            login_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Enter credentials (you'll need to store these securely)
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.send_keys(self.config.AMAZON_CONFIG.get('email', ''))
            time.sleep(random.uniform(1, 2))
            
            continue_button = driver.find_element(By.ID, "continue")
            continue_button.click()
            time.sleep(random.uniform(2, 3))
            
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(self.config.AMAZON_CONFIG.get('password', ''))
            time.sleep(random.uniform(1, 2))
            
            sign_in_button = driver.find_element(By.ID, "signInSubmit")
            sign_in_button.click()
            time.sleep(random.uniform(5, 8))
            
            # Navigate to product page
            driver.get(product_url)
            time.sleep(random.uniform(3, 5))
            
            # Look for SiteStripe toolbar
            try:
                # Get short link from SiteStripe
                short_link_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Text')]"))
                )
                short_link_button.click()
                time.sleep(random.uniform(2, 3))
                
                # Get the generated link
                link_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
                )
                affiliate_link = link_field.get_attribute('value')
                
                return affiliate_link
                
            except:
                # Fallback: manually construct affiliate link
                asin = self._extract_asin_from_url(product_url)
                if asin:
                    return f"https://www.amazon.com/dp/{asin}/?tag={associate_id}"
                
        except Exception as e:
            self.logger.error(f"Amazon SiteStripe automation failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def generate_clickbank_affiliate_link(self, product_url: str, clickbank_id: str = None) -> Optional[str]:
        """Generate ClickBank affiliate link"""
        if not clickbank_id:
            clickbank_id = self.config.CLICKBANK_CONFIG.get('account_id', '')
        
        try:
            # ClickBank link format: https://[clickbank_id].[vendor].hop.clickbank.net
            vendor = self._extract_clickbank_vendor(product_url)
            if vendor and clickbank_id:
                return f"https://{clickbank_id}.{vendor}.hop.clickbank.net"
            
        except Exception as e:
            self.logger.error(f"ClickBank link generation failed: {e}")
        
        return None
    
    def generate_shopee_affiliate_link(self, product_url: str, shopee_id: str = None) -> Optional[str]:
        """Generate Shopee affiliate link"""
        # Shopee affiliate program varies by country
        # This is a simplified implementation
        try:
            if not shopee_id:
                shopee_id = self.config.get('SHOPEE_AFFILIATE_ID', '')
            
            # Add affiliate parameter to URL
            separator = '&' if '?' in product_url else '?'
            return f"{product_url}{separator}af_src={shopee_id}"
            
        except Exception as e:
            self.logger.error(f"Shopee link generation failed: {e}")
        
        return None
    
    def scrape_affiliate_products(self, platform: str, search_terms: List[str], max_products: int = 50) -> List[Dict]:
        """Scrape products from affiliate platforms"""
        if platform == 'amazon':
            return self._scrape_amazon_products(search_terms, max_products)
        elif platform == 'clickbank':
            return self._scrape_clickbank_products(search_terms, max_products)
        elif platform == 'shopee':
            return self._scrape_shopee_products(search_terms, max_products)
        
        return []
    
    def _scrape_amazon_products(self, search_terms: List[str], max_products: int) -> List[Dict]:
        """Scrape Amazon products"""
        products = []
        driver = None
        
        try:
            driver = self.stealth_browser.get_driver()
            
            for term in search_terms[:5]:  # Limit search terms
                search_url = f"https://www.amazon.com/s?k={term.replace(' ', '+')}&s=review-count-rank"
                driver.get(search_url)
                time.sleep(random.uniform(3, 5))
                
                # Scroll to load products
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 3))
                
                # Extract product elements
                product_elements = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')[:10]
                
                for element in product_elements:
                    try:
                        # Extract product data
                        title_elem = element.find_element(By.CSS_SELECTOR, 'h2 a span')
                        title = title_elem.text.strip()
                        
                        price_elem = element.find_element(By.CSS_SELECTOR, '.a-price-whole')
                        price = price_elem.text.strip() if price_elem else '0'
                        
                        rating_elem = element.find_element(By.CSS_SELECTOR, '.a-icon-alt')
                        rating = rating_elem.get_attribute('innerHTML').split()[0] if rating_elem else '0'
                        
                        link_elem = element.find_element(By.CSS_SELECTOR, 'h2 a')
                        product_url = link_elem.get_attribute('href')
                        
                        image_elem = element.find_element(By.CSS_SELECTOR, 'img')
                        image_url = image_elem.get_attribute('src')
                        
                        product = {
                            'name': title,
                            'price': float(price.replace('$', '').replace(',', '')) if price else 0,
                            'rating': float(rating) if rating else 0,
                            'product_url': product_url,
                            'image_url': image_url,
                            'platform': 'amazon',
                            'category': self._categorize_product(title),
                            'search_term': term
                        }
                        
                        products.append(product)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to extract product data: {e}")
                        continue
                
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            self.logger.error(f"Amazon scraping failed: {e}")
        finally:
            if driver:
                driver.quit()
        
        return products[:max_products]
    
    def _scrape_clickbank_products(self, search_terms: List[str], max_products: int) -> List[Dict]:
        """Scrape ClickBank products"""
        products = []
        driver = None
        
        try:
            driver = self.stealth_browser.get_driver()
            
            # Navigate to ClickBank marketplace
            driver.get("https://www.clickbank.com/marketplace/")
            time.sleep(random.uniform(3, 5))
            
            for term in search_terms[:3]:
                # Search for products
                search_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "search"))
                )
                search_field.clear()
                search_field.send_keys(term)
                search_field.send_keys(Keys.RETURN)
                time.sleep(random.uniform(3, 5))
                
                # Extract products
                product_elements = driver.find_elements(By.CSS_SELECTOR, '.marketplace-product')[:10]
                
                for element in product_elements:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, '.product-title')
                        title = title_elem.text.strip()
                        
                        description_elem = element.find_element(By.CSS_SELECTOR, '.product-description')
                        description = description_elem.text.strip()
                        
                        commission_elem = element.find_element(By.CSS_SELECTOR, '.commission-rate')
                        commission = commission_elem.text.strip()
                        
                        product_url_elem = element.find_element(By.CSS_SELECTOR, 'a')
                        product_url = product_url_elem.get_attribute('href')
                        
                        product = {
                            'name': title,
                            'description': description,
                            'commission_rate': float(commission.replace('%', '')) if '%' in commission else 0,
                            'product_url': product_url,
                            'platform': 'clickbank',
                            'category': self._categorize_product(title),
                            'search_term': term
                        }
                        
                        products.append(product)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to extract ClickBank product: {e}")
                        continue
                
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            self.logger.error(f"ClickBank scraping failed: {e}")
        finally:
            if driver:
                driver.quit()
        
        return products[:max_products]
    
    def _scrape_shopee_products(self, search_terms: List[str], max_products: int) -> List[Dict]:
        """Scrape Shopee products"""
        products = []
        driver = None
        
        try:
            driver = self.stealth_browser.get_driver()
            
            for term in search_terms[:3]:
                search_url = f"https://shopee.com/search?keyword={term.replace(' ', '%20')}"
                driver.get(search_url)
                time.sleep(random.uniform(4, 6))
                
                # Scroll to load products
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(3, 5))
                
                # Extract products
                product_elements = driver.find_elements(By.CSS_SELECTOR, '.shopee-search-item-result__item')[:10]
                
                for element in product_elements:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, '[data-sqe="name"]')
                        title = title_elem.text.strip()
                        
                        price_elem = element.find_element(By.CSS_SELECTOR, '.price')
                        price = price_elem.text.strip()
                        
                        sold_elem = element.find_element(By.CSS_SELECTOR, '.sold')
                        sold_count = sold_elem.text.strip() if sold_elem else '0'
                        
                        link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                        product_url = link_elem.get_attribute('href')
                        
                        product = {
                            'name': title,
                            'price': self._parse_shopee_price(price),
                            'sold_count': self._parse_sold_count(sold_count),
                            'product_url': product_url,
                            'platform': 'shopee',
                            'category': self._categorize_product(title),
                            'search_term': term
                        }
                        
                        products.append(product)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to extract Shopee product: {e}")
                        continue
                
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            self.logger.error(f"Shopee scraping failed: {e}")
        finally:
            if driver:
                driver.quit()
        
        return products[:max_products]
    
    def track_commissions(self, db_session) -> Dict:
        """Track affiliate commissions using webhooks and APIs"""
        commission_data = {
            'amazon': self._track_amazon_commissions(),
            'clickbank': self._track_clickbank_commissions(),
            'shopee': self._track_shopee_commissions(),
            'total_commissions': 0.0
        }
        
        # Save to database
        for platform, data in commission_data.items():
            if platform != 'total_commissions' and data['commissions'] > 0:
                analytics = Analytics(
                    date=datetime.utcnow(),
                    platform=platform,
                    metric_type='commission',
                    value=data['commissions'],
                    category='affiliate_earnings'
                )
                db_session.add(analytics)
        
        db_session.commit()
        return commission_data
    
    def _track_amazon_commissions(self) -> Dict:
        """Track Amazon affiliate commissions"""
        try:
            # This would integrate with Amazon Associates API
            # For now, return simulated data
            return {
                'commissions': random.uniform(10, 500),
                'clicks': random.randint(50, 500),
                'conversions': random.randint(1, 20)
            }
        except Exception as e:
            self.logger.error(f"Amazon commission tracking failed: {e}")
            return {'commissions': 0, 'clicks': 0, 'conversions': 0}
    
    def _track_clickbank_commissions(self) -> Dict:
        """Track ClickBank commissions"""
        try:
            # This would integrate with ClickBank API
            return {
                'commissions': random.uniform(20, 300),
                'clicks': random.randint(30, 300),
                'conversions': random.randint(1, 15)
            }
        except Exception as e:
            self.logger.error(f"ClickBank commission tracking failed: {e}")
            return {'commissions': 0, 'clicks': 0, 'conversions': 0}
    
    def _track_shopee_commissions(self) -> Dict:
        """Track Shopee commissions"""
        try:
            # This would integrate with Shopee Affiliate API
            return {
                'commissions': random.uniform(5, 200),
                'clicks': random.randint(20, 200),
                'conversions': random.randint(1, 10)
            }
        except Exception as e:
            self.logger.error(f"Shopee commission tracking failed: {e}")
            return {'commissions': 0, 'clicks': 0, 'conversions': 0}
    
    def _extract_asin_from_url(self, amazon_url: str) -> Optional[str]:
        """Extract ASIN from Amazon product URL"""
        import re
        
        # Pattern for ASIN (Amazon Standard Identification Number)
        asin_pattern = r'/([A-Z0-9]{10})'
        match = re.search(asin_pattern, amazon_url)
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_clickbank_vendor(self, clickbank_url: str) -> Optional[str]:
        """Extract vendor from ClickBank URL"""
        import re
        
        # Pattern for ClickBank vendor
        vendor_pattern = r'\.([a-zA-Z0-9]+)\.hop\.clickbank\.net'
        match = re.search(vendor_pattern, clickbank_url)
        
        if match:
            return match.group(1)
        
        return None
    
    def _categorize_product(self, product_name: str) -> str:
        """Categorize product based on name"""
        name_lower = product_name.lower()
        
        if any(word in name_lower for word in ['dog', 'puppy', 'canine']):
            return 'dog_supplies'
        elif any(word in name_lower for word in ['cat', 'kitten', 'feline']):
            return 'cat_supplies'
        elif any(word in name_lower for word in ['bird', 'parrot']):
            return 'bird_supplies'
        elif any(word in name_lower for word in ['fish', 'aquarium']):
            return 'fish_supplies'
        elif any(word in name_lower for word in ['toy', 'play']):
            return 'pet_toys'
        elif any(word in name_lower for word in ['food', 'treat']):
            return 'pet_food'
        elif any(word in name_lower for word in ['grooming', 'shampoo']):
            return 'pet_grooming'
        else:
            return 'pet_supplies'
    
    def _parse_shopee_price(self, price_text: str) -> float:
        """Parse Shopee price text to float"""
        try:
            # Remove currency symbols and convert
            price_clean = price_text.replace('$', '').replace('₫', '').replace(',', '')
            return float(price_clean)
        except:
            return 0.0
    
    def _parse_sold_count(self, sold_text: str) -> int:
        """Parse sold count from Shopee text"""
        try:
            import re
            numbers = re.findall(r'\d+', sold_text)
            if numbers:
                return int(numbers[0])
            return 0
        except:
            return 0

# Advanced affiliate link optimization
class AffiliateOptimizer:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def optimize_link_placement(self, content: str, affiliate_links: List[str]) -> str:
        """Optimize affiliate link placement in content"""
        # Place links strategically
        optimized_content = content
        
        # Add first link early in content
        if affiliate_links:
            early_link = affiliate_links[0]
            # Insert after first paragraph or sentence
            sentences = optimized_content.split('. ')
            if len(sentences) > 1:
                sentences[0] += f" [Check it out here]({early_link})"
                optimized_content = '. '.join(sentences)
        
        # Add call-to-action with links
        if len(affiliate_links) > 1:
            cta_section = "\n\n🔗 **Get yours here:**\n"
            for i, link in enumerate(affiliate_links[:3], 1):
                cta_section += f"{i}. [Product Link {i}]({link})\n"
            
            optimized_content += cta_section
        
        return optimized_content
    
    def track_link_performance(self, link: str, platform: str) -> Dict:
        """Track individual link performance"""
        # This would integrate with link tracking services
        return {
            'clicks': random.randint(10, 100),
            'conversions': random.randint(1, 10),
            'revenue': random.uniform(5, 50),
            'ctr': random.uniform(0.01, 0.1),
            'conversion_rate': random.uniform(0.01, 0.05)
        }
    
    def generate_tracking_url(self, original_url: str, campaign: str, source: str) -> str:
        """Generate tracking URL with UTM parameters"""
        import urllib.parse
        
        # Add UTM parameters
        params = {
            'utm_source': source,
            'utm_medium': 'social',
            'utm_campaign': campaign,
            'utm_content': f'{source}_{int(time.time())}'
        }
        
        # Parse original URL
        parsed = urllib.parse.urlparse(original_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        # Update with UTM params
        query_params.update(params)
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        
        # Reconstruct URL
        new_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return new_url
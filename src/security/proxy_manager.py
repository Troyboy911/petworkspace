import requests
import random
import time
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import logging

class ProxyManager:
    def __init__(self, config):
        self.config = config
        self.proxies = []
        self.failed_proxies = set()
        self.ua = UserAgent()
        self.logger = logging.getLogger(__name__)
        self.load_proxies()
        
    def load_proxies(self):
        """Load proxy list from various sources"""
        # Free proxy sources (in production, use paid proxies)
        proxy_sources = [
            self._get_free_proxies,
            self._get_proxy_list,
            self._load_local_proxies
        ]
        
        for source in proxy_sources:
            try:
                proxies = source()
                self.proxies.extend(proxies)
            except Exception as e:
                self.logger.error(f"Failed to load proxies from {source.__name__}: {e}")
        
        self.logger.info(f"Loaded {len(self.proxies)} proxies")
    
    def _get_free_proxies(self) -> List[Dict]:
        """Get free proxies from public sources"""
        proxies = []
        
        try:
            # ProxyScrape API
            response = requests.get(
                "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&simplified=true",
                timeout=30
            )
            
            if response.status_code == 200:
                proxy_lines = response.text.strip().split('\r\n')
                for proxy in proxy_lines[:50]:  # Limit to 50
                    if ':' in proxy:
                        ip, port = proxy.split(':')
                        proxies.append({
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        })
        except Exception as e:
            self.logger.error(f"Failed to get ProxyScrape proxies: {e}")
        
        return proxies
    
    def _get_proxy_list(self) -> List[Dict]:
        """Get proxies from proxy-list.download"""
        proxies = []
        
        try:
            response = requests.get(
                "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
                timeout=30
            )
            
            if response.status_code == 200:
                proxy_lines = response.text.strip().split('\r\n')
                for proxy in proxy_lines[:30]:
                    if ':' in proxy:
                        ip, port = proxy.split(':')
                        proxies.append({
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        })
        except Exception as e:
            self.logger.error(f"Failed to get proxy-list proxies: {e}")
        
        return proxies
    
    def _load_local_proxies(self) -> List[Dict]:
        """Load proxies from local file if exists"""
        proxies = []
        
        try:
            with open('config/proxies/proxy_list.txt', 'r') as f:
                proxy_lines = f.readlines()
                for proxy in proxy_lines:
                    proxy = proxy.strip()
                    if ':' in proxy:
                        ip, port = proxy.split(':')
                        proxies.append({
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        })
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.error(f"Failed to load local proxies: {e}")
        
        return proxies
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Get a random working proxy"""
        available_proxies = [p for p in self.proxies if str(p) not in self.failed_proxies]
        
        if not available_proxies:
            self.logger.warning("No available proxies, resetting failed list")
            self.failed_proxies.clear()
            available_proxies = self.proxies
        
        if available_proxies:
            proxy = random.choice(available_proxies)
            return proxy
        
        return None
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return self.ua.random
    
    def mark_proxy_failed(self, proxy: Dict):
        """Mark a proxy as failed"""
        proxy_str = str(proxy)
        self.failed_proxies.add(proxy_str)
        self.logger.warning(f"Proxy marked as failed: {proxy_str}")
    
    def test_proxy(self, proxy: Dict, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy,
                timeout=timeout,
                headers={'User-Agent': self.get_random_user_agent()}
            )
            
            if response.status_code == 200:
                self.logger.info(f"Proxy test successful: {proxy}")
                return True
                
        except Exception as e:
            self.logger.error(f"Proxy test failed: {proxy} - {e}")
            
        return False
    
    def get_working_proxy(self, max_attempts: int = 5) -> Optional[Dict]:
        """Get a working proxy with testing"""
        for attempt in range(max_attempts):
            proxy = self.get_random_proxy()
            if proxy and self.test_proxy(proxy):
                return proxy
            elif proxy:
                self.mark_proxy_failed(proxy)
                
            time.sleep(1)
        
        return None
    
    def rotate_proxy(self, session: requests.Session) -> bool:
        """Rotate to a new proxy in the session"""
        proxy = self.get_working_proxy()
        if proxy:
            session.proxies.update(proxy)
            session.headers.update({'User-Agent': self.get_random_user_agent()})
            return True
        return False
    
    def get_request_session(self) -> requests.Session:
        """Get a configured requests session with proxy and headers"""
        session = requests.Session()
        
        proxy = self.get_working_proxy()
        if proxy:
            session.proxies.update(proxy)
        
        session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session

class CaptchaBypass:
    def __init__(self, config):
        self.config = config
        self.service = config.CAPTCHA_SERVICE
        self.api_key = config.CAPTCHA_API_KEY
        self.logger = logging.getLogger(__name__)
        
    def solve_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA using 2captcha or anti-captcha"""
        if self.service == '2captcha':
            return self._solve_2captcha(site_key, page_url)
        elif self.service == 'anticaptcha':
            return self._solve_anticaptcha(site_key, page_url)
        return None
    
    def _solve_2captcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve using 2captcha service"""
        try:
            # Submit captcha
            submit_url = f"http://2captcha.com/in.php"
            params = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            response = requests.get(submit_url, params=params)
            result = response.json()
            
            if result.get('status') == 1:
                captcha_id = result.get('request')
                
                # Poll for solution
                for attempt in range(30):  # 3 minutes max
                    time.sleep(6)
                    
                    poll_url = f"http://2captcha.com/res.php"
                    poll_params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': captcha_id,
                        'json': 1
                    }
                    
                    poll_response = requests.get(poll_url, params=poll_params)
                    poll_result = poll_response.json()
                    
                    if poll_result.get('status') == 1:
                        return poll_result.get('request')
                        
                self.logger.error("2captcha timeout")
                
        except Exception as e:
            self.logger.error(f"2captcha solving failed: {e}")
            
        return None
    
    def _solve_anticaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve using anti-captcha service"""
        try:
            # This would use the anti-captcha API
            # Implementation similar to 2captcha but with different API endpoints
            pass
        except Exception as e:
            self.logger.error(f"Anti-captcha solving failed: {e}")
            
        return None

# Advanced stealth techniques
class StealthTechniques:
    def __init__(self, config):
        self.config = config
        self.ua = UserAgent()
        self.logger = logging.getLogger(__name__)
        
    def get_stealth_headers(self) -> Dict:
        """Get headers that mimic real browser behavior"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    def randomize_behavior(self):
        """Randomize behavior patterns"""
        # Random delays
        delay = random.uniform(self.config.REQUEST_DELAY_MIN, self.config.REQUEST_DELAY_MAX)
        time.sleep(delay)
        
        # Random mouse movements (for Selenium)
        # This would be implemented in the browser automation
        
    def mimic_human_behavior(self, driver):
        """Mimic human behavior in browser"""
        try:
            # Random scroll
            scroll_height = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_height});")
            
            # Random mouse movements
            actions = webdriver.ActionChains(driver)
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset).perform()
            
            # Random pause
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            self.logger.error(f"Human behavior mimicry failed: {e}")
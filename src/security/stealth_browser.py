import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import random
import time
import logging
from typing import Optional
from config.config import Config

class StealthBrowser:
    def __init__(self, config: Config):
        self.config = config
        self.ua = UserAgent()
        self.logger = logging.getLogger(__name__)
        
    def get_driver(self, headless: bool = False, proxy: Optional[str] = None) -> uc.Chrome:
        """Get an undetected Chrome driver with stealth configurations"""
        options = uc.ChromeOptions()
        
        # Basic options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--disable-css')
        
        # User agent
        user_agent = self.ua.random
        options.add_argument(f'--user-agent={user_agent}')
        
        # Proxy configuration
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        # Window size randomization
        window_sizes = [(1366, 768), (1920, 1080), (1440, 900), (1536, 864)]
        width, height = random.choice(window_sizes)
        options.add_argument(f'--window-size={width},{height}')
        
        # Headless mode with stealth
        if headless:
            options.add_argument('--headless=new')  # New headless mode
            options.add_argument('--disable-gpu')
        
        # Additional stealth options
        options.add_argument('--disable-blink-features')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values": {
                "cookies": 2,
                "images": 2,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "media_stream": 2,
                "media_stream_mic": 2,
                "media_stream_camera": 2,
                "protocol_handlers": 2,
                "ppapi_broker": 2,
                "automatic_downloads": 2,
                "midi_sysex": 2,
                "push_messaging": 2,
                "ssl_cert_decisions": 2,
                "metro_switch_to_desktop": 2,
                "protected_media_identifier": 2,
                "app_banner": 2,
                "site_engagement": 2,
                "durable_storage": 2
            }
        })
        
        # Create driver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Execute stealth scripts
        self._execute_stealth_scripts(driver)
        
        # Randomize initial behavior
        self._randomize_initial_behavior(driver)
        
        return driver
    
    def _execute_stealth_scripts(self, driver: uc.Chrome):
        """Execute JavaScript to enhance stealth"""
        scripts = [
            # Override navigator.webdriver
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            
            # Override navigator.plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            
            # Override navigator.languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """,
            
            # Override screen properties
            """
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24
            });
            """,
            
            # Add chrome runtime
            """
            window.chrome = {
                runtime: {},
                loadTimes: () => {},
                csi: () => {}
            };
            """,
            
            # Add permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Override device memory
            """
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            """,
            
            # Add platform
            """
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            """
        ]
        
        for script in scripts:
            try:
                driver.execute_script(script)
            except Exception as e:
                self.logger.error(f"Failed to execute stealth script: {e}")
    
    def _randomize_initial_behavior(self, driver: uc.Chrome):
        """Randomize initial browser behavior"""
        # Random delay
        time.sleep(random.uniform(1, 3))
        
        # Random mouse movement
        try:
            action = ActionChains(driver)
            x_offset = random.randint(100, 500)
            y_offset = random.randint(100, 500)
            action.move_by_offset(x_offset, y_offset).perform()
        except:
            pass
        
        # Random scroll
        try:
            scroll_amount = random.randint(100, 300)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        except:
            pass
    
    def human_like_behavior(self, driver: uc.Chrome, min_actions: int = 3, max_actions: int = 8):
        """Perform human-like behaviors"""
        num_actions = random.randint(min_actions, max_actions)
        
        for _ in range(num_actions):
            action_type = random.choice(['scroll', 'mouse_move', 'pause', 'click'])
            
            if action_type == 'scroll':
                self._random_scroll(driver)
            elif action_type == 'mouse_move':
                self._random_mouse_move(driver)
            elif action_type == 'pause':
                self._random_pause()
            elif action_type == 'click':
                self._random_click(driver)
    
    def _random_scroll(self, driver: uc.Chrome):
        """Perform random scrolling"""
        scroll_type = random.choice(['up', 'down', 'top', 'bottom'])
        
        if scroll_type == 'up':
            scroll_amount = random.randint(-300, -50)
        elif scroll_type == 'down':
            scroll_amount = random.randint(50, 300)
        elif scroll_type == 'top':
            driver.execute_script("window.scrollTo(0, 0);")
            return
        else:  # bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            return
        
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 2))
    
    def _random_mouse_move(self, driver: uc.Chrome):
        """Perform random mouse movements"""
        try:
            action = ActionChains(driver)
            
            # Random movement pattern
            movements = random.randint(1, 5)
            for _ in range(movements):
                x_offset = random.randint(-200, 200)
                y_offset = random.randint(-200, 200)
                action.move_by_offset(x_offset, y_offset).perform()
                time.sleep(random.uniform(0.1, 0.5))
                
        except Exception as e:
            self.logger.error(f"Mouse movement failed: {e}")
    
    def _random_pause(self):
        """Pause for random duration"""
        pause_duration = random.uniform(0.5, 3)
        time.sleep(pause_duration)
    
    def _random_click(self, driver: uc.Chrome):
        """Perform random clicks on clickable elements"""
        try:
            # Find clickable elements
            clickable_elements = driver.find_elements(
                By.XPATH,
                "//button | //a | //input[@type='button'] | //div[@onclick]"
            )
            
            if clickable_elements:
                element = random.choice(clickable_elements)
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    time.sleep(random.uniform(0.5, 2))
                    
        except Exception as e:
            self.logger.error(f"Random click failed: {e}")
    
    def wait_for_element_human_like(self, driver: uc.Chrome, by: By, value: str, timeout: int = 10):
        """Wait for element with human-like patience"""
        # Random delay before waiting
        time.sleep(random.uniform(0.5, 2))
        
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            
            # Random delay after finding
            time.sleep(random.uniform(0.3, 1.5))
            return element
            
        except Exception as e:
            self.logger.error(f"Element not found: {value} - {e}")
            return None
    
    def fill_form_like_human(self, driver: uc.Chrome, element, text: str):
        """Fill form field like a human would"""
        try:
            # Clear field
            element.clear()
            time.sleep(random.uniform(0.2, 0.8))
            
            # Type with random delays
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.3))
            
            # Random pause after typing
            time.sleep(random.uniform(0.5, 2))
            
        except Exception as e:
            self.logger.error(f"Human-like form filling failed: {e}")
    
    def close_driver(self, driver: uc.Chrome):
        """Safely close the driver"""
        try:
            # Random delay before closing
            time.sleep(random.uniform(0.5, 1.5))
            
            # Close all tabs
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"Failed to close driver properly: {e}")

# Anti-detection techniques
class AntiDetection:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def randomize_fingerprint(self, driver: uc.Chrome):
        """Randomize browser fingerprint"""
        fingerprint_scripts = [
            # Randomize screen resolution
            """
            Object.defineProperty(screen, 'width', {
                get: () => Math.floor(Math.random() * 200) + 1366
            });
            Object.defineProperty(screen, 'height', {
                get: () => Math.floor(Math.random() * 200) + 768
            });
            """,
            
            # Randomize timezone
            """
            Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                value: () => ({
                    timeZone: ['America/New_York', 'America/Los_Angeles', 'Europe/London'][Math.floor(Math.random() * 3)],
                    locale: 'en-US'
                })
            });
            """,
            
            # Randomize WebGL fingerprint
            """
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter(parameter);
            };
            """
        ]
        
        for script in fingerprint_scripts:
            try:
                driver.execute_script(script)
            except Exception as e:
                self.logger.error(f"Fingerprint randomization failed: {e}")
    
    def bypass_bot_detection(self, driver: uc.Chrome):
        """Advanced bot detection bypass"""
        bypass_scripts = [
            # Hide automation properties
            """
            delete navigator.__proto__.webdriver;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """,
            
            # Add realistic properties
            """
            // Add realistic chrome object
            window.chrome = {
                app: {
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                },
                runtime: {
                    OnInstalledReason: {
                        CHROME_UPDATE: 'chrome_update',
                        INSTALL: 'install',
                        SHARED_MODULE_UPDATE: 'shared_module_update',
                        UPDATE: 'update'
                    },
                    OnRestartRequiredReason: {
                        APP_UPDATE: 'app_update',
                        OS_UPDATE: 'os_update',
                        PERIODIC: 'periodic'
                    },
                    PlatformArch: {
                        ARM: 'arm',
                        ARM64: 'arm64',
                        MIPS: 'mips',
                        MIPS64: 'mips64',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64'
                    },
                    PlatformNaclArch: {
                        ARM: 'arm',
                        MIPS: 'mips',
                        MIPS64: 'mips64',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64'
                    },
                    PlatformOs: {
                        ANDROID: 'android',
                        CROS: 'cros',
                        LINUX: 'linux',
                        MAC: 'mac',
                        OPENBSD: 'openbsd',
                        WIN: 'win'
                    },
                    RequestUpdateCheckStatus: {
                        NO_UPDATE: 'no_update',
                        THROTTLED: 'throttled',
                        UPDATE_AVAILABLE: 'update_available'
                    }
                }
            };
            """,
            
            # Add realistic permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """
        ]
        
        for script in bypass_scripts:
            try:
                driver.execute_script(script)
            except Exception as e:
                self.logger.error(f"Bot detection bypass failed: {e}")
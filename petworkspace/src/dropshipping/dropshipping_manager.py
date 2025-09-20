import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config.config import Config
from src.models import Product, Order, Analytics
from src.security.proxy_manager import ProxyManager

class DropshippingManager:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.proxy_manager = ProxyManager(config)
        self.shopify_session = None
        self.aliexpress_session = None
        self.setup_connections()
        
    def setup_connections(self):
        """Setup API connections"""
        # Shopify API setup
        if self.config.SHOPIFY_CONFIG['api_key']:
            self.shopify_session = self._setup_shopify_session()
        
        # AliExpress API setup (would use their API)
        self.aliexpress_session = self._setup_aliexpress_session()
    
    def _setup_shopify_session(self) -> requests.Session:
        """Setup Shopify API session"""
        session = requests.Session()
        
        # Shopify authentication
        shop_url = self.config.SHOPIFY_CONFIG['store_url']
        api_key = self.config.SHOPIFY_CONFIG['api_key']
        password = self.config.SHOPIFY_CONFIG['password']
        
        session.auth = (api_key, password)
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PetAutomation/1.0'
        })
        
        return session
    
    def _setup_aliexpress_session(self) -> requests.Session:
        """Setup AliExpress API session"""
        session = requests.Session()
        
        # Add proxy rotation
        proxy = self.proxy_manager.get_working_proxy()
        if proxy:
            session.proxies.update(proxy)
        
        session.headers.update({
            'User-Agent': self.proxy_manager.get_random_user_agent(),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def sync_products_shopify(self, products: List[Dict]) -> List[Dict]:
        """Sync products with Shopify store"""
        synced_products = []
        
        if not self.shopify_session:
            self.logger.error("Shopify session not available")
            return synced_products
        
        try:
            shop_url = self.config.SHOPIFY_CONFIG['store_url']
            
            for product in products:
                # Create Shopify product
                shopify_product = self._create_shopify_product(product)
                
                # Upload to Shopify
                response = self.shopify_session.post(
                    f"https://{shop_url}/admin/api/2023-10/products.json",
                    json={"product": shopify_product}
                )
                
                if response.status_code == 201:
                    created_product = response.json()['product']
                    
                    # Add to synced list
                    synced_product = product.copy()
                    synced_product['shopify_id'] = created_product['id']
                    synced_product['sync_status'] = 'success'
                    synced_products.append(synced_product)
                    
                    self.logger.info(f"Synced product to Shopify: {product['name']}")
                else:
                    self.logger.error(f"Failed to sync product: {response.text}")
                    
                time.sleep(random.uniform(1, 3))  # Rate limiting
                
        except Exception as e:
            self.logger.error(f"Shopify sync failed: {e}")
        
        return synced_products
    
    def _create_shopify_product(self, product: Dict) -> Dict:
        """Create Shopify product data structure"""
        # Calculate pricing (5x margin minimum)
        cost_price = product.get('cost_price', product.get('price', 10))
        selling_price = cost_price * random.uniform(5, 8)  # 5-8x margin
        
        return {
            "title": product['name'],
            "body_html": f"<p>{product.get('description', 'Premium pet product')}</p>",
            "vendor": product.get('supplier', 'Pet Supplier'),
            "product_type": product.get('category', 'Pet Supplies'),
            "tags": product.get('tags', ['pet', 'supplies']),
            "variants": [{
                "price": str(selling_price),
                "cost": str(cost_price),
                "sku": f"PET-{int(time.time())}",
                "inventory_management": "shopify",
                "inventory_quantity": random.randint(50, 200)
            }],
            "images": [{
                "src": product.get('image_url', '')
            }] if product.get('image_url') else []
        }
    
    def auto_fulfill_order(self, order: Order) -> bool:
        """Automatically fulfill order through dropshipping supplier"""
        try:
            product = order.product
            
            # Determine supplier
            if product.supplier == 'aliexpress':
                return self._fulfill_via_aliexpress(order)
            elif product.supplier == 'amazon':
                return self._fulfill_via_amazon(order)
            elif product.supplier == 'shopify':
                return self._fulfill_via_shopify(order)
            else:
                # Default to AliExpress
                return self._fulfill_via_aliexpress(order)
                
        except Exception as e:
            self.logger.error(f"Order fulfillment failed: {e}")
            return False
    
    def _fulfill_via_aliexpress(self, order: Order) -> bool:
        """Fulfill order via AliExpress"""
        try:
            # Search for product on AliExpress
            product = order.product
            search_results = self._search_aliexpress_product(product.name)
            
            if not search_results:
                self.logger.error(f"Product not found on AliExpress: {product.name}")
                return False
            
            # Select best supplier (highest rated, fastest shipping)
            best_supplier = self._select_best_aliexpress_supplier(search_results)
            
            # Place order with supplier
            order_result = self._place_aliexpress_order(best_supplier, order)
            
            if order_result['success']:
                # Update order status
                order.status = 'processing'
                order.supplier_order_id = order_result['order_id']
                order.tracking_number = order_result.get('tracking_number')
                
                self.logger.info(f"Order fulfilled via AliExpress: {order.order_id}")
                return True
            else:
                self.logger.error(f"AliExpress order placement failed: {order_result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"AliExpress fulfillment failed: {e}")
            return False
    
    def _search_aliexpress_product(self, product_name: str) -> List[Dict]:
        """Search for product on AliExpress"""
        results = []
        
        try:
            search_url = f"https://www.aliexpress.com/wholesale?SearchText={product_name.replace(' ', '+')}"
            
            response = self.aliexpress_session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                # Parse search results (simplified)
                # In practice, you'd use proper HTML parsing
                results = self._parse_aliexpress_search_results(response.text)
                
        except Exception as e:
            self.logger.error(f"AliExpress search failed: {e}")
        
        return results
    
    def _parse_aliexpress_search_results(self, html: str) -> List[Dict]:
        """Parse AliExpress search results"""
        # This is a simplified parser
        # In practice, use BeautifulSoup or similar
        results = []
        
        try:
            import re
            
            # Extract product data using regex (not recommended for production)
            product_pattern = r'"productId":(\d+),"productTitle":"([^"]+)",.*?,"salePrice":"([^"]+)"'
            matches = re.findall(product_pattern, html)
            
            for match in matches[:10]:  # Limit results
                product_id, title, price = match
                
                result = {
                    'product_id': product_id,
                    'title': title,
                    'price': float(price),
                    'supplier': 'aliexpress',
                    'rating': random.uniform(4.0, 4.8),  # Simulated
                    'shipping_time': random.randint(7, 21),  # Days
                    'orders': random.randint(100, 10000)
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"AliExpress results parsing failed: {e}")
        
        return results
    
    def _select_best_aliexpress_supplier(self, suppliers: List[Dict]) -> Dict:
        """Select best AliExpress supplier based on rating, price, and shipping"""
        best_supplier = None
        best_score = 0
        
        for supplier in suppliers:
            # Calculate score based on multiple factors
            rating_score = supplier.get('rating', 0) * 20  # Weight: 40%
            price_score = (1 / max(supplier.get('price', 1), 1)) * 100  # Weight: 30%
            shipping_score = (30 - min(supplier.get('shipping_time', 30), 30)) * 3.33  # Weight: 30%
            
            total_score = (rating_score * 0.4) + (price_score * 0.3) + (shipping_score * 0.3)
            
            if total_score > best_score:
                best_score = total_score
                best_supplier = supplier
        
        return best_supplier
    
    def _place_aliexpress_order(self, supplier: Dict, order: Order) -> Dict:
        """Place order with AliExpress supplier"""
        try:
            # This would automate the AliExpress ordering process
            # For security and practicality, this is simulated
            
            order_data = {
                'product_id': supplier['product_id'],
                'quantity': order.quantity,
                'customer_name': order.customer_name,
                'customer_address': order.customer_address,
                'shipping_method': 'ePacket',  # Fast and reliable
                'order_notes': f"Dropship order - {order.order_id}"
            }
            
            # Simulate order placement
            time.sleep(random.uniform(2, 4))
            
            # Generate mock order ID and tracking
            order_id = f"AE{int(time.time())}{random.randint(1000, 9999)}"
            tracking_number = f"LP{random.randint(1000000000, 9999999999)}CN"
            
            return {
                'success': True,
                'order_id': order_id,
                'tracking_number': tracking_number,
                'estimated_delivery': datetime.utcnow() + timedelta(days=supplier.get('shipping_time', 14))
            }
            
        except Exception as e:
            self.logger.error(f"AliExpress order placement failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def monitor_inventory_levels(self, db_session) -> List[Dict]:
        """Monitor inventory levels and alert for low stock"""
        low_stock_alerts = []
        
        try:
            # Get products from database
            products = db_session.query(Product).filter_by(is_active=True).all()
            
            for product in products:
                # Check Shopify inventory
                if hasattr(product, 'shopify_id') and product.shopify_id:
                    inventory = self._check_shopify_inventory(product.shopify_id)
                    
                    if inventory and inventory['available'] < 10:  # Low stock threshold
                        alert = {
                            'product_id': product.id,
                            'product_name': product.name,
                            'current_stock': inventory['available'],
                            'threshold': 10,
                            'alert_type': 'low_inventory',
                            'supplier': product.supplier
                        }
                        low_stock_alerts.append(alert)
                        
                        # Auto-reorder if enabled
                        if self.config.get('AUTO_REORDER_ENABLED', False):
                            self._auto_reorder_product(product, inventory)
                
                time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            self.logger.error(f"Inventory monitoring failed: {e}")
        
        return low_stock_alerts
    
    def _check_shopify_inventory(self, shopify_id: int) -> Optional[Dict]:
        """Check Shopify inventory for product"""
        try:
            if not self.shopify_session:
                return None
            
            shop_url = self.config.SHOPIFY_CONFIG['store_url']
            response = self.shopify_session.get(
                f"https://{shop_url}/admin/api/2023-10/products/{shopify_id}.json"
            )
            
            if response.status_code == 200:
                product_data = response.json()['product']
                variant = product_data['variants'][0] if product_data['variants'] else {}
                
                return {
                    'available': variant.get('inventory_quantity', 0),
                    'sku': variant.get('sku', ''),
                    'price': float(variant.get('price', 0))
                }
                
        except Exception as e:
            self.logger.error(f"Shopify inventory check failed: {e}")
        
        return None
    
    def _auto_reorder_product(self, product: Product, inventory: Dict):
        """Automatically reorder low inventory products"""
        try:
            # Calculate reorder quantity
            reorder_quantity = max(50, 100 - inventory['available'])  # Reorder up to 100
            
            # Place supplier order
            if product.supplier == 'aliexpress':
                reorder_result = self._reorder_from_aliexpress(product, reorder_quantity)
            elif product.supplier == 'amazon':
                reorder_result = self._reorder_from_amazon(product, reorder_quantity)
            else:
                reorder_result = False
            
            if reorder_result:
                self.logger.info(f"Auto-reordered {reorder_quantity} units of {product.name}")
                
        except Exception as e:
            self.logger.error(f"Auto-reorder failed for {product.name}: {e}")
    
    def _reorder_from_aliexpress(self, product: Product, quantity: int) -> bool:
        """Reorder from AliExpress supplier"""
        # This would automate the reordering process
        # For now, this is a placeholder
        self.logger.info(f"Reordering {quantity} units from AliExpress: {product.name}")
        return True
    
    def _reorder_from_amazon(self, product: Product, quantity: int) -> bool:
        """Reorder from Amazon supplier"""
        # This would automate the reordering process
        self.logger.info(f"Reordering {quantity} units from Amazon: {product.name}")
        return True
    
    def dynamic_pricing_adjustment(self, db_session) -> List[Dict]:
        """Adjust pricing dynamically based on competition and demand"""
        pricing_updates = []
        
        try:
            products = db_session.query(Product).filter_by(is_active=True).all()
            
            for product in products:
                # Analyze market conditions
                market_analysis = self._analyze_market_conditions(product)
                
                # Calculate optimal price
                optimal_price = self._calculate_optimal_price(product, market_analysis)
                
                # Update if different from current price
                if abs(optimal_price - product.price) > 0.01:  # More than 1 cent difference
                    old_price = product.price
                    product.price = optimal_price
                    
                    # Update Shopify if synced
                    if hasattr(product, 'shopify_id') and product.shopify_id:
                        self._update_shopify_price(product.shopify_id, optimal_price)
                    
                    pricing_update = {
                        'product_id': product.id,
                        'product_name': product.name,
                        'old_price': old_price,
                        'new_price': optimal_price,
                        'change_percent': ((optimal_price - old_price) / old_price) * 100,
                        'reason': market_analysis.get('pricing_reason', 'market_adjustment')
                    }
                    
                    pricing_updates.append(pricing_update)
                    
                    # Log pricing change
                    analytics = Analytics(
                        date=datetime.utcnow(),
                        platform='pricing',
                        metric_type='price_change',
                        value=optimal_price,
                        category=product.category,
                        notes=f"Price changed from ${old_price} to ${optimal_price}"
                    )
                    db_session.add(analytics)
                
                time.sleep(random.uniform(0.5, 1.5))
            
            db_session.commit()
            
        except Exception as e:
            self.logger.error(f"Dynamic pricing adjustment failed: {e}")
            db_session.rollback()
        
        return pricing_updates
    
    def _analyze_market_conditions(self, product: Product) -> Dict:
        """Analyze market conditions for pricing"""
        analysis = {
            'competition_level': 'medium',
            'demand_level': 'medium',
            'seasonal_factor': 1.0,
            'pricing_reason': 'market_analysis'
        }
        
        try:
            # Check competitor prices (simulated)
            competitor_prices = self._get_competitor_prices(product.name)
            
            if competitor_prices:
                avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
                
                if product.price < avg_competitor_price * 0.8:
                    analysis['competition_level'] = 'low'
                    analysis['pricing_reason'] = 'underpriced_vs_competition'
                elif product.price > avg_competitor_price * 1.2:
                    analysis['competition_level'] = 'high'
                    analysis['pricing_reason'] = 'overpriced_vs_competition'
            
            # Check demand indicators (based on analytics)
            recent_sales = self._get_recent_sales_volume(product.id)
            
            if recent_sales > 20:  # High demand
                analysis['demand_level'] = 'high'
                analysis['pricing_reason'] = 'high_demand'
            elif recent_sales < 5:  # Low demand
                analysis['demand_level'] = 'low'
                analysis['pricing_reason'] = 'low_demand'
            
            # Seasonal adjustments
            current_month = datetime.utcnow().month
            
            # Pet supplies peak during spring and holiday seasons
            if current_month in [3, 4, 5, 11, 12]:  # Spring and holidays
                analysis['seasonal_factor'] = 1.1
            elif current_month in [1, 2]:  # Post-holiday
                analysis['seasonal_factor'] = 0.9
            
        except Exception as e:
            self.logger.error(f"Market analysis failed for {product.name}: {e}")
        
        return analysis
    
    def _get_competitor_prices(self, product_name: str) -> List[float]:
        """Get competitor prices (simulated)"""
        # This would scrape competitor prices
        # For now, return simulated data
        base_price = random.uniform(15, 50)
        return [base_price * random.uniform(0.8, 1.2) for _ in range(5)]
    
    def _get_recent_sales_volume(self, product_id: int) -> int:
        """Get recent sales volume for product"""
        # This would query sales data
        # For now, return simulated data
        return random.randint(1, 30)
    
    def _calculate_optimal_price(self, product: Product, market_analysis: Dict) -> float:
        """Calculate optimal price based on market analysis"""
        base_price = product.cost_price * 5  # 5x minimum margin
        
        # Apply market adjustments
        if market_analysis['competition_level'] == 'high':
            base_price *= 0.95  # Reduce price slightly
        elif market_analysis['competition_level'] == 'low':
            base_price *= 1.05  # Increase price slightly
        
        if market_analysis['demand_level'] == 'high':
            base_price *= 1.1  # Increase price for high demand
        elif market_analysis['demand_level'] == 'low':
            base_price *= 0.95  # Reduce price for low demand
        
        # Apply seasonal factor
        base_price *= market_analysis['seasonal_factor']
        
        # Round to attractive price point
        return self._round_to_attractive_price(base_price)
    
    def _round_to_attractive_price(self, price: float) -> float:
        """Round to psychologically attractive price"""
        if price < 10:
            return round(price - 0.01, 2)  # $9.99 instead of $10.00
        elif price < 100:
            return round(price - 0.01, 2)  # $19.99, $29.99, etc.
        else:
            return round(price, 2)  # Round to nearest cent for higher prices
    
    def _update_shopify_price(self, shopify_id: int, new_price: float):
        """Update product price on Shopify"""
        try:
            if not self.shopify_session:
                return
            
            shop_url = self.config.SHOPIFY_CONFIG['store_url']
            
            # Update variant price
            data = {
                "variant": {
                    "price": str(new_price)
                }
            }
            
            response = self.shopify_session.put(
                f"https://{shop_url}/admin/api/2023-10/products/{shopify_id}/variants/{shopify_id}.json",
                json=data
            )
            
            if response.status_code == 200:
                self.logger.info(f"Updated Shopify price for product {shopify_id}: ${new_price}")
            else:
                self.logger.error(f"Failed to update Shopify price: {response.text}")
                
        except Exception as e:
            self.logger.error(f"Shopify price update failed: {e}")

# Advanced order management
class OrderOptimizer:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def optimize_order_routing(self, order: Order) -> Dict:
        """Optimize order routing to best supplier"""
        product = order.product
        
        # Analyze supplier options
        suppliers = self._analyze_supplier_options(product)
        
        # Select best supplier based on multiple factors
        best_supplier = self._select_optimal_supplier(suppliers, order)
        
        return {
            'supplier': best_supplier['name'],
            'estimated_cost': best_supplier['cost'],
            'estimated_delivery': best_supplier['delivery_time'],
            'confidence_score': best_supplier['score']
        }
    
    def _analyze_supplier_options(self, product: Product) -> List[Dict]:
        """Analyze available supplier options"""
        suppliers = []
        
        # AliExpress analysis
        aliexpress_data = {
            'name': 'aliexpress',
            'cost': product.cost_price * 0.8,  # Usually cheaper
            'delivery_time': 14,  # Average 14 days
            'reliability': 0.8,
            'quality_score': 0.7
        }
        suppliers.append(aliexpress_data)
        
        # Amazon analysis (if available)
        amazon_data = {
            'name': 'amazon',
            'cost': product.cost_price * 1.2,  # Usually more expensive
            'delivery_time': 3,  # Fast delivery
            'reliability': 0.95,
            'quality_score': 0.9
        }
        suppliers.append(amazon_data)
        
        return suppliers
    
    def _select_optimal_supplier(self, suppliers: List[Dict], order: Order) -> Dict:
        """Select optimal supplier based on multiple criteria"""
        best_supplier = None
        best_score = 0
        
        for supplier in suppliers:
            # Calculate weighted score
            cost_score = (1 / max(supplier['cost'], 1)) * 100  # Lower cost = higher score
            speed_score = (30 - min(supplier['delivery_time'], 30)) * 3.33  # Faster = higher score
            reliability_score = supplier['reliability'] * 100
            quality_score = supplier['quality_score'] * 100
            
            # Weighted total score
            total_score = (cost_score * 0.3) + (speed_score * 0.3) + (reliability_score * 0.2) + (quality_score * 0.2)
            
            if total_score > best_score:
                best_score = total_score
                best_supplier = supplier
        
        best_supplier['score'] = best_score
        return best_supplier
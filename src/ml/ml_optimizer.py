import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import joblib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from config.config import Config
from src.models import Product, Analytics, Trend, MLModel, create_session

class MLOptimizer:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
    def train_roi_prediction_model(self, db_session) -> Dict:
        """Train ML model to predict ROI for products/niches"""
        try:
            # Collect training data
            training_data = self._collect_roi_training_data(db_session)
            
            if len(training_data) < 50:  # Need minimum data
                self.logger.warning("Insufficient training data for ROI model")
                return {'success': False, 'error': 'Insufficient data'}
            
            # Prepare features and target
            X, y = self._prepare_roi_features(training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train multiple models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear_reg': LinearRegression()
            }
            
            best_model = None
            best_score = -float('inf')
            
            for name, model in models.items():
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test_scaled)
                score = r2_score(y_test, y_pred)
                
                if score > best_score:
                    best_score = score
                    best_model = (name, model)
            
            # Save best model
            model_name = f"roi_predictor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_name] = best_model[1]
            self.scalers[model_name] = scaler
            
            # Save to database
            ml_model = MLModel(
                model_name=model_name,
                model_type='roi_prediction',
                accuracy=best_score,
                parameters={'model_type': best_model[0]},
                training_data_size=len(training_data),
                is_active=True
            )
            db_session.add(ml_model)
            db_session.commit()
            
            # Save model to file
            self._save_model(model_name, best_model[1], scaler)
            
            return {
                'success': True,
                'model_name': model_name,
                'accuracy': best_score,
                'model_type': best_model[0],
                'training_size': len(training_data)
            }
            
        except Exception as e:
            self.logger.error(f"ROI model training failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def predict_product_roi(self, product_data: Dict, model_name: str = None) -> Dict:
        """Predict ROI for a specific product"""
        try:
            if not self.models and not model_name:
                # Load latest model
                model_name = self._get_latest_model('roi_prediction')
            
            if not model_name or model_name not in self.models:
                return {'success': False, 'error': 'Model not available'}
            
            model = self.models[model_name]
            scaler = self.scalers.get(model_name)
            
            # Prepare features
            features = self._prepare_product_features(product_data)
            
            if scaler:
                features = scaler.transform(features.reshape(1, -1))
            
            # Predict ROI
            predicted_roi = model.predict(features)[0]
            
            # Get confidence interval
            confidence_interval = self._calculate_confidence_interval(model, features)
            
            return {
                'success': True,
                'predicted_roi': float(predicted_roi),
                'confidence_lower': float(confidence_interval[0]),
                'confidence_upper': float(confidence_interval[1]),
                'model_name': model_name
            }
            
        except Exception as e:
            self.logger.error(f"ROI prediction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def train_trend_forecasting_model(self, db_session) -> Dict:
        """Train model to forecast trending products/niches"""
        try:
            # Collect trend data
            trend_data = self._collect_trend_data(db_session)
            
            if len(trend_data) < 30:
                return {'success': False, 'error': 'Insufficient trend data'}
            
            # Prepare time series features
            X, y = self._prepare_trend_features(trend_data)
            
            # Train time series model
            from sklearn.linear_model import Ridge
            from sklearn.pipeline import make_pipeline
            
            model = make_pipeline(StandardScaler(), Ridge(alpha=0.1))
            model.fit(X, y)
            
            # Evaluate model
            scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            avg_score = scores.mean()
            
            # Save model
            model_name = f"trend_forecaster_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_name] = model
            
            # Save to database
            ml_model = MLModel(
                model_name=model_name,
                model_type='trend_forecasting',
                accuracy=avg_score,
                parameters={'model_type': 'ridge_regression'},
                training_data_size=len(trend_data),
                is_active=True
            )
            db_session.add(ml_model)
            db_session.commit()
            
            return {
                'success': True,
                'model_name': model_name,
                'accuracy': avg_score,
                'training_size': len(trend_data)
            }
            
        except Exception as e:
            self.logger.error(f"Trend forecasting model training failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def forecast_trending_keywords(self, days_ahead: int = 7) -> List[Dict]:
        """Forecast trending keywords for the next N days"""
        try:
            model_name = self._get_latest_model('trend_forecasting')
            if not model_name:
                return []
            
            model = self.models[model_name]
            
            # Get current trend data
            current_trends = self._get_current_trends()
            
            forecasts = []
            for trend in current_trends:
                # Prepare features for forecasting
                features = self._prepare_forecast_features(trend, days_ahead)
                
                # Predict trend score
                predicted_score = model.predict(features.reshape(1, -1))[0]
                
                forecasts.append({
                    'keyword': trend['keyword'],
                    'current_score': trend['current_score'],
                    'predicted_score': float(predicted_score),
                    'trend_direction': 'up' if predicted_score > trend['current_score'] else 'down',
                    'confidence': abs(predicted_score - trend['current_score']) / trend['current_score']
                })
            
            # Sort by predicted score
            forecasts.sort(key=lambda x: x['predicted_score'], reverse=True)
            
            return forecasts
            
        except Exception as e:
            self.logger.error(f"Trend forecasting failed: {e}")
            return []
    
    def cluster_products_for_targeting(self, products: List[Dict], n_clusters: int = 5) -> List[Dict]:
        """Cluster products for targeted marketing"""
        try:
            # Prepare product features
            features = self._prepare_clustering_features(products)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(features)
            
            # Analyze clusters
            clustered_products = []
            for i, product in enumerate(products):
                cluster_id = clusters[i]
                
                clustered_product = product.copy()
                clustered_product['cluster_id'] = int(cluster_id)
                clustered_product['cluster_label'] = self._generate_cluster_label(cluster_id, products, clusters)
                
                clustered_products.append(clustered_product)
            
            return clustered_products
            
        except Exception as e:
            self.logger.error(f"Product clustering failed: {e}")
            return []
    
    def optimize_content_strategy(self, performance_data: List[Dict]) -> Dict:
        """Optimize content strategy based on performance data"""
        try:
            # Analyze content performance patterns
            df = pd.DataFrame(performance_data)
            
            # Find high-performing content characteristics
            high_performers = df[df['engagement_rate'] > df['engagement_rate'].quantile(0.8)]
            
            # Extract winning patterns
            winning_patterns = {
                'optimal_length': int(high_performers['content_length'].mean()),
                'best_hashtags': self._extract_common_hashtags(high_performers),
                'optimal_posting_times': self._extract_optimal_posting_times(high_performers),
                'best_content_types': high_performers['content_type'].value_counts().head(3).to_dict(),
                'emotional_triggers': self._extract_emotional_triggers(high_performers)
            }
            
            # Generate recommendations
            recommendations = self._generate_content_recommendations(winning_patterns)
            
            return {
                'success': True,
                'patterns': winning_patterns,
                'recommendations': recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Content strategy optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def predict_high_value_customers(self, customer_data: List[Dict]) -> List[Dict]:
        """Predict high-value customers for targeting"""
        try:
            # Prepare customer features
            features = self._prepare_customer_features(customer_data)
            
            # Use clustering to identify high-value segments
            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(features)
            
            # Identify high-value cluster (highest average metrics)
            cluster_values = []
            for i in range(3):
                cluster_customers = [customer_data[j] for j in range(len(customer_data)) if clusters[j] == i]
                avg_value = sum(c.get('lifetime_value', 0) for c in cluster_customers) / len(cluster_customers)
                cluster_values.append(avg_value)
            
            high_value_cluster = cluster_values.index(max(cluster_values))
            
            # Return high-value customers
            high_value_customers = []
            for i, customer in enumerate(customer_data):
                if clusters[i] == high_value_cluster:
                    customer['predicted_value'] = 'high'
                    customer['cluster_id'] = int(high_value_cluster)
                    high_value_customers.append(customer)
            
            return high_value_customers
            
        except Exception as e:
            self.logger.error(f"High-value customer prediction failed: {e}")
            return []
    
    def _collect_roi_training_data(self, db_session) -> List[Dict]:
        """Collect training data for ROI prediction"""
        # Get historical product performance data
        from sqlalchemy import func
        
        results = db_session.query(
            Product.name,
            Product.category,
            Product.price,
            Product.cost_price,
            func.count(Order.id).label('total_orders'),
            func.avg(Order.total_price).label('avg_order_value'),
            func.sum(Order.profit).label('total_profit')
        ).join(Order).group_by(Product.id).all()
        
        training_data = []
        for row in results:
            # Calculate ROI metrics
            total_revenue = row.total_orders * row.avg_order_value
            total_cost = row.total_orders * row.cost_price
            roi = (row.total_profit / max(total_cost, 1)) * 100
            
            training_data.append({
                'product_name': row.name,
                'category': row.category,
                'price': float(row.price),
                'cost_price': float(row.cost_price),
                'total_orders': int(row.total_orders),
                'avg_order_value': float(row.avg_order_value),
                'total_profit': float(row.total_profit),
                'roi': roi
            })
        
        return training_data
    
    def _prepare_roi_features(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for ROI prediction"""
        df = pd.DataFrame(data)
        
        # Feature engineering
        df['price_to_cost_ratio'] = df['price'] / df['cost_price']
        df['orders_per_dollar'] = df['total_orders'] / df['price']
        df['category_encoded'] = LabelEncoder().fit_transform(df['category'])
        
        # Select features
        features = ['price', 'cost_price', 'price_to_cost_ratio', 'orders_per_dollar', 'category_encoded']
        X = df[features].values
        y = df['roi'].values
        
        return X, y
    
    def _prepare_product_features(self, product_data: Dict) -> np.ndarray:
        """Prepare features for product ROI prediction"""
        features = [
            product_data.get('price', 0),
            product_data.get('cost_price', 0),
            product_data.get('price', 1) / max(product_data.get('cost_price', 1), 1),
            product_data.get('orders_per_dollar', 0),
            0  # category_encoded (would need category mapping)
        ]
        
        return np.array(features)
    
    def _collect_trend_data(self, db_session) -> List[Dict]:
        """Collect trend data for forecasting"""
        # Get historical trend data
        from sqlalchemy import func, extract
        
        results = db_session.query(
            Trend.keyword,
            Trend.category,
            Trend.volume,
            Trend.growth_rate,
            Trend.sentiment_score,
            extract('day', Trend.created_at).label('day'),
            extract('month', Trend.created_at).label('month'),
            extract('year', Trend.created_at).label('year')
        ).all()
        
        trend_data = []
        for row in results:
            trend_data.append({
                'keyword': row.keyword,
                'category': row.category,
                'volume': row.volume,
                'growth_rate': row.growth_rate,
                'sentiment_score': row.sentiment_score,
                'day': row.day,
                'month': row.month,
                'year': row.year
            })
        
        return trend_data
    
    def _prepare_trend_features(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for trend forecasting"""
        df = pd.DataFrame(data)
        
        # Feature engineering
        df['volume_ma_7'] = df['volume'].rolling(window=7).mean()
        df['growth_rate_ma_7'] = df['growth_rate'].rolling(window=7).mean()
        df['volume_trend'] = df['volume'].pct_change()
        df['sentiment_volume_interaction'] = df['sentiment_score'] * df['volume']
        
        # Target: next day's volume
        df['target_volume'] = df['volume'].shift(-1)
        
        # Select features
        features = ['volume', 'growth_rate', 'sentiment_score', 'volume_ma_7', 'growth_rate_ma_7', 'volume_trend', 'sentiment_volume_interaction']
        
        # Remove NaN values
        df_clean = df.dropna()
        
        X = df_clean[features].values
        y = df_clean['target_volume'].values
        
        return X, y
    
    def _get_current_trends(self) -> List[Dict]:
        """Get current trending keywords"""
        # This would query current trend data
        # Simulated for now
        keywords = ['dog toys', 'cat food', 'pet grooming', 'dog training', 'cat litter']
        return [
            {
                'keyword': kw,
                'current_score': random.uniform(50, 100),
                'platform': 'google'
            }
            for kw in keywords
        ]
    
    def _prepare_forecast_features(self, trend: Dict, days_ahead: int) -> np.ndarray:
        """Prepare features for trend forecasting"""
        return np.array([
            trend['current_score'],
            days_ahead,
            random.uniform(0.8, 1.2),  # seasonal factor
            random.uniform(0.9, 1.1)   # market factor
        ])
    
    def _prepare_clustering_features(self, products: List[Dict]) -> np.ndarray:
        """Prepare features for product clustering"""
        features = []
        
        for product in products:
            feature_vector = [
                product.get('price', 0),
                product.get('rating', 0),
                product.get('reviews', 0),
                len(product.get('category', '')),
                product.get('commission_rate', 0)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _generate_cluster_label(self, cluster_id: int, products: List[Dict], clusters: np.ndarray) -> str:
        """Generate descriptive label for cluster"""
        cluster_products = [products[i] for i in range(len(products)) if clusters[i] == cluster_id]
        
        if not cluster_products:
            return f"Cluster {cluster_id}"
        
        # Analyze common characteristics
        avg_price = sum(p.get('price', 0) for p in cluster_products) / len(cluster_products)
        avg_rating = sum(p.get('rating', 0) for p in cluster_products) / len(cluster_products)
        
        if avg_price > 50 and avg_rating > 4.5:
            return "Premium High-Quality"
        elif avg_price < 20:
            return "Budget-Friendly"
        elif avg_rating > 4.0:
            return "Popular Well-Rated"
        else:
            return f"Cluster {cluster_id}"
    
    def _calculate_confidence_interval(self, model, features: np.ndarray) -> Tuple[float, float]:
        """Calculate confidence interval for prediction"""
        # Simplified confidence interval calculation
        prediction = model.predict(features)[0]
        margin = prediction * 0.2  # 20% margin
        
        return (prediction - margin, prediction + margin)
    
    def _extract_common_hashtags(self, high_performers: pd.DataFrame) -> List[str]:
        """Extract common hashtags from high-performing content"""
        all_hashtags = []
        
        for hashtags in high_performers['hashtags']:
            if isinstance(hashtags, list):
                all_hashtags.extend(hashtags)
        
        # Count frequency
        from collections import Counter
        hashtag_counts = Counter(all_hashtags)
        
        return [tag for tag, count in hashtag_counts.most_common(10)]
    
    def _extract_optimal_posting_times(self, high_performers: pd.DataFrame) -> List[int]:
        """Extract optimal posting times from high-performing content"""
        posting_times = []
        
        for post_time in high_performers['posting_time']:
            if isinstance(post_time, datetime):
                posting_times.append(post_time.hour)
        
        # Find most common hours
        from collections import Counter
        hour_counts = Counter(posting_times)
        
        return [hour for hour, count in hour_counts.most_common(5)]
    
    def _extract_emotional_triggers(self, high_performers: pd.DataFrame) -> List[str]:
        """Extract emotional triggers from high-performing content"""
        emotional_words = ['love', 'amazing', 'incredible', 'unbelievable', 'shocking', 'heartwarming']
        triggers = []
        
        for content in high_performers['content']:
            if isinstance(content, str):
                words = content.lower().split()
                found_triggers = [word for word in emotional_words if word in words]
                triggers.extend(found_triggers)
        
        from collections import Counter
        trigger_counts = Counter(triggers)
        
        return [trigger for trigger, count in trigger_counts.most_common(5)]
    
    def _generate_content_recommendations(self, patterns: Dict) -> List[str]:
        """Generate actionable content recommendations"""
        recommendations = []
        
        # Length recommendation
        recommendations.append(f"Optimal content length: {patterns['optimal_length']} characters")
        
        # Hashtag recommendations
        recommendations.append(f"Use these hashtags: {', '.join(patterns['best_hashtags'][:5])}")
        
        # Posting time recommendations
        hours = ', '.join(map(str, patterns['optimal_posting_times']))
        recommendations.append(f"Best posting times: {hours}:00")
        
        # Content type recommendations
        top_types = list(patterns['best_content_types'].keys())[:3]
        recommendations.append(f"Focus on content types: {', '.join(top_types)}")
        
        # Emotional trigger recommendations
        recommendations.append(f"Include emotional triggers: {', '.join(patterns['emotional_triggers'])}")
        
        return recommendations
    
    def _prepare_customer_features(self, customer_data: List[Dict]) -> np.ndarray:
        """Prepare features for customer analysis"""
        features = []
        
        for customer in customer_data:
            feature_vector = [
                customer.get('age', 0),
                customer.get('purchase_frequency', 0),
                customer.get('avg_order_value', 0),
                customer.get('lifetime_value', 0),
                len(customer.get('preferred_categories', [])),
                customer.get('engagement_score', 0)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _get_latest_model(self, model_type: str) -> Optional[str]:
        """Get the latest trained model of specified type"""
        db_session = create_session(self.config.DATABASE_URL)
        
        latest_model = db_session.query(MLModel).filter_by(
            model_type=model_type,
            is_active=True
        ).order_by(MLModel.last_trained.desc()).first()
        
        db_session.close()
        
        return latest_model.model_name if latest_model else None
    
    def _save_model(self, model_name: str, model, scaler):
        """Save trained model to file"""
        import os
        
        models_dir = 'models'
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        
        # Save model
        joblib.dump(model, f'{models_dir}/{model_name}_model.pkl')
        
        # Save scaler
        if scaler:
            joblib.dump(scaler, f'{models_dir}/{model_name}_scaler.pkl')
    
    def load_model(self, model_name: str) -> bool:
        """Load model from file"""
        try:
            import os
            
            model_path = f'models/{model_name}_model.pkl'
            scaler_path = f'models/{model_name}_scaler.pkl'
            
            if os.path.exists(model_path):
                self.models[model_name] = joblib.load(model_path)
                
                if os.path.exists(scaler_path):
                    self.scalers[model_name] = joblib.load(scaler_path)
                
                return True
            
        except Exception as e:
            self.logger.error(f"Model loading failed: {e}")
        
        return False

# Advanced analytics and insights
class AnalyticsEngine:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_performance_insights(self, analytics_data: List[Dict]) -> Dict:
        """Generate actionable insights from analytics data"""
        try:
            df = pd.DataFrame(analytics_data)
            
            insights = {
                'revenue_trends': self._analyze_revenue_trends(df),
                'top_performing_products': self._identify_top_products(df),
                'underperforming_products': self._identify_underperforming_products(df),
                'seasonal_patterns': self._detect_seasonal_patterns(df),
                'growth_opportunities': self._identify_growth_opportunities(df),
                'risk_factors': self._identify_risk_factors(df)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Performance insights generation failed: {e}")
            return {}
    
    def _analyze_revenue_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze revenue trends"""
        revenue_data = df[df['metric_type'] == 'revenue']
        
        if revenue_data.empty:
            return {'trend': 'stable', 'change_percent': 0}
        
        # Calculate trend
        recent_revenue = revenue_data.tail(7)['value'].mean()
        previous_revenue = revenue_data.tail(14).head(7)['value'].mean()
        
        if previous_revenue > 0:
            change_percent = ((recent_revenue - previous_revenue) / previous_revenue) * 100
        else:
            change_percent = 0
        
        trend = 'growing' if change_percent > 5 else 'declining' if change_percent < -5 else 'stable'
        
        return {
            'trend': trend,
            'change_percent': change_percent,
            'recent_avg': recent_revenue,
            'previous_avg': previous_revenue
        }
    
    def _identify_top_products(self, df: pd.DataFrame) -> List[Dict]:
        """Identify top performing products"""
        product_performance = df[df['metric_type'] == 'revenue'].groupby('category')['value'].sum().sort_values(ascending=False)
        
        top_products = []
        for category, revenue in product_performance.head(5).items():
            top_products.append({
                'category': category,
                'total_revenue': revenue,
                'performance_score': revenue / product_performance.sum() * 100
            })
        
        return top_products
    
    def _identify_underperforming_products(self, df: pd.DataFrame) -> List[Dict]:
        """Identify underperforming products that need attention"""
        product_performance = df[df['metric_type'] == 'revenue'].groupby('category')['value'].sum()
        
        underperforming = []
        for category, revenue in product_performance.items():
            if revenue < product_performance.mean() * 0.5:  # Less than 50% of average
                underperforming.append({
                    'category': category,
                    'revenue': revenue,
                    'avg_revenue': product_performance.mean(),
                    'improvement_potential': product_performance.mean() - revenue
                })
        
        return underperforming
    
    def _detect_seasonal_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect seasonal patterns in data"""
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        
        monthly_performance = df[df['metric_type'] == 'revenue'].groupby('month')['value'].mean()
        
        peak_months = monthly_performance.nlargest(3).index.tolist()
        low_months = monthly_performance.nsmallest(3).index.tolist()
        
        return {
            'peak_months': peak_months,
            'low_months': low_months,
            'seasonality_strength': monthly_performance.std() / monthly_performance.mean()
        }
    
    def _identify_growth_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        """Identify growth opportunities"""
        opportunities = []
        
        # High engagement, low conversion products
        engagement_data = df[df['metric_type'] == 'engagement']
        conversion_data = df[df['metric_type'] == 'conversion']
        
        if not engagement_data.empty and not conversion_data.empty:
            high_engagement = engagement_data[engagement_data['value'] > engagement_data['value'].quantile(0.8)]
            low_conversion = conversion_data[conversion_data['value'] < conversion_data['value'].quantile(0.2)]
            
            for category in high_engagement['category'].unique():
                if category in low_conversion['category'].values:
                    opportunities.append({
                        'type': 'engagement_conversion_gap',
                        'category': category,
                        'opportunity': 'High engagement but low conversion - optimize CTAs'
                    })
        
        return opportunities
    
    def _identify_risk_factors(self, df: pd.DataFrame) -> List[Dict]:
        """Identify potential risk factors"""
        risks = []
        
        # Declining trends
        revenue_trends = self._analyze_revenue_trends(df)
        if revenue_trends['trend'] == 'declining' and revenue_trends['change_percent'] < -10:
            risks.append({
                'type': 'declining_revenue',
                'severity': 'high',
                'impact': revenue_trends['change_percent'],
                'recommendation': 'Investigate cause of revenue decline'
            })
        
        # High dependency on single category
        category_revenue = df[df['metric_type'] == 'revenue'].groupby('category')['value'].sum()
        total_revenue = category_revenue.sum()
        
        for category, revenue in category_revenue.items():
            if revenue / total_revenue > 0.5:  # More than 50% from single category
                risks.append({
                    'type': 'revenue_concentration',
                    'category': category,
                    'dependency_percent': (revenue / total_revenue) * 100,
                    'recommendation': 'Diversify product portfolio'
                })
        
        return risks
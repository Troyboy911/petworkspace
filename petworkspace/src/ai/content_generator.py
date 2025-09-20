import openai
import groq
from typing import List, Dict, Optional
import json
import random
import re
from datetime import datetime
import logging
from config.config import Config
from src.models import Content, Product, Trend

class AIContentGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI clients
        self.openai_client = None
        self.groq_client = None
        
        if config.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            
        if config.GROQ_API_KEY:
            self.groq_client = groq.Groq(api_key=config.GROQ_API_KEY)
        
        # Pet-related content templates
        self.templates = {
            'viral_post': [
                "🔥 {pet_owners} are going CRAZY over this {product}! My {pet_type} hasn't stopped playing with it since we got it! 🐕\n\n{benefit_statement}\n\n👇 Link in bio!",
                "I couldn't believe what happened when I gave my {pet_type} this {product}... 😱\n\n{transformation_story}\n\n{pet_type} parents NEED to see this! ⬇️",
                "Your {pet_type} will thank you for this {product} 🐾\n\n{benefit_statement}\n\nTrust me, this is a game-changer! 🔗",
                "STOP scrolling! 🛑 This {product} changed my {pet_type}'s life! {benefit_statement} 🚀\n\nEvery {pet_type} deserves this! 💝"
            ],
            'product_description': [
                "Give your {pet_type} the {benefit} they deserve with our premium {product}. {key_features}\n\n✅ {benefit_1}\n✅ {benefit_2}\n✅ {benefit_3}\n\nOrder now and see the difference! 🛒",
                "Transform your {pet_type}'s {aspect} with this amazing {product}. {emotional_hook}\n\n{specifications}\n\n{guarantee_statement} 💯"
            ],
            'email_campaign': [
                "Subject: Your {pet_type} needs this {product} 🐾\n\nHi {name},\n\nI noticed you're a proud {pet_type} parent like me! I wanted to share something that completely changed {pet_pronoun} life...\n\n{story_hook}\n\n{benefit_statement}\n\n{call_to_action}\n\nBest regards,\n{sender_name}",
                "{name}, is your {pet_type} getting the {benefit} they deserve? 🤔\n\n{problem_statement}\n\n{solution_statement}\n\n{urgency_statement}\n\n{call_to_action}"
            ],
            'tiktok_caption': [
                "POV: Your {pet_type} discovers the {product} 🎬 {hashtags}",
                "This {product} had my {pet_type} like... 😂 {hashtags}",
                "{pet_type} reaction to {product} = PRICELESS! 😍 {hashtags}",
                "Don't walk, RUN to get this for your {pet_type}! 🏃‍♂️💨 {hashtags}"
            ]
        }
        
        # High-engagement hashtags
        self.hashtag_sets = {
            'pet_supplies': ['#petsoftiktok', '#dogsoftiktok', '#catsoftiktok', '#petproducts', '#petcare', '#fyp', '#viral'],
            'dog_products': ['#doglovers', '#doglife', '#dogmom', '#dogdad', '#puppylove', '#dogtoys', '#dogaccessories'],
            'cat_products': ['#catlovers', '#catlife', '#catmom', '#catdad', '#kitten', '#cattoys', '#cataccessories'],
            'general_pet': ['#petlover', '#furbaby', '#petparent', '#animallover', '#petcare', '#pethealth']
        }
    
    def generate_viral_post(self, product: Product, trend: Optional[Trend] = None, platform: str = 'twitter') -> Dict:
        """Generate viral social media post"""
        try:
            # Get product details
            product_name = product.name
            product_category = product.category
            
            # Determine pet type and benefits
            pet_type = self._extract_pet_type(product_category)
            benefits = self._generate_benefits(product_name, pet_type)
            
            # Select template based on platform
            if platform == 'tiktok':
                template = random.choice(self.templates['tiktok_caption'])
            else:
                template = random.choice(self.templates['viral_post'])
            
            # Generate content using AI
            if self.openai_client:
                content = self._generate_with_openai(template, product, pet_type, benefits, platform)
            elif self.groq_client:
                content = self._generate_with_groq(template, product, pet_type, benefits, platform)
            else:
                content = self._generate_manual(template, product, pet_type, benefits, platform)
            
            # Generate hashtags
            hashtags = self._generate_hashtags(product_category, platform)
            
            return {
                'content': content,
                'hashtags': hashtags,
                'platform': platform,
                'content_type': 'viral_post',
                'product_id': product.id,
                'trend_id': trend.id if trend else None
            }
            
        except Exception as e:
            self.logger.error(f"Viral post generation failed: {e}")
            return self._generate_fallback_post(product, platform)
    
    def generate_product_description(self, product: Product, seo_keywords: List[str] = None) -> Dict:
        """Generate SEO-optimized product description"""
        try:
            product_name = product.name
            category = product.category
            
            # Extract key features and benefits
            features = self._extract_product_features(product_name, category)
            
            # Generate SEO keywords if not provided
            if not seo_keywords:
                seo_keywords = self._generate_seo_keywords(product_name, category)
            
            # Create description using AI
            if self.openai_client:
                description = self._generate_description_with_openai(product, features, seo_keywords)
            elif self.groq_client:
                description = self._generate_description_with_groq(product, features, seo_keywords)
            else:
                description = self._generate_description_manual(product, features, seo_keywords)
            
            return {
                'content': description,
                'seo_keywords': seo_keywords,
                'content_type': 'product_description',
                'product_id': product.id
            }
            
        except Exception as e:
            self.logger.error(f"Product description generation failed: {e}")
            return self._generate_fallback_description(product)
    
    def generate_email_campaign(self, product: Product, email_type: str = 'product_launch') -> Dict:
        """Generate email campaign content"""
        try:
            pet_type = self._extract_pet_type(product.category)
            benefits = self._generate_benefits(product.name, pet_type)
            
            # Select email template
            template = random.choice(self.templates['email_campaign'])
            
            if self.openai_client:
                email_content = self._generate_email_with_openai(template, product, pet_type, benefits, email_type)
            elif self.groq_client:
                email_content = self._generate_email_with_groq(template, product, pet_type, benefits, email_type)
            else:
                email_content = self._generate_email_manual(template, product, pet_type, benefits, email_type)
            
            return {
                'content': email_content,
                'subject': self._extract_subject(email_content),
                'content_type': 'email_campaign',
                'product_id': product.id,
                'email_type': email_type
            }
            
        except Exception as e:
            self.logger.error(f"Email campaign generation failed: {e}")
            return self._generate_fallback_email(product, email_type)
    
    def _generate_with_openai(self, template: str, product: Product, pet_type: str, benefits: List[str], platform: str) -> str:
        """Generate content using OpenAI"""
        prompt = f"""
        Create a viral social media post for {platform} using this template:
        {template}
        
        Product: {product.name}
        Pet Type: {pet_type}
        Benefits: {', '.join(benefits)}
        Category: {product.category}
        
        Requirements:
        - Make it engaging and shareable
        - Include emotional triggers
        - Add urgency or FOMO
        - Keep platform-appropriate length
        - Include call-to-action
        - Make it sound authentic and personal
        
        Generate the post content:
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a viral social media content creator specializing in pet products."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_with_groq(self, template: str, product: Product, pet_type: str, benefits: List[str], platform: str) -> str:
        """Generate content using Groq"""
        prompt = f"""
        Create engaging social media content for {platform}:
        Template: {template}
        Product: {product.name}
        Pet Type: {pet_type}
        Benefits: {', '.join(benefits)}
        
        Make it viral and engaging!
        """
        
        response = self.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You create viral pet product content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_manual(self, template: str, product: Product, pet_type: str, benefits: List[str], platform: str) -> str:
        """Manual content generation fallback"""
        replacements = {
            '{pet_type}': pet_type,
            '{product}': product.name,
            '{pet_owners}': f"{pet_type} owners",
            '{benefit_statement}': f"This {product.name} will make your {pet_type} happier and healthier!",
            '{transformation_story}': f"Within minutes of using this {product.name}, I noticed a complete transformation in my {pet_type}'s behavior!",
            '{hashtags}': ' '.join(self._generate_hashtags(product.category, platform)[:5])
        }
        
        content = template
        for key, value in replacements.items():
            content = content.replace(key, value)
        
        return content
    
    def _generate_hashtags(self, category: str, platform: str) -> List[str]:
        """Generate platform-specific hashtags"""
        base_hashtags = []
        
        # Determine relevant hashtag set
        if 'dog' in category.lower():
            base_hashtags = self.hashtag_sets['dog_products'].copy()
        elif 'cat' in category.lower():
            base_hashtags = self.hashtag_sets['cat_products'].copy()
        else:
            base_hashtags = self.hashtag_sets['general_pet'].copy()
        
        # Add platform-specific hashtags
        if platform == 'tiktok':
            base_hashtags.extend(['#fyp', '#foryou', '#viral', '#trending'])
        elif platform == 'instagram':
            base_hashtags.extend(['#instapet', '#petstagram', '#petsofinstagram'])
        
        # Shuffle and limit based on platform
        random.shuffle(base_hashtags)
        
        if platform == 'twitter':
            return base_hashtags[:3]  # Twitter prefers fewer hashtags
        elif platform == 'instagram':
            return base_hashtags[:20]  # Instagram allows more
        else:
            return base_hashtags[:10]
    
    def _extract_pet_type(self, category: str) -> str:
        """Extract pet type from category"""
        category_lower = category.lower()
        if 'dog' in category_lower:
            return 'dog'
        elif 'cat' in category_lower:
            return 'cat'
        elif 'bird' in category_lower:
            return 'bird'
        elif 'fish' in category_lower:
            return 'fish'
        else:
            return 'pet'
    
    def _generate_benefits(self, product_name: str, pet_type: str) -> List[str]:
        """Generate product benefits"""
        benefits = [
            f"Keeps your {pet_type} happy and healthy",
            f"Perfect for {pet_type} entertainment",
            f"Essential for {pet_type} care",
            f"Made with {pet_type}-safe materials"
        ]
        
        # Add product-specific benefits
        if 'toy' in product_name.lower():
            benefits.extend([
                f"Reduces {pet_type} anxiety",
                f"Promotes healthy chewing habits",
                f"Keeps {pet_type} mentally stimulated"
            ])
        elif 'food' in product_name.lower():
            benefits.extend([
                f"Nutritious and delicious",
                f"Supports {pet_type} immune system",
                f"Made with natural ingredients"
            ])
        elif 'grooming' in product_name.lower():
            benefits.extend([
                f"Keeps {pet_type} coat shiny",
                f"Reduces shedding",
                f"Gentle on {pet_type} skin"
            ])
        
        return benefits
    
    def _generate_seo_keywords(self, product_name: str, category: str) -> List[str]:
        """Generate SEO keywords"""
        base_keywords = [
            product_name.lower(),
            category.lower(),
            'pet supplies',
            'pet products',
            'pet accessories'
        ]
        
        # Add long-tail keywords
        seo_keywords = base_keywords + [
            f"best {product_name.lower()}",
            f"{product_name.lower()} for pets",
            f"affordable {category.lower()}",
            f"premium {product_name.lower()}",
            f"{category.lower()} online",
            f"buy {product_name.lower()}"
        ]
        
        return list(set(seo_keywords))
    
    def generate_ab_test_variants(self, base_content: Dict, num_variants: int = 2) -> List[Dict]:
        """Generate A/B test variants"""
        variants = []
        
        for i in range(num_variants):
            variant = base_content.copy()
            
            # Modify content slightly
            if i == 0:  # Variant A - Emotional appeal
                variant['content'] = self._add_emotional_appeal(variant['content'])
                variant['variant_type'] = 'emotional'
            elif i == 1:  # Variant B - Urgency/Scarcity
                variant['content'] = self._add_urgency_scarcity(variant['content'])
                variant['variant_type'] = 'urgency'
            
            variant['variant_id'] = f"variant_{i+1}"
            variants.append(variant)
        
        return variants
    
    def _add_emotional_appeal(self, content: str) -> str:
        """Add emotional appeal to content"""
        emotional_phrases = [
            "Your furry friend deserves the best",
            "Show them how much you care",
            "Because they give us unconditional love",
            "Make every moment special",
            "Create lasting memories together"
        ]
        
        phrase = random.choice(emotional_phrases)
        return f"{phrase}\n\n{content}"
    
    def _add_urgency_scarcity(self, content: str) -> str:
        """Add urgency and scarcity to content"""
        urgency_phrases = [
            "⚡ Limited time offer!",
            "🔥 Going viral - Get yours before they're gone!",
            "⏰ Only a few left in stock!",
            "🚨 Don't miss out - Pet parents are stocking up!",
            "💨 Selling fast - Grab yours today!"
        ]
        
        phrase = random.choice(urgency_phrases)
        return f"{phrase}\n\n{content}"
    
    def _generate_fallback_post(self, product: Product, platform: str) -> Dict:
        """Generate fallback content when AI fails"""
        return {
            'content': f"Check out this amazing {product.name}! Perfect for your pet! 🐾",
            'hashtags': ['#petproducts', '#petcare', '#fyp'],
            'platform': platform,
            'content_type': 'viral_post',
            'product_id': product.id
        }
    
    def _generate_fallback_description(self, product: Product) -> Dict:
        """Generate fallback product description"""
        return {
            'content': f"{product.name} - Premium quality pet product. Perfect for your furry friends!",
            'seo_keywords': [product.name.lower(), 'pet supplies'],
            'content_type': 'product_description',
            'product_id': product.id
        }
    
    def _generate_fallback_email(self, product: Product, email_type: str) -> Dict:
        """Generate fallback email content"""
        return {
            'content': f"Hi there!\n\nWe found an amazing product your pet will love - {product.name}! Check it out today!",
            'subject': f"Your pet needs this {product.name}!",
            'content_type': 'email_campaign',
            'product_id': product.id,
            'email_type': email_type
        }
    
    def _extract_subject(self, email_content: str) -> str:
        """Extract subject line from email content"""
        lines = email_content.split('\n')
        for line in lines:
            if line.lower().startswith('subject:'):
                return line.replace('Subject:', '').strip()
        
        # Fallback subject
        return "Amazing pet product you need to see! 🐾"

# Content optimization functions
class ContentOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimize content for specific platform"""
        if platform == 'twitter':
            return self._optimize_for_twitter(content)
        elif platform == 'instagram':
            return self._optimize_for_instagram(content)
        elif platform == 'tiktok':
            return self._optimize_for_tiktok(content)
        elif platform == 'reddit':
            return self._optimize_for_reddit(content)
        
        return content
    
    def _optimize_for_twitter(self, content: str) -> str:
        """Optimize for Twitter's character limit and style"""
        # Ensure under 280 characters
        if len(content) > 280:
            content = content[:277] + "..."
        
        return content
    
    def _optimize_for_instagram(self, content: str) -> str:
        """Optimize for Instagram format"""
        # Add line breaks for readability
        content = content.replace('. ', '.\n\n')
        return content
    
    def _optimize_for_tiktok(self, content: str) -> str:
        """Optimize for TikTok's style"""
        # Make it more casual and trendy
        content = content.replace('!', '🎉')
        content = content.replace('amazing', '🔥')
        return content
    
    def _optimize_for_reddit(self, content: str) -> str:
        """Optimize for Reddit's community style"""
        # Add more context and detail
        return f"Hey fellow pet lovers! {content}\n\nWhat's your experience with products like this?"
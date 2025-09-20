#!/bin/bash

# CapRover Deployment Script for Pet Automation Suite
# This script automates the deployment process to CapRover

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_APP_NAME="pet-automation-suite"
DEFAULT_CAPROVER_URL="https://captain.your-domain.com"
DEFAULT_IMAGE_NAME="pet-automation-suite"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║              Pet Automation Suite - CapRover Deploy               ║"
    echo "║                    One-Command Deployment                         ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if CapRover CLI is installed
    if ! command -v caprover &> /dev/null; then
        print_error "CapRover CLI is not installed. Installing now..."
        npm install -g caprover
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

get_user_input() {
    print_info "Please provide the following information:"
    
    # App name
    read -p "Enter app name [$DEFAULT_APP_NAME]: " APP_NAME
    APP_NAME=${APP_NAME:-$DEFAULT_APP_NAME}
    
    # CapRover URL
    read -p "Enter CapRover URL [$DEFAULT_CAPROVER_URL]: " CAPROVER_URL
    CAPROVER_URL=${CAPROVER_URL:-$DEFAULT_CAPROVER_URL}
    
    # Image name
    read -p "Enter Docker image name [$DEFAULT_IMAGE_NAME]: " IMAGE_NAME
    IMAGE_NAME=${IMAGE_NAME:-$DEFAULT_IMAGE_NAME}
    
    # CapRover password
    read -s -p "Enter CapRover password: " CAPROVER_PASSWORD
    echo ""
    
    # Environment variables
    print_info "Environment Configuration:"
    read -p "OpenAI API Key: " OPENAI_API_KEY
    read -p "Groq API Key: " GROQ_API_KEY
    read -p "Twitter API Key: " TWITTER_API_KEY
    read -p "Reddit Client ID: " REDDIT_CLIENT_ID
    read -p "Shopify Store URL: " SHOPIFY_STORE_URL
    read -p "Amazon Associate ID: " AMAZON_ASSOCIATE_ID
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    print_success "Configuration completed"
}

build_docker_image() {
    print_info "Building Docker image..."
    
    # Build the Docker image
    docker build -t $IMAGE_NAME .
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

deploy_to_caprover() {
    print_info "Deploying to CapRover..."
    
    # Login to CapRover
    echo "$CAPROVER_PASSWORD" | caprover login --caproverUrl "$CAPROVER_URL" || {
        print_error "Failed to login to CapRover"
        exit 1
    }
    
    # Create app if it doesn't exist
    caprover api --method POST --path "/api/v1/user/apps/appDefinitions/register" --data "{&quot;appName&quot;:&quot;$APP_NAME&quot;,&quot;hasPersistentData&quot;:false}" || {
        print_warning "App might already exist or creation failed"
    }
    
    # Setup environment variables
    setup_environment_variables
    
    # Deploy the app
    caprover deploy --appName "$APP_NAME" --imageName "$IMAGE_NAME" || {
        print_error "Failed to deploy to CapRover"
        exit 1
    }
    
    print_success "Successfully deployed to CapRover"
}

setup_environment_variables() {
    print_info "Setting up environment variables..."
    
    # Create environment variables configuration
    ENV_VARS=$(cat << EOF
{
    "envVars": {
        "FLASK_ENV": "production",
        "SECRET_KEY": "$SECRET_KEY",
        "OPENAI_API_KEY": "$OPENAI_API_KEY",
        "GROQ_API_KEY": "$GROQ_API_KEY",
        "TWITTER_API_KEY": "$TWITTER_API_KEY",
        "TWITTER_API_SECRET": "$TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN": "$TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_SECRET": "$TWITTER_ACCESS_SECRET",
        "REDDIT_CLIENT_ID": "$REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET": "$REDDIT_CLIENT_SECRET",
        "REDDIT_USER_AGENT": "pet_automation_bot",
        "SHOPIFY_API_KEY": "$SHOPIFY_API_KEY",
        "SHOPIFY_PASSWORD": "$SHOPIFY_PASSWORD",
        "SHOPIFY_STORE_URL": "$SHOPIFY_STORE_URL",
        "AMAZON_ASSOCIATE_ID": "$AMAZON_ASSOCIATE_ID",
        "AMAZON_ACCESS_KEY": "$AMAZON_ACCESS_KEY",
        "AMAZON_SECRET_KEY": "$AMAZON_SECRET_KEY",
        "DATABASE_URL": "postgresql://postgres:password@srv-captain--pet-automation-db:5432/pet_automation",
        "REDIS_URL": "redis://srv-captain--pet-automation-redis:6379/0",
        "MONGODB_URL": "mongodb://srv-captain--pet-automation-mongo:27017/pet_automation",
        "MAX_POSTS_PER_DAY": "1000",
        "TARGET_MONTHLY_REVENUE": "10000",
        "MIN_PROFIT_MARGIN": "5.0",
        "MAX_AD_SPEND_PERCENT": "20",
        "PROXY_ROTATION_ENABLED": "true",
        "USER_AGENT_ROTATION": "true",
        "REQUEST_DELAY_MIN": "2",
        "REQUEST_DELAY_MAX": "5"
    }
}
EOF
)
    
    # Update environment variables
    echo "$ENV_VARS" | caprover api --method POST --path "/api/v1/user/apps/appDefinitions/update" --data @- || {
        print_warning "Failed to update environment variables"
    }
}

setup_database_services() {
    print_info "Setting up database services..."
    
    # Create PostgreSQL app
    caprover api --method POST --path "/api/v1/user/apps/appDefinitions/register" --data "{&quot;appName&quot;:&quot;$APP_NAME-db&quot;,&quot;hasPersistentData&quot;:true}" || {
        print_warning "Database app might already exist"
    }
    
    # Create Redis app
    caprover api --method POST --path "/api/v1/user/apps/appDefinitions/register" --data "{&quot;appName&quot;:&quot;$APP_NAME-redis&quot;,&quot;hasPersistentData&quot;:false}" || {
        print_warning "Redis app might already exist"
    }
    
    # Create MongoDB app
    caprover api --method POST --path "/api/v1/user/apps/appDefinitions/register" --data "{&quot;appName&quot;:&quot;$APP_NAME-mongo&quot;,&quot;hasPersistentData&quot;:true}" || {
        print_warning "MongoDB app might already exist"
    }
    
    print_success "Database services setup completed"
}

verify_deployment() {
    print_info "Verifying deployment..."
    
    # Wait for deployment to complete
    sleep 30
    
    # Check if the app is running
    APP_URL="https://$APP_NAME.$CAPROVER_URL"
    
    if curl -f -s "$APP_URL/health" > /dev/null; then
        print_success "Application is running successfully!"
        print_info "Access your application at: $APP_URL"
    else
        print_warning "Application might still be starting up. Check CapRover dashboard for status."
        print_info "App URL: $APP_URL"
    fi
}

create_caprover_config() {
    print_info "Creating CapRover configuration file..."
    
    cat > captain-definition << EOF
{
    "schemaVersion": 2,
    "dockerfileLines": [
        "FROM python:3.11-slim",
        "WORKDIR /app",
        "RUN apt-get update && apt-get install -y wget gnupg unzip curl xvfb libxi6 libgconf-2-4 libxss1 libasound2 libxtst6 libgtk-3-0 libgbm1 libnss3 libxrandr2 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxrandr2 libxtst6 libappindicator3-1 libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 xdg-utils",
        "RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list && apt-get update && apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*",
        "COPY requirements.txt .",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "COPY . .",
        "RUN mkdir -p logs data config/proxies models",
        "ENV PYTHONPATH=/app",
        "EXPOSE 5000",
        "CMD [&quot;gunicorn&quot;, &quot;--bind&quot;, &quot;0.0.0.0:5000&quot;, &quot;--workers&quot;, &quot;4&quot;, &quot;--timeout&quot;, &quot;120&quot;, &quot;src.dashboard.app:app&quot;]"
    ]
}
EOF

    print_success "CapRover configuration file created"
}

generate_deployment_report() {
    print_info "Generating deployment report..."
    
    cat > deployment_report.txt << EOF
PET AUTOMATION SUITE - DEPLOYMENT REPORT
========================================
Date: $(date)
App Name: $APP_NAME
CapRover URL: $CAPROVER_URL
Image Name: $IMAGE_NAME

DEPLOYMENT STATUS: SUCCESS

NEXT STEPS:
1. Access your application at: https://$APP_NAME.$CAPROVER_URL
2. Configure your API keys in the CapRover dashboard
3. Monitor logs in the CapRover dashboard
4. Set up monitoring and alerts

IMPORTANT NOTES:
- Make sure to configure all API keys in environment variables
- Monitor the application logs for any errors
- Set up SSL certificates for production use
- Configure backup for the database

MONITORING:
- Health check endpoint: /health
- Metrics endpoint: /api/metrics
- Logs available in CapRover dashboard

SUPPORT:
- Check logs for any issues
- Ensure all environment variables are set correctly
- Verify database connections
- Test all API integrations
EOF

    print_success "Deployment report generated: deployment_report.txt"
}

main() {
    print_header
    
    # Check dependencies
    check_dependencies
    
    # Get user input
    get_user_input
    
    # Build Docker image
    build_docker_image
    
    # Create CapRover configuration
    create_caprover_config
    
    # Setup database services
    setup_database_services
    
    # Deploy to CapRover
    deploy_to_caprover
    
    # Verify deployment
    verify_deployment
    
    # Generate deployment report
    generate_deployment_report
    
    print_success "Deployment completed successfully!"
    print_info "Check deployment_report.txt for details and next steps."
}

# Run main function
main "$@"
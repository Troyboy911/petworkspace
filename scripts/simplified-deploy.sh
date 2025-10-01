#!/bin/bash

# Simplified CapRover Deployment Script for Pet Automation Suite
# This script provides an easier deployment process

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}     Pet Automation Suite - Simplified Deployment        ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Check if caprover CLI is installed
if ! command -v caprover &> /dev/null; then
    echo "Installing CapRover CLI..."
    npm install -g caprover
fi

# Get user input
read -p "Enter your CapRover server URL (e.g., https://captain.yourdomain.com): " CAPROVER_URL
read -p "Enter your CapRover admin password: " CAPROVER_PASSWORD
read -p "Enter app name [pet-automation]: " APP_NAME
APP_NAME=${APP_NAME:-pet-automation}

# Login to CapRover
echo "Logging in to CapRover..."
echo "$CAPROVER_PASSWORD" | caprover login --caproverUrl "$CAPROVER_URL"

# Create app if it doesn't exist
echo "Creating app on CapRover..."
caprover api --method POST --path "/api/v1/user/apps/appDefinitions/register" --data "{&quot;appName&quot;:&quot;$APP_NAME&quot;,&quot;hasPersistentData&quot;:false}" || {
    echo "App might already exist, continuing..."
}

# Set up environment variables
echo "Setting up environment variables..."
read -p "Enter OpenAI API Key: " OPENAI_API_KEY
read -p "Enter Shopify API Key (or press Enter to skip): " SHOPIFY_API_KEY
read -p "Enter Amazon Associate ID (or press Enter to skip): " AMAZON_ASSOCIATE_ID

# Generate a random secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create environment variables configuration
ENV_VARS=$(cat << EOF
{
    "appName": "$APP_NAME",
    "envVars": {
        "FLASK_ENV": "production",
        "SECRET_KEY": "$SECRET_KEY",
        "OPENAI_API_KEY": "$OPENAI_API_KEY",
        "SHOPIFY_API_KEY": "$SHOPIFY_API_KEY",
        "AMAZON_ASSOCIATE_ID": "$AMAZON_ASSOCIATE_ID",
        "MAX_POSTS_PER_DAY": "1000",
        "TARGET_MONTHLY_REVENUE": "10000",
        "MIN_PROFIT_MARGIN": "5.0"
    }
}
EOF
)

# Update environment variables
echo "$ENV_VARS" | caprover api --method POST --path "/api/v1/user/apps/appDefinitions/update" --data @-

# Deploy the app
echo "Deploying app to CapRover..."
caprover deploy --appName "$APP_NAME"

echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${GREEN}Your app will be available at: https://$APP_NAME.$CAPROVER_URL${NC}"
echo ""
echo "IMPORTANT: The first deployment may take several minutes as it builds the Docker image."
echo "You can check the deployment status in the CapRover dashboard."
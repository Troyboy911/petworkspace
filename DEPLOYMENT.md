# Pet Automation Suite - Deployment Guide

This guide provides detailed instructions for deploying the Pet Automation Suite using CapRover or Docker Compose.

## Prerequisites

- A server with Docker installed
- CapRover installed on your server (for CapRover deployment)
- Domain name pointing to your server (for CapRover deployment)
- API keys for various services (OpenAI, social media platforms, etc.)

## Option 1: Easy Deployment with CapRover

CapRover is a free and open-source PaaS that makes deployment simple. Follow these steps for a one-command deployment:

### 1. Install CapRover CLI

```bash
npm install -g caprover
```

### 2. Use the Simplified Deployment Script

We've created a simplified deployment script that handles everything for you:

```bash
# Make the script executable
chmod +x scripts/simplified-deploy.sh

# Run the deployment script
./scripts/simplified-deploy.sh
```

The script will:
- Install CapRover CLI if needed
- Log in to your CapRover server
- Create the app
- Configure environment variables
- Deploy the application

### 3. Follow the Interactive Prompts

The script will ask for:
- Your CapRover server URL
- CapRover admin password
- App name (defaults to "pet-automation")
- Essential API keys

### 4. Access Your Application

Once deployed, your application will be available at:
```
https://your-app-name.your-domain.com
```

## Option 2: Manual CapRover Deployment

If you prefer to deploy manually:

### 1. Log in to CapRover

```bash
caprover login
```

### 2. Create a New App

```bash
caprover api --method POST --path "/api/v1/user/apps/appDefinitions/register" --data '{"appName":"pet-automation","hasPersistentData":false}'
```

### 3. Set Environment Variables

Create a file named `env-vars.json` with your environment variables:

```json
{
  "appName": "pet-automation",
  "envVars": {
    "FLASK_ENV": "production",
    "SECRET_KEY": "your-secret-key",
    "OPENAI_API_KEY": "your-openai-key",
    "SHOPIFY_API_KEY": "your-shopify-key",
    "AMAZON_ASSOCIATE_ID": "your-amazon-id",
    "MAX_POSTS_PER_DAY": "1000",
    "TARGET_MONTHLY_REVENUE": "10000",
    "MIN_PROFIT_MARGIN": "5.0"
  }
}
```

Then apply these variables:

```bash
caprover api --method POST --path "/api/v1/user/apps/appDefinitions/update" --data @env-vars.json
```

### 4. Deploy the App

```bash
caprover deploy --appName pet-automation
```

## Option 3: Docker Compose Deployment

For deployment using Docker Compose:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pet-automation-suite.git
cd pet-automation-suite
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Start the Services

```bash
docker-compose up -d
```

This will start all the services defined in `docker-compose.yml`.

### 4. Access the Dashboard

The dashboard will be available at:
```
http://your-server-ip:5000
```

## Troubleshooting

### Common Issues

#### 1. Deployment Fails

Check the logs:
```bash
caprover logs --appName pet-automation
```

#### 2. Database Connection Issues

Verify database services are running:
```bash
docker-compose ps
```

#### 3. API Connection Issues

Check that all API keys are correctly set in environment variables.

#### 4. Application Not Responding

Check the health endpoint:
```
https://your-app-name.your-domain.com/health
```

## Scaling the Application

### Horizontal Scaling

To scale the application horizontally:

```bash
# Using Docker Compose
docker-compose up -d --scale worker=3 --scale scraper=2
```

### Vertical Scaling

For vertical scaling, adjust the resources in your CapRover dashboard or modify the Docker Compose file.

## Monitoring

The application provides a health check endpoint at `/health` that returns the current status of all components.

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
docker exec -t pet-automation-db pg_dump -U postgres pet_automation > backup.sql

# MongoDB backup
docker exec -t pet-automation-mongo mongodump --out /dump
```

### Restore from Backup

```bash
# PostgreSQL restore
cat backup.sql | docker exec -i pet-automation-db psql -U postgres pet_automation

# MongoDB restore
docker exec -t pet-automation-mongo mongorestore /dump
```

## Security Considerations

- Always use strong passwords for database services
- Keep API keys secure and rotate them regularly
- Use HTTPS for all connections
- Implement proper firewall rules

## Support

For additional support, please refer to the documentation or create an issue in the GitHub repository.
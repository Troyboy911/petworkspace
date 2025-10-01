#!/bin/bash

# Pet Automation Suite - Local Testing Script
# This script helps you quickly test the application locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Pet Automation Suite - Local Test${NC}"
echo -e "${BLUE}================================${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 installed${NC}"

# Step 2: Check if .env exists
echo -e "\n${YELLOW}Step 2: Checking environment configuration...${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys before continuing${NC}"
    echo -e "${YELLOW}  Press Enter to continue or Ctrl+C to exit and edit .env${NC}"
    read -r
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Step 3: Check if port 5000 is available
echo -e "\n${YELLOW}Step 3: Checking port availability...${NC}"

if port_in_use 5000; then
    echo -e "${RED}❌ Port 5000 is already in use${NC}"
    echo "Please stop the service using port 5000 or change PORT in .env"
    exit 1
fi
echo -e "${GREEN}✓ Port 5000 is available${NC}"

# Step 4: Start Docker services
echo -e "\n${YELLOW}Step 4: Starting Docker services...${NC}"

echo "Starting databases (PostgreSQL, Redis, MongoDB)..."
docker-compose up -d postgres redis mongodb

echo "Waiting for databases to be ready..."
sleep 10

# Check if databases are running
if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    docker-compose logs postgres
    exit 1
fi

if docker-compose ps | grep -q "redis.*Up"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis failed to start${NC}"
    docker-compose logs redis
    exit 1
fi

if docker-compose ps | grep -q "mongodb.*Up"; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
else
    echo -e "${RED}❌ MongoDB failed to start${NC}"
    docker-compose logs mongodb
    exit 1
fi

# Step 5: Start application
echo -e "\n${YELLOW}Step 5: Starting application...${NC}"

echo "Starting Flask app and Celery workers..."
docker-compose up -d app celery-worker celery-beat

echo "Waiting for application to start..."
sleep 15

# Step 6: Health check
echo -e "\n${YELLOW}Step 6: Running health checks...${NC}"

MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Application is healthy${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "Waiting for application... (attempt $RETRY_COUNT/$MAX_RETRIES)"
        sleep 3
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Application failed to start${NC}"
    echo "Checking logs..."
    docker-compose logs app
    exit 1
fi

# Step 7: Display status
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✓ All services are running!${NC}"
echo -e "${GREEN}================================${NC}\n"

echo -e "${BLUE}Service Status:${NC}"
docker-compose ps

echo -e "\n${BLUE}Access Points:${NC}"
echo -e "  Dashboard: ${GREEN}http://localhost:5000${NC}"
echo -e "  Health Check: ${GREEN}http://localhost:5000/health${NC}"
echo -e "  API Docs: ${GREEN}http://localhost:5000/api/docs${NC}"

echo -e "\n${BLUE}Useful Commands:${NC}"
echo -e "  View logs: ${YELLOW}docker-compose logs -f app${NC}"
echo -e "  Stop services: ${YELLOW}docker-compose down${NC}"
echo -e "  Restart services: ${YELLOW}docker-compose restart${NC}"
echo -e "  View all logs: ${YELLOW}docker-compose logs -f${NC}"

echo -e "\n${BLUE}Testing Endpoints:${NC}"
echo -e "  Test trends: ${YELLOW}curl http://localhost:5000/api/test/trends${NC}"
echo -e "  Test content: ${YELLOW}curl http://localhost:5000/api/test/content${NC}"
echo -e "  Test social: ${YELLOW}curl http://localhost:5000/api/test/social${NC}"

# Step 8: Open browser (optional)
echo -e "\n${YELLOW}Would you like to open the dashboard in your browser? (y/n)${NC}"
read -r OPEN_BROWSER

if [ "$OPEN_BROWSER" = "y" ] || [ "$OPEN_BROWSER" = "Y" ]; then
    if command_exists xdg-open; then
        xdg-open http://localhost:5000
    elif command_exists open; then
        open http://localhost:5000
    elif command_exists start; then
        start http://localhost:5000
    else
        echo -e "${YELLOW}Please open http://localhost:5000 in your browser${NC}"
    fi
fi

echo -e "\n${GREEN}Local testing environment is ready! 🚀${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop watching logs, or run 'docker-compose down' to stop all services${NC}\n"

# Follow logs
docker-compose logs -f app
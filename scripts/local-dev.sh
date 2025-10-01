#!/bin/bash

# Local Development Setup Script
# This script sets up the development environment on localhost

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Pet Automation Suite - Local Development Setup                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p logs data config/proxies models temp

# Setup environment variables
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp .env.example .env
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/your_secret_key_here/$SECRET_KEY/g" .env
    rm .env.bak 2>/dev/null || true
    
    echo -e "${YELLOW}⚠ Please edit .env file with your API keys${NC}"
fi

# Initialize database
echo -e "${BLUE}Initializing database...${NC}"
python3 << EOF
from src.models import create_database, create_session
from config.config import Config

try:
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization: {e}")
EOF

echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${BLUE}To start the development server:${NC}"
echo -e "  1. Activate virtual environment: ${GREEN}source venv/bin/activate${NC}"
echo -e "  2. Start Flask app: ${GREEN}python src/dashboard/app.py${NC}"
echo -e "  3. Or use: ${GREEN}flask run --host=0.0.0.0 --port=5000${NC}"
echo ""
echo -e "${BLUE}To start background workers:${NC}"
echo -e "  ${GREEN}celery -A src.celery_app worker --loglevel=info${NC}"
echo ""
echo -e "${BLUE}Access the dashboard at:${NC} ${GREEN}http://localhost:5000${NC}"
# Local Testing Guide - Pet Automation Suite

This guide will help you test the Pet Automation Suite on your local machine before deploying to production.

## Prerequisites

Before you start, make sure you have:
- Python 3.9 or higher installed
- Docker and Docker Compose installed (optional, but recommended)
- Git installed

## Option 1: Quick Test with Docker (Recommended - 5 minutes)

This is the easiest way to test everything locally with all dependencies.

### Step 1: Clone the Repository
```bash
git clone https://github.com/Troyboy911/petworkspace.git
cd petworkspace
```

### Step 2: Create Environment File
```bash
cp .env.example .env
```

Edit `.env` and add your API keys (you can use dummy keys for basic testing):
```bash
# Minimum required for basic testing
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your_secret_key_here

# Optional for full testing
TWITTER_API_KEY=your_twitter_key
REDDIT_CLIENT_ID=your_reddit_id
# ... etc
```

### Step 3: Start All Services
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- MongoDB for analytics
- The main Flask application
- Celery workers for background tasks

### Step 4: Access the Dashboard
Open your browser and go to:
```
http://localhost:5000
```

You should see the Pet Automation Suite dashboard!

### Step 5: Check Service Health
```bash
# Check if all containers are running
docker-compose ps

# View logs
docker-compose logs -f app

# Check specific service
docker-compose logs -f celery-worker
```

### Step 6: Stop Services
```bash
docker-compose down
```

---

## Option 2: Manual Setup (15 minutes)

If you prefer to run without Docker or want more control:

### Step 1: Clone and Setup
```bash
git clone https://github.com/Troyboy911/petworkspace.git
cd petworkspace
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Local Databases

**Option A: Use Docker for databases only**
```bash
# Start only database services
docker-compose up -d postgres redis mongodb
```

**Option B: Install databases locally**
- Install PostgreSQL, Redis, and MongoDB on your system
- Update `.env` with your local database URLs

### Step 5: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
# Database URLs (if using Docker databases)
DATABASE_URL=postgresql://petuser:petpass123@localhost:5432/petautomation
REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017/petautomation

# Flask settings
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-for-testing

# API Keys (add your real keys or use dummy ones for testing)
OPENAI_API_KEY=sk-test-key
GROQ_API_KEY=gsk-test-key
```

### Step 6: Initialize Database
```bash
# Run database migrations
python -m src.database.init_db
```

### Step 7: Start the Application

**Terminal 1 - Flask App:**
```bash
python -m src.app
```

**Terminal 2 - Celery Worker:**
```bash
celery -A src.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
celery -A src.tasks.celery_app beat --loglevel=info
```

### Step 8: Access Dashboard
Open browser to: `http://localhost:5000`

---

## Testing Features

### 1. Test Trend Scraping
```bash
# Via dashboard: Click "Scrape Trends" button
# Or via API:
curl -X POST http://localhost:5000/api/trends/scrape
```

### 2. Test Content Generation
```bash
# Via dashboard: Click "Generate Content" button
# Or via API:
curl -X POST http://localhost:5000/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{"trend": "cat toys", "platform": "twitter"}'
```

### 3. Test Social Media Posting
```bash
# Via dashboard: Click "Post to Social" button
# Or via API:
curl -X POST http://localhost:5000/api/social/post \
  -H "Content-Type: application/json" \
  -d '{"content": "Test post", "platforms": ["twitter"]}'
```

### 4. View Analytics
Navigate to: `http://localhost:5000/analytics`

### 5. Check System Health
Navigate to: `http://localhost:5000/health`

---

## Testing Without API Keys

You can test the basic functionality without real API keys:

1. **Mock Mode**: Set in `.env`:
```bash
MOCK_MODE=true
```

2. **Test Endpoints**: Use the `/test` endpoints:
```bash
# Test trend scraping (mock data)
curl http://localhost:5000/api/test/trends

# Test content generation (mock data)
curl http://localhost:5000/api/test/content

# Test social posting (mock data)
curl http://localhost:5000/api/test/social
```

---

## Common Issues & Solutions

### Issue 1: Port Already in Use
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change the port in .env
PORT=8000
```

### Issue 2: Database Connection Error
```bash
# Check if databases are running
docker-compose ps

# Restart database services
docker-compose restart postgres redis mongodb

# Check database logs
docker-compose logs postgres
```

### Issue 3: Module Not Found
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 4: Permission Denied
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or run with bash
bash scripts/local-dev.sh
```

### Issue 5: Celery Not Starting
```bash
# Check Redis is running
redis-cli ping

# Clear Celery tasks
celery -A src.tasks.celery_app purge

# Restart Celery worker
celery -A src.tasks.celery_app worker --loglevel=debug
```

---

## Quick Test Script

Use the provided script for automated testing:

```bash
# Make it executable
chmod +x scripts/local-dev.sh

# Run it
./scripts/local-dev.sh
```

This script will:
1. Check prerequisites
2. Setup environment
3. Start all services
4. Run basic health checks
5. Open dashboard in browser

---

## Performance Testing

### Load Testing with Apache Bench
```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Ubuntu/Debian
brew install httpd  # Mac

# Test dashboard endpoint
ab -n 100 -c 10 http://localhost:5000/

# Test API endpoint
ab -n 100 -c 10 http://localhost:5000/api/health
```

### Monitor Resource Usage
```bash
# With Docker
docker stats

# Without Docker
htop  # or top
```

---

## Development Tips

### 1. Hot Reload
Flask auto-reloads when you change code (in DEBUG mode):
```bash
FLASK_ENV=development
DEBUG=True
```

### 2. View Logs
```bash
# Docker logs
docker-compose logs -f app

# Local logs
tail -f logs/app.log
```

### 3. Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U petuser -d petautomation

# Access Redis
docker-compose exec redis redis-cli

# Access MongoDB
docker-compose exec mongodb mongosh
```

### 4. Run Tests
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_trends.py

# Run with coverage
pytest --cov=src tests/
```

---

## Next Steps

Once local testing is successful:

1. **Push to GitHub**: Your code will auto-deploy to Hostinger
2. **Monitor Deployment**: Check GitHub Actions for deployment status
3. **Verify Production**: Access your production URL
4. **Configure API Keys**: Add real API keys in production `.env`

---

## Need Help?

- Check logs: `docker-compose logs -f`
- View health status: `http://localhost:5000/health`
- Check Celery tasks: `http://localhost:5000/celery/tasks`
- Review documentation: `README.md`, `DEPLOYMENT.md`

Happy Testing! 🚀
# 🧪 Complete Testing Guide

## Quick Start (30 seconds)

```bash
# 1. Clone the repo
git clone https://github.com/Troyboy911/petworkspace.git
cd petworkspace

# 2. Run the test script
./test.sh
```

That's it! The dashboard will open at `http://localhost:5000`

---

## What You Need

### Minimum Requirements
- **Docker** & **Docker Compose** installed
- **5GB** free disk space
- **4GB** RAM

### Optional (for full functionality)
- API keys for:
  - OpenAI (for content generation)
  - Twitter/X (for social posting)
  - Reddit (for trend scraping)
  - Amazon Associates (for affiliate links)

---

## Testing Methods

### Method 1: One-Command Test (Easiest) ⭐

```bash
./test.sh
```

This script:
1. Creates `.env` if missing
2. Starts all Docker services
3. Waits for startup
4. Opens dashboard in browser
5. Shows you the logs

**Stop testing:**
```bash
docker-compose -f docker-compose.local.yml down
```

---

### Method 2: Step-by-Step Test

#### Step 1: Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (optional for basic testing)
nano .env
```

#### Step 2: Start Services
```bash
# Start all services
docker-compose -f docker-compose.local.yml up -d

# Or start specific services
docker-compose -f docker-compose.local.yml up -d postgres redis mongodb
```

#### Step 3: Check Status
```bash
# View running containers
docker-compose -f docker-compose.local.yml ps

# Check logs
docker-compose -f docker-compose.local.yml logs -f app
```

#### Step 4: Access Dashboard
Open browser: `http://localhost:5000`

#### Step 5: Stop Services
```bash
docker-compose -f docker-compose.local.yml down
```

---

### Method 3: Manual Testing (No Docker)

If you prefer not to use Docker:

#### Step 1: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

#### Step 2: Install Databases
You'll need to install locally:
- PostgreSQL 15+
- Redis 7+
- MongoDB 6+

#### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env with your local database URLs
```

#### Step 4: Initialize Database
```bash
python -m src.database.init_db
```

#### Step 5: Start Services

**Terminal 1 - Flask App:**
```bash
python -m src.app
```

**Terminal 2 - Celery Worker:**
```bash
celery -A src.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```bash
celery -A src.tasks.celery_app beat --loglevel=info
```

---

## Testing Features

### 1. Dashboard Access
```
http://localhost:5000
```

You should see:
- Revenue metrics
- Active campaigns
- System health
- Quick action buttons

### 2. Health Check
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "mongodb": "connected"
}
```

### 3. Test Endpoints

#### Test Trend Scraping
```bash
curl http://localhost:5000/api/test/trends
```

#### Test Content Generation
```bash
curl -X POST http://localhost:5000/api/test/content \
  -H "Content-Type: application/json" \
  -d '{"trend": "cat toys"}'
```

#### Test Social Posting
```bash
curl -X POST http://localhost:5000/api/test/social \
  -H "Content-Type: application/json" \
  -d '{"content": "Test post"}'
```

### 4. View Logs

```bash
# All logs
docker-compose -f docker-compose.local.yml logs -f

# Specific service
docker-compose -f docker-compose.local.yml logs -f app
docker-compose -f docker-compose.local.yml logs -f celery-worker

# Last 100 lines
docker-compose -f docker-compose.local.yml logs --tail=100 app
```

### 5. Database Access

#### PostgreSQL
```bash
docker-compose -f docker-compose.local.yml exec postgres psql -U petuser -d petautomation
```

#### Redis
```bash
docker-compose -f docker-compose.local.yml exec redis redis-cli
```

#### MongoDB
```bash
docker-compose -f docker-compose.local.yml exec mongodb mongosh
```

---

## Testing Without API Keys

You can test basic functionality without real API keys:

### Option 1: Use Mock Mode
In `.env`:
```bash
MOCK_MODE=true
```

### Option 2: Use Test Endpoints
These endpoints return mock data:
```bash
curl http://localhost:5000/api/test/trends
curl http://localhost:5000/api/test/content
curl http://localhost:5000/api/test/social
```

---

## Common Issues

### Issue: Port 5000 Already in Use
```bash
# Find what's using the port
lsof -i :5000

# Kill it
kill -9 <PID>

# Or change port in .env
PORT=8000
```

### Issue: Docker Services Won't Start
```bash
# Stop all containers
docker-compose -f docker-compose.local.yml down

# Remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.local.yml down -v

# Rebuild and start
docker-compose -f docker-compose.local.yml up -d --build
```

### Issue: Application Shows Error
```bash
# Check logs
docker-compose -f docker-compose.local.yml logs app

# Restart app
docker-compose -f docker-compose.local.yml restart app

# Check database connection
docker-compose -f docker-compose.local.yml exec postgres pg_isready -U petuser
```

### Issue: Celery Tasks Not Running
```bash
# Check Celery worker logs
docker-compose -f docker-compose.local.yml logs celery-worker

# Restart Celery
docker-compose -f docker-compose.local.yml restart celery-worker celery-beat

# Check Redis connection
docker-compose -f docker-compose.local.yml exec redis redis-cli ping
```

---

## Performance Testing

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test dashboard (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:5000/

# Test API endpoint
ab -n 100 -c 10 http://localhost:5000/api/health
```

### Monitor Resources
```bash
# Docker stats
docker stats

# Specific container
docker stats pet-app-local
```

---

## Useful Commands

### Container Management
```bash
# Start all services
docker-compose -f docker-compose.local.yml up -d

# Stop all services
docker-compose -f docker-compose.local.yml down

# Restart specific service
docker-compose -f docker-compose.local.yml restart app

# View running containers
docker-compose -f docker-compose.local.yml ps

# Remove everything (including volumes)
docker-compose -f docker-compose.local.yml down -v
```

### Logs
```bash
# Follow all logs
docker-compose -f docker-compose.local.yml logs -f

# Follow specific service
docker-compose -f docker-compose.local.yml logs -f app

# Last 50 lines
docker-compose -f docker-compose.local.yml logs --tail=50

# Since specific time
docker-compose -f docker-compose.local.yml logs --since 10m
```

### Debugging
```bash
# Execute command in container
docker-compose -f docker-compose.local.yml exec app bash

# Check environment variables
docker-compose -f docker-compose.local.yml exec app env

# Test database connection
docker-compose -f docker-compose.local.yml exec app python -c "from src.database import db; print(db.engine.url)"
```

---

## Next Steps After Testing

Once local testing is successful:

1. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add local testing setup"
   ```

2. **Push to GitHub**
   ```bash
   git push origin main
   ```

3. **Auto-Deploy to Hostinger**
   - GitHub Actions will automatically deploy
   - Check deployment status in GitHub Actions tab

4. **Verify Production**
   - Access your production URL
   - Check health endpoint
   - Monitor logs

---

## Tips for Effective Testing

1. **Start Small**: Test with mock data first
2. **Check Logs**: Always check logs when something fails
3. **Use Health Endpoints**: Monitor `/health` for system status
4. **Test Incrementally**: Test one feature at a time
5. **Clean Up**: Stop services when not testing to free resources

---

## Getting Help

- **Logs**: Check `docker-compose logs -f`
- **Health**: Visit `http://localhost:5000/health`
- **Documentation**: See `README.md`, `DEPLOYMENT.md`
- **GitHub Issues**: Report bugs on GitHub

---

## Summary

**Quickest way to test:**
```bash
./test.sh
```

**Stop testing:**
```bash
docker-compose -f docker-compose.local.yml down
```

**View logs:**
```bash
docker-compose -f docker-compose.local.yml logs -f
```

Happy Testing! 🚀
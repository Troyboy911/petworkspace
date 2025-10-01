# 🚀 Coolify Deployment Guide

## 📋 Overview

Coolify is a self-hosted deployment platform that makes deploying applications easy. This guide will help you deploy the Pet Automation Suite using Coolify.

---

## 🔑 Your Coolify Information

### Application Name
```
calm-crane-t8o0gosgwc8ok8s4sc8ok040
```

### SSH Keys

**Private Key** (for GitHub Actions):
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACD/jmjVbueqtuA6oPIf6VmwPxx2lZ/aexgb1+hhk1JNZQAAAKCgneRXoJ3k
VwAAAAtzc2gtZWQyNTUxOQAAACD/jmjVbueqtuA6oPIf6VmwPxx2lZ/aexgb1+hhk1JNZQ
AAAEAqDSbieUxe2BvubKA3FUzYWkHhOp6fYNyFGc13sH53Lv+OaNVu56q24Dqg8h/pWbA/
HHaVn9p7GBvX6GGTUk1lAAAAF3BocHNlY2xpYi1nZW5lcmF0ZWQta2V5AQIDBAUG
-----END OPENSSH PRIVATE KEY-----
```

**Public Key**:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP+OaNVu56q24Dqg8h/pWbA/HHaVn9p7GBvX6GGTUk1l coolify-generated-ssh-key
```

---

## 🎯 Deployment Methods

### Method 1: GitHub Actions (Automated) ⭐

This is the easiest method - automatic deployment on every push!

#### Step 1: Add GitHub Secrets

1. Go to: https://github.com/Troyboy911/petworkspace/settings/secrets/actions

2. Add these secrets:

**Secret 1: COOLIFY_SSH_KEY**
- Name: `COOLIFY_SSH_KEY`
- Value: Copy the private key above (including BEGIN and END lines)

**Secret 2: COOLIFY_HOST**
- Name: `COOLIFY_HOST`
- Value: Your Coolify server IP or domain

#### Step 2: Push to GitHub

```bash
git add .
git commit -m "Deploy to Coolify"
git push origin main
```

The deployment will start automatically!

#### Step 3: Monitor Deployment

Watch the deployment at:
https://github.com/Troyboy911/petworkspace/actions

---

### Method 2: Coolify Dashboard (Manual)

#### Step 1: Access Coolify Dashboard

1. Log in to your Coolify instance
2. Find your application: `calm-crane-t8o0gosgwc8ok8s4sc8ok040`

#### Step 2: Configure Git Repository

1. Go to your application settings
2. Set Git Repository: `https://github.com/Troyboy911/petworkspace.git`
3. Set Branch: `main`
4. Set Build Pack: `Docker Compose`

#### Step 3: Configure Environment Variables

Add these environment variables in Coolify:

```bash
# Database URLs (will be auto-configured by Docker Compose)
DATABASE_URL=postgresql://petuser:petpass123@postgres:5432/petautomation
REDIS_URL=redis://redis:6379/0
MONGODB_URL=mongodb://mongodb:27017/petautomation

# Flask Settings
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# API Keys (add your real keys)
OPENAI_API_KEY=your_openai_key
TWITTER_API_KEY=your_twitter_key
REDDIT_CLIENT_ID=your_reddit_id
# ... etc
```

#### Step 4: Deploy

Click "Deploy" button in Coolify dashboard!

---

### Method 3: Coolify CLI

If you have Coolify CLI installed:

```bash
# Deploy to Coolify
coolify deploy \
  --app calm-crane-t8o0gosgwc8ok8s4sc8ok040 \
  --git https://github.com/Troyboy911/petworkspace.git \
  --branch main
```

---

## 🔧 Configuration

### Docker Compose Setup

Coolify will automatically detect and use your `docker-compose.yml` file.

The file includes:
- PostgreSQL database
- Redis cache
- MongoDB analytics
- Flask application
- Celery workers
- Celery beat scheduler

### Port Configuration

Default ports:
- **Application**: 5000
- **PostgreSQL**: 5432
- **Redis**: 6379
- **MongoDB**: 27017

Coolify will automatically expose port 5000 to the internet.

### Domain Configuration

In Coolify dashboard:
1. Go to your application
2. Click "Domains"
3. Add your custom domain
4. Coolify will automatically configure SSL with Let's Encrypt

---

## 📊 Monitoring

### View Logs

**In Coolify Dashboard:**
1. Go to your application
2. Click "Logs"
3. View real-time logs

**Via SSH:**
```bash
# SSH into Coolify server
ssh root@your-coolify-server

# View application logs
cd /var/www/pet-automation/pet-automation-suite
docker-compose logs -f
```

### Health Checks

Coolify automatically monitors:
- Application health endpoint: `/health`
- Container status
- Resource usage

### Metrics

View in Coolify dashboard:
- CPU usage
- Memory usage
- Network traffic
- Disk usage

---

## 🔄 Updates & Redeployment

### Automatic Updates (GitHub Actions)

Every push to `main` branch automatically:
1. Triggers GitHub Actions
2. Connects to Coolify server
3. Pulls latest code
4. Rebuilds containers
5. Restarts services

### Manual Redeploy

**Via Coolify Dashboard:**
1. Go to your application
2. Click "Redeploy"

**Via SSH:**
```bash
ssh root@your-coolify-server
cd /var/www/pet-automation/pet-automation-suite
git pull origin main
docker-compose up -d --build
```

---

## 🆘 Troubleshooting

### Issue: Deployment Fails

**Check Coolify Logs:**
1. Go to Coolify dashboard
2. View deployment logs
3. Look for error messages

**Common Issues:**
- Missing environment variables
- Port conflicts
- Insufficient resources
- Docker build errors

### Issue: Application Not Starting

**Check Container Logs:**
```bash
ssh root@your-coolify-server
cd /var/www/pet-automation/pet-automation-suite
docker-compose logs app
```

**Restart Services:**
```bash
docker-compose restart
```

### Issue: Database Connection Errors

**Check Database Status:**
```bash
docker-compose ps
docker-compose logs postgres
```

**Restart Database:**
```bash
docker-compose restart postgres
```

---

## 🔐 Security

### SSH Access

Coolify uses SSH keys for secure access:
- Private key stored in GitHub Secrets
- Public key added to Coolify server
- No passwords needed

### Environment Variables

Store sensitive data in:
1. Coolify dashboard (encrypted)
2. `.env` file on server (not in Git)
3. GitHub Secrets (for CI/CD)

### SSL/TLS

Coolify automatically:
- Generates SSL certificates
- Renews certificates
- Redirects HTTP to HTTPS

---

## 📈 Scaling

### Horizontal Scaling

In Coolify dashboard:
1. Go to your application
2. Increase number of replicas
3. Coolify handles load balancing

### Vertical Scaling

Adjust resources in `docker-compose.yml`:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 🎯 Best Practices

### 1. Use Environment Variables
Never hardcode secrets in code

### 2. Monitor Resources
Check CPU/Memory usage regularly

### 3. Regular Backups
Coolify can backup:
- Database data
- Application files
- Configuration

### 4. Health Checks
Ensure `/health` endpoint works

### 5. Logging
Use structured logging for debugging

---

## 📚 Additional Resources

### Coolify Documentation
- Official Docs: https://coolify.io/docs
- GitHub: https://github.com/coollabsio/coolify

### Your Application
- Repository: https://github.com/Troyboy911/petworkspace
- App Name: calm-crane-t8o0gosgwc8ok8s4sc8ok040

---

## ✅ Quick Start Checklist

- [ ] Add `COOLIFY_SSH_KEY` to GitHub Secrets
- [ ] Add `COOLIFY_HOST` to GitHub Secrets
- [ ] Configure environment variables in Coolify
- [ ] Push code to GitHub (triggers deployment)
- [ ] Monitor deployment in GitHub Actions
- [ ] Verify application is running
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate (automatic)
- [ ] Configure monitoring and alerts

---

## 🎉 Success!

Once deployed, your application will be accessible at:
- Coolify-provided domain
- Your custom domain (if configured)
- Direct IP access on port 5000

**Happy Deploying with Coolify!** 🚀
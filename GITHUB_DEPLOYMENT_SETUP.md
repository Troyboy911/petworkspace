# 🚀 GitHub Auto-Deployment Setup Guide

This guide will help you set up automatic deployment from GitHub to your Hostinger VPS.

## 📋 Prerequisites

- GitHub account with access to repository: `Troyboy911/petworkspace`
- Hostinger VPS at: `89.116.159.31`
- SSH access to VPS as `root`

---

## 🔑 Step 1: Add SSH Key to Your VPS

You need to add the deployment SSH key to your Hostinger VPS so GitHub Actions can connect.

### Copy this public key:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPHDyT7svNRoUAIz0uM5eeFtSET1EjsQQKxzafE+ekPR github-actions-deploy
```

### Add it to your VPS:

**Option A: Via SSH (Recommended)**
```bash
# Connect to your VPS
ssh root@89.116.159.31

# Add the public key
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPHDyT7svNRoUAIz0uM5eeFtSET1EjsQQKxzafE+ekPR github-actions-deploy" >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# Exit
exit
```

**Option B: Via Hostinger Control Panel**
1. Log in to Hostinger control panel
2. Go to VPS → SSH Access
3. Add the public key above to authorized keys

---

## 🔐 Step 2: Add GitHub Secrets

Go to your GitHub repository settings and add the following secret:

### Navigate to:
```
https://github.com/Troyboy911/petworkspace/settings/secrets/actions
```

### Add this secret:

**Secret Name:** `VPS_SSH_KEY`

**Secret Value:** (Copy the entire private key below, including the BEGIN and END lines)
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDxw8k+7LzUaFACM9LjOXnhbUhE9RI7EECsc2nxPnpD0QAAAJjdWfZK3Vn2
SgAAAAtzc2gtZWQyNTUxOQAAACDxw8k+7LzUaFACM9LjOXnhbUhE9RI7EECsc2nxPnpD0Q
AAAECImsvHggawB5HuIMs+EF3Wklt0GdrsxnyLligzxgJ46vHDyT7svNRoUAIz0uM5eeFt
SET1EjsQQKxzafE+ekPRAAAAFWdpdGh1Yi1hY3Rpb25zLWRlcGxveQ==
-----END OPENSSH PRIVATE KEY-----
```

### How to add the secret:
1. Click "New repository secret"
2. Name: `VPS_SSH_KEY`
3. Value: Paste the entire private key above
4. Click "Add secret"

---

## 📝 Step 3: Configure Environment Variables on VPS

After the first deployment, you need to configure your API keys on the VPS.

### Connect to your VPS:
```bash
ssh root@89.116.159.31
```

### Navigate to the deployment directory:
```bash
cd /var/www/pet-automation/pet-automation-suite
```

### Edit the .env file:
```bash
nano .env
```

### Add your API keys:
```bash
# OpenAI API Key (Required for content generation)
OPENAI_API_KEY=your_openai_key_here

# Database URLs (Auto-configured by Docker)
DATABASE_URL=postgresql://petuser:petpass123@postgres:5432/petautomation
REDIS_URL=redis://redis:6379/0
MONGODB_URL=mongodb://mongodb:27017/petautomation

# Flask Settings
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# Social Media APIs (Optional - add when ready)
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_twitter_token
TWITTER_ACCESS_SECRET=your_twitter_token_secret

REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=PetAutomation/1.0

# Affiliate APIs (Optional - add when ready)
AMAZON_ACCESS_KEY=your_amazon_key
AMAZON_SECRET_KEY=your_amazon_secret
AMAZON_ASSOCIATE_TAG=your_associate_tag

# Shopify (Optional - add when ready)
SHOPIFY_API_KEY=your_shopify_key
SHOPIFY_API_SECRET=your_shopify_secret
SHOPIFY_STORE_URL=your_store_url
```

### Save and exit:
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

### Restart the services:
```bash
docker-compose restart
```

---

## 🚀 Step 4: Push to GitHub (Auto-Deploy)

Once you've completed steps 1-3, any push to the `main` branch will automatically deploy!

### From your local machine:
```bash
# Navigate to your project
cd /path/to/pet-automation-suite

# Add all files
git add .

# Commit changes
git commit -m "Initial deployment setup"

# Push to GitHub (this triggers auto-deployment)
git push origin main
```

### Monitor the deployment:
1. Go to: https://github.com/Troyboy911/petworkspace/actions
2. Click on the latest workflow run
3. Watch the deployment progress in real-time

---

## 📊 Step 5: Verify Deployment

### Check if the application is running:
```bash
# Via browser
http://89.116.159.31:5000

# Via curl
curl http://89.116.159.31:5000/health
```

### Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "mongodb": "connected"
}
```

---

## 🔧 Troubleshooting

### Issue: GitHub Actions can't connect to VPS
**Solution:**
1. Verify the SSH key was added correctly to VPS
2. Check GitHub secret `VPS_SSH_KEY` is set correctly
3. Try connecting manually: `ssh -i /path/to/deploy_key root@89.116.159.31`

### Issue: Deployment succeeds but app doesn't start
**Solution:**
```bash
# SSH into VPS
ssh root@89.116.159.31

# Check logs
cd /var/www/pet-automation/pet-automation-suite
docker-compose logs -f app

# Check if containers are running
docker-compose ps

# Restart services
docker-compose restart
```

### Issue: Health check fails
**Solution:**
```bash
# Check if port 5000 is open
netstat -tulpn | grep 5000

# Check firewall
ufw status
ufw allow 5000

# Check Docker logs
docker-compose logs app
```

### Issue: Database connection errors
**Solution:**
```bash
# Check if databases are running
docker-compose ps

# Restart databases
docker-compose restart postgres redis mongodb

# Check database logs
docker-compose logs postgres
```

---

## 🎯 What Happens on Each Push

When you push to GitHub, the workflow automatically:

1. ✅ Connects to your VPS via SSH
2. ✅ Creates a backup of current deployment
3. ✅ Pulls latest code from GitHub
4. ✅ Installs Docker & Docker Compose (if needed)
5. ✅ Stops old containers
6. ✅ Pulls latest Docker images
7. ✅ Starts new containers
8. ✅ Runs health checks
9. ✅ Cleans up old Docker images
10. ✅ Reports deployment status

---

## 📱 Accessing Your Application

After successful deployment:

- **Dashboard**: http://89.116.159.31:5000
- **Health Check**: http://89.116.159.31:5000/health
- **API Docs**: http://89.116.159.31:5000/api/docs

---

## 🔒 Security Notes

1. **SSH Key**: The private key is stored securely in GitHub Secrets
2. **API Keys**: Store all API keys in `.env` on the VPS, never commit them
3. **Firewall**: Consider restricting port 5000 to specific IPs
4. **HTTPS**: Set up SSL certificate for production use

---

## 🎉 Next Steps

1. ✅ Complete steps 1-3 above
2. ✅ Push code to GitHub
3. ✅ Watch automatic deployment
4. ✅ Configure API keys on VPS
5. ✅ Access your dashboard
6. ✅ Start generating passive income!

---

## 📞 Need Help?

- Check GitHub Actions logs: https://github.com/Troyboy911/petworkspace/actions
- Check VPS logs: `ssh root@89.116.159.31 "cd /var/www/pet-automation/pet-automation-suite && docker-compose logs"`
- Review documentation: `README.md`, `DEPLOYMENT.md`, `TESTING_GUIDE.md`

Happy Deploying! 🚀
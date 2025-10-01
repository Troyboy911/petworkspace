# Pet Automation Suite - Quick Start Guide

Get your Pet Automation Suite up and running in minutes!

## 🚀 Three Deployment Options

### Option 1: Local Development (Fastest - 5 minutes)

Perfect for testing and development on your local machine.

```bash
# 1. Run the setup script
chmod +x scripts/local-dev.sh
./scripts/local-dev.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Edit .env with your API keys
nano .env

# 4. Start the application
python src/dashboard/app.py

# 5. Access dashboard
# Open browser: http://localhost:5000
```

**That's it!** Your local development environment is ready.

---

### Option 2: Hostinger Deployment (Recommended - 10 minutes)

Deploy to your Hostinger VPS or shared hosting.

```bash
# 1. SSH into your Hostinger server
ssh your-username@your-server.com

# 2. Clone or upload the project
git clone https://github.com/yourusername/pet-automation-suite.git
cd pet-automation-suite

# 3. Run deployment script
chmod +x scripts/hostinger-deploy.sh
./scripts/hostinger-deploy.sh

# 4. Follow the prompts and configure your API keys

# 5. Access your dashboard
# Open browser: http://your-domain.com:8000
```

**Done!** Your application is now running on Hostinger.

---

### Option 3: GitHub Auto-Deployment (Best for Production - 15 minutes)

Set up automatic deployment from GitHub to Hostinger.

```bash
# 1. Run GitHub setup script
chmod +x scripts/setup-github.sh
./scripts/setup-github.sh

# 2. Follow the interactive prompts to:
#    - Create GitHub repository
#    - Configure secrets
#    - Set up SSH keys
#    - Test connection

# 3. Push code to trigger deployment
git add .
git commit -m "Initial deployment"
git push origin main

# 4. Monitor deployment
# Go to: https://github.com/yourusername/pet-automation-suite/actions

# 5. Access your dashboard
# Open browser: http://your-domain.com
```

**Automated!** Every push to GitHub now automatically deploys to Hostinger.

---

## 📋 Prerequisites

### For All Options:
- Python 3.9+ installed
- Basic command line knowledge

### For Hostinger Deployment:
- Hostinger VPS or shared hosting account
- SSH access enabled
- Domain name (optional but recommended)

### For GitHub Auto-Deployment:
- GitHub account
- Hostinger server with SSH access
- GitHub CLI (optional, makes setup easier)

---

## 🔑 Required API Keys

Before running the application, you'll need API keys for:

### Essential (for basic functionality):
- **OpenAI API Key** - For AI content generation
  - Get it: https://platform.openai.com/api-keys
  - Free tier available

### Optional (for full functionality):
- **Twitter API** - For Twitter posting
  - Get it: https://developer.twitter.com/
  
- **Reddit API** - For Reddit posting
  - Get it: https://www.reddit.com/prefs/apps
  
- **Shopify API** - For dropshipping
  - Get it: https://shopify.dev/
  
- **Amazon Associates** - For affiliate links
  - Get it: https://affiliate-program.amazon.com/

---

## 🎯 First Steps After Installation

### 1. Access the Dashboard
Open your browser and go to:
- Local: `http://localhost:5000`
- Hostinger: `http://your-domain.com:8000`

### 2. Configure API Keys
Edit the `.env` file with your API keys:
```bash
nano .env
```

### 3. Test the System
- Click "Train ML Model" to initialize AI models
- Click "Generate Content" to create sample content
- Check the Analytics page for insights

### 4. Start Automation
The system will automatically:
- Scrape trends every 2 hours
- Generate content every 4 hours
- Post to social media every hour
- Process orders as they come in
- Update pricing dynamically

---

## 📊 Monitoring Your System

### View Logs
```bash
# Application logs
tail -f logs/gunicorn.log

# Worker logs
tail -f logs/celery.log

# All logs
tail -f logs/*.log
```

### Check Service Status
```bash
# If using systemd
systemctl status pet-automation
systemctl status pet-automation-worker

# If using manual deployment
ps aux | grep gunicorn
ps aux | grep celery
```

### Health Check
Visit: `http://your-domain.com/health`

---

## 🔧 Common Issues and Solutions

### Issue: Application won't start
**Solution:**
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check if port is in use
lsof -i :5000

# Check logs
tail -f logs/gunicorn.log
```

### Issue: Database errors
**Solution:**
```bash
# Reinitialize database
python3 -c "from src.models import create_database; from config.config import Config; create_database(Config.DATABASE_URL)"
```

### Issue: API keys not working
**Solution:**
1. Verify keys are correct in `.env`
2. Check for extra spaces or quotes
3. Restart the application
4. Check API provider's status page

### Issue: GitHub Actions failing
**Solution:**
1. Check GitHub Secrets are configured
2. Verify SSH key is added to Hostinger
3. Test SSH connection manually
4. Review Actions logs for specific errors

---

## 🎓 Learning Resources

### Documentation
- **README.md** - Complete feature overview
- **DEPLOYMENT.md** - Detailed deployment guide
- **GITHUB_SETUP.md** - GitHub integration guide
- **API Documentation** - In-app at `/api/docs`

### Video Tutorials (Coming Soon)
- Local setup walkthrough
- Hostinger deployment
- GitHub Actions configuration
- Using the dashboard

---

## 💡 Pro Tips

1. **Start Local First** - Test everything locally before deploying
2. **Use Environment Variables** - Never commit API keys to Git
3. **Monitor Logs** - Check logs regularly for issues
4. **Backup Database** - Set up automated backups
5. **Use HTTPS** - Configure SSL for production
6. **Scale Gradually** - Start with low post limits, increase gradually
7. **Test API Keys** - Verify each API key works before full deployment
8. **Read the Logs** - Most issues are clearly explained in logs

---

## 🆘 Getting Help

### Self-Help
1. Check the logs: `tail -f logs/*.log`
2. Review documentation in this repository
3. Check GitHub Issues for similar problems
4. Verify all prerequisites are met

### Community Support
- Create an issue on GitHub
- Check existing issues for solutions
- Review closed issues for past problems

### Professional Support
- Contact the development team
- Request custom features
- Get deployment assistance

---

## 🎉 Success Checklist

- [ ] Application installed and running
- [ ] Dashboard accessible in browser
- [ ] API keys configured in `.env`
- [ ] Database initialized successfully
- [ ] Health check endpoint responding
- [ ] Logs showing no errors
- [ ] First content generated
- [ ] Social media accounts connected
- [ ] Monitoring set up
- [ ] Backups configured

**Congratulations!** You're ready to start automating your pet supplies business! 🚀

---

## 📈 Next Steps

1. **Configure Social Media Accounts** - Add your social media credentials
2. **Set Up Products** - Import or add products to your catalog
3. **Customize Content** - Adjust content templates to your brand
4. **Monitor Performance** - Check analytics daily
5. **Scale Up** - Gradually increase posting frequency
6. **Optimize** - Use ML insights to improve performance

---

## 🔗 Quick Links

- **Dashboard**: http://localhost:5000 (local) or http://your-domain.com (production)
- **Health Check**: /health
- **API Docs**: /api/docs
- **GitHub Repo**: https://github.com/yourusername/pet-automation-suite
- **GitHub Actions**: https://github.com/yourusername/pet-automation-suite/actions

---

**Need help?** Check the documentation or create an issue on GitHub!

**Ready to scale?** Follow the optimization guides in the main README!

**Happy automating!** 🐾💰
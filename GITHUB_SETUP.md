# GitHub Setup and Auto-Deployment Guide

This guide will help you set up GitHub repository with CI/CD pipeline for automatic deployment to Hostinger.

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it: `pet-automation-suite`
3. Make it private (recommended for production code)
4. Don't initialize with README (we already have one)

## Step 2: Initialize Git and Push Code

```bash
cd pet-automation-suite

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Pet Automation Suite"

# Add remote repository (replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/pet-automation-suite.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Configure GitHub Secrets

Go to your repository on GitHub:
1. Click on **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

### Required Secrets for Hostinger Deployment

| Secret Name | Description | Example |
|------------|-------------|---------|
| `HOSTINGER_SSH_KEY` | Your SSH private key for Hostinger | Contents of `~/.ssh/id_rsa` |
| `HOSTINGER_HOST` | Hostinger server hostname | `123.45.67.89` or `server.hostinger.com` |
| `HOSTINGER_USER` | SSH username | `u123456789` |
| `HOSTINGER_PORT` | SSH port (usually 22) | `22` |
| `HOSTINGER_DOMAIN` | Your domain name | `yourdomain.com` |
| `DEPLOY_PATH` | Deployment path on server | `/home/u123456789/pet-automation` |

### Optional Secrets for Docker Hub (if using Docker)

| Secret Name | Description |
|------------|-------------|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password or access token |

### Optional Secrets for CapRover (if using CapRover)

| Secret Name | Description |
|------------|-------------|
| `CAPROVER_URL` | CapRover server URL |
| `CAPROVER_PASSWORD` | CapRover admin password |
| `CAPROVER_APP_NAME` | App name in CapRover |

### Optional Secrets for Notifications

| Secret Name | Description |
|------------|-------------|
| `SLACK_WEBHOOK` | Slack webhook URL for notifications |

## Step 4: Generate SSH Key for Hostinger

If you don't have an SSH key yet:

```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Display public key (add this to Hostinger)
cat ~/.ssh/id_rsa.pub

# Display private key (add this to GitHub secrets)
cat ~/.ssh/id_rsa
```

### Add SSH Key to Hostinger

1. Log in to Hostinger control panel
2. Go to **Advanced** → **SSH Access**
3. Add your public key (`~/.ssh/id_rsa.pub`)

## Step 5: Test SSH Connection

```bash
# Test SSH connection to Hostinger
ssh -p 22 u123456789@server.hostinger.com

# If successful, you should see the Hostinger shell
```

## Step 6: Prepare Hostinger Server

SSH into your Hostinger server and run:

```bash
# Create deployment directory
mkdir -p ~/pet-automation
cd ~/pet-automation

# Create .env file with your API keys
nano .env

# Add your environment variables:
# OPENAI_API_KEY=your_key_here
# SHOPIFY_API_KEY=your_key_here
# etc.

# Create logs directory
mkdir -p logs

# Install Python 3.11 (if not already installed)
# This depends on your Hostinger plan
```

## Step 7: Configure GitHub Actions Workflow

The workflow is already configured in `.github/workflows/deploy.yml`. It will:

1. **On every push to `main` branch:**
   - Run tests
   - Build Docker image (optional)
   - Deploy to Hostinger
   - Verify deployment

2. **On every push to `production` branch:**
   - All of the above
   - Deploy to CapRover (if configured)

## Step 8: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on **Actions** tab
3. If prompted, click **I understand my workflows, go ahead and enable them**

## Step 9: Trigger First Deployment

```bash
# Make a small change
echo "# Pet Automation Suite" >> README.md

# Commit and push
git add README.md
git commit -m "Trigger first deployment"
git push origin main
```

## Step 10: Monitor Deployment

1. Go to **Actions** tab in your GitHub repository
2. Click on the running workflow
3. Watch the deployment progress in real-time
4. Check each step for any errors

## Deployment Workflow Explained

### Automatic Deployment Triggers

- **Push to `main` branch**: Deploys to Hostinger staging/production
- **Push to `production` branch**: Deploys to both Hostinger and CapRover
- **Pull Request**: Runs tests only (no deployment)
- **Manual trigger**: Can be triggered manually from Actions tab

### Deployment Steps

1. **Test**: Runs linting and unit tests
2. **Build**: Builds Docker image (if using Docker)
3. **Deploy**: 
   - Creates deployment package
   - Uploads to Hostinger via SSH
   - Extracts files
   - Installs dependencies
   - Runs database migrations
   - Restarts services
4. **Verify**: Checks health endpoint

## Manual Deployment (Alternative)

If you prefer to deploy manually:

```bash
# SSH into Hostinger
ssh -p 22 u123456789@server.hostinger.com

# Navigate to project directory
cd ~/pet-automation

# Pull latest changes
git pull origin main

# Run deployment script
bash scripts/hostinger-deploy.sh
```

## Rollback Procedure

If deployment fails, you can rollback:

```bash
# SSH into Hostinger
ssh -p 22 u123456789@server.hostinger.com

# Navigate to deployment directory
cd ~/pet-automation

# List backups
ls -la backups/

# Restore from backup
rm -rf current
cp -r backups/backup_YYYYMMDD_HHMMSS current

# Restart services
bash restart.sh
```

## Monitoring and Logs

### View Application Logs

```bash
# SSH into Hostinger
ssh -p 22 u123456789@server.hostinger.com

# View gunicorn logs
tail -f ~/pet-automation/logs/gunicorn.log

# View celery logs
tail -f ~/pet-automation/logs/celery.log
```

### Check Service Status

```bash
# If using systemd
systemctl status pet-automation
systemctl status pet-automation-worker

# If using manual process management
ps aux | grep gunicorn
ps aux | grep celery
```

## Troubleshooting

### Deployment Fails

1. Check GitHub Actions logs for error messages
2. Verify all secrets are correctly set
3. Test SSH connection manually
4. Check Hostinger server logs

### Application Not Starting

1. Check logs: `tail -f ~/pet-automation/logs/gunicorn.log`
2. Verify .env file has all required variables
3. Check Python version: `python3 --version`
4. Verify dependencies: `pip list`

### Database Issues

1. Check database file permissions
2. Verify DATABASE_URL in .env
3. Run database initialization manually:
   ```bash
   cd ~/pet-automation/current
   source venv/bin/activate
   python -c "from src.models import create_database; from config.config import Config; create_database(Config.DATABASE_URL)"
   ```

## Best Practices

1. **Always test locally first** before pushing to GitHub
2. **Use feature branches** for development
3. **Create pull requests** for code review
4. **Tag releases** for version tracking
5. **Monitor logs** after each deployment
6. **Keep backups** of your database
7. **Rotate API keys** regularly
8. **Use environment-specific branches** (main, staging, production)

## Security Considerations

1. **Never commit .env files** to GitHub
2. **Use GitHub Secrets** for sensitive data
3. **Rotate SSH keys** periodically
4. **Enable 2FA** on GitHub account
5. **Review GitHub Actions logs** for exposed secrets
6. **Use private repository** for production code
7. **Limit SSH access** to specific IP addresses

## Continuous Improvement

### Adding New Features

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ... code changes ...

# Commit changes
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create pull request on GitHub
# After review and approval, merge to main
```

### Updating Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

## Support

For issues or questions:
- Check GitHub Actions logs
- Review Hostinger server logs
- Consult the main README.md
- Create an issue in the GitHub repository

---

**Congratulations!** Your Pet Automation Suite is now set up with automatic deployment from GitHub to Hostinger! 🚀
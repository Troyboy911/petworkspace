#!/bin/bash

# GitHub Setup Script
# This script helps you set up the GitHub repository and configure secrets

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Pet Automation Suite - GitHub Setup Helper                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is not installed. Please install git first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git found${NC}"

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✓ GitHub CLI found${NC}"
    USE_GH_CLI=true
else
    echo -e "${YELLOW}⚠ GitHub CLI not found. Will use manual setup.${NC}"
    echo -e "${BLUE}  Install GitHub CLI for easier setup: https://cli.github.com/${NC}"
    USE_GH_CLI=false
fi

# Get user input
echo ""
echo -e "${BLUE}Please provide the following information:${NC}"
echo ""

read -p "GitHub username: " GITHUB_USERNAME
read -p "Repository name [pet-automation-suite]: " REPO_NAME
REPO_NAME=${REPO_NAME:-pet-automation-suite}

read -p "Make repository private? (y/N): " PRIVATE_REPO
if [[ $PRIVATE_REPO =~ ^[Yy]$ ]]; then
    REPO_VISIBILITY="private"
else
    REPO_VISIBILITY="public"
fi

# Initialize git repository
echo ""
echo -e "${BLUE}Initializing git repository...${NC}"

if [ ! -d .git ]; then
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${YELLOW}⚠ Git repository already initialized${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo -e "${BLUE}Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
venv/
.env
*.log
logs/
data/
temp/
models/*.pkl
backups/
EOF
    echo -e "${GREEN}✓ .gitignore created${NC}"
fi

# Add all files
echo -e "${BLUE}Adding files to git...${NC}"
git add .

# Create initial commit
if ! git rev-parse HEAD > /dev/null 2>&1; then
    echo -e "${BLUE}Creating initial commit...${NC}"
    git commit -m "Initial commit: Pet Automation Suite"
    echo -e "${GREEN}✓ Initial commit created${NC}"
else
    echo -e "${YELLOW}⚠ Repository already has commits${NC}"
fi

# Create GitHub repository
echo ""
if [ "$USE_GH_CLI" = true ]; then
    echo -e "${BLUE}Creating GitHub repository using GitHub CLI...${NC}"
    
    # Check if logged in
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}⚠ Not logged in to GitHub CLI. Logging in...${NC}"
        gh auth login
    fi
    
    # Create repository
    if [ "$REPO_VISIBILITY" = "private" ]; then
        gh repo create "$GITHUB_USERNAME/$REPO_NAME" --private --source=. --remote=origin --push
    else
        gh repo create "$GITHUB_USERNAME/$REPO_NAME" --public --source=. --remote=origin --push
    fi
    
    echo -e "${GREEN}✓ Repository created and pushed to GitHub${NC}"
else
    echo -e "${YELLOW}Please create the repository manually on GitHub:${NC}"
    echo -e "  1. Go to https://github.com/new"
    echo -e "  2. Repository name: ${BLUE}$REPO_NAME${NC}"
    echo -e "  3. Visibility: ${BLUE}$REPO_VISIBILITY${NC}"
    echo -e "  4. Don't initialize with README"
    echo -e "  5. Click 'Create repository'"
    echo ""
    read -p "Press Enter after creating the repository..."
    
    # Add remote and push
    echo -e "${BLUE}Adding remote and pushing...${NC}"
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git" 2>/dev/null || git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    git branch -M main
    git push -u origin main
    
    echo -e "${GREEN}✓ Code pushed to GitHub${NC}"
fi

# Configure GitHub Secrets
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    GitHub Secrets Configuration                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$USE_GH_CLI" = true ]; then
    echo -e "${BLUE}Setting up GitHub Secrets...${NC}"
    echo ""
    
    # Hostinger SSH Key
    echo -e "${YELLOW}Hostinger SSH Configuration:${NC}"
    read -p "Path to SSH private key [~/.ssh/id_rsa]: " SSH_KEY_PATH
    SSH_KEY_PATH=${SSH_KEY_PATH:-~/.ssh/id_rsa}
    
    if [ -f "$SSH_KEY_PATH" ]; then
        gh secret set HOSTINGER_SSH_KEY < "$SSH_KEY_PATH"
        echo -e "${GREEN}✓ HOSTINGER_SSH_KEY set${NC}"
    else
        echo -e "${RED}✗ SSH key not found at $SSH_KEY_PATH${NC}"
        echo -e "${YELLOW}  Generate one with: ssh-keygen -t rsa -b 4096${NC}"
    fi
    
    # Hostinger Host
    read -p "Hostinger server hostname/IP: " HOSTINGER_HOST
    echo "$HOSTINGER_HOST" | gh secret set HOSTINGER_HOST
    echo -e "${GREEN}✓ HOSTINGER_HOST set${NC}"
    
    # Hostinger User
    read -p "Hostinger SSH username: " HOSTINGER_USER
    echo "$HOSTINGER_USER" | gh secret set HOSTINGER_USER
    echo -e "${GREEN}✓ HOSTINGER_USER set${NC}"
    
    # Hostinger Port
    read -p "Hostinger SSH port [22]: " HOSTINGER_PORT
    HOSTINGER_PORT=${HOSTINGER_PORT:-22}
    echo "$HOSTINGER_PORT" | gh secret set HOSTINGER_PORT
    echo -e "${GREEN}✓ HOSTINGER_PORT set${NC}"
    
    # Deploy Path
    read -p "Deployment path [/home/$HOSTINGER_USER/pet-automation]: " DEPLOY_PATH
    DEPLOY_PATH=${DEPLOY_PATH:-/home/$HOSTINGER_USER/pet-automation}
    echo "$DEPLOY_PATH" | gh secret set DEPLOY_PATH
    echo -e "${GREEN}✓ DEPLOY_PATH set${NC}"
    
    # Hostinger Domain
    read -p "Your domain name: " HOSTINGER_DOMAIN
    echo "$HOSTINGER_DOMAIN" | gh secret set HOSTINGER_DOMAIN
    echo -e "${GREEN}✓ HOSTINGER_DOMAIN set${NC}"
    
    # Optional: Docker Hub
    echo ""
    read -p "Configure Docker Hub? (y/N): " SETUP_DOCKER
    if [[ $SETUP_DOCKER =~ ^[Yy]$ ]]; then
        read -p "Docker Hub username: " DOCKER_USERNAME
        echo "$DOCKER_USERNAME" | gh secret set DOCKER_USERNAME
        
        read -s -p "Docker Hub password/token: " DOCKER_PASSWORD
        echo ""
        echo "$DOCKER_PASSWORD" | gh secret set DOCKER_PASSWORD
        
        echo -e "${GREEN}✓ Docker Hub secrets set${NC}"
    fi
    
    # Optional: Slack
    echo ""
    read -p "Configure Slack notifications? (y/N): " SETUP_SLACK
    if [[ $SETUP_SLACK =~ ^[Yy]$ ]]; then
        read -p "Slack webhook URL: " SLACK_WEBHOOK
        echo "$SLACK_WEBHOOK" | gh secret set SLACK_WEBHOOK
        
        echo -e "${GREEN}✓ Slack webhook set${NC}"
    fi
    
else
    echo -e "${YELLOW}Please configure GitHub Secrets manually:${NC}"
    echo ""
    echo -e "1. Go to: ${BLUE}https://github.com/$GITHUB_USERNAME/$REPO_NAME/settings/secrets/actions${NC}"
    echo -e "2. Click 'New repository secret'"
    echo -e "3. Add the following secrets:"
    echo ""
    echo -e "   ${BLUE}Required Secrets:${NC}"
    echo -e "   - HOSTINGER_SSH_KEY: Your SSH private key"
    echo -e "   - HOSTINGER_HOST: Server hostname/IP"
    echo -e "   - HOSTINGER_USER: SSH username"
    echo -e "   - HOSTINGER_PORT: SSH port (usually 22)"
    echo -e "   - DEPLOY_PATH: Deployment path on server"
    echo -e "   - HOSTINGER_DOMAIN: Your domain name"
    echo ""
    echo -e "   ${BLUE}Optional Secrets:${NC}"
    echo -e "   - DOCKER_USERNAME: Docker Hub username"
    echo -e "   - DOCKER_PASSWORD: Docker Hub password"
    echo -e "   - SLACK_WEBHOOK: Slack webhook URL"
    echo ""
    read -p "Press Enter after configuring secrets..."
fi

# Generate SSH key if needed
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      SSH Key Configuration                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}No SSH key found. Generating one...${NC}"
    read -p "Email for SSH key: " SSH_EMAIL
    ssh-keygen -t rsa -b 4096 -C "$SSH_EMAIL"
    echo -e "${GREEN}✓ SSH key generated${NC}"
fi

echo ""
echo -e "${BLUE}Add this public key to Hostinger:${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════════${NC}"
cat ~/.ssh/id_rsa.pub
echo -e "${YELLOW}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Steps to add SSH key to Hostinger:${NC}"
echo -e "1. Log in to Hostinger control panel"
echo -e "2. Go to Advanced → SSH Access"
echo -e "3. Paste the public key above"
echo -e "4. Save"
echo ""
read -p "Press Enter after adding the SSH key to Hostinger..."

# Test SSH connection
echo ""
echo -e "${BLUE}Testing SSH connection...${NC}"
read -p "Hostinger server hostname/IP: " TEST_HOST
read -p "SSH username: " TEST_USER
read -p "SSH port [22]: " TEST_PORT
TEST_PORT=${TEST_PORT:-22}

if ssh -p "$TEST_PORT" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$TEST_USER@$TEST_HOST" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${GREEN}✓ SSH connection successful${NC}"
else
    echo -e "${RED}✗ SSH connection failed${NC}"
    echo -e "${YELLOW}  Please check your SSH configuration and try again${NC}"
fi

# Create deployment report
echo ""
echo -e "${BLUE}Creating setup report...${NC}"

cat > github_setup_report.txt << EOF
Pet Automation Suite - GitHub Setup Report
==========================================
Date: $(date)

Repository Information:
- GitHub Username: $GITHUB_USERNAME
- Repository Name: $REPO_NAME
- Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME
- Visibility: $REPO_VISIBILITY

Deployment Configuration:
- Hostinger Host: $HOSTINGER_HOST
- SSH User: $HOSTINGER_USER
- SSH Port: $HOSTINGER_PORT
- Deploy Path: $DEPLOY_PATH
- Domain: $HOSTINGER_DOMAIN

Next Steps:
1. Verify GitHub Secrets are configured correctly
2. Test SSH connection to Hostinger
3. Push code to trigger first deployment
4. Monitor deployment in GitHub Actions
5. Access dashboard at: http://$HOSTINGER_DOMAIN

Useful Commands:
- View GitHub Actions: https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions
- SSH to Hostinger: ssh -p $HOSTINGER_PORT $HOSTINGER_USER@$HOSTINGER_HOST
- View logs: tail -f $DEPLOY_PATH/logs/gunicorn.log

Documentation:
- GitHub Setup: GITHUB_SETUP.md
- Deployment Guide: DEPLOYMENT.md
- Main README: README.md

Support:
- Check GitHub Actions logs for deployment issues
- Review Hostinger server logs
- Consult documentation files
EOF

echo -e "${GREEN}✓ Setup report created: github_setup_report.txt${NC}"

# Final summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Setup Complete! 🚀                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Repository URL:${NC} https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo -e "${BLUE}Actions URL:${NC} https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Verify all GitHub Secrets are configured"
echo -e "2. Make a commit to trigger deployment:"
echo -e "   ${GREEN}git add .${NC}"
echo -e "   ${GREEN}git commit -m 'Trigger deployment'${NC}"
echo -e "   ${GREEN}git push origin main${NC}"
echo -e "3. Monitor deployment in GitHub Actions"
echo -e "4. Access your dashboard at: ${BLUE}http://$HOSTINGER_DOMAIN${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "- Setup report: ${GREEN}github_setup_report.txt${NC}"
echo -e "- GitHub guide: ${GREEN}GITHUB_SETUP.md${NC}"
echo -e "- Deployment guide: ${GREEN}DEPLOYMENT.md${NC}"
echo ""
echo -e "${GREEN}Happy deploying! 🎉${NC}"
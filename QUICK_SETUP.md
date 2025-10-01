# ⚡ Quick Setup - 3 Steps to Auto-Deployment

## 🎯 Your Repository
**GitHub**: https://github.com/Troyboy911/petworkspace
**VPS**: 89.116.159.31

---

## ✅ Step 1: Add SSH Key to VPS (2 minutes)

Connect to your VPS and add the deployment key:

```bash
# Connect to VPS
ssh root@89.116.159.31

# Add the deployment key
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPHDyT7svNRoUAIz0uM5eeFtSET1EjsQQKxzafE+ekPR github-actions-deploy" >> ~/.ssh/authorized_keys

# Set permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# Exit
exit
```

---

## 🔐 Step 2: Add GitHub Secret (1 minute)

1. Go to: https://github.com/Troyboy911/petworkspace/settings/secrets/actions

2. Click **"New repository secret"**

3. **Name**: `VPS_SSH_KEY`

4. **Value**: Copy and paste this entire private key:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDxw8k+7LzUaFACM9LjOXnhbUhE9RI7EECsc2nxPnpD0QAAAJjdWfZK3Vn2
SgAAAAtzc2gtZWQyNTUxOQAAACDxw8k+7LzUaFACM9LjOXnhbUhE9RI7EECsc2nxPnpD0Q
AAAECImsvHggawB5HuIMs+EF3Wklt0GdrsxnyLligzxgJ46vHDyT7svNRoUAIz0uM5eeFt
SET1EjsQQKxzafE+ekPRAAAAFWdpdGh1Yi1hY3Rpb25zLWRlcGxveQ==
-----END OPENSSH PRIVATE KEY-----
```

5. Click **"Add secret"**

---

## 🚀 Step 3: Trigger Deployment (30 seconds)

The code is already pushed! Now trigger the deployment:

### Option A: Automatic (Already Running!)
The deployment should already be running since we just pushed. Check it here:
https://github.com/Troyboy911/petworkspace/actions

### Option B: Manual Trigger
1. Go to: https://github.com/Troyboy911/petworkspace/actions
2. Click on "Deploy to Hostinger VPS" workflow
3. Click "Run workflow" → "Run workflow"

---

## 📊 Monitor Deployment

Watch the deployment in real-time:
https://github.com/Troyboy911/petworkspace/actions

The deployment will:
- ✅ Connect to your VPS
- ✅ Clone/update the code
- ✅ Install Docker (if needed)
- ✅ Start all services
- ✅ Run health checks

**Time**: ~5-10 minutes for first deployment

---

## 🎉 After Deployment

### Access Your Dashboard
```
http://89.116.159.31:5000
```

### Configure API Keys
```bash
# SSH into VPS
ssh root@89.116.159.31

# Edit environment file
cd /var/www/pet-automation/pet-automation-suite
nano .env

# Add your API keys (see .env.example for all options)
OPENAI_API_KEY=your_key_here
TWITTER_API_KEY=your_key_here
# ... etc

# Save and restart
docker-compose restart
```

---

## 🧪 Test Locally First (Optional)

Want to test before deploying?

```bash
# Clone the repo
git clone https://github.com/Troyboy911/petworkspace.git
cd petworkspace

# Run the test script
./test.sh
```

Opens dashboard at: http://localhost:5000

---

## 📚 Full Documentation

- **Quick Start**: `QUICKSTART.md`
- **Testing Guide**: `TESTING_GUIDE.md`
- **Local Testing**: `LOCAL_TESTING.md`
- **Deployment Details**: `GITHUB_DEPLOYMENT_SETUP.md`
- **Full README**: `README.md`

---

## 🆘 Troubleshooting

### Deployment Failed?
1. Check GitHub Actions logs: https://github.com/Troyboy911/petworkspace/actions
2. Verify SSH key was added to VPS (Step 1)
3. Verify GitHub secret was added (Step 2)

### App Not Starting?
```bash
# SSH into VPS
ssh root@89.116.159.31

# Check logs
cd /var/www/pet-automation/pet-automation-suite
docker-compose logs -f

# Restart services
docker-compose restart
```

### Can't Access Dashboard?
```bash
# Check if port 5000 is open
ssh root@89.116.159.31 "ufw allow 5000"

# Check if app is running
curl http://89.116.159.31:5000/health
```

---

## 🎯 What's Next?

1. ✅ Complete Steps 1-2 above
2. ✅ Wait for deployment to finish
3. ✅ Access dashboard at http://89.116.159.31:5000
4. ✅ Configure API keys in .env
5. ✅ Start generating passive income!

---

## 🔄 Future Deployments

After initial setup, just push to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

**Automatic deployment happens on every push to main branch!** 🚀

---

Need help? Check the full documentation or GitHub Actions logs!
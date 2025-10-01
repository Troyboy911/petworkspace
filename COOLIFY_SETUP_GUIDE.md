# 🔧 Coolify Deployment Setup Guide

## ❌ Issue: Missing Server Host Configuration

The Coolify deployment workflow was missing the `COOLIFY_HOST` configuration. Here's how to fix it:

## ✅ Solution

### Step 1: Add GitHub Secrets

1. **Go to**: https://github.com/Troyboy911/petworkspace/settings/secrets/actions

2. **Add these secrets**:

**Secret 1: COOLIFY_HOST**
- **Name**: `COOLIFY_HOST`
- **Value**: Your Coolify server IP address or domain
- **Example**: `192.168.1.100` or `coolify.yourdomain.com`

**Secret 2: COOLIFY_SSH_KEY**
- **Name**: `COOLIFY_SSH_KEY`
- **Value**: Your SSH private key for Coolify server
- **Format**: Include BEGIN and END lines

### Step 2: Test Connection

**Test SSH connection to your Coolify server:**
```bash
ssh root@YOUR_COOLIFY_IP
```

### Step 3: Deploy

**Option A: Automatic (on push)**
```bash
git push origin main
```

**Option B: Manual (with custom host)**
1. Go to: https://github.com/Troyboy911/petworkspace/actions
2. Click "Deploy to Coolify"
3. Click "Run workflow"
4. Enter your Coolify server IP/hostname

## 📋 Coolify Server Setup

### If you don't have Coolify yet:

**Install Coolify on your server:**
```bash
curl -fsSL https://get.coollabs.io/coolify/install.sh | bash
```

**Access Coolify:**
- URL: `http://YOUR_SERVER_IP:3000`
- Default credentials will be provided during setup

### If you already have Coolify:

**Find your server IP:**
- Check your VPS provider dashboard
- Or run: `curl ifconfig.me` on your server

## 🎯 Complete Setup Checklist

- [ ] Install Coolify (if not already installed)
- [ ] Get your Coolify server IP/domain
- [ ] Add `COOLIFY_HOST` to GitHub Secrets
- [ ] Add `COOLIFY_SSH_KEY` to GitHub Secrets
- [ ] Test SSH connection
- [ ] Push to GitHub to trigger deployment
- [ ] Access your app via Coolify dashboard

## 🆘 Troubleshooting

### Issue: SSH Connection Fails
```bash
# Check if Coolify server is accessible
ping YOUR_COOLIFY_IP

# Test SSH manually
ssh root@YOUR_COOLIFY_IP

# Check firewall
sudo ufw status
sudo ufw allow 22
```

### Issue: Coolify Not Running
```bash
# Check Coolify status
sudo systemctl status coolify

# Restart Coolify
sudo systemctl restart coolify
```

### Issue: Deployment Fails
- Check GitHub Actions logs
- Verify SSH key is correct
- Ensure Coolify is running
- Check network connectivity

## 📊 Expected Results

After successful setup:
- **GitHub Actions**: Green checkmark ✅
- **Coolify Dashboard**: Application running
- **App URL**: Provided by Coolify
- **Dashboard**: http://YOUR_COOLIFY_IP:5000

## 🚀 Ready to Deploy!

Your Coolify deployment is now ready. Just add the secrets and push!
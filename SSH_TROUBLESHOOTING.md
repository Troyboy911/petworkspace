# 🔧 SSH Connection Troubleshooting Guide

## ❌ Issue: SSH Connection Failing

Your VPS at `89.116.159.31` is not responding to connections. Here's how to fix it:

---

## 🔍 Diagnosis

The server is not responding to:
- Ping requests (100% packet loss)
- SSH connection attempts (timeout)

**Possible Causes:**
1. VPS is powered off or suspended
2. Firewall blocking connections
3. IP address has changed
4. SSH service not running
5. Network configuration issue

---

## ✅ Solutions (Try in Order)

### Solution 1: Check VPS Status in Hostinger Panel

1. **Log in to Hostinger**
   - URL: https://hpanel.hostinger.com
   - Email: smallhandman99@gmail.com
   - Password: Fuckyou123???

2. **Check VPS Status**
   - Go to VPS section
   - Check if VPS is "Running" or "Stopped"
   - If stopped, click "Start"

3. **Verify IP Address**
   - Check if IP is still `89.116.159.31`
   - If changed, update the deployment workflow

---

### Solution 2: Check Firewall Settings

If VPS is running but not accessible:

1. **Access VPS Console** (via Hostinger panel)
   - Go to VPS → Console/Terminal
   - This gives you direct access without SSH

2. **Check Firewall**
   ```bash
   # Check UFW status
   sudo ufw status
   
   # If SSH is blocked, allow it
   sudo ufw allow 22/tcp
   sudo ufw allow 5000/tcp
   
   # Restart firewall
   sudo ufw reload
   ```

3. **Check SSH Service**
   ```bash
   # Check if SSH is running
   sudo systemctl status ssh
   
   # If not running, start it
   sudo systemctl start ssh
   sudo systemctl enable ssh
   ```

---

### Solution 3: Alternative Deployment Methods

Since SSH is not working, here are alternative deployment options:

#### Option A: Manual Deployment via Hostinger Panel

1. **Access File Manager** in Hostinger panel
2. **Upload Files**:
   - Download your code as ZIP from GitHub
   - Upload to `/var/www/pet-automation`
   - Extract files

3. **Install Docker** (via console):
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

4. **Start Services**:
   ```bash
   cd /var/www/pet-automation/pet-automation-suite
   docker-compose up -d
   ```

#### Option B: Use Different VPS Provider

If Hostinger VPS continues to have issues, consider:

1. **DigitalOcean** (You have API key)
   - Use your DigitalOcean API key from your credentials
   - Create droplet with one-click Docker
   - More reliable SSH access

2. **Azure VM** (You have credentials)
   - IP: 48.217.66.79
   - User: troyboy911
   - Password: Fuckyou123???
   - Already set up with SSH key

#### Option C: Deploy to CapRover

CapRover provides easier deployment without SSH:

1. **Install CapRover** on your VPS (via console)
2. **Deploy via Git**
3. **No SSH needed** for deployments

---

### Solution 4: Use Azure VM Instead

You already have an Azure VM set up! Let's use that:

**Azure VM Details:**
- IP: `48.217.66.79`
- User: `troyboy911`
- Password: `Fuckyou123???`
- SSH Key: `~/.ssh/id_ed25519_mothership_key`

**Test Connection:**
```bash
ssh troyboy911@48.217.66.79
```

If this works, we can update the deployment to use Azure instead!

---

## 🔄 Update Deployment to Use Azure VM

If Azure VM is accessible, update the workflow:

1. **Update GitHub Secret**
   - Name: `VPS_SSH_KEY`
   - Value: Your Azure SSH key

2. **Update Workflow File**
   - Change host to: `48.217.66.79`
   - Change username to: `troyboy911`

---

## 🆘 Immediate Actions

### Step 1: Check Hostinger Panel
1. Log in to Hostinger
2. Check VPS status
3. Start VPS if stopped
4. Verify IP address

### Step 2: Try Azure VM
```bash
# Test if Azure VM is accessible
ssh troyboy911@48.217.66.79
```

### Step 3: Use Console Access
If SSH fails, use Hostinger's web console to:
- Check firewall
- Start SSH service
- Verify network settings

---

## 📞 Contact Hostinger Support

If VPS is down or inaccessible:

1. **Hostinger Support**
   - Live Chat: Available 24/7
   - Email: support@hostinger.com
   - Phone: Check Hostinger panel

2. **What to Ask**
   - "My VPS at 89.116.159.31 is not responding"
   - "Cannot SSH or ping the server"
   - "Please check if VPS is running"

---

## 🎯 Recommended Next Steps

1. **Immediate**: Check Hostinger panel for VPS status
2. **Alternative**: Test Azure VM connection
3. **Backup Plan**: Deploy to DigitalOcean or Azure
4. **Long-term**: Set up monitoring to catch issues early

---

## 📝 Update Deployment After Fix

Once SSH is working again:

1. **Test Connection**
   ```bash
   ssh root@89.116.159.31
   ```

2. **Add Deployment Key**
   ```bash
   echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPHDyT7svNRoUAIz0uM5eeFtSET1EjsQQKxzafE+ekPR github-actions-deploy" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

3. **Trigger Deployment**
   - Go to GitHub Actions
   - Run workflow manually

---

## 🔍 Diagnostic Commands

Once you have console access:

```bash
# Check network
ip addr show
ping 8.8.8.8

# Check SSH
systemctl status ssh
netstat -tulpn | grep 22

# Check firewall
ufw status
iptables -L

# Check logs
tail -f /var/log/auth.log
journalctl -u ssh -f
```

---

## ✅ Prevention

After fixing, set up monitoring:

1. **Uptime Monitoring**
   - Use UptimeRobot (free)
   - Monitor: http://89.116.159.31:5000

2. **SSH Monitoring**
   - Set up alerts for SSH failures
   - Regular health checks

3. **Backup VPS**
   - Keep Azure VM as backup
   - Or set up on DigitalOcean

---

Need help? Check Hostinger panel first, then try Azure VM as alternative!
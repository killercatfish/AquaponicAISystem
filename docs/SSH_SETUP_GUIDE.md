# SSH Key Setup for GitHub

## Why SSH Keys?

SSH keys let you push to GitHub without entering your password every time. Much better than HTTPS with Personal Access Tokens!

---

## One-Time Setup

### 1. Generate SSH Key on Raspberry Pi
```bash
# Generate key (use default location, passphrase optional)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Press Enter for default location: /home/pi/.ssh/id_ed25519
# Press Enter twice for no passphrase (or add one for security)
```

### 2. Copy Your Public Key
```bash
# Display your public key
cat ~/.ssh/id_ed25519.pub

# Copy the ENTIRE output (starts with "ssh-ed25519 ...")
```

### 3. Add to GitHub

1. Go to: https://github.com/settings/keys
2. Click **"New SSH key"**
3. Title: `Raspberry Pi - Aquaponics`
4. Key type: **Authentication Key**
5. Paste your public key
6. Click **"Add SSH key"**

### 4. Change Git Remote to SSH
```bash
cd ~/AquaponicAISystem

# Switch from HTTPS to SSH
git remote set-url origin git@github.com:killercatfish/AquaponicAISystem.git

# Verify
git remote -v
# Should show: git@github.com:killercatfish/...
```

### 5. Test Connection
```bash
# Test SSH connection to GitHub
ssh -T git@github.com

# Should say: "Hi killercatfish! You've successfully authenticated..."
```

---

## Now Push Without Password!
```bash
git push origin main
# No password prompt! 🎉
```

---

## Troubleshooting

### "Permission denied (publickey)"
- Check you added the correct key to GitHub
- Verify you copied the **public** key (.pub file)
- Make sure remote URL uses `git@github.com:` not `https://`

### "Could not resolve hostname"
- Check internet connection
- Try: `ping github.com`

---

**Status:** ✅ Configured on aquaponics Pi (2025-11-06)

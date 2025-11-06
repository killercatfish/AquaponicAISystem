
## SSH Key Setup (Recommended)

For passwordless Git pushes, set up SSH keys:
```bash
# Generate key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add public key to GitHub (see docs/SSH_SETUP_GUIDE.md)

# Switch remote to SSH
git remote set-url origin git@github.com:killercatfish/AquaponicAISystem.git
```

See full guide: `docs/SSH_SETUP_GUIDE.md`

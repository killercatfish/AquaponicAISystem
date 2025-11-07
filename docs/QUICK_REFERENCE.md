# QUICK REFERENCE CARD
## Daily Commands & URLs

**Dashboard Access:**
```
Local:  http://aquaponics.local:8000
Remote: http://100.117.109.76:8000
```

**SSH Access:**
```
Local:  ssh pi@aquaponics.local
Remote: ssh pi@aquaponics  (via Tailscale)
```

**Check Status:**
```bash
tailscale status              # Tailscale connection
sudo systemctl status hydroponics  # Dashboard service
ps aux | grep uvicorn        # Dashboard process
```

**Restart Services:**
```bash
sudo systemctl restart hydroponics  # Restart dashboard
sudo tailscale down && sudo tailscale up  # Restart VPN
```

**View Logs:**
```bash
tail -f ~/AquaponicAISystem/data/logs/hydroponics.log
sudo journalctl -u tailscaled -f
```

**Update System:**
```bash
cd ~/AquaponicAISystem
git pull
source venv/bin/activate
pip install -r requirements-raspi.txt --break-system-packages
sudo systemctl restart hydroponics
```

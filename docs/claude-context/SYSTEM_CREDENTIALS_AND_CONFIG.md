# AQUAPONICS SYSTEM CREDENTIALS & CONFIGURATION
## System Documentation for Knowledge Base

**⚠️ SECURITY NOTE:** This file contains sensitive credentials. Store securely and do NOT commit to public GitHub repositories!

**Last Updated:** 2025-11-06  
**Document Version:** 1.0

---

## RASPBERRY PI 5 - MAIN CONTROLLER

### Network Configuration

| Property | Value |
|----------|-------|
| **Hostname** | `aquaponics.local` |
| **IP Address** | `192.168.1.188` (DHCP) |
| **MAC Address** | *(Check with `ip addr` command)* |
| **WiFi Network** | *(Your home network)* |
| **Connection Type** | WiFi |

### System Credentials

| Service | Username | Password | Notes |
|---------|----------|----------|-------|
| **SSH/Terminal** | `pi` | `aquaponics2025` | Main system login |
| **VNC** (if enabled) | `pi` | `aquaponics2025` | Remote desktop |
| **Flask Dashboard** | *(none yet)* | *(none yet)* | Add when implemented |

### SSH Connection Commands

```bash
# From Mac/Linux:
ssh pi@aquaponics.local
# Password: aquaponics2025

# Or using IP:
ssh pi@192.168.1.188
# Password: aquaponics2025

# With VS Code Remote SSH:
# Host: aquaponics.local
# User: pi
# Password: aquaponics2025
```

### Hardware Specifications

| Component | Specification |
|-----------|--------------|
| **Model** | Raspberry Pi 5 |
| **RAM** | *(4GB or 8GB?)* |
| **Storage** | 256GB microSD |
| **OS** | Raspberry Pi OS (64-bit) |
| **OS Version** | Bookworm (Debian 12) |
| **Kernel** | *(Run `uname -r` to check)* |
| **Python Version** | Python 3.11+ |

### Installation Date

**Fresh Install:** 2025-11-06  
**Configured By:** Josh  
**Purpose:** Aquaponics monitoring system with 4 sensors + IoT relay control

---

## SENSOR CONFIGURATION

### Connected Sensors

| Sensor | Model | Interface | Address/Pin | Status |
|--------|-------|-----------|-------------|--------|
| **Temperature** | DS18B20 | 1-Wire | GPIO4 (Pin 7) | ⏳ Pending |
| **pH** | Atlas Scientific | I2C | 0x63 (99) | ⏳ Pending |
| **Dissolved Oxygen** | Atlas Scientific | Analog via ADS1115 | I2C 0x48, Channel A0 | ⏳ Pending |
| **Water Level** | HC-SR04 Ultrasonic | GPIO | TRIG: GPIO23, ECHO: GPIO24 | ⏳ Pending |

**Status Legend:**
- ⏳ Pending = Not yet wired
- 🔧 In Progress = Currently wiring/testing
- ✅ Operational = Tested and working
- ❌ Error = Needs troubleshooting

### Sensor Serial Numbers / IDs

**Temperature Sensor 1:**
- Serial: `28-xxxxxxxxxxxx` *(Will populate after first reading)*
- Location: Bucket reservoir, center
- Calibration: Factory (±0.5°C)

**pH Sensor:**
- Serial: *(Check Atlas board if visible)*
- Calibration Date: *(To be added)*
- Calibration Points: pH 4.0, 7.0, 10.0

**DO Sensor:**
- Serial: *(Check Atlas board if visible)*
- Calibration Date: *(To be added)*
- Calibration: 0% (zero oxygen), 100% (air saturated)

**Water Level Sensor:**
- Model: HC-SR04 (or specific model)
- Range: 2-400 cm
- Mounting height: *(Measure from bucket bottom)*

---

## IOT RELAY CONFIGURATION

### Digital Loggers IoT Relay

| Property | Value |
|----------|-------|
| **Model** | Digital Loggers IoT Relay *(confirm model)* |
| **IP Address** | *(To be configured)* |
| **Hostname** | *(To be configured)* |
| **Web Interface** | `http://[relay-ip]` |
| **Username** | `admin` *(default, change!)* |
| **Password** | *(Check device label or manual)* |

### Relay Channel Assignments

| Channel | Device | Schedule | Status |
|---------|--------|----------|--------|
| **Outlet 1** | Water Pump | 15 min ON / 45 min OFF (hourly) | ⏳ Pending |
| **Outlet 2** | Grow Lights | 6:00 AM - 10:00 PM | ⏳ Pending |
| **Outlet 3** | *(Spare)* | N/A | Available |
| **Outlet 4** | *(Spare)* | N/A | Available |

---

## GITHUB REPOSITORY

### Repository Information

| Property | Value |
|----------|-------|
| **Repository Name** | `AquaponicAISystem` |
| **GitHub URL** | https://github.com/killercatfish/AquaponicAISystem |
| **Clone URL (HTTPS)** | `https://github.com/killercatfish/AquaponicAISystem.git` |
| **Clone URL (SSH)** | `git@github.com:killercatfish/AquaponicAISystem.git` |
| **Primary Branch** | `main` |
| **Development Branch** | `hardware-integration` |

### GitHub Credentials

| Service | Username | Token/Key | Notes |
|---------|----------|-----------|-------|
| **GitHub Account** | `killercatfish` | *(Use SSH key or PAT)* | Your main account |
| **Git Config (Pi)** | *(Your name)* | *(Your email)* | Set with `git config` |

### Git Setup on Pi

```bash
# Set your identity (run once)
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Clone repository to Pi
cd ~
git clone https://github.com/killercatfish/AquaponicAISystem.git
cd AquaponicAISystem

# Create development branch
git checkout -b hardware-integration
```

---

## FLASK DASHBOARD

### Web Interface

| Property | Value |
|----------|-------|
| **Local URL** | `http://aquaponics.local:5000` |
| **IP URL** | `http://192.168.1.188:5000` |
| **Port** | 5000 (default Flask) |
| **Authentication** | *(To be implemented)* |
| **Admin Username** | *(To be created)* |
| **Admin Password** | *(To be created)* |

### API Endpoints

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/` | GET | Dashboard homepage | No |
| `/api/sensors` | GET | Current sensor readings JSON | No |
| `/api/health` | GET | System health check | No |
| `/api/relay/pump/on` | POST | Turn pump ON | *(Future)* |
| `/api/relay/pump/off` | POST | Turn pump OFF | *(Future)* |
| `/api/relay/lights/on` | POST | Turn lights ON | *(Future)* |
| `/api/relay/lights/off` | POST | Turn lights OFF | *(Future)* |

---

## NETWORK CONFIGURATION

### Router Settings (For Reference)

| Property | Value |
|----------|-------|
| **Router IP** | `192.168.1.1` *(typical default)* |
| **Router Admin** | *(Your router login)* |
| **DHCP Range** | *(Your router's DHCP range)* |
| **DNS Servers** | *(Auto or manual?)* |

### Static IP Configuration (Optional Future Enhancement)

**If you want to assign a permanent IP to the Pi:**

```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add these lines at the end:
interface wlan0
static ip_address=192.168.1.188/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Save, then reboot:
sudo reboot
```

---

## BACKUP STRATEGY

### SD Card Backups

**Recommendation:** Back up SD card after major milestones

| Date | Milestone | Backup Location | Notes |
|------|-----------|-----------------|-------|
| 2025-11-06 | Fresh OS install | *(To be created)* | Clean slate with SSH enabled |
| *(Future)* | First sensor working | *(To be created)* | Temperature sensor operational |
| *(Future)* | All sensors working | *(To be created)* | Complete hardware integration |
| *(Future)* | Database + logging | *(To be created)* | Full system operational |

### How to Create SD Card Backup (Windows)

**Using Win32 Disk Imager or Raspberry Pi Imager:**

1. Power off Pi
2. Remove SD card
3. Insert into PC
4. Use imaging tool to create `.img` backup file
5. Store backup file safely
6. Label with date and milestone

### Code Backups

**GitHub serves as code backup:**
- Push commits regularly
- Create tags for milestones
- Branch for experiments

---

## IMPORTANT FILE LOCATIONS ON PI

### Project Files

```
/home/pi/AquaponicAISystem/          # Main repository
├── app.py                           # Flask application
├── sensors/                         # Sensor modules
│   ├── temperature.py
│   ├── ph.py
│   ├── do_sensor.py
│   ├── water_level.py
│   └── relay.py
├── templates/                       # HTML templates
├── static/                          # CSS, JS, images
├── logs/                            # Application logs
└── data/                            # SQLite database (future)
```

### System Configuration Files

```
/boot/config.txt                     # Pi hardware config
/etc/dhcpcd.conf                     # Network config
/etc/hostname                        # System hostname
/etc/hosts                           # Host mappings
~/.ssh/                              # SSH keys
~/.gitconfig                         # Git configuration
```

---

## MAINTENANCE SCHEDULE

### Regular Tasks

| Task | Frequency | Last Done | Next Due |
|------|-----------|-----------|----------|
| **Update OS** | Monthly | *(TBD)* | *(TBD)* |
| **Backup SD card** | After milestones | *(TBD)* | *(TBD)* |
| **Calibrate pH sensor** | Quarterly | *(TBD)* | *(TBD)* |
| **Calibrate DO sensor** | Quarterly | *(TBD)* | *(TBD)* |
| **Check sensor connections** | Monthly | *(TBD)* | *(TBD)* |
| **Git push commits** | Daily during dev | *(TBD)* | *(TBD)* |
| **Review logs** | Weekly | *(TBD)* | *(TBD)* |

### Update Commands

```bash
# Update Raspberry Pi OS
sudo apt update
sudo apt upgrade -y
sudo reboot

# Update Python packages
pip3 list --outdated
pip3 install --upgrade --break-system-packages [package-name]

# Pull latest code from GitHub
cd ~/AquaponicAISystem
git pull origin main
```

---

## SECURITY BEST PRACTICES

### ✅ Completed

- [x] Changed default password from `raspberry` to custom password
- [x] Enabled SSH for remote access
- [x] Configured unique hostname

### ⏳ To Do

- [ ] Change IoT relay default password
- [ ] Set up SSH key authentication (more secure than password)
- [ ] Configure firewall (ufw) to limit exposed ports
- [ ] Add authentication to Flask dashboard
- [ ] Regular security updates
- [ ] Disable root login via SSH

### SSH Key Setup (More Secure - Future Enhancement)

**On your Mac:**
```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "aquaponics-pi"

# Copy public key to Pi
ssh-copy-id pi@aquaponics.local

# Now you can SSH without password!
ssh pi@aquaponics.local
```

---

## TROUBLESHOOTING REFERENCE

### Common Commands

```bash
# Check IP address
hostname -I

# Check WiFi connection
iwconfig

# Check system info
cat /etc/os-release

# Check running services
systemctl status

# Check disk space
df -h

# Check memory usage
free -h

# Reboot
sudo reboot

# Shutdown
sudo shutdown -h now

# View system logs
sudo journalctl -xe

# Check temperature/throttling
vcgencmd measure_temp
```

### Port Forwarding (If Accessing from Outside Home)

**If you want to access your Pi from outside your home network:**

⚠️ **Security Risk!** Only do this if you understand the implications.

1. Log into your router
2. Forward external port (e.g., 2222) to Pi port 22 (SSH)
3. Forward external port (e.g., 8080) to Pi port 5000 (Flask)
4. Use dynamic DNS service if your ISP changes your public IP
5. **Use SSH keys, NOT passwords!**
6. Consider VPN instead (more secure)

---

## CONTACT INFORMATION

### Project Owner

**Name:** Josh  
**GitHub:** killercatfish  
**Project Start:** 2015 (concept), 2025 (hardware implementation)  
**Location:** Lowell, Massachusetts, US

### Support Resources

- **Raspberry Pi Forums:** https://forums.raspberrypi.com/
- **Atlas Scientific Support:** https://atlas-scientific.com/support/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **GitHub Issues:** *(Your repo issues page)*

---

## CHANGE LOG

| Date | Change | By | Notes |
|------|--------|-----|-------|
| 2025-11-06 | Initial system setup | Josh | Fresh Pi OS install, SSH configured |
| 2025-11-06 | Created credentials doc | Josh | Documentation for knowledge base |
| *(Future)* | Temperature sensor wired | Josh | First sensor operational |
| *(Future)* | pH sensor wired | Josh | Second sensor operational |
| *(Future)* | DO sensor wired | Josh | Third sensor operational |
| *(Future)* | Water level sensor wired | Josh | Fourth sensor operational |
| *(Future)* | IoT relay configured | Josh | Pump and light control |
| *(Future)* | Flask dashboard deployed | Josh | Web interface live |

---

## QUICK REFERENCE CARD (Print This Section)

```
═══════════════════════════════════════════════════
AQUAPONICS SYSTEM - QUICK REFERENCE
═══════════════════════════════════════════════════

Raspberry Pi SSH:
  ssh pi@aquaponics.local
  Password: aquaponics2025
  IP: 192.168.1.188

Flask Dashboard:
  http://aquaponics.local:5000

GitHub Repo:
  https://github.com/killercatfish/AquaponicAISystem

Project Directory on Pi:
  /home/pi/AquaponicAISystem/

Useful Commands:
  sudo reboot              # Restart Pi
  sudo shutdown -h now     # Power off Pi
  git status               # Check repo status
  git pull origin main     # Update code
  python3 app.py           # Run Flask app

Emergency:
  Power off: Unplug Pi
  Reset password: Use SD card method
  Backup SD card: Use imaging tool

═══════════════════════════════════════════════════
Last Updated: 2025-11-06
═══════════════════════════════════════════════════
```

---

## NOTES & OBSERVATIONS

**Add your own notes here as you work on the project:**

- 2025-11-06: Fresh install completed, SSH working, ready for sensor wiring
- *(Add your notes as you progress)*

---

**Remember:** Update this document as your system evolves!

**Security:** Store this file securely. Consider encrypting it or keeping it in a private repository.


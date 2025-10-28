# STEM DREAM Aquaponics Control System - Complete Setup Guide

This guide walks you through setting up the complete Raspberry Pi 5 aquaponics monitoring and control system with ML plant health detection and LLM integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Assembly](#hardware-assembly)
3. [Raspberry Pi OS Setup](#raspberry-pi-os-setup)
4. [Software Installation](#software-installation)
5. [Sensor Calibration](#sensor-calibration)
6. [Configuration](#configuration)
7. [Running the System](#running-the-system)
8. [Using the Dashboard](#using-the-dashboard)
9. [LLM Setup (Optional)](#llm-setup-optional)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

---

## Prerequisites

### Hardware Required

- âœ… Raspberry Pi 5 8GB with power supply
- âœ… MicroSD card (128GB recommended)
- âœ… Adafruit Controllable Four Outlet Power Relay Module v2
- âœ… Atlas Scientific pH, EC, and DO sensor kits
- âœ… DS18B20 waterproof temperature sensors (2x)
- âœ… HC-SR04 ultrasonic water level sensor
- âœ… Raspberry Pi Camera Module 3
- âœ… Jumper wires, breadboard, resistors
- âœ… Waterproof enclosures

### Software/Accounts Needed

- Computer for initial Pi setup
- Internet connection
- (Optional) OpenAI or Anthropic API key for LLM
- (Optional) Email account for alerts
- (Optional) Twilio account for SMS alerts

---

## Hardware Assembly

### Step 1: Prepare Raspberry Pi 5

1. Flash Raspberry Pi OS (64-bit) to microSD card using Raspberry Pi Imager
2. Enable SSH during initial setup
3. Insert microSD card into Pi 5
4. Connect Pi 5 to network via Ethernet or WiFi
5. Power on and SSH into Pi: `ssh pi@raspberrypi.local`

### Step 2: Enable Required Interfaces

```bash
sudo raspi-config
```

Navigate and enable:
- **Interface Options â†’ I2C â†’ Enable**
- **Interface Options â†’ 1-Wire â†’ Enable** 
- **Interface Options â†’ Camera â†’ Enable**

Reboot: `sudo reboot`

### Step 3: Wire Atlas Scientific Sensors

**Important:** Use electrically isolated carrier boards to prevent ground loops!

```
Each Atlas Sensor:
VCC â†’ Pi 5V (Pin 2 or 4)
SDA â†’ Pi GPIO2/SDA (Pin 3)
SCL â†’ Pi GPIO3/SCL (Pin 5)
GND â†’ Pi GND (Pin 6)
```

**Default I2C Addresses:**
- pH sensor: 0x63
- EC sensor: 0x64
- DO sensor: 0x61

Verify detection:
```bash
sudo i2cdetect -y 1
```

You should see addresses 61, 63, and 64 displayed.

### Step 4: Wire DS18B20 Temperature Sensors

```
DS18B20:
Red Wire    â†’ Pi 3.3V (Pin 1)
Black Wire  â†’ Pi GND (Pin 6)
Yellow Wire â†’ Pi GPIO4 (Pin 7)

IMPORTANT: Add 4.7kÎ© pull-up resistor between GPIO4 and 3.3V!
```

### Step 5: Wire HC-SR04 Water Level Sensor

```
HC-SR04:
VCC   â†’ Pi 5V (Pin 2)
TRIG  â†’ Pi GPIO17 (Pin 11)
ECHO  â†’ Voltage divider â†’ Pi GPIO27 (Pin 13)
GND   â†’ Pi GND (Pin 6)

VOLTAGE DIVIDER (CRITICAL):
ECHO â†’ 1kÎ© â†’ GPIO27 â†’ 2.2kÎ© â†’ GND
```

### Step 6: Connect Relay Module

```
Raspberry Pi 5          Relay Module
GPIO23 (Pin 16) â”€â”€â”€â”€â”€â”€â”€â†’ Control+ terminal
GND (Pin 14) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â†’ Control- terminal
```

### Step 7: Mount Camera

1. Connect Camera Module 3 to Pi 5 camera connector
2. Mount camera 30-50cm above plants
3. Position grow lights at 45Â° angles for consistent imaging

### Step 8: Final Hardware Checklist

- [ ] All sensors wired and detected
- [ ] Relay module connected and responding
- [ ] Camera mounted and functional
- [ ] All connections secure and insulated
- [ ] Sensors submerged in water (except ultrasonic)
- [ ] Pi 5 in waterproof enclosure

---

## Raspberry Pi OS Setup

### Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Install System Dependencies

```bash
sudo apt install -y python3-pip python3-venv python3-opencv \
                    python3-picamera2 i2c-tools python3-smbus2 \
                    python3-gpiozero git libatlas-base-dev
```

### Enable 1-Wire for Temperature Sensors

```bash
sudo nano /boot/firmware/config.txt
```

Add line:
```
dtoverlay=w1-gpio
```

Reboot: `sudo reboot`

Verify temperature sensors:
```bash
ls /sys/bus/w1/devices/
# Should show 28-* directories for each DS18B20
```

---

## Software Installation

### Step 1: Download System Files

```bash
cd ~
mkdir hydroponics
cd hydroponics
```

Copy all system files into this directory:
- main.py
- sensors.py
- ml_vision.py
- llm_interface.py
- database.py
- alerts.py
- config.py
- requirements.txt
- templates/dashboard.html

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This may take 10-20 minutes on Pi 5.

### Step 4: Create Models Directory

```bash
mkdir models
```

**For Plant Disease Detection:**

Download a pre-trained model or train your own. Example:

```bash
# Option 1: Download PlantVillage model (placeholder - replace with actual URL)
# wget https://your-model-source/plant_disease.tflite -O models/plant_disease.tflite

# Option 2: Use mock mode initially (works without model)
# The system will run in mock mode if no model is found
```

### Step 5: Create Static Directory

```bash
mkdir static
# Add any CSS/JS assets here if needed
```

---

## Sensor Calibration

### pH Sensor Calibration (Required)

**Materials needed:**
- pH 4.0 buffer solution
- pH 7.0 buffer solution  
- pH storage solution (3M KCl)

**Procedure:**

```bash
cd ~/hydroponics
source venv/bin/activate
python3
```

```python
from sensors import atlas_sensors
atlas_sensors.initialize()

# Step 1: Calibrate pH 7.0 (mid-point)
# Rinse probe, immerse in pH 7.0 buffer
atlas_sensors.calibrate_ph('mid', 7.00)
# Wait 30 seconds for stabilization

# Step 2: Rinse probe thoroughly

# Step 3: Calibrate pH 4.0 (low point)
# Immerse in pH 4.0 buffer
atlas_sensors.calibrate_ph('low', 4.00)
# Wait 30 seconds

# IMPORTANT: Store probe in pH storage solution, NEVER distilled water!
```

### EC Sensor Calibration

**Materials needed:**
- 1.413 mS/cm calibration solution
- 2.77 mS/cm calibration solution (for wider range)

**Procedure:**

```python
from sensors import atlas_sensors
atlas_sensors.initialize()

# Step 1: Dry calibration
# Remove probe from water, let dry
atlas_sensors.calibrate_ec('dry', 0)

# Step 2: Low-point calibration
# Immerse in 1.413 mS/cm solution
atlas_sensors.calibrate_ec('low', 1413)  # Value in ÂµS/cm

# Step 3: High-point calibration (optional but recommended)
# Rinse and immerse in 2.77 mS/cm solution
atlas_sensors.calibrate_ec('high', 2770)
```

### DO Sensor Calibration

**Materials needed:**
- Just air! (atmospheric calibration)

**Procedure:**

```python
from sensors import atlas_sensors
atlas_sensors.initialize()

# Remove probe from water
# Let sit in air for 2 minutes (shake off water droplets)
atlas_sensors.calibrate_do('atm')

# That's it! For zero calibration, use sodium sulfite solution
```

---

## Configuration

### Step 1: Create .env File

```bash
cd ~/hydroponics
nano .env
```

**Add your settings:**

```bash
# LLM Settings (choose one)
LLM_BACKEND=mock  # Options: openai, anthropic, ollama, mock

# If using OpenAI:
# LLM_BACKEND=openai
# LLM_API_KEY=your-openai-api-key-here

# If using Anthropic Claude:
# LLM_BACKEND=anthropic
# LLM_API_KEY=your-anthropic-api-key-here

# If using local Ollama:
# LLM_BACKEND=ollama
# OLLAMA_URL=http://localhost:11434

# Email Alerts (optional)
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=recipient@email.com

# SMS Alerts (optional - requires Twilio account)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM=+1234567890
SMS_TO=+1234567890
```

### Step 2: Customize config.py

Edit `config.py` to adjust thresholds for your system:

```python
# For hydroponics (leafy greens):
ph_min: float = 5.8
ph_max: float = 6.2

# For aquaponics with fish:
ph_min: float = 6.5
ph_max: float = 7.5
```

**Important thresholds to review:**
- pH range (depends on plants/fish)
- EC range (depends on plant type)
- DO critical level (6+ mg/L for fish)
- Temperature range (depends on species)

---

## Running the System

### Manual Start (Testing)

```bash
cd ~/hydroponics
source venv/bin/activate
python3 main.py
```

System will start on http://raspberrypi.local:8000

### Auto-Start on Boot (Production)

Create systemd service:

```bash
sudo nano /etc/systemd/system/hydroponics.service
```

**Add:**

```ini
[Unit]
Description=STEM DREAM Aquaponics Control System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/hydroponics
Environment="PATH=/home/pi/hydroponics/venv/bin"
ExecStart=/home/pi/hydroponics/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable hydroponics.service
sudo systemctl start hydroponics.service
```

**Check status:**

```bash
sudo systemctl status hydroponics.service
```

**View logs:**

```bash
sudo journalctl -u hydroponics.service -f
```

---

## Using the Dashboard

### Access Dashboard

Open browser and navigate to:
- `http://raspberrypi.local:8000` (from local network)
- `http://[pi-ip-address]:8000` (find IP with `hostname -I`)

### Dashboard Features

**Real-Time Monitoring:**
- Water quality (pH, EC, DO)
- Temperature (reservoir, fish tank)
- Water level
- Equipment status

**Equipment Control:**
- Toggle pumps, lights, heater, aerator
- Manual override for testing

**Plant Health:**
- Click "Analyze Now" to capture image and run ML detection
- View detected issues and recommendations

**Alerts:**
- Recent alerts displayed with severity levels
- Critical alerts trigger notifications

**Chat Assistant:**
- Ask questions about your system
- Get explanations of parameters
- Troubleshooting help

### Example Chat Questions

- "What's wrong with my pH?"
- "Why are my plants yellowing?"
- "Is my dissolved oxygen level safe for trout?"
- "How do I calibrate the pH sensor?"
- "What does EC measure?"

---

## LLM Setup (Optional)

### Option 1: Mock LLM (Default)

No setup needed! System includes pattern-matching responses.

### Option 2: OpenAI GPT-4

1. Get API key from https://platform.openai.com/
2. Add to .env:
```bash
LLM_BACKEND=openai
LLM_API_KEY=sk-...your-key...
```

### Option 3: Anthropic Claude

1. Get API key from https://console.anthropic.com/
2. Add to .env:
```bash
LLM_BACKEND=anthropic
LLM_API_KEY=sk-ant-...your-key...
```

### Option 4: Local Ollama (No API key needed!)

**Install Ollama on Pi 5:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Download a model:**

```bash
ollama pull llama3  # or mistral, mixtral, etc.
```

**Configure system:**

```bash
# In .env:
LLM_BACKEND=ollama
OLLAMA_URL=http://localhost:11434
```

---

## Troubleshooting

### Sensors Not Detected

**Check I2C:**
```bash
sudo i2cdetect -y 1
```

If nothing appears:
- Verify wiring (SDA/SCL correct?)
- Check 5V power to sensors
- Ensure I2C enabled in raspi-config

**Check 1-Wire:**
```bash
ls /sys/bus/w1/devices/
cat /sys/bus/w1/devices/28-*/w1_slave
```

If no devices:
- Verify wiring
- Check pull-up resistor
- Ensure 1-Wire enabled

### Relays Not Working

```bash
# Test relay manually:
python3
```

```python
from gpiozero import DigitalOutputDevice
relay = DigitalOutputDevice(23)
relay.on()   # Should activate relay
relay.off()  # Should deactivate
```

If not working:
- Check GPIO pin number
- Verify power to relay module
- Test with LED instead

### Camera Not Working

```bash
# Test camera:
rpicam-still -o test.jpg
```

If error:
- Check camera cable connection
- Verify camera enabled in raspi-config
- Try: `sudo raspi-config` â†’ Camera â†’ Enable

### System Won't Start

```bash
# Check logs:
sudo journalctl -u hydroponics.service -f

# Check for Python errors:
cd ~/hydroponics
source venv/bin/activate
python3 main.py
```

Common issues:
- Missing dependencies: `pip install -r requirements.txt`
- Permission errors: Run as pi user
- Port already in use: Change port in config.py

---

## Maintenance

### Daily

- [ ] Check dashboard for alerts
- [ ] Verify all sensors reading correctly
- [ ] Monitor plant health status

### Weekly

- [ ] Clean pH probe with HI7061L solution
- [ ] Check DO membrane for damage
- [ ] Wipe camera lens
- [ ] Review sensor trends

### Monthly

- [ ] Calibrate pH sensor
- [ ] Cross-check sensors with handheld meters
- [ ] Test alert system
- [ ] Backup database:
```bash
cp ~/hydroponics/hydroponics.db ~/hydroponics_backup_$(date +%Y%m%d).db
```

### Quarterly

- [ ] Replace DO membrane
- [ ] Calibrate EC sensor
- [ ] Full system cleaning

### Annually

- [ ] Replace pH probe (~$40-60)
- [ ] Replace calibration solutions
- [ ] Deep system maintenance

---

## Next Steps

### For NFT Hydroponic Testing (Current)

1. âœ… Complete hardware assembly
2. âœ… Calibrate all sensors
3. âœ… Start system and verify readings
4. âœ… Plant lettuce seedlings
5. Monitor for 2-4 weeks
6. Iterate on thresholds and automation

### For Future Trout Aquaponics

**CRITICAL Requirements Before Adding Fish:**

1. **System Cycling (4-6 weeks minimum)**
   - Add ammonia source
   - Monitor ammonia â†’ nitrite â†’ nitrate conversion
   - Cycle complete when ammonia and nitrite = 0

2. **Temperature Control**
   - Install chiller for 10-15Â°C water
   - Critical for rainbow trout survival

3. **Dissolved Oxygen**
   - Maintain 7-9 mg/L continuously
   - Install backup battery air pump
   - Add extra air stones

4. **Monitoring**
   - Test ammonia/nitrite daily first month
   - Check DO 3x daily minimum
   - Temperature logged continuously

5. **Emergency Preparedness**
   - UPS backup power
   - Battery air pump
   - Emergency contact plan

**DO NOT add fish until all requirements met!**

---

## Support Resources

**Documentation:**
- Atlas Scientific: https://atlas-scientific.com/
- Raspberry Pi: https://www.raspberrypi.com/documentation/
- FastAPI: https://fastapi.tiangolo.com/

**Community:**
- Aquaponics Association: https://aquaponicsassociation.org/
- Raspberry Pi Forums: https://forums.raspberrypi.com/

**Project Issues:**
- Check logs: `sudo journalctl -u hydroponics.service`
- Database: SQLite Browser for hydroponics.db
- Discord/Forum: (Add your support channel)

---

## License

This STEM DREAM Aquaponics Control System is open source under MIT License.
Educational use encouraged! ðŸŒ±ðŸŸ

---

**Happy Growing! ðŸŒ¿**

Remember: The goal is to learn through real-world STEM applications. Document everything, iterate constantly, and don't be afraid to fail fast and improve!

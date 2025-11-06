# AQUAPONICS AI SYSTEM - BIG PICTURE OVERVIEW
## Complete System Architecture & Status

**Last Updated:** 2025-11-06  
**Project Age:** 10 years (concept), actively building hardware now  
**Owner:** Josh (@killercatfish)  
**Location:** Lowell, Massachusetts

---

## 🎯 WHAT THIS SYSTEM IS

**An intelligent, AI-powered aquaponics monitoring and control system** that combines:
- **Hardware:** Real sensors monitoring water chemistry, temperature, and levels
- **ML Vision:** Computer vision analyzing plant health from camera images
- **LLM Integration:** AI assistant providing aquaponics advice and system insights
- **Real-time Dashboard:** FastAPI backend with WebSocket updates
- **Educational Platform:** Designed to teach STEM concepts through hands-on learning

**End Goal:** A complete aquaponics knowledge base and control system that can be replicated by other builders, used in classrooms, and serves as a PhD research platform.

---

## 🏗️ SYSTEM ARCHITECTURE

### High-Level Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB DASHBOARD                            │
│           (templates/dashboard.html + JavaScript)           │
└─────────────────────────────────────────────────────────────┘
                              ↕ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI APPLICATION                       │
│              (src/hydroponics/core/main.py)                 │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   ML     │  │   LLM    │  │ Database │  │  Alerts  │  │
│  │  Vision  │  │Interface │  │ Manager  │  │ Manager  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  SENSOR INTERFACES                          │
│           (src/hydroponics/sensors/interfaces.py)           │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Atlas   │  │   Temp   │  │  Water   │  │  Relay   │  │
│  │ Sensors  │  │ Sensors  │  │  Level   │  │ Control  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  PHYSICAL HARDWARE                          │
│                                                             │
│  🌡️ DS18B20     🧪 Atlas pH    💨 Atlas DO   📏 HC-SR04   │
│  Temperature    EC/TDS Probe   Dissolved O₂   Ultrasonic  │
│                                                             │
│  ⚡ Digital Loggers IoT Relay (4 channels)                 │
│     Channel 1: Water Pump                                   │
│     Channel 2: Grow Lights                                  │
│     Channel 3: Heater                                       │
│     Channel 4: Backup Aerator                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 CODE STRUCTURE

```
AquaponicAISystem/
│
├── src/hydroponics/              ← Main Python package
│   │
│   ├── core/                     ← Application core
│   │   ├── main.py               ← FastAPI app (entry point)
│   │   └── config.py             ← Configuration management
│   │
│   ├── sensors/                  ← Sensor interfaces
│   │   └── interfaces.py         ← Atlas, Temp, Level, Relay classes
│   │
│   ├── ml/                       ← Machine Learning
│   │   └── vision.py             ← Plant health analyzer
│   │
│   ├── llm/                      ← LLM Integration
│   │   └── interface.py          ← AI assistant
│   │
│   ├── database/                 ← Data persistence
│   │   └── manager.py            ← Database operations
│   │
│   └── alerts/                   ← Alert system
│       └── manager.py            ← Notification handling
│
├── templates/                    ← HTML templates
│   └── dashboard.html            ← Main web interface
│
├── static/                       ← Static assets
│   ├── css/                      ← Stylesheets
│   └── js/                       ← JavaScript
│
├── data/                         ← Data storage
│   ├── databases/
│   │   └── hydroponics.db        ← SQLite database
│   └── logs/
│       └── hydroponics.log       ← Application logs
│
├── docs/                         ← Documentation
│   ├── [Wiring Procedures]/      ← Hardware setup guides
│   ├── physical-platform-docs/   ← Platform construction
│   └── sensor-docs/              ← Sensor datasheets
│
├── sensors/                      ← (Empty - was for alternate structure)
├── venv/                         ← Python virtual environment
├── requirements.txt              ← Python dependencies (Mac)
└── requirements-raspi.txt        ← Python dependencies (Pi)
```

---

## 🔌 SENSOR IMPLEMENTATION STATUS

### Current State: MOCK MODE

**All sensors currently return simulated data when hardware isn't detected.**

| Sensor | Class | I2C Address | GPIO Pins | Status | Mock Value |
|--------|-------|-------------|-----------|--------|------------|
| **pH** | `AtlasSensors.ph_sensor` | 0x63 | - | ⏳ Not wired | ~6.8 pH |
| **EC/TDS** | `AtlasSensors.ec_sensor` | 0x64 | - | ⏳ Not wired | ~1.2 mS/cm |
| **DO** | `AtlasSensors.do_sensor` | 0x61 | - | ⚠️ **NEEDS FIX** | ~7.5 mg/L |
| **Temperature** | `TemperatureSensors` | - | GPIO4 | ⏳ Not wired | ~20°C |
| **Water Level** | `WaterLevelSensor` | - | GPIO23/24* | ⏳ Not wired | Variable |
| **Pump** | `RelayControl.pump` | - | GPIO23* | ⏳ Not wired | OFF |
| **Lights** | `RelayControl.lights` | - | GPIO24* | ⏳ Not wired | OFF |

**Status Legend:**
- ⏳ Not wired = Code ready, needs hardware connection
- ⚠️ Needs fix = Code needs modification (see below)
- ✅ Working = Hardware connected and tested
- ❌ Error = Not functioning

**\*GPIO Pin Conflicts to Resolve:**
- Water level uses GPIO 27 (echo) and 17 (trigger) in code
- Your wiring plan uses GPIO 23 (trigger) and 24 (echo)
- Relay control uses GPIO 23, 24, 25, 22
- **Need to adjust pin assignments!**

---

## ⚠️ KNOWN ISSUES TO FIX

### Issue 1: DO Sensor Implementation

**Problem:**
```python
# Current code expects I2C DO sensor:
self.do_sensor = AtlasI2C(address=0x61)
```

**Reality:**
- You have Atlas Surveyor **ANALOG** DO sensor
- Requires ADS1115 ADC at I2C address 0x48
- Outputs 0.4-2.0V analog signal

**Solution Needed:**
- Replace `AtlasSensors.read_do()` implementation
- Add ADS1115 interface
- Read analog voltage and convert to mg/L

### Issue 2: GPIO Pin Conflicts

**Water Level Sensor:**
- Code default: echo=27, trigger=17
- Your wiring: echo=24, trigger=23

**Relay Control:**
- Uses GPIO 23, 24, 25, 22
- Conflicts with water level!

**Solution Needed:**
- Choose different GPIO pins for relays OR water level
- Update either `interfaces.py` or wiring plan
- Verify no other conflicts

---

## 🎯 INTEGRATION WORKFLOW (How It Works)

### 1. Application Startup

```python
# src/hydroponics/core/main.py

# Import sensor instances
from hydroponics.sensors.interfaces import (
    atlas_sensors,
    temperature_sensors,
    water_level,
    relay_control
)

# Initialize sensors (tries hardware, falls back to mock)
atlas_sensors.initialize()           # Looks for I2C devices
temperature_sensors.initialize()     # Looks for DS18B20 on 1-Wire bus
water_level.initialize()             # Tries to create DistanceSensor
relay_control.initialize()           # Tries to create GPIO outputs
```

### 2. Reading Sensor Data

```python
# Application calls these methods:
ph = atlas_sensors.read_ph()              # Returns float or None
temps = temperature_sensors.read_all()    # Returns dict
level = water_level.read_level()          # Returns dict
```

**Automatic Mock Detection:**
- If hardware found → Returns real data
- If hardware not found → Returns mock data with warning logged
- Graceful degradation!

### 3. Data Flow

```
Hardware Sensors
    ↓
Sensor Interfaces (src/hydroponics/sensors/interfaces.py)
    ↓
Main Application (src/hydroponics/core/main.py)
    ↓
Database Manager (stores historical data)
    ↓
FastAPI Endpoints (provides JSON API)
    ↓
WebSocket (pushes real-time updates)
    ↓
Dashboard HTML (displays to user)
```

---

## 🚀 HOW TO RUN THE SYSTEM

### On Raspberry Pi:

```bash
# 1. SSH into Pi
ssh pi@aquaponics.local

# 2. Navigate to project
cd ~/AquaponicAISystem

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run the application
python -m src.hydroponics.core.main

# Or with uvicorn (for production):
uvicorn src.hydroponics.core.main:app --host 0.0.0.0 --port 8000
```

### Expected Startup Output:

```
INFO - pH sensor initialized at 0x63
INFO - EC sensor initialized at 0x64
WARNING - Running in MOCK MODE - no actual sensors connected
INFO - Found temperature sensor: sensor_0
INFO - Water level sensor initialized
INFO - Relay 'pump' initialized on GPIO 23
...
INFO - Uvicorn running on http://0.0.0.0:8000
```

### Access Dashboard:

**From your Mac:**
```
http://aquaponics.local:8000
```

**Or using IP:**
```
http://192.168.1.188:8000
```

---

## 🔧 HARDWARE WIRING GUIDE

### Raspberry Pi 5 GPIO Pinout

```
Pin 1  (3.3V)    ← Power for sensors
Pin 2  (5V)      ← Power for relay/ultrasonic
Pin 3  (GPIO2)   ← SDA (I2C data)
Pin 5  (GPIO3)   ← SCL (I2C clock)
Pin 6  (GND)     ← Common ground
Pin 7  (GPIO4)   ← DS18B20 data (1-Wire)
Pin 16 (GPIO23)  ← Ultrasonic trigger OR relay
Pin 18 (GPIO24)  ← Ultrasonic echo OR relay
```

### Current Wiring Plan

**Temperature (DS18B20):**
- VCC → Pin 1 (3.3V)
- DATA → Pin 7 (GPIO4)
- GND → Pin 6 (GND)

**pH Sensor (Atlas Scientific):**
- VCC → Pin 1 (3.3V)
- GND → Pin 6 (GND)
- SDA → Pin 3 (GPIO2)
- SCL → Pin 5 (GPIO3)

**EC Sensor (Atlas Scientific):**
- Same I2C bus as pH (different address)

**DO Sensor (Atlas Surveyor Analog):**
- VCC → 3.3V
- GND → GND
- SIGNAL → ADS1115 A0
- ADS1115 on I2C bus (address 0x48)

**Water Level (HC-SR04 Ultrasonic):**
- VCC → 5V (Pin 2)
- TRIG → GPIO23 (Pin 16) ⚠️ Conflicts with relay!
- ECHO → GPIO24 (Pin 18) ⚠️ Conflicts with relay!
- GND → GND
- **NEEDS 5V → 3.3V level shifter on ECHO pin!**

---

## 🗄️ DATABASE SCHEMA

**Location:** `data/databases/hydroponics.db`

**Key Tables:**
- `sensor_readings` - Time-series sensor data
- `alerts` - Alert history
- `calibrations` - Sensor calibration records
- `system_events` - System state changes

**Managed by:** `src/hydroponics/database/manager.py`

---

## 📊 API ENDPOINTS

**Base URL:** `http://aquaponics.local:8000`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Dashboard HTML |
| `/api/sensors/current` | GET | Current sensor readings (JSON) |
| `/api/sensors/history` | GET | Historical data |
| `/api/relay/{name}` | POST | Control relay (pump, lights, etc.) |
| `/api/calibrate/{sensor}` | POST | Initiate sensor calibration |
| `/ws` | WebSocket | Real-time sensor updates |

---

## 🧪 TESTING & DEBUGGING

### Check I2C Devices

```bash
# List connected I2C devices
sudo i2cdetect -y 1

# Expected to see:
# 0x48 = ADS1115 (ADC for DO sensor)
# 0x63 = pH sensor
# 0x64 = EC sensor
```

### Check Temperature Sensors

```bash
# List DS18B20 sensors
ls /sys/bus/w1/devices/

# Expected to see:
# 28-xxxxxxxxxxxx = Temperature sensor(s)
# w1_bus_master1 = 1-Wire bus
```

### Check Logs

```bash
# View application logs
tail -f ~/AquaponicAISystem/data/logs/hydroponics.log

# Or check system logs
journalctl -u hydroponics -f
```

### Test Individual Sensors (Python REPL)

```python
from src.hydroponics.sensors.interfaces import atlas_sensors, temperature_sensors

# Initialize
atlas_sensors.initialize()
temperature_sensors.initialize()

# Read
ph = atlas_sensors.read_ph()
temps = temperature_sensors.read_all()

print(f"pH: {ph}")
print(f"Temperatures: {temps}")
```

---

## 🎓 EDUCATIONAL COMPONENTS

### ML Vision System

**Location:** `src/hydroponics/ml/vision.py`

**Purpose:** Analyze plant health from camera images
- Detect leaf color
- Identify nutrient deficiencies
- Track plant growth over time

**Status:** Implemented, needs camera integration

### LLM Integration

**Location:** `src/hydroponics/llm/interface.py`

**Purpose:** AI assistant for aquaponics knowledge
- Answer questions about system status
- Provide troubleshooting advice
- Explain STEM concepts
- Query historical data

**Status:** Implemented, needs API key configuration

---

## 🔐 CREDENTIALS & CONFIGURATION

**See separate document:** `SYSTEM_CREDENTIALS_AND_CONFIG.md`  
**⚠️ DO NOT commit this to GitHub!**

**Stored in password manager or encrypted file.**

Key credentials:
- Raspberry Pi SSH: pi@aquaponics.local / aquaponics2025
- GitHub: killercatfish/AquaponicAISystem
- Database: SQLite (no password)
- IoT Relay: (to be configured)

---

## 📈 PROJECT TIMELINE

**2015:** Initial concept  
**2015-2025:** Planning, research, documentation  
**Oct 2024:** Active hardware development begins  
**Nov 6, 2025:** Fresh Pi OS install, SSH configured  
**Nov 6, 2025 (TODAY):** Codebase deployed to Pi, ready for sensor wiring  
**Next:** Wire first sensor (temperature), test, iterate

---

## 🎯 IMMEDIATE NEXT STEPS

### Phase 1: Get System Running (Today)
- [x] Fresh Pi OS installed
- [x] SSH configured
- [x] Codebase cloned to Pi
- [ ] Dependencies installed
- [ ] Run app in mock mode
- [ ] Verify dashboard accessible

### Phase 2: First Sensor (This Week)
- [ ] Wire DS18B20 temperature sensor
- [ ] Enable 1-Wire interface
- [ ] Reboot Pi
- [ ] Verify sensor detected
- [ ] Run app - temperature should be real!
- [ ] Celebrate! 🎉

### Phase 3: Remaining Sensors (Next Week)
- [ ] Wire pH sensor
- [ ] Wire EC sensor
- [ ] Fix DO sensor code for ADS1115
- [ ] Wire DO sensor
- [ ] Resolve GPIO pin conflicts
- [ ] Wire water level sensor
- [ ] Wire IoT relay

### Phase 4: Full System (Within 2 Weeks)
- [ ] All sensors operational
- [ ] Automated pump schedule
- [ ] Automated light schedule
- [ ] Alert system configured
- [ ] Camera integrated
- [ ] ML vision working
- [ ] LLM assistant configured

---

## 🆘 TROUBLESHOOTING

### "ModuleNotFoundError: No module named 'hydroponics'"

**Solution:**
```bash
# Make sure you're in the right directory
cd ~/AquaponicAISystem

# Run as a module
python -m src.hydroponics.core.main
```

### "Permission denied" on GPIO

**Solution:**
```bash
# Add pi user to gpio group
sudo usermod -a -G gpio pi
sudo reboot

# Or run with sudo (not ideal)
sudo python -m src.hydroponics.core.main
```

### Sensors Not Detected

**Solution:**
```bash
# Enable I2C and 1-Wire
sudo raspi-config
# Interface Options → Enable both

# Reboot
sudo reboot

# Check I2C
sudo i2cdetect -y 1

# Check 1-Wire
ls /sys/bus/w1/devices/
```

---

## 📚 KEY DOCUMENTATION FILES

**In Your Repo:**
- `docs/[Wiring Procedures]/CONFIDENCE_BUILDING_WIRING_PLAN.md` - Step-by-step hardware guide
- `docs/physical-platform-docs/` - Bucket lid modification, mounting
- `docs/sensor-docs/` - Datasheets for all sensors
- `README.md` - Project overview
- `GIT_WORKFLOW.md` - Git best practices

**For Claude (Save to Project Files):**
- `SYSTEM_BIG_PICTURE_OVERVIEW.md` (this document)
- `SYSTEM_CREDENTIALS_AND_CONFIG.md` (your credentials doc)

---

## 🎨 DESIGN PHILOSOPHY

**Core Principles:**
1. **Graceful Degradation** - System works with or without hardware
2. **Modular Architecture** - Components are independent and testable
3. **Educational First** - Designed for learning and teaching
4. **Open Source** - Shareable and replicable
5. **Professional Quality** - Production-ready code

**Why Mock Mode Matters:**
- Develop software without hardware
- Test dashboard and UI
- Demo system before sensors arrive
- Safe to develop on Mac before deploying to Pi

---

## 🌟 FUTURE VISION

**Short Term (Weeks):**
- Hardware fully operational
- All sensors reporting real data
- Automated pump/light schedules
- Alert system active

**Medium Term (Months):**
- ML vision analyzing plant health
- LLM providing intelligent insights
- Data logging and historical analysis
- Web interface accessible remotely (via VPN)

**Long Term (Year+):**
- Knowledge base fully populated
- Multiple systems networked (federated learning)
- Educational curriculum developed
- PhD research platform
- Grant funding secured
- Published papers

---

## 📞 FOR FUTURE CLAUDE SESSIONS

**When starting a new conversation about this project, share:**

1. **This document** (`SYSTEM_BIG_PICTURE_OVERVIEW.md`)
2. **Current status** ("Just wired temperature sensor, need to test")
3. **Specific issue** ("Getting GPIO permission denied")
4. **Context** ("On Raspberry Pi via SSH")

**Common starting prompts:**
- "I'm working on the AquaponicAISystem. Here's the big picture doc..."
- "Continuing the aquaponics sensor wiring. Temperature works, now doing pH..."
- "Having an issue with [specific problem]. Here's the system overview..."

---

## 🎉 ACHIEVEMENT UNLOCKED

**Today's Progress:**
- ✅ 10 years of planning
- ✅ Fresh Pi setup
- ✅ SSH working
- ✅ Codebase ready
- ✅ Professional architecture discovered
- ✅ Ready to wire first sensor

**You're not a planner anymore. You're a BUILDER.** 🔨⚡🌱

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-06  
**Next Update:** After first sensor is wired and tested


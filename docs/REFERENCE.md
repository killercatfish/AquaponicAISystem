# Quick Reference Guide

## Common Commands

### Setup & Installation
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate              # Linux/Mac
venv\Scripts\activate                 # Windows

# Install dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate
```

### Running the System
```bash
# Test before running
python test_system.py

# Run main application
python main.py

# Run in background (Linux)
nohup python main.py &

# View logs
tail -f hydroponics.log

# Stop background process
killall python
```

### Git Commands
```bash
# Initialize Git
./setup_git.sh

# Check status
git status

# Stage files
git add .

# Commit
git commit -m "Your message"

# Push to GitHub
git push origin main

# Pull updates
git pull origin main

# View history
git log --oneline
```

### Database Management
```bash
# View database
sqlite3 hydroponics.db

# In SQLite shell:
.tables                    # List tables
SELECT * FROM sensor_readings LIMIT 10;
.exit                      # Exit

# Backup database
cp hydroponics.db backup_$(date +%Y%m%d).db

# Fresh start
rm hydroponics.db
```

### Testing & Debugging
```bash
# Run full test suite
python test_system.py

# Test specific component
python -c "from sensors import atlas_sensors; atlas_sensors.initialize(); print(atlas_sensors.read_ph())"

# Check I2C devices (Raspberry Pi)
sudo i2cdetect -y 1

# Test camera (Raspberry Pi)
rpicam-still -o test.jpg

# View system logs
journalctl -u hydroponics.service -f
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (User)                        │
│                  http://localhost:8000                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Web Server                        │
│                      (main.py)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Endpoints: /api/status, /api/sensors, /ws, etc.   │   │
│  └─────────────────────────────────────────────────────┘   │
└───┬─────────────┬──────────────┬────────────┬──────────────┘
    │             │              │            │
    ▼             ▼              ▼            ▼
┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
│ Sensors │  │ ML Vision│  │   LLM   │  │ Database │
│ Module  │  │  Module  │  │Interface│  │ Manager  │
│sensors.py│  │ml_vision.│  │llm_int..│  │database.│
└────┬────┘  └─────┬────┘  └────┬────┘  └─────┬────┘
     │            │             │             │
     ▼            ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐
│Hardware │  │ Camera  │  │LLM API   │  │ SQLite  │
│Sensors  │  │ Pi Cam  │  │(Optional)│  │   DB    │
│pH,EC,DO │  │         │  │          │  │         │
└─────────┘  └─────────┘  └──────────┘  └─────────┘
```

## Module Responsibilities

### main.py
- FastAPI application setup
- WebSocket connections
- API endpoints
- Scheduled tasks (APScheduler)
- System state management

### sensors.py
- Atlas Scientific sensors (pH, EC, DO)
- DS18B20 temperature sensors
- HC-SR04 water level sensor
- 4-channel relay control
- Mock mode for testing

### ml_vision.py
- TensorFlow Lite model loading
- Pi Camera capture
- Image preprocessing
- Plant disease/deficiency detection
- Recommendation generation

### llm_interface.py
- OpenAI/Anthropic/Ollama integration
- Context building from system state
- Natural language query processing
- Educational explanations
- Mock mode responses

### database.py
- SQLite/InfluxDB connections
- Sensor data logging
- Alert logging
- Historical data queries
- Data export functions

### alerts.py
- Threshold monitoring
- Alert level determination (info/warning/critical)
- Email notifications (via yagmail)
- SMS notifications (via Twilio)
- Alert cooldown management

### config.py
- System configuration
- Sensor thresholds
- API keys (loaded from .env)
- Hardware pin assignments
- Feature toggles

## Data Flow

### Sensor Reading Cycle (Every 5 minutes)
```
1. Scheduler triggers read_all_sensors()
2. sensors.py reads all sensor values
3. Values stored in system_state dict
4. database.py logs to SQLite
5. alerts.py checks thresholds
6. WebSocket broadcasts update to dashboard
```

### Plant Analysis Cycle (Every 1 hour)
```
1. Scheduler triggers analyze_plant_health()
2. ml_vision.py captures image
3. Model runs inference
4. Results stored in system_state
5. database.py logs analysis
6. Alerts generated if issues detected
7. WebSocket broadcasts update
```

### User Query Flow
```
1. User types question in dashboard
2. WebSocket sends to /api/chat
3. llm_interface.py builds context from system_state
4. LLM generates response (cloud or local)
5. database.py logs conversation
6. Response sent back via WebSocket
7. Dashboard displays answer
```

## Configuration Quick Reference

### Important Thresholds (config.py)

```python
# pH (Acidity/Alkalinity)
ph_min = 6.0           # Below this: warning
ph_max = 7.0           # Above this: warning
ph_critical_low = 5.0  # Below this: CRITICAL
ph_critical_high = 8.0 # Above this: CRITICAL

# EC - Electrical Conductivity (mS/cm)
ec_min = 1.0           # Below: plants underfed
ec_max = 1.8           # Above: risk of burn
ec_critical_low = 0.5  # Too weak
ec_critical_high = 3.0 # Nutrient burn

# DO - Dissolved Oxygen (mg/L)
do_normal = 7.0        # Target for health
do_critical = 5.0      # Below: fish/plant stress

# Temperature (°C)
temp_min = 18.0        # Below: slow growth
temp_max = 22.0        # Above: disease risk
```

### Sensor I2C Addresses
```python
pH sensor:  0x63 (99 decimal)
EC sensor:  0x64 (100 decimal)
DO sensor:  0x61 (97 decimal)
```

### GPIO Pin Assignments
```python
Temperature: GPIO4 (Pin 7)
Water Level Trigger: GPIO17 (Pin 11)
Water Level Echo: GPIO27 (Pin 13)
Relay Pump: GPIO23 (Pin 16)
Relay Lights: GPIO24 (Pin 18)
Relay Heater: GPIO25 (Pin 22)
Relay Aerator: GPIO22 (Pin 15)
```

## API Endpoints

### GET Endpoints
- `/` - Dashboard HTML
- `/api/status` - Full system state
- `/api/sensors` - Current sensor readings
- `/api/history/{sensor}/{hours}` - Historical data

### POST Endpoints
- `/api/relay/{name}/{action}` - Control relay (on/off)
- `/api/analyze_now` - Trigger plant analysis
- `/api/chat` - Send message to LLM

### WebSocket
- `/ws` - Real-time bidirectional updates

## Troubleshooting Quick Guide

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| Port in use | Change `web_port` in config.py |
| Database locked | `killall python && rm hydroponics.db` |
| No sensor readings | Check I2C: `sudo i2cdetect -y 1` |
| Camera not working | `rpicam-still -o test.jpg` |
| Mock mode warnings | Normal! Hardware not required yet |
| Dashboard not loading | Check `python main.py` for errors |
| WebSocket disconnects | Check browser console for errors |

## File Locations

### Configuration
- `config.py` - Main configuration
- `.env` - Secrets (API keys, passwords)
- `.env.example` - Template

### Data
- `hydroponics.db` - SQLite database
- `hydroponics.log` - System logs
- `models/` - ML models

### Code
- `main.py` - Application entry point
- `sensors.py` - Hardware interfaces
- `ml_vision.py` - Plant detection
- `llm_interface.py` - AI chatbot
- `database.py` - Data persistence
- `alerts.py` - Notifications
- `config.py` - Configuration

### Documentation
- `README.md` - Project overview
- `SETUP_GUIDE.md` - Hardware setup
- `QUICKSTART.md` - Testing guide
- `PROJECT_STATUS.md` - Current status
- `CONTRIBUTING.md` - How to contribute

### Web
- `templates/dashboard.html` - Web interface
- `static/` - CSS/JS assets (if any)

## Environment Variables

Create `.env` file with:
```bash
# LLM Configuration
LLM_BACKEND=mock
LLM_API_KEY=your-key-here

# Ollama (local LLM)
OLLAMA_URL=http://localhost:11434

# Email Alerts
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=alert-recipient@email.com

# SMS Alerts (Twilio)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_FROM=+1234567890
SMS_TO=+1234567890
```

## Testing Checklist

Quick test before deploying:
```bash
✓ python test_system.py          # All tests pass
✓ python main.py                 # Starts without error
✓ Open http://localhost:8000     # Dashboard loads
✓ Toggle a relay                 # Control works
✓ Click "Analyze Now"            # ML runs
✓ Ask chat a question            # LLM responds
✓ Check hydroponics.log          # No errors
✓ Check hydroponics.db exists    # Database created
```

## Performance Benchmarks

Expected performance on Raspberry Pi 5:

| Operation | Time | Frequency |
|-----------|------|-----------|
| Sensor Reading | 3-5s | Every 5 min |
| Plant Analysis | 5-10s | Every 1 hour |
| LLM Response (mock) | <1s | On demand |
| LLM Response (API) | 2-5s | On demand |
| Database Write | <100ms | Every 5 min |
| Dashboard Update | <100ms | Real-time |

## Memory Usage

Typical RAM usage:
- Base system: ~200 MB
- With camera: +100 MB
- With ML model: +150 MB
- **Total: ~450 MB** (plenty of headroom on 8GB Pi 5)

## Network Ports

- `8000` - Web dashboard (default)
- `8086` - InfluxDB (if enabled)
- `11434` - Ollama (if using local LLM)

## Backup Strategy

Recommended backups:
```bash
# Daily database backup
cp hydroponics.db backups/db_$(date +%Y%m%d).db

# Weekly code backup (use Git!)
git commit -am "Weekly backup"
git push

# Export sensor data
python -c "from database import DatabaseManager; db = DatabaseManager(); db.export_data(start, end, 'export.csv')"
```

---

**Pro Tip:** Keep this file open in a terminal while working on the system!

```bash
# View in terminal with less
less REFERENCE.md

# Or use cat with grep
cat REFERENCE.md | grep -A 5 "Common Commands"
```

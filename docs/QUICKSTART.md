# Quick Start Guide - Testing Before Hardware Arrives

This guide helps you test the STEM DREAM Aquaponics Control System in **mock mode** before your sensors arrive.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Quick Setup (5 minutes)

### 1. Create Project Directory

```bash
mkdir stem-dream-aquaponics
cd stem-dream-aquaponics
```

### 2. Copy All Project Files

Copy these files into your project directory:
- `main.py` - Main application
- `sensors.py` - Sensor interfaces
- `ml_vision.py` - Plant health detection
- `llm_interface.py` - LLM chatbot
- `database.py` - Data logging
- `alerts.py` - Alert system
- `config.py` - Configuration
- `requirements.txt` - Dependencies
- `test_system.py` - Test script
- `setup_git.sh` - Git setup script
- `templates/dashboard.html` - Web interface
- `README.md` - Documentation
- `SETUP_GUIDE.md` - Hardware setup

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ This may take 5-10 minutes depending on your internet connection.

### 5. Run Tests

```bash
python test_system.py
```

Expected output:
```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
STEM DREAM Aquaponics Control System - Test Suite
Testing all components in mock mode...
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

============================================================
  Testing Module Imports
============================================================
✓ fastapi
✓ uvicorn
...

✅ All tests passed! System is ready for hardware integration.
```

### 6. Run the System

```bash
python main.py
```

Open your browser to: **http://localhost:8000**

You should see the dashboard with **mock sensor data**!

## What You Can Test Now

### ✅ Web Dashboard
- View real-time sensor readings (mock data)
- See charts and graphs
- Monitor system status
- View alerts

### ✅ Equipment Control
- Toggle relays on/off
- See relay status updates
- Test manual override

### ✅ Plant Health Analysis
- Click "Analyze Now" button
- View mock plant health results
- See recommendations

### ✅ LLM Chat Assistant
- Ask questions like:
  - "What's my current pH?"
  - "Why is my dissolved oxygen low?"
  - "What does EC measure?"
- Get educational responses (mock mode)

### ✅ Database Logging
- Sensor data being logged every 5 minutes
- View `hydroponics.db` file created
- Check logs in `hydroponics.log`

### ✅ Alert System
- Simulated alerts for out-of-range values
- View alert history
- Test notification logic

## Mock Mode Features

The system runs in **mock mode** automatically when hardware is not detected:

| Component | Mock Behavior |
|-----------|---------------|
| **pH Sensor** | Returns 6.5-7.0 varying over time |
| **EC Sensor** | Returns 1.0-1.5 mS/cm |
| **DO Sensor** | Returns 7.0-8.0 mg/L |
| **Temperature** | Returns 18-22°C |
| **Water Level** | Returns 60-80% |
| **Camera** | Generates random image data |
| **ML Model** | Returns "healthy" with 85% confidence |
| **Relays** | Logs commands without GPIO access |

## Testing Checklist

Before sensors arrive, verify:

- [ ] Web dashboard loads at http://localhost:8000
- [ ] Sensor readings update (even if mock data)
- [ ] Charts display (may be empty initially)
- [ ] Equipment toggles respond (check logs)
- [ ] Plant health analysis runs
- [ ] LLM chat responds to questions
- [ ] Alerts appear when simulated
- [ ] Database file created (`hydroponics.db`)
- [ ] Log file created (`hydroponics.log`)

## Common Issues

### Port Already in Use
```bash
# Change port in config.py
web_port: int = 8001  # Change from 8000

# Or kill existing process
killall python
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Import Errors
Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

### Database Locked
```bash
# Stop any running instances
killall python

# Delete database to start fresh
rm hydroponics.db
```

## Viewing the Database

Install SQLite browser:
```bash
# macOS
brew install --cask db-browser-for-sqlite

# Ubuntu/Debian
sudo apt install sqlitebrowser

# Windows
# Download from: https://sqlitebrowser.org/
```

Open `hydroponics.db` to view:
- sensor_readings table
- alerts table
- plant_analysis table
- system_actions table

## Viewing Logs

```bash
# Watch logs in real-time
tail -f hydroponics.log

# View all logs
cat hydroponics.log

# Search for errors
grep ERROR hydroponics.log
```

## Configuration

Edit `config.py` to customize:

```python
# Sensor read interval
sensor_read_interval: int = 5  # minutes

# Plant analysis interval
plant_analysis_interval: int = 1  # hours

# LLM backend
llm_backend: str = 'mock'  # Change to 'openai' or 'anthropic' later

# Thresholds
ph_min: float = 6.0
ph_max: float = 7.0
```

## Preparing for Hardware

When sensors arrive:

1. **Stop the system**: `Ctrl+C` in terminal
2. **Follow SETUP_GUIDE.md** for hardware wiring
3. **Enable I2C/1-Wire**: `sudo raspi-config`
4. **Test sensors**: `sudo i2cdetect -y 1`
5. **Calibrate sensors**: Follow calibration procedures
6. **Restart system**: `python main.py`
7. **Verify real readings**: Check dashboard shows actual data

## Git Setup (Optional)

To version control your project:

```bash
# Make script executable
chmod +x setup_git.sh

# Run Git setup
./setup_git.sh

# Create initial commit
git commit -m "Initial commit: STEM DREAM Aquaponics Control System"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/repo-name.git
git push -u origin main
```

## Next Steps

1. ✅ **Test system thoroughly in mock mode**
2. 📝 **Document any issues or questions**
3. 🔧 **Customize thresholds for your plants/fish**
4. 📚 **Read through code to understand architecture**
5. 🎨 **Customize dashboard.html if desired**
6. 🐙 **Push to GitHub for version control**
7. 📦 **Wait for sensors to arrive!**
8. 🔌 **Follow SETUP_GUIDE.md for hardware integration**

## Getting Help

- Check `README.md` for overview
- Read `SETUP_GUIDE.md` for hardware details
- Review code comments for explanations
- Test with `python test_system.py`
- Check logs: `tail -f hydroponics.log`

## Educational Exploration

While waiting for hardware, explore:

### Python Concepts
- FastAPI web framework
- Async/await patterns
- WebSocket real-time updates
- SQLite database operations
- Class-based architecture

### STEM Learning
- Water chemistry (pH, EC, DO)
- Plant nutrient uptake
- Nitrogen cycle (for aquaponics)
- Temperature effects on dissolved oxygen
- Machine learning for image classification
- Natural language processing with LLMs

### System Design
- Sensor abstraction layers
- Mock testing strategies
- Real-time monitoring architecture
- Alert threshold systems
- Database schema design

## Success Criteria

You're ready for hardware when:

✅ All tests pass (`python test_system.py`)
✅ Dashboard loads and displays mock data
✅ No errors in `hydroponics.log`
✅ Database is logging correctly
✅ You understand the basic architecture
✅ Git repository is set up (optional)
✅ You've customized config for your system

---

**🎉 Happy Testing!**

The goal is to have everything working in software so when hardware arrives, you just connect and calibrate! This saves a lot of debugging time and lets you learn the system before dealing with hardware issues.

Questions? Check the code comments or README.md for detailed explanations of each component.

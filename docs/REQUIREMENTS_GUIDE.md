# Requirements Files Guide

## Two Files, Two Purposes

### requirements.txt (Development/Mac/PC)
**[Download requirements.txt](computer:///mnt/user-data/outputs/requirements.txt)**

**Use when:** Testing on Mac, Windows, or Linux PC
**Contains:** Core packages only
**Hardware:** None required (mock mode)

```python
# Installs these:
✅ fastapi, uvicorn (web)
✅ numpy, pillow (data/images)
✅ requests, python-dotenv (utils)
✅ apscheduler (scheduling)

# Skips these (commented out):
❌ atlas-i2c (sensors)
❌ gpiozero (GPIO)
❌ picamera2 (camera)
❌ tflite-runtime (ML)
```

---

### requirements-raspi.txt (Production/Raspberry Pi)
**[Download requirements-raspi.txt](computer:///mnt/user-data/outputs/requirements-raspi.txt)**

**Use when:** Deploying to Raspberry Pi with real hardware
**Contains:** All packages including hardware interfaces
**Hardware:** Sensors, camera, GPIO required

```python
# Installs these:
✅ Everything from requirements.txt
✅ atlas-i2c (pH/EC/DO sensors)
✅ gpiozero (GPIO control)
✅ picamera2 (camera)
✅ tflite-runtime (ML inference)
✅ opencv-python (image processing)

# Optional (commented):
⚠️ openai/anthropic (LLMs)
⚠️ yagmail (email alerts)
⚠️ twilio (SMS alerts)
```

---

## Quick Comparison Table

| Feature | requirements.txt | requirements-raspi.txt |
|---------|-----------------|------------------------|
| **Platform** | Mac/Windows/Linux | Raspberry Pi |
| **Hardware** | None (mock mode) | Sensors, camera, GPIO |
| **Size** | ~50MB | ~200MB+ |
| **Install Time** | 2-3 minutes | 10-15 minutes |
| **Test System** | ✅ Yes | ✅ Yes |
| **Real Sensors** | ❌ No | ✅ Yes |
| **ML Vision** | ❌ Mock only | ✅ Real camera |
| **GPIO Control** | ❌ Mock only | ✅ Real relays |

---

## When to Use Which

### Use requirements.txt When:
- ✅ Developing on Mac/PC
- ✅ Testing code changes
- ✅ Learning the system
- ✅ Setting up Git repository
- ✅ Mock mode is sufficient
- ✅ No hardware available yet

**Installation:**
```bash
pip install -r requirements.txt
```

### Use requirements-raspi.txt When:
- ✅ Deploying to Raspberry Pi
- ✅ Connecting real sensors
- ✅ Using camera for ML
- ✅ Controlling real equipment
- ✅ Production system
- ✅ Hardware is ready

**Installation:**
```bash
# First install system packages
sudo apt install -y python3-opencv python3-picamera2 i2c-tools

# Then install Python packages
pip install -r requirements-raspi.txt
```

---

## Version Strategy: Why `>=` Instead of `==`

Both files now use flexible versions (`>=`) instead of exact versions (`==`).

### Why This Change?

**Old Way (Exact Versions):**
```python
pillow==10.2.0    # Must be exactly 10.2.0
```
❌ Breaks on Python 3.14
❌ Breaks if package version removed
❌ No security updates

**New Way (Minimum Versions):**
```python
pillow>=10.0.0    # At least 10.0.0, can be newer
```
✅ Works on Python 3.9-3.14
✅ Gets latest compatible version
✅ Includes security patches
✅ Future-proof

### Benefits

1. **Python 3.14 Compatible** - Works with newest Python
2. **Backwards Compatible** - Still works on older Python
3. **Auto-Updates** - Gets bug fixes and security patches
4. **Less Maintenance** - Don't need to update version numbers constantly

### Trade-offs

**Pros:**
- More flexible
- Better compatibility
- Automatic improvements

**Cons:**
- Slightly less reproducible (but close)
- May get breaking changes (rare with semantic versioning)

**For this project:** Flexible versions are better because:
- It's educational (latest features are good)
- Mock mode is forgiving
- Real sensors have stable APIs
- Active development benefits from updates

---

## Installation Workflow

### Phase 1: Development (Your Mac Now)
```bash
cd AquaponicsAISystem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Use Mac version
python test_system.py            # All tests pass
python main.py                   # Mock mode works
```

### Phase 2: Deployment (Raspberry Pi Later)
```bash
# On Raspberry Pi
cd ~/aquaponics
python3 -m venv venv
source venv/bin/activate

# Install system dependencies first
sudo apt install -y python3-opencv python3-picamera2 \
                    i2c-tools python3-smbus libatlas-base-dev

# Install Python packages
pip install -r requirements-raspi.txt

# Enable hardware
sudo raspi-config  # Enable I2C, 1-Wire, Camera

# Test with real hardware
python test_system.py
python main.py
```

---

## Customizing for Your Needs

### Adding OpenAI Support
Edit requirements file and uncomment:
```python
openai>=1.10.0
```

Then:
```bash
pip install openai
```

Add to `.env`:
```bash
LLM_BACKEND=openai
LLM_API_KEY=sk-your-key-here
```

### Adding Email Alerts
Edit requirements file and uncomment:
```python
yagmail>=0.15.0
```

Then:
```bash
pip install yagmail
```

Add to `.env`:
```bash
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=recipient@email.com
```

### Adding SMS Alerts
Edit requirements file and uncomment:
```python
twilio>=8.13.0
```

Then:
```bash
pip install twilio
```

Add to `.env`:
```bash
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_FROM=+1234567890
SMS_TO=+1234567890
```

---

## Upgrading Packages

### Check for Updates
```bash
pip list --outdated
```

### Update All
```bash
pip install --upgrade -r requirements.txt
```

### Update One Package
```bash
pip install --upgrade fastapi
```

### Pin to Specific Version (if needed)
```bash
pip install fastapi==0.109.0
```

---

## Troubleshooting

### "Package not found"
**Solution:** Update pip first
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "Build failed" on Raspberry Pi
**Solution:** Install system packages first
```bash
sudo apt install -y python3-dev build-essential
```

### "Import error" after install
**Solution:** Check you're in virtual environment
```bash
which python  # Should show venv path
source venv/bin/activate
```

### Different behavior on Pi vs Mac
**Solution:** This is expected! Hardware differences mean:
- Mac: All mock mode
- Pi: Can use real hardware

---

## Best Practices

### ✅ Do This:
- Use `requirements.txt` for development
- Use `requirements-raspi.txt` for production
- Keep both files in sync (same versions)
- Commit both to Git
- Test on Mac before deploying to Pi

### ❌ Don't Do This:
- Mix packages between files
- Install hardware packages on Mac (won't work)
- Skip system dependencies on Pi
- Use exact versions for everything
- Install as root (use venv!)

---

## Summary

| File | Purpose | When |
|------|---------|------|
| **requirements.txt** | Development/Testing | Mac/PC, no hardware |
| **requirements-raspi.txt** | Production | Raspberry Pi with sensors |

Both now use flexible versions (`>=`) for better Python 3.14 compatibility!

**Current Status:**
- ✅ Mac version ready to use NOW
- ✅ Pi version ready for deployment LATER
- ✅ Both Python 3.9-3.14 compatible
- ✅ Both use flexible versioning

---

**Questions?** The updated files should work perfectly on both platforms! 🚀

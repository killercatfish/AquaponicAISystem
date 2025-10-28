# Installation Instructions

## Quick Fix for Your Error

You got an error because `atlas-i2c==1.0.0` doesn't exist. I've fixed this!

**Download the updated file:**
- [**requirements.txt (Mac-friendly)**](computer:///mnt/user-data/outputs/requirements.txt) ⭐ Use this one!
- [requirements-raspi.txt (Raspberry Pi full)](computer:///mnt/user-data/outputs/requirements-raspi.txt) - Save for later

---

## Installation on Mac (Development/Testing)

### Step 1: Download Updated requirements.txt
Replace your current `requirements.txt` with the new one from the link above.

### Step 2: Install Core Dependencies
```bash
cd AquaponicsAISystem
source venv/bin/activate
pip install -r requirements.txt
```

This will install **only** the packages needed for testing in mock mode:
- ✅ FastAPI, uvicorn (web server)
- ✅ websockets, jinja2 (web interface)
- ✅ numpy, pillow (basic data/image)
- ✅ requests (for API calls)
- ✅ apscheduler (scheduling)
- ✅ python-dotenv (configuration)

**Hardware-specific packages are commented out** - they won't install on Mac anyway!

### Step 3: Test It
```bash
python test_system.py
```

Expected output:
```
✅ All tests passed! System is ready for hardware integration.
```

### Step 4: Run It
```bash
python main.py
```

Open: http://localhost:8000

---

## Installation on Raspberry Pi (Production)

When you deploy to Raspberry Pi with actual hardware:

### Step 1: Use Full Requirements
```bash
# Use the Raspberry Pi version
cp requirements-raspi.txt requirements.txt

# Or download it fresh
wget https://your-repo/requirements-raspi.txt -O requirements.txt
```

### Step 2: Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv i2c-tools \
                    python3-opencv python3-picamera2 \
                    libatlas-base-dev
```

### Step 3: Enable Hardware Interfaces
```bash
sudo raspi-config
# Navigate to: Interface Options
# Enable: I2C, 1-Wire, Camera
# Reboot
```

### Step 4: Install Python Packages
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Uncomment Optional Features
Edit `requirements.txt` or `requirements-raspi.txt` and uncomment what you need:

**For LLM chatbot:**
```python
openai==1.10.0        # If using OpenAI
# OR
anthropic==0.16.1     # If using Claude
```

**For email alerts:**
```python
yagmail==0.15.293
```

**For SMS alerts:**
```python
twilio==8.13.0
```

Then reinstall:
```bash
pip install -r requirements.txt
```

---

## What's Different Between Files?

### requirements.txt (Mac-friendly)
- ✅ Core packages only
- ✅ No hardware-specific packages
- ✅ Works on Mac, Windows, Linux
- ✅ Perfect for development/testing
- ❌ Won't access real sensors

### requirements-raspi.txt (Raspberry Pi full)
- ✅ All hardware packages
- ✅ Sensor interfaces (I2C, GPIO)
- ✅ Camera support
- ✅ ML inference
- ❌ Some packages only work on Pi
- ❌ Won't install on Mac

---

## Current Status After Fix

Run these commands in your Mac terminal:

```bash
cd AquaponicsAISystem
source venv/bin/activate

# Download and replace requirements.txt with the new version
# Then:
pip install -r requirements.txt
```

You should see:
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 websockets-12.0 
jinja2-3.1.3 numpy-1.26.3 pillow-10.2.0 requests-2.31.0 
apscheduler-3.10.4 python-dotenv-1.0.1
```

Then test:
```bash
python test_system.py
```

Expected: **All 8 tests should pass!** ✅

---

## Troubleshooting

### Still Getting atlas-i2c Error?
Make sure you downloaded the **new** requirements.txt file. The old one has the wrong version.

### Other Package Errors on Mac?
That's normal! Packages like `gpiozero`, `picamera2`, `atlas-i2c` are **Raspberry Pi only**. 

The updated requirements.txt has them commented out, so they won't cause errors.

### Want to Use OpenAI or Claude?
Uncomment the line in requirements.txt:
```python
# openai==1.10.0  # Remove the # to install
```

Then:
```bash
pip install openai
# OR
pip install anthropic
```

And add your API key to `.env`:
```bash
LLM_BACKEND=openai
LLM_API_KEY=sk-your-key-here
```

---

## Package Purpose Guide

| Package | Why You Need It | Required? |
|---------|----------------|-----------|
| fastapi | Web framework | ✅ Yes |
| uvicorn | ASGI server | ✅ Yes |
| websockets | Real-time updates | ✅ Yes |
| jinja2 | HTML templates | ✅ Yes |
| numpy | Data arrays | ✅ Yes |
| pillow | Image handling | ✅ Yes |
| requests | HTTP requests | ✅ Yes |
| apscheduler | Task scheduling | ✅ Yes |
| python-dotenv | .env file support | ✅ Yes |
| atlas-i2c | pH/EC/DO sensors | ❌ Pi only |
| gpiozero | GPIO control | ❌ Pi only |
| picamera2 | Camera control | ❌ Pi only |
| opencv-python | Image processing | ⚠️ Optional |
| tflite-runtime | ML inference | ⚠️ Optional |
| openai | OpenAI API | ⚠️ Optional |
| anthropic | Claude API | ⚠️ Optional |
| yagmail | Email alerts | ⚠️ Optional |
| twilio | SMS alerts | ⚠️ Optional |

---

## Next Steps

1. ✅ Download updated requirements.txt
2. ✅ Install with: `pip install -r requirements.txt`
3. ✅ Test with: `python test_system.py`
4. ✅ Run with: `python main.py`
5. ✅ Open: http://localhost:8000

Everything should work now! 🎉

When you deploy to Raspberry Pi later, use `requirements-raspi.txt` instead.

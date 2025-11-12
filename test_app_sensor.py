import sys
sys.path.insert(0, '/home/pi/AquaponicAISystem/src')

from hydroponics.sensors.interfaces import temperature_sensors

# Initialize
temperature_sensors.initialize()

# Check if mock mode
print(f"Mock mode: {temperature_sensors.mock_mode}")
print(f"Sensors found: {temperature_sensors.sensors}")

# Try to read
temps = temperature_sensors.read_all()
print(f"Temperature readings: {temps}")

#!/usr/bin/env python3
import os
import glob
import time

# Enable 1-Wire
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Find sensor
base_dir = '/sys/bus/w1/devices/'
try:
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    print(f"✓ Found temperature sensor: {device_folder.split('/')[-1]}")
except IndexError:
    print("✗ No temperature sensor found!")
    print("  Check wiring and run: ls /sys/bus/w1/devices/")
    exit(1)

def read_temp():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    
    # Check for valid reading
    if lines[0].strip()[-3:] == 'YES':
        temp_pos = lines[1].find('t=')
        if temp_pos != -1:
            temp_c = float(lines[1][temp_pos+2:]) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f
    return None, None

# Main loop
print("\n" + "="*50)
print("TEMPERATURE SENSOR TEST")
print("="*50)
print("Press Ctrl+C to stop\n")

try:
    while True:
        temp_c, temp_f = read_temp()
        if temp_c:
            print(f"Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
        else:
            print("Error reading sensor - check connections")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n\nTest complete! ✓")

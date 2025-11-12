"""
Sensor interface modules for Atlas Scientific and other sensors
"""

import time
import logging
from typing import Optional, Dict
import glob

logger = logging.getLogger(__name__)

try:
    from atlas_i2c import AtlasI2C
except ImportError:
    logger.warning("atlas_i2c not installed, using mock sensors")
    AtlasI2C = None

try:
    from gpiozero import DigitalOutputDevice, DistanceSensor
except ImportError:
    logger.warning("gpiozero not installed, using mock sensors")
    DigitalOutputDevice = None
    DistanceSensor = None


class AtlasSensors:
    """Interface for Atlas Scientific sensors (pH, EC, DO)"""
    
    def __init__(self):
        self.ph_sensor = None
        self.ec_sensor = None
        self.do_sensor = None
        self.initialized = False
        self.mock_mode = AtlasI2C is None
    
    def initialize(self):
        """Initialize all Atlas sensors"""
        if self.mock_mode:
            logger.warning("Running in MOCK MODE - no actual sensors connected")
            self.initialized = True
            return
        
        try:
            # Initialize pH sensor (address 0x63)
            self.ph_sensor = AtlasI2C(address=0x63)
            self.ph_sensor.write("C,0")  # Disable continuous mode
            logger.info("pH sensor initialized at 0x63")
            
            # Initialize EC sensor (address 0x64)
            self.ec_sensor = AtlasI2C(address=0x64)
            self.ec_sensor.write("C,0")
            logger.info("EC sensor initialized at 0x64")
            
            # Initialize DO sensor (address 0x61)
            self.do_sensor = AtlasI2C(address=0x61)
            self.do_sensor.write("C,0")
            logger.info("DO sensor initialized at 0x61")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Atlas sensors: {e}")
            self.mock_mode = True
    
    def read_ph(self) -> Optional[float]:
        """Read pH value"""
        if self.mock_mode:
            return 6.8 + (time.time() % 10) * 0.05  # Mock data
        
        try:
            self.ph_sensor.write("R")
            time.sleep(1)
            response = self.ph_sensor.read()
            if response.status_code == 1:
                return float(response.data)
        except Exception as e:
            logger.error(f"Error reading pH: {e}")
        return None
    
    def read_ec(self) -> Optional[float]:
        """Read EC/TDS value (in mS/cm)"""
        if self.mock_mode:
            return 1.2 + (time.time() % 8) * 0.05  # Mock data
        
        try:
            self.ec_sensor.write("R")
            time.sleep(1)
            response = self.ec_sensor.read()
            if response.status_code == 1:
                # Response is in ÂµS/cm, convert to mS/cm
                return float(response.data.split(',')[0]) / 1000
        except Exception as e:
            logger.error(f"Error reading EC: {e}")
        return None
    
    def read_do(self) -> Optional[float]:
        """Read dissolved oxygen (in mg/L)"""
        if self.mock_mode:
            return 7.5 + (time.time() % 6) * 0.2  # Mock data
        
        try:
            self.do_sensor.write("R")
            time.sleep(1)
            response = self.do_sensor.read()
            if response.status_code == 1:
                return float(response.data)
        except Exception as e:
            logger.error(f"Error reading DO: {e}")
        return None
    
    def set_temperature_compensation(self, temp_c: float):
        """Set temperature compensation for all sensors"""
        if self.mock_mode:
            return
        
        try:
            self.ph_sensor.write(f"T,{temp_c}")
            self.ec_sensor.write(f"T,{temp_c}")
            self.do_sensor.write(f"T,{temp_c}")
        except Exception as e:
            logger.error(f"Error setting temperature compensation: {e}")
    
    def calibrate_ph(self, point: str, value: float):
        """
        Calibrate pH sensor
        point: 'mid' (pH 7), 'low' (pH 4), 'high' (pH 10)
        """
        if self.mock_mode:
            logger.info(f"Mock calibration: pH {point} = {value}")
            return
        
        try:
            self.ph_sensor.write(f"Cal,{point},{value}")
            time.sleep(2)
            logger.info(f"pH calibration {point} = {value} complete")
        except Exception as e:
            logger.error(f"Error calibrating pH: {e}")
    
    def calibrate_ec(self, point: str, value: int):
        """
        Calibrate EC sensor
        point: 'dry', 'low', 'high'
        value: in ÂµS/cm (e.g., 1413 for 1.413 mS/cm)
        """
        if self.mock_mode:
            logger.info(f"Mock calibration: EC {point} = {value}")
            return
        
        try:
            if point == 'dry':
                self.ec_sensor.write("Cal,dry")
            else:
                self.ec_sensor.write(f"Cal,{point},{value}")
            time.sleep(2)
            logger.info(f"EC calibration {point} complete")
        except Exception as e:
            logger.error(f"Error calibrating EC: {e}")
    
    def calibrate_do(self, point: str = 'atm'):
        """
        Calibrate DO sensor
        point: 'atm' (atmospheric) or 'zero'
        """
        if self.mock_mode:
            logger.info(f"Mock calibration: DO {point}")
            return
        
        try:
            if point == 'zero':
                self.do_sensor.write("Cal,0")
            else:
                self.do_sensor.write("Cal")
            time.sleep(2)
            logger.info(f"DO calibration {point} complete")
        except Exception as e:
            logger.error(f"Error calibrating DO: {e}")


class TemperatureSensors:
    """Interface for DS18B20 temperature sensors"""
    
    def __init__(self):
        self.sensors = {}
        self.mock_mode = False
        self.base_dir = '/sys/bus/w1/devices/'
    
    def initialize(self):
        """Find and initialize all DS18B20 sensors"""
        try:
            device_folders = glob.glob(self.base_dir + '28-*')
            
            if not device_folders:
                logger.warning("No DS18B20 sensors found, using mock mode")
                self.mock_mode = True
                return
            
            # Name sensors based on expected positions
            sensor_names = ['reservoir', 'fish_tank']
            for i, folder in enumerate(device_folders):
                sensor_name = sensor_names[i] if i < len(sensor_names) else f"sensor_{i}"
                self.sensors[sensor_name] = folder + '/w1_slave'
                logger.info(f"Found temperature sensor: {sensor_name}")
            
        except Exception as e:
            logger.error(f"Error initializing temperature sensors: {e}")
            self.mock_mode = True
    
    def read_sensor(self, device_file: str) -> Optional[float]:
        """Read a single DS18B20 sensor"""
        try:
            with open(device_file, 'r') as f:
                lines = f.readlines()
            
            if lines[0].strip()[-3:] != 'YES':
                return None
            
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
        except Exception as e:
            logger.error(f"Error reading temperature sensor: {e}")
        return None
    
    def read_all(self) -> Dict[str, Optional[float]]:
        """Read all temperature sensors"""
        if self.mock_mode:
            return {
                'reservoir': 20.0 + (time.time() % 5) * 0.5,
                'fish_tank': 14.0 + (time.time() % 4) * 0.3
            }
        
        readings = {}
        for name, device_file in self.sensors.items():
            readings[name] = self.read_sensor(device_file)
        return readings


class WaterLevelSensor:
    """Interface for HC-SR04 ultrasonic water level sensor"""
    
    def __init__(self, echo_pin: int = 27, trigger_pin: int = 17):
        self.sensor = None
        self.mock_mode = DistanceSensor is None
        self.echo_pin = echo_pin
        self.trigger_pin = trigger_pin
        self.tank_height_cm = 60  # Adjust for your tank
    
    def initialize(self):
        """Initialize ultrasonic sensor"""
        if self.mock_mode:
            logger.warning("Running water level in MOCK MODE")
            return
        
        try:
            self.sensor = DistanceSensor(
                echo=self.echo_pin,
                trigger=self.trigger_pin,
                max_distance=4
            )
            logger.info("Water level sensor initialized")
        except Exception as e:
            logger.error(f"Error initializing water level sensor: {e}")
            self.mock_mode = True
    
    def read_level(self) -> Dict[str, float]:
        """Read water level"""
        if self.mock_mode:
            # Mock data
            distance = 15.0 + (time.time() % 10)
            water_level = self.tank_height_cm - distance
            return {
                'distance_cm': distance,
                'water_level_cm': water_level,
                'water_level_percent': (water_level / self.tank_height_cm) * 100
            }
        
        try:
            distance_cm = self.sensor.distance * 100
            water_level_cm = self.tank_height_cm - distance_cm
            water_level_percent = (water_level_cm / self.tank_height_cm) * 100
            
            return {
                'distance_cm': distance_cm,
                'water_level_cm': water_level_cm,
                'water_level_percent': max(0, min(100, water_level_percent))
            }
        except Exception as e:
            logger.error(f"Error reading water level: {e}")
            return {'distance_cm': None, 'water_level_cm': None, 'water_level_percent': None}


class RelayControl:
    """Control for Adafruit 4-outlet relay module"""
    
    def __init__(self):
        self.relays = {}
        self.mock_mode = DigitalOutputDevice is None
        
        # GPIO pins for relay control (adjust based on wiring)
        self.relay_pins = {
            'pump': 23,      # Main water pump
            'lights': 24,    # Grow lights
            'heater': 25,    # Water heater
            'backup_aerator': 22  # Emergency air pump
        }
    
    def initialize(self):
        """Initialize relay control"""
        if self.mock_mode:
            logger.warning("Running relay control in MOCK MODE")
            return
        
        try:
            for name, pin in self.relay_pins.items():
                self.relays[name] = DigitalOutputDevice(pin)
                self.relays[name].off()  # Ensure off on startup
                logger.info(f"Relay '{name}' initialized on GPIO {pin}")
        except Exception as e:
            logger.error(f"Error initializing relays: {e}")
            self.mock_mode = True
    
    def set_relay(self, name: str, state: bool):
        """Set relay state (True=ON, False=OFF)"""
        if self.mock_mode:
            logger.info(f"Mock relay: {name} = {'ON' if state else 'OFF'}")
            return
        
        try:
            if name not in self.relays:
                raise ValueError(f"Unknown relay: {name}")
            
            if state:
                self.relays[name].on()
            else:
                self.relays[name].off()
            
            logger.info(f"Relay {name} set to {'ON' if state else 'OFF'}")
        except Exception as e:
            logger.error(f"Error controlling relay {name}: {e}")
    
    def get_state(self, name: str) -> bool:
        """Get current relay state"""
        if self.mock_mode:
            return False
        
        try:
            return self.relays[name].is_active
        except Exception as e:
            logger.error(f"Error getting relay state: {e}")
            return False
    
    def cleanup(self):
        """Turn off all relays on shutdown"""
        if self.mock_mode:
            return
        
        for name, relay in self.relays.items():
            relay.off()
        logger.info("All relays turned off")


# Global instances
atlas_sensors = AtlasSensors()
temperature_sensors = TemperatureSensors()
water_level = WaterLevelSensor()
relay_control = RelayControl()

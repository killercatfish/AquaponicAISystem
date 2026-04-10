"""
Sensor interface modules for Atlas Scientific and other sensors
"""

import time
import logging
import subprocess
from typing import Optional, Dict
import glob

logger = logging.getLogger(__name__)

try:
    from atlas_i2c.atlas_i2c import AtlasI2C
except ImportError:
    logger.warning("atlas_i2c not installed, using mock sensors")
    AtlasI2C = None

try:
    from gpiozero import DistanceSensor
except ImportError:
    logger.warning("gpiozero not installed, using mock water level sensor")
    DistanceSensor = None


class AtlasSensors:
    """Interface for Atlas Scientific sensors (pH, EC, DO)"""
    
    def __init__(self):
        self.ph_sensor = None
        self.ec_sensor = None
        self.do_sensor = None
        self.initialized = False
        self.ph_mock = AtlasI2C is None
        self.ec_mock = AtlasI2C is None
        self.do_mock = AtlasI2C is None

    def initialize(self):
        """Initialize all Atlas sensors independently"""
        if AtlasI2C is None:
            logger.warning("Running in MOCK MODE - no actual sensors connected")
            self.initialized = True
            return

        # Initialize pH sensor (address 0x63)
        try:
            self.ph_sensor = AtlasI2C(address=0x63)
            self.ph_sensor.write("C,0")  # Disable continuous mode
            self.ph_mock = False
            logger.info("pH sensor initialized at 0x63")
        except Exception as e:
            logger.error(f"Error initializing pH sensor: {e}")
            self.ph_mock = True

        # Initialize EC sensor (address 0x64)
        try:
            self.ec_sensor = AtlasI2C(address=0x64)
            self.ec_sensor.write("C,0")
            self.ec_mock = False
            logger.info("EC sensor initialized at 0x64")
        except Exception as e:
            logger.error(f"Error initializing EC sensor: {e}")
            self.ec_mock = True

        # Initialize DO sensor (address 0x61)
        try:
            self.do_sensor = AtlasI2C(address=0x61)
            self.do_sensor.write("C,0")
            self.do_mock = False
            logger.info("DO sensor initialized at 0x61")
        except Exception as e:
            logger.error(f"Error initializing DO sensor: {e}")
            self.do_mock = True

        self.initialized = True
    
    def read_ph(self) -> Optional[float]:
        """Read pH value"""
        if self.ph_mock:
            return 6.8 + (time.time() % 10) * 0.05  # Mock data
        
        try:
            self.ph_sensor.write("R")
            time.sleep(1)
            response = self.ph_sensor.read('R')
            if response.status_code == 1:
                return float(response.data.decode())
        except Exception as e:
            logger.error(f"Error reading pH: {e}")
        return None
    
    def read_ec(self) -> Optional[float]:
        """Read EC/TDS value (in mS/cm)"""
        if self.ec_mock:
            return 1.2 + (time.time() % 8) * 0.05  # Mock data
        
        try:
            self.ec_sensor.write("R")
            time.sleep(1)
            response = self.ec_sensor.read('R')
            if response.status_code == 1:
                # Response is in µS/cm, convert to mS/cm
                return float(response.data.decode().split(',')[0]) / 1000
        except Exception as e:
            logger.error(f"Error reading EC: {e}")
        return None
    
    def read_do(self) -> Optional[float]:
        """Read dissolved oxygen (in mg/L)"""
        if self.do_mock:
            return 7.5 + (time.time() % 6) * 0.2  # Mock data
        
        try:
            self.do_sensor.write("R")
            time.sleep(1)
            response = self.do_sensor.read('R')
            if response.status_code == 1:
                return float(response.data.decode())
        except Exception as e:
            logger.error(f"Error reading DO: {e}")
        return None
    
    def set_temperature_compensation(self, temp_c: float):
        """Set temperature compensation for all sensors"""
        if not self.ph_mock:
            try:
                self.ph_sensor.write(f"T,{temp_c}")
            except Exception as e:
                logger.error(f"Error setting pH temperature compensation: {e}")
        if not self.ec_mock:
            try:
                self.ec_sensor.write(f"T,{temp_c}")
            except Exception as e:
                logger.error(f"Error setting EC temperature compensation: {e}")
        if not self.do_mock:
            try:
                self.do_sensor.write(f"T,{temp_c}")
            except Exception as e:
                logger.error(f"Error setting DO temperature compensation: {e}")
    
    def calibrate_ph(self, point: str, value: float):
        """
        Calibrate pH sensor
        point: 'mid' (pH 7), 'low' (pH 4), 'high' (pH 10)
        """
        if self.ph_mock:
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
        if self.ec_mock:
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
        if self.do_mock:
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
                self.sensors[sensor_name] = folder + '/temperature'
                logger.info(f"Found temperature sensor: {sensor_name}")
            
        except Exception as e:
            logger.error(f"Error initializing temperature sensors: {e}")
            self.mock_mode = True
    
    def read_sensor(self, device_file: str) -> Optional[float]:
        """Read a single DS18B20 sensor from sysfs temperature file"""
        try:
            with open(device_file, 'r') as f:
                raw = f.read().strip()
            temp_c = int(raw) / 1000.0
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
    """Control for Adafruit 4-outlet relay module via pinctrl GPIO"""

    def __init__(self):
        self.relay_states = {}
        self.mock_mode = False

        # GPIO pins for relay control
        self.relay_pins = {
            'heater': 23,         # Water heater (GPIO23 → relay signal)
            'pump': 24,           # Main water pump
            'lights': 25,         # Grow lights
            'backup_aerator': 22  # Emergency air pump
        }

    def _gpio_set(self, pin: int, high: bool):
        """Set a GPIO pin high or low using pinctrl command"""
        level = 'dh' if high else 'dl'
        subprocess.run(
            ['pinctrl', 'set', str(pin), 'op', level],
            check=True,
            capture_output=True,
            timeout=5
        )

    def initialize(self):
        """Initialize relay control — set all pins as outputs, driven low"""
        try:
            for name, pin in self.relay_pins.items():
                self._gpio_set(pin, False)
                self.relay_states[name] = False
                logger.info(f"Relay '{name}' initialized on GPIO {pin}")
        except FileNotFoundError:
            logger.warning("pinctrl not found — running relay control in MOCK MODE")
            self.mock_mode = True
        except Exception as e:
            logger.error(f"Error initializing relays: {e}")
            self.mock_mode = True

    def set_relay(self, name: str, state: bool):
        """Set relay state (True=ON, False=OFF)"""
        if self.mock_mode:
            logger.info(f"Mock relay: {name} = {'ON' if state else 'OFF'}")
            return

        if name not in self.relay_pins:
            logger.error(f"Unknown relay: {name}")
            return

        try:
            self._gpio_set(self.relay_pins[name], state)
            self.relay_states[name] = state
            logger.info(f"Relay {name} set to {'ON' if state else 'OFF'}")
        except Exception as e:
            logger.error(f"Error controlling relay {name}: {e}")

    def get_state(self, name: str) -> bool:
        """Get current relay state"""
        if self.mock_mode:
            return False
        return self.relay_states.get(name, False)

    def cleanup(self):
        """Turn off all relays on shutdown"""
        if self.mock_mode:
            return
        for name, pin in self.relay_pins.items():
            try:
                self._gpio_set(pin, False)
            except Exception:
                pass
        logger.info("All relays turned off")


# Global instances
atlas_sensors = AtlasSensors()
temperature_sensors = TemperatureSensors()
water_level = WaterLevelSensor()
relay_control = RelayControl()

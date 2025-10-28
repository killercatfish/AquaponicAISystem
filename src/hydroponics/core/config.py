"""
Configuration file for STEM DREAM Aquaponics Control System
Edit this file to customize your system settings
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """System configuration"""
    
    # === DATABASE SETTINGS ===
    database_path: str = "data/databases/hydroponics.db"
    use_influxdb: bool = False
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = ""
    influxdb_org: str = "aquaponics"
    influxdb_bucket: str = "sensors"
    
    # === SENSOR SETTINGS ===
    # How often to read sensors (minutes)
    sensor_read_interval: int = 5
    
    # Temperature compensation enabled
    temp_compensation: bool = True
    
    # === WATER QUALITY THRESHOLDS ===
    # Adjust these based on your system type
    
    # pH thresholds
    ph_min: float = 6.0
    ph_max: float = 7.0
    ph_critical_low: float = 5.0
    ph_critical_high: float = 8.0
    
    # EC thresholds (mS/cm)
    ec_min: float = 1.0
    ec_max: float = 1.8
    ec_critical_low: float = 0.5
    ec_critical_high: float = 3.0
    
    # Dissolved Oxygen thresholds (mg/L)
    do_normal: float = 7.0
    do_critical: float = 5.0
    
    # Temperature thresholds (Â°C)
    temp_min: float = 18.0
    temp_max: float = 22.0
    temp_critical_low: float = 10.0
    temp_critical_high: float = 28.0
    
    # Water level threshold (%)
    water_level_critical: float = 20.0
    
    # === PLANT ANALYSIS SETTINGS ===
    # How often to analyze plant health (hours)
    plant_analysis_interval: int = 1
    
    # ML model path
    ml_model_path: str = "models/plant_disease.tflite"
    
    # Confidence threshold for detections
    detection_confidence_threshold: float = 0.15
    
    # === AUTOMATION SETTINGS ===
    # Enable automated control
    auto_control_enabled: bool = True
    
    # Pump control
    pump_on_minutes: int = 15
    pump_off_minutes: int = 15
    
    # Light schedule (24h format)
    lights_on_hour: int = 6
    lights_off_hour: int = 22
    
    # === LLM SETTINGS ===
    # LLM backend: 'openai', 'anthropic', 'ollama', or 'mock'
    llm_backend: str = os.getenv('LLM_BACKEND', 'mock')
    
    # API keys (use environment variables for security)
    llm_api_key: str = os.getenv('LLM_API_KEY', '')
    
    # Ollama settings (for local LLM)
    ollama_url: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    ollama_model: str = 'llama3'
    
    # === EMAIL ALERT SETTINGS ===
    email_enabled: bool = False
    email_from: str = os.getenv('EMAIL_FROM', '')
    email_password: str = os.getenv('EMAIL_PASSWORD', '')
    email_to: str = os.getenv('EMAIL_TO', '')
    
    # === SMS ALERT SETTINGS (Twilio) ===
    sms_enabled: bool = False
    twilio_account_sid: str = os.getenv('TWILIO_ACCOUNT_SID', '')
    twilio_auth_token: str = os.getenv('TWILIO_AUTH_TOKEN', '')
    twilio_from: str = os.getenv('TWILIO_FROM', '')
    sms_to: str = os.getenv('SMS_TO', '')
    
    # === WEB INTERFACE SETTINGS ===
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    
    # === SYSTEM SETTINGS ===
    system_name: str = "STEM DREAM Aquaponics"
    location: str = "Basement Lab"
    
    # System type: 'hydroponics' or 'aquaponics'
    system_type: str = 'hydroponics'
    
    # Fish species (if aquaponics)
    fish_species: str = 'rainbow_trout'
    
    # Plant type
    plant_type: str = 'lettuce'
    
    # === DATA RETENTION ===
    # Days to keep sensor data
    data_retention_days: int = 90
    
    # === LOGGING ===
    log_level: str = 'INFO'
    log_file: str = 'data/logs/hydroponics.log' 
    
    # === HARDWARE PIN ASSIGNMENTS ===
    # Atlas Scientific I2C addresses
    i2c_ph_address: int = 0x63
    i2c_ec_address: int = 0x64
    i2c_do_address: int = 0x61
    
    # Temperature sensor (DS18B20) GPIO pin
    temp_sensor_pin: int = 4
    
    # Water level sensor (HC-SR04) pins
    water_level_trigger_pin: int = 17
    water_level_echo_pin: int = 27
    
    # Relay control GPIO pins
    relay_pump_pin: int = 23
    relay_lights_pin: int = 24
    relay_heater_pin: int = 25
    relay_backup_aerator_pin: int = 22
    
    # === CALIBRATION SETTINGS ===
    # Automatically save calibration
    auto_save_calibration: bool = True
    
    # Calibration reminder (days)
    calibration_reminder_days: int = 30


# Create global config instance
config = Config()


# === HELPER FUNCTIONS ===

def load_config_from_file(filepath: str = ".env"):
    """Load configuration from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv(filepath)
        
        # Reload config with environment variables
        global config
        config = Config()
        
        print(f"Configuration loaded from {filepath}")
    except Exception as e:
        print(f"Could not load config file: {e}")


def save_config_to_file(filepath: str = "config_backup.txt"):
    """Save current configuration to file"""
    try:
        import json
        
        config_dict = {
            key: value for key, value in config.__dict__.items()
            if not key.startswith('_')
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"Configuration saved to {filepath}")
    except Exception as e:
        print(f"Could not save config: {e}")


def print_config():
    """Print current configuration"""
    print("\n=== STEM DREAM Aquaponics Configuration ===\n")
    
    print(f"System Name: {config.system_name}")
    print(f"System Type: {config.system_type}")
    print(f"Location: {config.location}")
    
    print("\n--- Sensor Settings ---")
    print(f"Read Interval: {config.sensor_read_interval} minutes")
    
    print("\n--- pH Thresholds ---")
    print(f"Optimal: {config.ph_min} - {config.ph_max}")
    print(f"Critical: < {config.ph_critical_low} or > {config.ph_critical_high}")
    
    print("\n--- EC Thresholds ---")
    print(f"Optimal: {config.ec_min} - {config.ec_max} mS/cm")
    
    print("\n--- DO Thresholds ---")
    print(f"Normal: {config.do_normal} mg/L")
    print(f"Critical: < {config.do_critical} mg/L")
    
    print("\n--- Temperature Thresholds ---")
    print(f"Optimal: {config.temp_min} - {config.temp_max}Â°C")
    
    print("\n--- LLM Settings ---")
    print(f"Backend: {config.llm_backend}")
    if config.llm_backend == 'ollama':
        print(f"Ollama URL: {config.ollama_url}")
    
    print("\n--- Alert Settings ---")
    print(f"Email Alerts: {'Enabled' if config.email_enabled else 'Disabled'}")
    print(f"SMS Alerts: {'Enabled' if config.sms_enabled else 'Disabled'}")
    
    print("\n--- Automation ---")
    print(f"Auto Control: {'Enabled' if config.auto_control_enabled else 'Disabled'}")
    print(f"Lights Schedule: {config.lights_on_hour}:00 - {config.lights_off_hour}:00")
    
    print("\n==========================================\n")


if __name__ == "__main__":
    print_config()

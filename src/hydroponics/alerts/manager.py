"""
Alert manager for monitoring thresholds and sending notifications
Supports email, SMS (via Twilio), and push notifications
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import yagmail
except ImportError:
    logger.warning("yagmail not installed, email alerts unavailable")
    yagmail = None

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    logger.warning("twilio not installed, SMS alerts unavailable")
    TwilioClient = None


class AlertManager:
    """Manage system alerts and notifications"""
    
    def __init__(self, config):
        self.config = config
        self.alert_history = {}  # Track recent alerts to avoid spam
        self.cooldown_minutes = 30  # Minimum time between same alerts
        
        # Initialize notification services
        self.email_client = None
        self.sms_client = None
        
        if config.email_enabled and yagmail:
            try:
                self.email_client = yagmail.SMTP(
                    config.email_from,
                    config.email_password
                )
                logger.info("Email alerts enabled")
            except Exception as e:
                logger.error(f"Error initializing email: {e}")
        
        if config.sms_enabled and TwilioClient:
            try:
                self.sms_client = TwilioClient(
                    config.twilio_account_sid,
                    config.twilio_auth_token
                )
                logger.info("SMS alerts enabled")
            except Exception as e:
                logger.error(f"Error initializing SMS: {e}")
        
        # Define alert thresholds
        self.thresholds = {
            'ph': {
                'critical_low': 5.0,
                'warning_low': 5.5,
                'warning_high': 7.5,
                'critical_high': 8.0,
                'optimal_min': 6.0,
                'optimal_max': 7.0
            },
            'ec': {
                'critical_low': 0.5,
                'warning_low': 0.8,
                'warning_high': 2.5,
                'critical_high': 3.0,
                'optimal_min': 1.0,
                'optimal_max': 1.8
            },
            'do': {
                'critical_low': 4.0,
                'warning_low': 5.0,
                'warning_high': 12.0,
                'critical_high': 15.0,
                'optimal_min': 6.0,
                'optimal_max': 9.0
            },
            'temp_reservoir': {
                'critical_low': 10.0,
                'warning_low': 16.0,
                'warning_high': 24.0,
                'critical_high': 28.0,
                'optimal_min': 18.0,
                'optimal_max': 22.0
            },
            'temp_fish_tank': {
                'critical_low': 8.0,
                'warning_low': 10.0,
                'warning_high': 18.0,
                'critical_high': 20.0,
                'optimal_min': 12.0,
                'optimal_max': 15.0
            },
            'water_level_percent': {
                'critical_low': 20.0,
                'warning_low': 30.0,
                'optimal_min': 50.0,
                'optimal_max': 90.0
            }
        }
    
    def check_thresholds(self, sensors: Dict) -> List[Dict]:
        """
        Check sensor values against thresholds
        Returns list of alert dictionaries
        """
        alerts = []
        
        for sensor_name, value in sensors.items():
            if value is None:
                continue
            
            if sensor_name not in self.thresholds:
                continue
            
            thresholds = self.thresholds[sensor_name]
            alert = self._check_sensor_threshold(sensor_name, value, thresholds)
            
            if alert:
                # Check if we've already sent this alert recently
                if not self._is_in_cooldown(alert):
                    alerts.append(alert)
                    self._record_alert(alert)
                    
                    # Send notifications for critical alerts
                    if alert['level'] == 'critical':
                        self._send_notifications(alert)
        
        return alerts
    
    def _check_sensor_threshold(
        self,
        sensor_name: str,
        value: float,
        thresholds: Dict
    ) -> Optional[Dict]:
        """Check a single sensor against thresholds"""
        
        # Critical low
        if 'critical_low' in thresholds and value < thresholds['critical_low']:
            return {
                'timestamp': datetime.now().isoformat(),
                'level': 'critical',
                'sensor': sensor_name,
                'value': value,
                'threshold': thresholds['critical_low'],
                'message': f"CRITICAL: {sensor_name} is dangerously low ({value:.2f})"
            }
        
        # Critical high
        if 'critical_high' in thresholds and value > thresholds['critical_high']:
            return {
                'timestamp': datetime.now().isoformat(),
                'level': 'critical',
                'sensor': sensor_name,
                'value': value,
                'threshold': thresholds['critical_high'],
                'message': f"CRITICAL: {sensor_name} is dangerously high ({value:.2f})"
            }
        
        # Warning low
        if 'warning_low' in thresholds and value < thresholds['warning_low']:
            return {
                'timestamp': datetime.now().isoformat(),
                'level': 'warning',
                'sensor': sensor_name,
                'value': value,
                'threshold': thresholds['warning_low'],
                'message': f"WARNING: {sensor_name} is low ({value:.2f})"
            }
        
        # Warning high
        if 'warning_high' in thresholds and value > thresholds['warning_high']:
            return {
                'timestamp': datetime.now().isoformat(),
                'level': 'warning',
                'sensor': sensor_name,
                'value': value,
                'threshold': thresholds['warning_high'],
                'message': f"WARNING: {sensor_name} is high ({value:.2f})"
            }
        
        return None
    
    def _is_in_cooldown(self, alert: Dict) -> bool:
        """Check if similar alert was sent recently"""
        alert_key = f"{alert['sensor']}_{alert['level']}"
        
        if alert_key in self.alert_history:
            last_sent = self.alert_history[alert_key]
            time_since = datetime.now() - last_sent
            
            if time_since < timedelta(minutes=self.cooldown_minutes):
                return True
        
        return False
    
    def _record_alert(self, alert: Dict):
        """Record alert in history"""
        alert_key = f"{alert['sensor']}_{alert['level']}"
        self.alert_history[alert_key] = datetime.now()
    
    def _send_notifications(self, alert: Dict):
        """Send notifications via enabled channels"""
        # Email notification
        if self.email_client and self.config.email_to:
            try:
                subject = f"AQUAPONICS ALERT: {alert['message']}"
                body = self._format_alert_email(alert)
                self.email_client.send(
                    to=self.config.email_to,
                    subject=subject,
                    contents=body
                )
                logger.info(f"Email alert sent: {alert['message']}")
            except Exception as e:
                logger.error(f"Error sending email alert: {e}")
        
        # SMS notification
        if self.sms_client and self.config.sms_to:
            try:
                message = f"AQUAPONICS ALERT: {alert['message']}"
                self.sms_client.messages.create(
                    body=message,
                    from_=self.config.twilio_from,
                    to=self.config.sms_to
                )
                logger.info(f"SMS alert sent: {alert['message']}")
            except Exception as e:
                logger.error(f"Error sending SMS alert: {e}")
    
    def _format_alert_email(self, alert: Dict) -> str:
        """Format alert as HTML email"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: {'#d32f2f' if alert['level'] == 'critical' else '#ff9800'};">
                {alert['level'].upper()} ALERT
            </h2>
            <p><strong>Sensor:</strong> {alert['sensor']}</p>
            <p><strong>Current Value:</strong> {alert['value']:.2f}</p>
            <p><strong>Threshold:</strong> {alert['threshold']:.2f}</p>
            <p><strong>Time:</strong> {alert['timestamp']}</p>
            <h3>Recommended Actions:</h3>
            <ul>
                {self._get_recommendations_html(alert)}
            </ul>
            <p><em>This is an automated alert from your STEM DREAM Aquaponics system.</em></p>
        </body>
        </html>
        """
        return html
    
    def _get_recommendations_html(self, alert: Dict) -> str:
        """Get HTML formatted recommendations for alert"""
        sensor = alert['sensor']
        level = alert['level']
        value = alert['value']
        
        recommendations = []
        
        if sensor == 'ph':
            if value < self.thresholds['ph']['optimal_min']:
                recommendations = [
                    "Add pH Up solution slowly (0.2 units at a time)",
                    "Wait 30 minutes and retest",
                    "Check if nutrient solution is old (replace if needed)",
                    "Verify calibration of pH sensor"
                ]
            else:
                recommendations = [
                    "Add pH Down solution slowly (0.2 units at a time)",
                    "Wait 30 minutes and retest",
                    "Check aeration (high pH can indicate CO2 depletion)",
                    "Verify calibration of pH sensor"
                ]
        
        elif sensor == 'do':
            if value < self.thresholds['do']['optimal_min']:
                recommendations = [
                    "IMMEDIATE: Increase aeration (add air stones)",
                    "Check water temperature (warmer = less DO)",
                    "Reduce feeding if fish present",
                    "Check for dead organisms in system",
                    "Verify air pump is working",
                    "If fish gasping at surface: 50% water change NOW"
                ]
        
        elif sensor == 'ec':
            if value < self.thresholds['ec']['optimal_min']:
                recommendations = [
                    "Add nutrient solution",
                    "Check plants for deficiency symptoms",
                    "Verify EC sensor calibration"
                ]
            else:
                recommendations = [
                    "Add fresh water to dilute",
                    "Check for salt buildup",
                    "Flush system if EC very high",
                    "Reduce nutrient dosing"
                ]
        
        elif 'temp' in sensor:
            if value < self.thresholds[sensor]['optimal_min']:
                recommendations = [
                    "Turn on water heater",
                    "Check heater is functioning",
                    "Insulate reservoir/tanks",
                    "Check ambient temperature"
                ]
            else:
                recommendations = [
                    "Turn off heater",
                    "Increase ventilation/cooling",
                    "Add ice packs if emergency",
                    "Consider chiller for long-term solution"
                ]
        
        elif sensor == 'water_level_percent':
            recommendations = [
                "Check for leaks",
                "Refill reservoir",
                "Verify auto top-off system working",
                "Check pump for proper operation"
            ]
        
        html = ""
        for rec in recommendations:
            html += f"<li>{rec}</li>\n"
        
        return html if html else "<li>Monitor situation closely</li>"
    
    def test_notifications(self):
        """Send test notifications to verify configuration"""
        test_alert = {
            'timestamp': datetime.now().isoformat(),
            'level': 'info',
            'sensor': 'system',
            'value': 0,
            'threshold': 0,
            'message': 'This is a test alert from your aquaponics system'
        }
        
        logger.info("Sending test notifications...")
        self._send_notifications(test_alert)

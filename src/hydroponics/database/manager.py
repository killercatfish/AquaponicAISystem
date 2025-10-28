"""
Database manager for logging sensor data, events, and system history
Supports both SQLite (simple) and InfluxDB (time-series)
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

logger = logging.getLogger(__name__)

try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    logger.warning("influxdb_client not installed, using SQLite only")
    InfluxDBClient = None


class DatabaseManager:
    """
    Manage data logging and retrieval
    Uses SQLite for simplicity, optionally InfluxDB for production
    """
    
    def __init__(self, db_path: str = "hydroponics.db", use_influxdb: bool = False):
        self.db_path = db_path
        self.use_influxdb = use_influxdb and InfluxDBClient is not None
        self.conn = None
        self.influx_client = None
        self.influx_write_api = None
        
        # Initialize database
        self._init_sqlite()
        
        if self.use_influxdb:
            self._init_influxdb()
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Create sensor readings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ph REAL,
                    ec REAL,
                    do REAL,
                    temp_reservoir REAL,
                    temp_fish_tank REAL,
                    water_level_percent REAL
                )
            """)
            
            # Create plant analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plant_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    confidence REAL,
                    issues TEXT,
                    recommendations TEXT
                )
            """)
            
            # Create system actions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT,
                    action_value TEXT,
                    user TEXT DEFAULT 'system'
                )
            """)
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    acknowledged BOOLEAN DEFAULT 0
                )
            """)
            
            # Create conversations table (for LLM chat history)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT,
                    assistant_response TEXT
                )
            """)
            
            # Create indices for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
                ON sensor_readings(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON alerts(timestamp)
            """)
            
            self.conn.commit()
            logger.info(f"SQLite database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing SQLite: {e}")
    
    def _init_influxdb(self):
        """Initialize InfluxDB connection (optional)"""
        try:
            # Configure these in production
            self.influx_client = InfluxDBClient(
                url="http://localhost:8086",
                token="your-token",
                org="your-org"
            )
            self.influx_write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            logger.info("InfluxDB client initialized")
        except Exception as e:
            logger.error(f"Error initializing InfluxDB: {e}")
            self.use_influxdb = False
    
    def log_sensor_reading(self, sensors: Dict):
        """Log sensor readings"""
        try:
            # SQLite logging
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_readings 
                (ph, ec, do, temp_reservoir, temp_fish_tank, water_level_percent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sensors.get('ph'),
                sensors.get('ec'),
                sensors.get('do'),
                sensors.get('temp_reservoir'),
                sensors.get('temp_fish_tank'),
                sensors.get('water_level_percent')
            ))
            self.conn.commit()
            
            # InfluxDB logging (if enabled)
            if self.use_influxdb:
                point = Point("sensors")
                for key, value in sensors.items():
                    if value is not None:
                        point = point.field(key, value)
                self.influx_write_api.write(bucket="aquaponics", record=point)
            
        except Exception as e:
            logger.error(f"Error logging sensor reading: {e}")
    
    def log_plant_analysis(self, result: Dict):
        """Log plant health analysis"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO plant_analysis 
                (status, confidence, issues, recommendations)
                VALUES (?, ?, ?, ?)
            """, (
                result.get('status'),
                result.get('confidence'),
                json.dumps(result.get('issues', [])),
                json.dumps(result.get('recommendations', []))
            ))
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging plant analysis: {e}")
    
    def log_action(self, action_type: str, action_value: str, user: str = 'system'):
        """Log system action"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO system_actions (action_type, action_value, user)
                VALUES (?, ?, ?)
            """, (action_type, action_value, user))
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    def log_alert(self, level: str, message: str):
        """Log alert"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (level, message)
                VALUES (?, ?)
            """, (level, message))
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
    
    def log_conversation(self, user_message: str, assistant_response: str):
        """Log LLM conversation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (user_message, assistant_response)
                VALUES (?, ?)
            """, (user_message, assistant_response))
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
    
    def get_sensor_history(
        self,
        sensor: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Get historical sensor data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT timestamp, {sensor}
                FROM sensor_readings
                WHERE timestamp BETWEEN ? AND ?
                AND {sensor} IS NOT NULL
                ORDER BY timestamp
            """, (start_time, end_time))
            
            rows = cursor.fetchall()
            return [
                {
                    'timestamp': row['timestamp'],
                    'value': row[sensor]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting sensor history: {e}")
            return []
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT timestamp, level, message, acknowledged
                FROM alerts
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [
                {
                    'timestamp': row['timestamp'],
                    'level': row['level'],
                    'message': row['message'],
                    'acknowledged': bool(row['acknowledged'])
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def get_daily_summary(self, date: datetime = None) -> Dict:
        """Get daily summary statistics"""
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        try:
            cursor = self.conn.cursor()
            
            # Get sensor statistics
            cursor.execute("""
                SELECT 
                    AVG(ph) as avg_ph, MIN(ph) as min_ph, MAX(ph) as max_ph,
                    AVG(ec) as avg_ec, MIN(ec) as min_ec, MAX(ec) as max_ec,
                    AVG(do) as avg_do, MIN(do) as min_do, MAX(do) as max_do,
                    AVG(temp_reservoir) as avg_temp,
                    COUNT(*) as reading_count
                FROM sensor_readings
                WHERE timestamp BETWEEN ? AND ?
            """, (start_of_day, end_of_day))
            
            row = cursor.fetchone()
            
            # Get alert count
            cursor.execute("""
                SELECT COUNT(*) as alert_count
                FROM alerts
                WHERE timestamp BETWEEN ? AND ?
            """, (start_of_day, end_of_day))
            
            alert_count = cursor.fetchone()['alert_count']
            
            return {
                'date': date.strftime('%Y-%m-%d'),
                'sensors': {
                    'ph': {
                        'avg': row['avg_ph'],
                        'min': row['min_ph'],
                        'max': row['max_ph']
                    },
                    'ec': {
                        'avg': row['avg_ec'],
                        'min': row['min_ec'],
                        'max': row['max_ec']
                    },
                    'do': {
                        'avg': row['avg_do'],
                        'min': row['min_do'],
                        'max': row['max_do']
                    },
                    'temp': row['avg_temp']
                },
                'reading_count': row['reading_count'],
                'alert_count': alert_count
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Remove data older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cursor = self.conn.cursor()
            
            # Delete old sensor readings
            cursor.execute("""
                DELETE FROM sensor_readings
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            # Delete old acknowledged alerts
            cursor.execute("""
                DELETE FROM alerts
                WHERE timestamp < ? AND acknowledged = 1
            """, (cutoff_date,))
            
            self.conn.commit()
            logger.info(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def export_data(
        self,
        start_time: datetime,
        end_time: datetime,
        output_file: str
    ):
        """Export data to CSV"""
        try:
            import csv
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM sensor_readings
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """, (start_time, end_time))
            
            rows = cursor.fetchall()
            
            with open(output_file, 'w', newline='') as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(row))
            
            logger.info(f"Exported data to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
    
    def close(self):
        """Close database connections"""
        if self.conn:
            self.conn.close()
        if self.influx_client:
            self.influx_client.close()
        logger.info("Database connections closed")

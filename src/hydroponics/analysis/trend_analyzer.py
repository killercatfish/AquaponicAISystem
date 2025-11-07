"""
Trend Analysis - Layer 3 Intelligence
Predicts problems before they happen by analyzing historical data
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics


class TrendAnalyzer:
    """Analyzes trends and predicts future problems"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def analyze_parameter_trend(self, parameter: str, hours: int = 24) -> dict:
        """
        Analyze trend for a parameter over time
        
        Returns:
        {
            'trend': 'rising'|'falling'|'stable'|'volatile',
            'rate_of_change': float,  # per hour
            'prediction': {...},
            'concern_level': 'none'|'watch'|'warning'|'critical',
            'time_to_threshold': hours (or None),
            'recommendation': str
        }
        """
        # Get historical data
        data = self._get_historical_data(parameter, hours)
        
        if len(data) < 5:
            return {
                'trend': 'insufficient_data',
                'concern_level': 'none',
                'recommendation': 'Need more data points (collecting...)'
            }
        
        # Calculate trend
        values = [d['value'] for d in data]
        timestamps = [d['timestamp'] for d in data]
        
        # Linear regression to find trend
        trend_direction, rate_of_change = self._calculate_trend(values, timestamps)
        
        # Detect volatility
        volatility = self._calculate_volatility(values)
        
        # Predict future
        current_value = values[-1]
        prediction = self._predict_future(
            parameter,
            current_value,
            rate_of_change,
            hours=24
        )
        
        # Assess concern level
        concern = self._assess_concern(
            parameter,
            current_value,
            trend_direction,
            rate_of_change,
            prediction
        )
        
        return {
            'parameter': parameter,
            'current_value': current_value,
            'trend': trend_direction,
            'rate_of_change': rate_of_change,
            'volatility': volatility,
            'prediction': prediction,
            'concern_level': concern['level'],
            'time_to_threshold': concern.get('time_to_threshold'),
            'recommendation': concern['recommendation'],
            'historical_data': data[-10:]  # Last 10 points for visualization
        }
    
    def _get_historical_data(self, parameter: str, hours: int) -> List[dict]:
        """Query database for historical readings"""
        # This connects to your existing database
        since = datetime.now() - timedelta(hours=hours)
        
        try:
            query = """
                SELECT timestamp, value 
                FROM sensor_readings 
                WHERE parameter = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """
            
            # Map parameter names to your DB schema
            param_map = {
                'ph': 'ph',
                'temperature': 'temp_reservoir',
                'do': 'do',
                'ec': 'ec'
            }
            
            db_param = param_map.get(parameter, parameter)
            
            # Execute query (assuming you have SQLite)
            cursor = self.db.conn.execute(query, (db_param, since.isoformat()))
            rows = cursor.fetchall()
            
            return [
                {'timestamp': row[0], 'value': row[1]}
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error querying historical data: {e}")
            return []
    
    def _calculate_trend(self, values: List[float], timestamps: List[str]) -> tuple:
        """
        Calculate trend direction and rate of change
        Uses simple linear regression
        """
        if len(values) < 2:
            return 'stable', 0.0
        
        # Convert timestamps to hours from first reading
        first_time = datetime.fromisoformat(timestamps[0])
        hours = [
            (datetime.fromisoformat(t) - first_time).total_seconds() / 3600
            for t in timestamps
        ]
        
        # Simple linear regression
        n = len(values)
        sum_x = sum(hours)
        sum_y = sum(values)
        sum_xy = sum(h * v for h, v in zip(hours, values))
        sum_x2 = sum(h * h for h in hours)
        
        # Slope (rate of change per hour)
        if n * sum_x2 - sum_x * sum_x == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine direction
        if abs(slope) < 0.01:  # Very small change
            direction = 'stable'
        elif slope > 0.05:
            direction = 'rising'
        elif slope < -0.05:
            direction = 'falling'
        else:
            direction = 'stable'
        
        return direction, slope
    
    def _calculate_volatility(self, values: List[float]) -> str:
        """Calculate how volatile the readings are"""
        if len(values) < 3:
            return 'unknown'
        
        std_dev = statistics.stdev(values)
        mean = statistics.mean(values)
        
        # Coefficient of variation
        cv = (std_dev / mean) * 100 if mean != 0 else 0
        
        if cv < 2:
            return 'stable'
        elif cv < 5:
            return 'moderate'
        else:
            return 'volatile'
    
    def _predict_future(self, parameter: str, current: float, rate: float, hours: int = 24) -> dict:
        """Predict future value"""
        predicted_value = current + (rate * hours)
        
        return {
            'hours_ahead': hours,
            'predicted_value': round(predicted_value, 2),
            'confidence': 'high' if abs(rate) > 0.01 else 'low'
        }
    
    def _assess_concern(self, parameter: str, current: float, trend: str, rate: float, prediction: dict) -> dict:
        """
        Assess concern level and time to threshold
        """
        # Define thresholds for each parameter
        thresholds = {
            'ph': {
                'critical_low': 6.0,
                'warning_low': 6.5,
                'optimal_low': 6.8,
                'optimal_high': 7.5,
                'warning_high': 8.0,
                'critical_high': 8.5
            },
            'temperature': {
                'critical_low': 15,
                'warning_low': 18,
                'optimal_low': 20,
                'optimal_high': 24,
                'warning_high': 26,
                'critical_high': 28
            },
            'do': {
                'critical_low': 4,
                'warning_low': 6,
                'optimal_low': 7,
                'optimal_high': 10,
                'warning_high': 12,
                'critical_high': 15
            }
        }
        
        thresh = thresholds.get(parameter, {})
        if not thresh:
            return {'level': 'none', 'recommendation': 'No thresholds defined'}
        
        concern = {
            'level': 'none',
            'recommendation': 'Continue monitoring',
            'time_to_threshold': None
        }
        
        # Check if falling and approaching critical low
        if trend == 'falling' and rate < 0:
            hours_to_warning = None
            hours_to_critical = None
            
            if current > thresh['warning_low']:
                hours_to_warning = (current - thresh['warning_low']) / abs(rate)
            
            if current > thresh['critical_low']:
                hours_to_critical = (current - thresh['critical_low']) / abs(rate)
            
            # Critical: Will hit critical threshold in < 12 hours
            if hours_to_critical and hours_to_critical < 12:
                concern = {
                    'level': 'critical',
                    'time_to_threshold': round(hours_to_critical, 1),
                    'recommendation': f"⚠️ URGENT: {parameter.upper()} dropping fast! Will reach critical threshold ({thresh['critical_low']}) in {hours_to_critical:.1f} hours. Take action NOW to reverse trend."
                }
            # Warning: Will hit warning threshold in < 24 hours
            elif hours_to_warning and hours_to_warning < 24:
                concern = {
                    'level': 'warning',
                    'time_to_threshold': round(hours_to_warning, 1),
                    'recommendation': f"⚠️ {parameter.upper()} declining. Will reach warning threshold ({thresh['warning_low']}) in {hours_to_warning:.1f} hours. Prepare to intervene."
                }
            # Watch: Falling but not immediate concern
            elif current > thresh['optimal_low']:
                concern = {
                    'level': 'watch',
                    'recommendation': f"📉 {parameter.upper()} trending down at {abs(rate):.3f}/hour. Monitor closely."
                }
        
        # Check if rising and approaching critical high
        elif trend == 'rising' and rate > 0:
            hours_to_warning = None
            hours_to_critical = None
            
            if current < thresh['warning_high']:
                hours_to_warning = (thresh['warning_high'] - current) / rate
            
            if current < thresh['critical_high']:
                hours_to_critical = (thresh['critical_high'] - current) / rate
            
            if hours_to_critical and hours_to_critical < 12:
                concern = {
                    'level': 'critical',
                    'time_to_threshold': round(hours_to_critical, 1),
                    'recommendation': f"⚠️ URGENT: {parameter.upper()} rising fast! Will reach critical threshold ({thresh['critical_high']}) in {hours_to_critical:.1f} hours. Take action NOW."
                }
            elif hours_to_warning and hours_to_warning < 24:
                concern = {
                    'level': 'warning',
                    'time_to_threshold': round(hours_to_warning, 1),
                    'recommendation': f"⚠️ {parameter.upper()} increasing. Will reach warning threshold ({thresh['warning_high']}) in {hours_to_warning:.1f} hours."
                }
            elif current < thresh['optimal_high']:
                concern = {
                    'level': 'watch',
                    'recommendation': f"📈 {parameter.upper()} trending up at {rate:.3f}/hour. Monitor closely."
                }
        
        # Stable or in optimal range
        else:
            if thresh['optimal_low'] <= current <= thresh['optimal_high']:
                concern = {
                    'level': 'none',
                    'recommendation': f"✅ {parameter.upper()} stable in optimal range. Continue current management."
                }
            else:
                concern = {
                    'level': 'watch',
                    'recommendation': f"👁️ {parameter.upper()} outside optimal but stable. Watch for changes."
                }
        
        return concern
    
    def analyze_all_trends(self) -> dict:
        """Analyze trends for all parameters"""
        parameters = ['ph', 'temperature', 'do']
        
        trends = {}
        highest_concern = 'none'
        urgent_actions = []
        
        for param in parameters:
            trend = self.analyze_parameter_trend(param, hours=24)
            trends[param] = trend
            
            # Track highest concern
            concern_levels = ['none', 'watch', 'warning', 'critical']
            if concern_levels.index(trend['concern_level']) > concern_levels.index(highest_concern):
                highest_concern = trend['concern_level']
            
            # Collect urgent actions
            if trend['concern_level'] in ['warning', 'critical']:
                urgent_actions.append({
                    'parameter': param,
                    'level': trend['concern_level'],
                    'action': trend['recommendation'],
                    'time_to_threshold': trend.get('time_to_threshold')
                })
        
        # Sort actions by urgency (shortest time first)
        urgent_actions.sort(key=lambda x: x.get('time_to_threshold', 999))
        
        return {
            'overall_concern': highest_concern,
            'trends': trends,
            'urgent_actions': urgent_actions,
            'timestamp': datetime.now().isoformat()
        }

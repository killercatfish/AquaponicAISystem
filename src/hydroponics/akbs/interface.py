"""
AKBS Interface for Sensor System
Connects live sensor data to aquaponics knowledge base
"""

import sys
from pathlib import Path

# Add AKBS to Python path
akbs_path = Path.home() / "aquaponics-knowledge-base-system"
sys.path.insert(0, str(akbs_path))

try:
    import chromadb
    from chromadb.config import Settings
    AKBS_AVAILABLE = True
except ImportError:
    AKBS_AVAILABLE = False
    print("⚠️  AKBS not available - install chromadb")


class AKBSInterface:
    """Interface to query AKBS knowledge base with sensor context"""
    
    def __init__(self):
        self.available = AKBS_AVAILABLE
        self.collection = None
        
        if AKBS_AVAILABLE:
            try:
                db_path = akbs_path / "data" / "knowledge_db"
                self.client = chromadb.PersistentClient(
                    path=str(db_path),
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = self.client.get_collection(name="aquaponics_knowledge")
                chunk_count = self.collection.count()
                print(f"✓ AKBS connected: {chunk_count} chunks available")
            except Exception as e:
                print(f"⚠️  AKBS connection failed: {e}")
                self.available = False
    
    def query(self, question: str, n_results: int = 3) -> dict:
        """
        Query knowledge base
        
        Returns:
        {
            'available': bool,
            'results': [
                {
                    'content': str,
                    'source': str,
                    'relevance': float
                }
            ]
        }
        """
        if not self.available or not self.collection:
            return {
                'available': False,
                'results': [],
                'error': 'AKBS not available'
            }
        
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'][0]:
                for doc, meta, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    formatted_results.append({
                        'content': doc[:500] + '...' if len(doc) > 500 else doc,
                        'source': meta.get('source', 'Unknown'),
                        'relevance': round(1 - dist, 3)  # Convert distance to relevance
                    })
            
            return {
                'available': True,
                'results': formatted_results,
                'query': question
            }
            
        except Exception as e:
            return {
                'available': False,
                'results': [],
                'error': str(e)
            }
    
    def query_with_sensor_context(self, sensor_data: dict, question: str = None) -> dict:
        """
        Query with current sensor readings as context
        
        Args:
            sensor_data: dict with pH, temp, DO, level
            question: optional specific question
        """
        # Build context from sensor data
        context_parts = ["Current system readings:"]
        
        if 'ph' in sensor_data:
            context_parts.append(f"- pH: {sensor_data['ph']:.2f}")
        if 'temperature' in sensor_data:
            context_parts.append(f"- Temperature: {sensor_data['temperature']:.1f}°C")
        if 'do' in sensor_data:
            context_parts.append(f"- Dissolved Oxygen: {sensor_data['do']:.1f} mg/L")
        if 'water_level' in sensor_data:
            context_parts.append(f"- Water Level: {sensor_data['water_level']:.1f} cm")
        
        context = "\n".join(context_parts)
        
        # Add user question if provided
        if question:
            full_query = f"{context}\n\nQuestion: {question}"
        else:
            full_query = f"{context}\n\nAre these values optimal? Any issues or recommendations?"
        
        return self.query(full_query, n_results=3)
    
    def get_parameter_info(self, parameter: str, value: float) -> dict:
        """
        Get information about a specific parameter
        
        Args:
            parameter: 'ph', 'temperature', 'do', or 'water_level'
            value: current reading
        """
        queries = {
            'ph': f"pH is {value}, is this optimal? What should I do?",
            'temperature': f"Water temperature is {value}°C, is this optimal?",
            'do': f"Dissolved oxygen is {value} mg/L, is this acceptable?",
            'water_level': f"Water level is {value} cm, recommendations?"
        }
        
        query = queries.get(parameter, f"{parameter} is {value}, more information?")
        return self.query(query, n_results=2)
    
    def get_intelligent_analysis(self, parameter: str, value: float, system_context: dict = None) -> dict:
        """
        Get intelligent analysis combining rule-based reasoning + knowledge base
        """
        from hydroponics.analysis.parameter_analyzer import ParameterAnalyzer
        
        analyzer = ParameterAnalyzer()
        
        # Get rule-based analysis
        if parameter == 'ph':
            rule_analysis = analyzer.analyze_ph(value)
        elif parameter == 'temperature':
            rule_analysis = analyzer.analyze_temperature(value)
        elif parameter == 'do':
            temp = system_context.get('temperature', 20) if system_context else 20
            rule_analysis = analyzer.analyze_do(value, temp)
        else:
            rule_analysis = {
                'status': 'unknown',
                'explanation': 'Analysis not available for this parameter'
            }
        
        # Get textbook context
        textbook_context = self.get_parameter_info(parameter, value)
        
        # Combine both
        return {
            'intelligent_analysis': rule_analysis,
            'textbook_knowledge': textbook_context,
            'combined': True
        }
        
    def get_predictive_analysis(self, sensor_data: dict) -> dict:
        """
        LAYER 3 & 4: Predictive + Correlation Analysis
        """
        from hydroponics.analysis.trend_analyzer import TrendAnalyzer
        from hydroponics.analysis.parameter_analyzer import ParameterAnalyzer
        from hydroponics.database.manager import DatabaseManager
        
        # Initialize analyzers
        db = DatabaseManager()
        trend_analyzer = TrendAnalyzer(db)
        param_analyzer = ParameterAnalyzer()
        
        # Get trend analysis
        trend_analysis = trend_analyzer.analyze_all_trends()
        
        # Get correlation analysis with trends
        correlation = param_analyzer.analyze_correlations_advanced(
            sensor_data,
            trend_analysis['trends']
        )
        
        # Get textbook context for identified issues
        textbook_context = []
        if correlation['root_cause']:
            query = f"Root cause: {correlation['root_cause']}. What should I do?"
            textbook_context = self.query(query, n_results=2)
        
        return {
            'trends': trend_analysis,
            'correlation': correlation,
            'textbook': textbook_context,
            'intelligence_level': 'predictive_correlation'
        }


# Global instance (initialized once)
akbs = None

def get_akbs():
    """Get or create global AKBS instance"""
    global akbs
    if akbs is None:
        akbs = AKBSInterface()
    return akbs

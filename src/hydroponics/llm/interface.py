"""
LLM Interface for natural language interaction with aquaponics system
Supports both local (Ollama) and cloud (OpenAI/Anthropic) LLMs
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import openai
except ImportError:
    logger.warning("openai not installed, cloud LLM unavailable")
    openai = None

try:
    import anthropic
except ImportError:
    logger.warning("anthropic not installed, Claude unavailable")
    anthropic = None

try:
    import requests
except ImportError:
    logger.warning("requests not installed, local LLM unavailable")
    requests = None


class AquaponicsLLM:
    """Natural language interface for aquaponics system"""
    
    def __init__(self, config):
        self.config = config
        self.conversation_history = []
        
        # Determine which LLM backend to use
        self.backend = config.llm_backend  # 'openai', 'anthropic', 'ollama', or 'mock'
        self.api_key = config.llm_api_key
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        
        if self.backend == 'openai' and openai and self.api_key:
            openai.api_key = self.api_key
            self.openai_client = openai
            logger.info("Initialized OpenAI client")
        
        elif self.backend == 'anthropic' and anthropic and self.api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("Initialized Anthropic client")
        
        elif self.backend == 'ollama':
            self.ollama_url = config.ollama_url or "http://localhost:11434"
            logger.info(f"Using Ollama at {self.ollama_url}")
        
        else:
            logger.warning("Running LLM in MOCK MODE")
            self.backend = 'mock'
    
    def get_response(self, user_message: str, system_state: Dict) -> str:
        """
        Get LLM response with system context
        
        Args:
            user_message: User's question or command
            system_state: Current system state including sensors, relays, etc.
        
        Returns:
            LLM's response as string
        """
        try:
            # Build context from system state
            context = self._build_context(system_state)
            
            # Route to appropriate backend
            if self.backend == 'openai':
                response = self._query_openai(user_message, context)
            elif self.backend == 'anthropic':
                response = self._query_anthropic(user_message, context)
            elif self.backend == 'ollama':
                response = self._query_ollama(user_message, context)
            else:
                response = self._mock_response(user_message, system_state)
            
            # Store in conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': user_message,
                'assistant': response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _build_context(self, system_state: Dict) -> str:
        """Build context string from system state"""
        sensors = system_state.get('sensors', {})
        relays = system_state.get('relays', {})
        plant_health = system_state.get('plant_health', {})
        alerts = system_state.get('alerts', [])
        
        context = f"""You are an expert aquaponics system assistant. You help users understand and optimize their system.

Current System Status (as of {system_state.get('last_update', 'unknown')}):

WATER QUALITY:
- pH: {sensors.get('ph', 'N/A')} (optimal: 6.0-7.0 for aquaponics, 5.8-6.2 for hydroponics)
- EC (Electrical Conductivity): {sensors.get('ec', 'N/A')} mS/cm (optimal: 1.0-1.8)
- Dissolved Oxygen: {sensors.get('do', 'N/A')} mg/L (critical: >6.0 for fish, >5.0 for plants)
- Reservoir Temperature: {sensors.get('temp_reservoir', 'N/A')}Â°C (optimal: 18-22Â°C)
- Fish Tank Temperature: {sensors.get('temp_fish_tank', 'N/A')}Â°C (trout optimal: 10-15Â°C)
- Water Level: {sensors.get('water_level_percent', 'N/A')}%

EQUIPMENT STATUS:
- Water Pump: {'ON' if relays.get('pump') else 'OFF'}
- Grow Lights: {'ON' if relays.get('lights') else 'OFF'}
- Heater: {'ON' if relays.get('heater') else 'OFF'}
- Backup Aerator: {'ON' if relays.get('backup_aerator') else 'OFF'}

PLANT HEALTH:
- Status: {plant_health.get('status', 'unknown')}
- Confidence: {plant_health.get('confidence', 0):.1%}
- Issues Detected: {', '.join([i.get('type', 'unknown') for i in plant_health.get('issues', [])]) or 'None'}
- Last Analysis: {plant_health.get('last_analysis', 'Never')}

RECENT ALERTS:
{self._format_alerts(alerts[-3:]) if alerts else 'No recent alerts'}

SYSTEM STATUS: {system_state.get('system_status', 'unknown')}

Remember:
- For fish systems (aquaponics): pH 7.0-7.5, DO >6 mg/L, temp depends on species
- For plant-only systems (hydroponics): pH 5.8-6.2, DO >5 mg/L
- Rainbow trout need: 10-15Â°C water temp, DO 7-9 mg/L, low ammonia/nitrite
- Provide specific, actionable advice based on current readings
- Warn about critical issues (low DO, extreme pH, high ammonia)
- Explain the "why" behind recommendations for educational value
"""
        return context
    
    def _format_alerts(self, alerts: List[Dict]) -> str:
        """Format alerts for context"""
        if not alerts:
            return "None"
        
        formatted = []
        for alert in alerts:
            formatted.append(
                f"- [{alert.get('level', 'info').upper()}] "
                f"{alert.get('message', 'Unknown alert')} "
                f"({alert.get('timestamp', 'unknown')})"
            )
        return '\n'.join(formatted)
    
    def _query_openai(self, user_message: str, context: str) -> str:
        """Query OpenAI GPT"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error querying OpenAI: {str(e)}"
    
    def _query_anthropic(self, user_message: str, context: str) -> str:
        """Query Anthropic Claude"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=context,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error querying Claude: {str(e)}"
    
    def _query_ollama(self, user_message: str, context: str) -> str:
        """Query local Ollama instance"""
        try:
            payload = {
                "model": "llama3",  # or "mistral", "mixtral", etc.
                "prompt": f"{context}\n\nUser: {user_message}\nAssistant:",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json().get('response', 'No response from Ollama')
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"Error querying local LLM: {str(e)}"
    
    def _mock_response(self, user_message: str, system_state: Dict) -> str:
        """Generate mock response for testing"""
        sensors = system_state.get('sensors', {})
        
        # Simple pattern matching for common queries
        message_lower = user_message.lower()
        
        if 'ph' in message_lower:
            ph = sensors.get('ph')
            if ph is None:
                return "I don't have a pH reading right now. Please check if the sensor is working."
            elif ph < 6.0:
                return f"Your pH is currently {ph:.1f}, which is too low. For aquaponics, aim for 6.5-7.5. For hydroponics, aim for 5.8-6.2. Add pH up solution slowly."
            elif ph > 7.5:
                return f"Your pH is currently {ph:.1f}, which is a bit high for optimal nutrient uptake. Add pH down solution slowly. Check in 30 minutes."
            else:
                return f"Your pH is {ph:.1f}, which is in a good range. Keep monitoring it daily."
        
        elif 'dissolved oxygen' in message_lower or 'do' in message_lower:
            do_val = sensors.get('do')
            if do_val is None:
                return "I don't have a DO reading right now. Check the sensor."
            elif do_val < 5:
                return f"WARNING: Dissolved oxygen is critically low at {do_val:.1f} mg/L! This can harm fish and plants. Increase aeration immediately. Check if the air pump is working and add air stones if needed."
            elif do_val < 6:
                return f"Dissolved oxygen is {do_val:.1f} mg/L, which is low. For fish health, aim for 7-9 mg/L. Increase aeration or check water temperature (warmer water holds less oxygen)."
            else:
                return f"Dissolved oxygen is good at {do_val:.1f} mg/L. Your fish and plants should be happy!"
        
        elif 'temperature' in message_lower or 'temp' in message_lower:
            temp = sensors.get('temp_reservoir')
            if temp is None:
                return "I don't have a temperature reading right now."
            elif temp < 15:
                return f"Water temperature is {temp:.1f}Â°C, which is quite cold. This slows plant growth and nutrient uptake. Consider adding a heater. However, this is good for rainbow trout!"
            elif temp > 24:
                return f"Water temperature is {temp:.1f}Â°C, which is high. This increases disease risk and reduces dissolved oxygen. Add cooling or improve ventilation. Too hot for trout!"
            else:
                return f"Water temperature is {temp:.1f}Â°C, which is in a good range for most plants."
        
        elif 'plant' in message_lower and ('health' in message_lower or 'problem' in message_lower):
            plant_health = system_state.get('plant_health', {})
            status = plant_health.get('status', 'unknown')
            if status == 'healthy':
                return "Your plants look healthy! Keep up the good work with your current care routine."
            elif 'deficiency' in status:
                return f"I detected {status.replace('_', ' ')}. Check your nutrient solution strength and pH. The issue might be nutrient lockout rather than actual deficiency."
            else:
                return f"I detected {status.replace('_', ' ')}. Check the recommendations in the plant health section for specific actions to take."
        
        elif 'help' in message_lower or 'what can you' in message_lower:
            return """I can help you with:
- Monitoring water quality (pH, EC, DO, temperature)
- Diagnosing plant health issues
- Providing recommendations for system optimization
- Explaining aquaponics/hydroponics concepts
- Troubleshooting problems

Try asking me things like:
- "What's wrong with my pH?"
- "Why are my plants yellowing?"
- "Is my dissolved oxygen level safe?"
- "How do I adjust nutrient levels?"
"""
        
        else:
            return f"I'm a mock assistant. In production, I would analyze your question '{user_message}' with the full system context and provide detailed advice. Your system status is: {system_state.get('system_status', 'unknown')}"
    
    def get_diagnosis(self, issue_description: str, system_state: Dict) -> str:
        """
        Get detailed diagnosis for a specific issue
        
        Args:
            issue_description: Description of the problem
            system_state: Current system state
        
        Returns:
            Detailed diagnosis and recommendations
        """
        prompt = f"""A user is experiencing the following issue with their aquaponics system:

{issue_description}

Based on the current system parameters, please provide:
1. The most likely cause(s) of this issue
2. Step-by-step troubleshooting steps
3. Immediate actions to take
4. Long-term prevention strategies
5. Related parameters to monitor

Be specific and educational - explain the "why" behind your recommendations."""

        return self.get_response(prompt, system_state)
    
    def suggest_optimizations(self, system_state: Dict) -> str:
        """
        Analyze system and suggest optimizations
        
        Args:
            system_state: Current system state
        
        Returns:
            Optimization suggestions
        """
        prompt = """Please analyze the current system state and suggest optimizations for:
1. Plant health and growth rate
2. Water quality stability
3. Energy efficiency
4. Disease prevention
5. Nutrient utilization

Prioritize suggestions by impact and ease of implementation."""

        return self.get_response(prompt, system_state)
    
    def explain_parameter(self, parameter: str) -> str:
        """
        Explain what a parameter means and why it matters
        
        Args:
            parameter: Parameter name (e.g., 'pH', 'EC', 'DO')
        
        Returns:
            Educational explanation
        """
        explanations = {
            'ph': """pH measures how acidic or alkaline your water is, on a scale from 0-14.

Why it matters:
- pH affects nutrient availability. Each nutrient has an optimal pH range for uptake
- Too high (>7.5): Iron, manganese, phosphorus become unavailable â†’ deficiencies
- Too low (<5.5): Aluminum and manganese can reach toxic levels
- Fish need 7.0-7.5, plants prefer 5.8-6.2 â†’ aquaponics compromises at 6.5-7.0

How to manage:
- Test daily, adjust slowly (0.2 units per day max)
- Use pH Up (potassium hydroxide) or pH Down (phosphoric acid)
- Understand that nutrient solutions naturally drift due to plant uptake""",
            
            'ec': """EC (Electrical Conductivity) measures the concentration of dissolved salts in water, indicating nutrient strength.

Units: mS/cm (millisiemens per centimeter) or ppm
Conversion: ~1.0 mS/cm = ~640 ppm

Why it matters:
- Too low: Plants starve, slow growth, pale leaves
- Too high: Nutrient burn, root damage, water stress
- Optimal range depends on plant type and growth stage

Typical targets:
- Lettuce/greens: 1.0-1.4 mS/cm
- Tomatoes/peppers: 2.0-2.5 mS/cm  
- Seedlings: 0.8-1.2 mS/cm

How to manage:
- Add nutrients to increase, add water to decrease
- Monitor daily (plants consume nutrients â†’ EC drops)""",
            
            'do': """DO (Dissolved Oxygen) measures oxygen dissolved in water, critical for root and fish respiration.

Units: mg/L (milligrams per liter) or ppm
Temperature dependent: Cold water holds more oxygen than warm water

Why it matters:
- Roots need oxygen to absorb nutrients â†’ low DO causes nutrient deficiencies
- Fish will die quickly if DO drops below 4 mg/L
- Low DO promotes anaerobic bacteria â†’ root rot, disease

Critical thresholds:
- Fish (especially trout): 6+ mg/L (7-9 optimal)
- Plant roots: 5+ mg/L minimum
- Below 4 mg/L: Emergency situation

How to manage:
- Add air stones and pumps to increase
- Keep water temperature down (warmer = less DO)
- Increase water flow and agitation
- Don't overfeed fish (decomposition uses oxygen)"""
        }
        
        param_lower = parameter.lower()
        if param_lower in explanations:
            return explanations[param_lower]
        else:
            return f"I don't have a detailed explanation for '{parameter}' yet. Try asking about pH, EC, or DO."

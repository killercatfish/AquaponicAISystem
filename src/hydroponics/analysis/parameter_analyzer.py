"""
Intelligent Parameter Analysis
Combines rule-based reasoning with knowledge base context
"""

class ParameterAnalyzer:
    """Analyzes sensor readings with aquaponics expertise"""
    
    def analyze_ph(self, ph_value: float, system_type: str = "NFT") -> dict:
        """
        Intelligent pH analysis with specific recommendations
        """
        analysis = {
            'parameter': 'pH',
            'value': ph_value,
            'status': 'unknown',
            'urgency': 'normal',
            'problems': [],
            'actions': [],
            'explanation': ''
        }
        
        # Critical low
        if ph_value < 6.0:
            analysis['status'] = 'critical'
            analysis['urgency'] = 'immediate'
            analysis['problems'] = [
                'pH dangerously low',
                'Biofilter efficiency severely reduced (<50%)',
                'Fish stress increasing',
                'Ammonia toxicity risk rising'
            ]
            analysis['actions'] = [
                'IMMEDIATE: Add 3 tsp sodium bicarbonate per 5 gallons',
                'Stop feeding for 24 hours (reduce CO2)',
                'Test ammonia within 1 hour',
                'Increase aeration by 50%',
                'Monitor pH every 2 hours until above 6.5'
            ]
            analysis['explanation'] = f"Your pH of {ph_value:.2f} is in the critical zone. This is likely causing a cascade of problems. Priority is raising pH immediately to protect biofilter bacteria."
        
        # Warning low
        elif ph_value < 6.5:
            analysis['status'] = 'warning'
            analysis['urgency'] = 'soon'
            analysis['problems'] = [
                'pH below optimal for biofilter (wants 7.0-8.5)',
                'Nitrification running at 50-70% efficiency',
                'pH likely to continue dropping'
            ]
            analysis['actions'] = [
                'Add 2 tsp potassium carbonate per 5 gallons',
                'Reduce feeding by 25% temporarily',
                'Test pH again in 6 hours',
                'Target: 6.5-7.0 for lettuce systems'
            ]
            analysis['explanation'] = f"At {ph_value:.2f}, your biofilter is stressed but functional. Act within 24 hours to prevent further drop."
        
        # Good range
        elif 6.5 <= ph_value <= 7.5:
            analysis['status'] = 'good'
            analysis['problems'] = []
            analysis['actions'] = [
                'Continue normal operations',
                'Monitor daily',
                'No immediate action needed'
            ]
            analysis['explanation'] = f"pH of {ph_value:.2f} is in the sweet spot for NFT lettuce + biofilter. Great work!"
        
        # Warning high
        elif ph_value < 8.5:
            analysis['status'] = 'warning'
            analysis['urgency'] = 'soon'
            analysis['problems'] = [
                'pH higher than optimal for lettuce',
                'Some nutrients becoming unavailable',
                'Ammonia toxicity increasing (NH3 form)'
            ]
            analysis['actions'] = [
                'Test ammonia immediately',
                'Reduce/stop lime additions',
                'Consider adding citric acid (pH down)',
                'Target: lower to 7.0-7.5'
            ]
            analysis['explanation'] = f"At {ph_value:.2f}, nutrients are starting to precipitate out of solution."
        
        # Critical high
        else:
            analysis['status'] = 'critical'
            analysis['urgency'] = 'immediate'
            analysis['problems'] = [
                'pH dangerously high',
                'Iron, manganese becoming unavailable',
                'NH3 toxicity risk',
                'Possible lime overdose'
            ]
            analysis['actions'] = [
                'IMMEDIATE: Add pH down (citric acid)',
                'Test ammonia - if high, partial water change',
                'Stop all lime additions',
                'Monitor every hour until below 8.0'
            ]
            analysis['explanation'] = f"pH of {ph_value:.2f} is critical. Plants cannot access nutrients."
        
        return analysis
    
    def analyze_temperature(self, temp_c: float, species: str = "lettuce") -> dict:
        """Analyze temperature with species-specific recommendations"""
        analysis = {
            'parameter': 'temperature',
            'value': temp_c,
            'status': 'unknown',
            'urgency': 'normal',
            'problems': [],
            'actions': [],
            'explanation': ''
        }
        
        # Lettuce optimal: 18-24°C
        if temp_c < 15:
            analysis['status'] = 'critical'
            analysis['urgency'] = 'soon'
            analysis['problems'] = [
                'Too cold - growth will stop',
                'Risk of root disease'
            ]
            analysis['actions'] = [
                'Add aquarium heater (50W per 10 gallons)',
                'Insulate reservoir',
                'Target: 18-22°C'
            ]
            analysis['explanation'] = f"At {temp_c:.1f}°C, lettuce growth is severely stunted."
        
        elif temp_c < 18:
            analysis['status'] = 'warning'
            analysis['urgency'] = 'normal'
            analysis['problems'] = ['Below optimal - slow growth']
            analysis['actions'] = [
                'Consider gentle heating',
                'Monitor growth rate',
                'Acceptable but not ideal'
            ]
            analysis['explanation'] = f"At {temp_c:.1f}°C, growth is slower than optimal but acceptable."
        
        elif 18 <= temp_c <= 24:
            analysis['status'] = 'good'
            analysis['actions'] = ['Continue monitoring', 'No action needed']
            analysis['explanation'] = f"Perfect! {temp_c:.1f}°C is ideal for lettuce."
        
        elif temp_c < 28:
            analysis['status'] = 'warning'
            analysis['urgency'] = 'soon'
            analysis['problems'] = [
                'Getting warm - check DO',
                'Plants may bolt (flower prematurely)'
            ]
            analysis['actions'] = [
                'Check dissolved oxygen (should be >6 mg/L)',
                'Increase aeration if DO dropping',
                'Consider shading reservoir',
                'Monitor for bolting (flowering)'
            ]
            analysis['explanation'] = f"At {temp_c:.1f}°C, watch for stress. Lettuce prefers cooler."
        
        else:
            analysis['status'] = 'critical'
            analysis['urgency'] = 'immediate'
            analysis['problems'] = [
                'Too hot - lettuce will bolt',
                'DO crash risk'
            ]
            analysis['actions'] = [
                'URGENT: Cool system (ice bottles, shade)',
                'Check DO immediately',
                'Consider switching to heat-tolerant species',
                'Harvest lettuce before it bolts'
            ]
            analysis['explanation'] = f"At {temp_c:.1f}°C, lettuce is stressed and will likely bolt soon."
        
        return analysis
    
    def analyze_do(self, do_value: float, temp_c: float = 20) -> dict:
        """Analyze DO with temperature consideration"""
        analysis = {
            'parameter': 'dissolved_oxygen',
            'value': do_value,
            'status': 'unknown',
            'urgency': 'normal',
            'problems': [],
            'actions': [],
            'explanation': ''
        }
        
        if do_value < 4:
            analysis['status'] = 'critical'
            analysis['urgency'] = 'immediate'
            analysis['problems'] = [
                'Fish will die within hours',
                'Biofilter bacteria dying',
                'Root rot starting in plants'
            ]
            analysis['actions'] = [
                'EMERGENCY: Add air stone/aerator NOW',
                'Reduce feeding to zero',
                'Check for dead zones in system',
                'Partial water change with aerated water',
                'Check pump - may be failing'
            ]
            analysis['explanation'] = f"DO of {do_value:.1f} mg/L is life-threatening. This is an emergency."
        
        elif do_value < 6:
            analysis['status'] = 'warning'
            analysis['urgency'] = 'soon'
            analysis['problems'] = [
                'Below safe threshold for most fish',
                'Biofilter efficiency reduced',
                'Fish showing stress behaviors'
            ]
            analysis['actions'] = [
                'Increase aeration immediately',
                'Check water temperature (high temp = low DO)',
                'Reduce feeding by 50%',
                'Target: >6 mg/L minimum'
            ]
            analysis['explanation'] = f"DO of {do_value:.1f} mg/L is marginal. Fish are stressed."
        
        elif 6 <= do_value <= 9:
            analysis['status'] = 'good'
            analysis['actions'] = ['Maintain current aeration', 'Monitor daily']
            analysis['explanation'] = f"DO of {do_value:.1f} mg/L is excellent. System is well-aerated."
        
        else:
            analysis['status'] = 'good'
            analysis['problems'] = []
            analysis['actions'] = ['Monitor for gas bubble disease (rare)']
            analysis['explanation'] = f"DO of {do_value:.1f} mg/L is very high (supersaturated). Usually not a problem."
        
        return analysis
    
    def analyze_system_holistic(self, readings: dict) -> dict:
        """
        Analyze multiple parameters together to find root causes
        """
        ph = readings.get('ph', 7.0)
        temp = readings.get('temperature', 22.0)
        do = readings.get('do', 7.5)
        
        holistic = {
            'overall_status': 'good',
            'root_cause': None,
            'cascading_effects': [],
            'priority_actions': [],
            'explanation': ''
        }
        
        # Pattern 1: Low pH + Low DO = Biofilter crash
        if ph < 6.5 and do < 6:
            holistic['overall_status'] = 'critical'
            holistic['root_cause'] = 'Biofilter failure causing cascade'
            holistic['cascading_effects'] = [
                'Low pH inhibits nitrification',
                'Poor nitrification → excess CO2',
                'CO2 displaces oxygen',
                'Low oxygen → fish stress → less eating',
                'Downward spiral in progress'
            ]
            holistic['priority_actions'] = [
                '1. FIRST: Raise pH (fixes root cause)',
                '2. THEN: Increase aeration (addresses symptom)',
                '3. Stop feeding 24h (breaks cycle)',
                '4. Monitor ammonia (biofilter compromised)',
                '5. Expected recovery: 48-72 hours'
            ]
            holistic['explanation'] = "Classic biofilter crash. Low pH started it, DO crash followed. Fix pH first!"
        
        # Pattern 2: High temp + Low DO
        elif temp > 24 and do < 7:
            holistic['overall_status'] = 'warning'
            holistic['root_cause'] = 'Temperature too high for DO saturation'
            holistic['cascading_effects'] = [
                'Warm water holds less oxygen',
                f'At {temp:.1f}°C, saturation is only ~{9 - (temp-20)*0.2:.1f} mg/L',
                'Current aeration insufficient for temperature'
            ]
            holistic['priority_actions'] = [
                '1. FIRST: Cool water (ice bottles, shade)',
                '2. THEN: Increase aeration 50%',
                '3. Reduce feeding (less oxygen demand)',
                '4. This will fix both problems'
            ]
            holistic['explanation'] = f"Temperature of {temp:.1f}°C is causing low DO. Cool first, then DO will rise naturally."
        
        # Pattern 3: All good
        elif 6.5 <= ph <= 7.5 and do >= 6 and 18 <= temp <= 24:
            holistic['overall_status'] = 'excellent'
            holistic['explanation'] = "All parameters in optimal ranges. System is healthy!"
            holistic['priority_actions'] = [
                'Continue current management',
                'Maintain monitoring schedule'
            ]
        
        # Pattern 4: Only pH off
        elif ph < 6.5 and do >= 6:
            holistic['root_cause'] = 'pH declining (but caught early)'
            holistic['priority_actions'] = [
                '1. Raise pH now (before it affects biofilter)',
                '2. DO and temp are good - pH is only issue',
                '3. Easy fix if done promptly'
            ]
            holistic['explanation'] = "Only pH is low. Good news: caught it before cascade! Fix it today."
        
        return holistic
    def analyze_correlations_advanced(self, readings: dict, trends: dict) -> dict:
        """
        LAYER 4: Advanced Multi-Parameter Correlation
        Identifies root causes and cascading effects using trends
        """
        ph = readings.get('ph', 7.0)
        temp = readings.get('temperature', 22.0)
        do = readings.get('do', 7.5)
        
        ph_trend = trends.get('ph', {})
        temp_trend = trends.get('temperature', {})
        do_trend = trends.get('do', {})
        
        analysis = {
            'root_cause': None,
            'cascading_effects': [],
            'intervention_priority': [],
            'system_state': 'unknown',
            'explanation': '',
            'predicted_outcome': ''
        }
        
        # PATTERN 1: Biofilter Crash in Progress
        if (ph < 6.5 and ph_trend.get('trend') == 'falling' and
            do < 7 and do_trend.get('trend') == 'falling'):
            
            analysis['root_cause'] = 'Biofilter collapse cascade'
            analysis['system_state'] = 'critical_cascade'
            analysis['cascading_effects'] = [
                '1. Low pH inhibits nitrifying bacteria',
                '2. Bacteria produce less, consume less O2',
                '3. Incomplete nitrification → excess CO2',
                '4. CO2 further lowers pH (positive feedback loop)',
                '5. DO drops as CO2 displaces oxygen',
                '6. Fish stress → stop eating → less waste',
                '7. Bacteria starve → die off accelerates',
                '⚠️ DOWNWARD SPIRAL ACTIVE'
            ]
            
            # Calculate time to system failure
            ph_hours = ph_trend.get('time_to_threshold', 999)
            do_hours = do_trend.get('time_to_threshold', 999)
            critical_hours = min(ph_hours, do_hours)
            
            analysis['intervention_priority'] = [
                {
                    'order': 1,
                    'action': 'IMMEDIATE: Raise pH to 7.0+',
                    'why': 'Breaks the cascade at root cause',
                    'method': 'Add 3 tsp sodium bicarbonate per 5 gal'
                },
                {
                    'order': 2,
                    'action': 'IMMEDIATE: Maximize aeration',
                    'why': 'Prevents fish death while pH recovers',
                    'method': 'Add extra air stones, increase pump flow'
                },
                {
                    'order': 3,
                    'action': 'Stop feeding for 24-48h',
                    'why': 'Reduces CO2 production, gives bacteria time to recover',
                    'method': 'No food until pH stable above 6.8'
                },
                {
                    'order': 4,
                    'action': 'Monitor ammonia every 2 hours',
                    'why': 'Biofilter compromised, ammonia may spike',
                    'method': 'Test kit, be ready for emergency water change'
                }
            ]
            
            analysis['explanation'] = f"""
🚨 CRITICAL SYSTEM FAILURE IN PROGRESS

Your system is in a biofilter collapse cascade. This is a self-reinforcing
failure where low pH causes bacteria to fail, which lowers pH further.

Time to system failure: ~{critical_hours:.1f} hours

Root cause: pH dropped below biofilter threshold
Effect chain: pH ↓ → Bacteria fail → CO2 ↑ → pH ↓↓ → DO ↓ → Crisis

The ONLY way to stop this is to break the cycle by raising pH immediately.
Everything else is secondary.
            """
            
            analysis['predicted_outcome'] = f"""
WITHOUT intervention: System failure in {critical_hours:.1f}h, fish death likely
WITH intervention: 48-72h recovery if pH raised within next 6 hours
            """
        
        # PATTERN 2: Temperature-Induced Oxygen Crisis
        elif (temp > 25 and temp_trend.get('trend') == 'rising' and
              do < 7 and do_trend.get('trend') == 'falling'):
            
            analysis['root_cause'] = 'Temperature rising → Oxygen capacity falling'
            analysis['system_state'] = 'temperature_oxygen_cascade'
            analysis['cascading_effects'] = [
                f'1. Water temp at {temp:.1f}°C (high)',
                f'2. Oxygen saturation capacity decreasing',
                f'3. At {temp:.1f}°C, max DO only ~{9-(temp-20)*0.2:.1f} mg/L',
                f'4. Current DO: {do:.1f} mg/L',
                '5. Fish metabolism increases with temp (need MORE O2)',
                '6. Available oxygen decreases (can provide LESS O2)',
                '7. Mismatch growing → stress increasing'
            ]
            
            temp_hours = temp_trend.get('time_to_threshold', 999)
            do_hours = do_trend.get('time_to_threshold', 999)
            
            analysis['intervention_priority'] = [
                {
                    'order': 1,
                    'action': 'Cool water immediately',
                    'why': 'Root cause - fixes DO capacity',
                    'method': 'Add frozen water bottles, shade reservoir, reduce light hours'
                },
                {
                    'order': 2,
                    'action': 'Increase aeration 50%',
                    'why': 'Compensates while cooling',
                    'method': 'Additional air stones or venturi'
                },
                {
                    'order': 3,
                    'action': 'Reduce feeding by 50%',
                    'why': 'Lowers oxygen demand',
                    'method': 'Feed less until temp below 24°C'
                }
            ]
            
            analysis['explanation'] = f"""
⚠️ TEMPERATURE-OXYGEN CRISIS DEVELOPING

Temperature is rising, which DECREASES how much oxygen water can hold.
At the same time, warm water makes fish need MORE oxygen.

This is a dangerous mismatch that will cause stress or death.

Root cause: Rising temperature
Time to critical: ~{min(temp_hours, do_hours):.1f} hours

Fix temperature FIRST, then DO will naturally improve.
            """
        
        # PATTERN 3: pH Crash Approaching (Predictive)
        elif (ph_trend.get('trend') == 'falling' and 
              ph_trend.get('concern_level') in ['warning', 'critical']):
            
            analysis['root_cause'] = 'pH declining - catch it early!'
            analysis['system_state'] = 'preventive_action_needed'
            
            hours_remaining = ph_trend.get('time_to_threshold', 24)
            
            analysis['intervention_priority'] = [
                {
                    'order': 1,
                    'action': f'Raise pH within next {hours_remaining:.0f} hours',
                    'why': 'Prevent cascade before it starts',
                    'method': 'Add buffer now while you have time'
                },
                {
                    'order': 2,
                    'action': 'Identify why pH is falling',
                    'why': 'Prevent recurrence',
                    'method': 'Check: overfeeding? low alkalinity? high CO2?'
                }
            ]
            
            analysis['explanation'] = f"""
📊 PREDICTIVE ALERT: pH Crash Approaching

Your pH is falling at {abs(ph_trend.get('rate_of_change', 0)):.3f} per hour.

At this rate, you'll hit warning threshold in {hours_remaining:.1f} hours.

GOOD NEWS: You caught it early! You have time to fix this before problems start.

This is EXACTLY what predictive monitoring is for - catching problems
before they become crises.
            """
        
        # PATTERN 4: All Parameters Optimal and Stable
        elif (6.5 <= ph <= 7.5 and 18 <= temp <= 24 and do >= 6 and
              ph_trend.get('trend') == 'stable' and
              temp_trend.get('trend') == 'stable' and
              do_trend.get('trend') == 'stable'):
            
            analysis['system_state'] = 'optimal_stable'
            analysis['explanation'] = """
✅ SYSTEM OPERATING OPTIMALLY

All parameters in range AND stable over time.
No concerning trends detected.
System is healthy and well-managed.

Continue current practices - you're doing great!
            """
        
        return analysis
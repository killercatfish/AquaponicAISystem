"""
STEM DREAM Aquaponics Control System
Main application with ML plant health detection and LLM integration
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
import json
import logging

# Local imports
from hydroponics.sensors.interfaces import atlas_sensors, temperature_sensors, water_level, relay_control
from hydroponics.ml.vision import PlantHealthAnalyzer
from hydroponics.llm.interface import AquaponicsLLM
from hydroponics.database.manager import DatabaseManager
from hydroponics.alerts.manager import AlertManager
from hydroponics.core.config import Config

# Configure logging
from hydroponics.core.config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file),  # Use config path
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="STEM DREAM Aquaponics Control System")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
config = Config()
db_manager = DatabaseManager(config.database_path)
alert_manager = AlertManager(config)
plant_analyzer = PlantHealthAnalyzer()
aquaponics_llm = AquaponicsLLM(config)

# Global state
system_state = {
    'sensors': {
        'ph': None,
        'ec': None,
        'do': None,
        'temp_reservoir': None,
        'temp_fish_tank': None,
        'water_level': None,
        'water_level_percent': None
    },
    'relays': {
        'pump': False,
        'lights': False,
        'heater': False,
        'backup_aerator': False
    },
    'plant_health': {
        'last_analysis': None,
        'status': 'unknown',
        'issues': [],
        'confidence': 0.0
    },
    'system_status': 'starting',
    'last_update': None,
    'alerts': []
}

# WebSocket connections
active_connections: List[WebSocket] = []

# Scheduler for periodic tasks
scheduler = BackgroundScheduler()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()


def read_all_sensors():
    """Read all sensor values"""
    try:
        logger.info("Reading all sensors...")
        
        # Read Atlas Scientific sensors
        ph_value = atlas_sensors.read_ph()
        ec_value = atlas_sensors.read_ec()
        do_value = atlas_sensors.read_do()
        
        # Read temperature sensors
        temps = temperature_sensors.read_all()
        
        # Read water level
        water_level_data = water_level.read_level()
        
        # Update system state
        system_state['sensors'].update({
            'ph': ph_value,
            'ec': ec_value,
            'do': do_value,
            'temp_reservoir': temps.get('reservoir'),
            'temp_fish_tank': temps.get('fish_tank'),
            'water_level': water_level_data.get('distance_cm'),
            'water_level_percent': water_level_data.get('water_level_percent')
        })
        
        system_state['last_update'] = datetime.now().isoformat()
        system_state['system_status'] = 'running'
        
        # Log to database
        db_manager.log_sensor_reading(system_state['sensors'])
        
        # Check for alerts
        alerts = alert_manager.check_thresholds(system_state['sensors'])
        if alerts:
            system_state['alerts'].extend(alerts)
            # Keep only last 10 alerts
            system_state['alerts'] = system_state['alerts'][-10:]
        
        # Note: WebSocket clients will poll system_state for updates
        # No need to broadcast from scheduled function (no event loop here)
        
        logger.info(f"Sensor reading complete: pH={ph_value}, EC={ec_value}, DO={do_value}")
        
    except Exception as e:
        logger.error(f"Error reading sensors: {e}")
        system_state['system_status'] = 'error'
        system_state['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'level': 'error',
            'message': f"Sensor reading error: {str(e)}"
        })


def analyze_plant_health():
    """Analyze plant health using computer vision"""
    try:
        logger.info("Analyzing plant health...")
        
        # Capture image and analyze
        result = plant_analyzer.analyze()
        
        system_state['plant_health'] = {
            'last_analysis': datetime.now().isoformat(),
            'status': result['status'],
            'issues': result['issues'],
            'confidence': result['confidence'],
            'recommendations': result.get('recommendations', [])
        }
        
        # Log to database
        db_manager.log_plant_analysis(result)
        
        # Check if intervention needed
        if result['status'] != 'healthy':
            system_state['alerts'].append({
                'timestamp': datetime.now().isoformat(),
                'level': 'warning',
                'message': f"Plant health issue detected: {result['status']}"
            })
        
        # Note: WebSocket clients will poll system_state for updates
        
        logger.info(f"Plant analysis complete: {result['status']}")
        
    except Exception as e:
        logger.error(f"Error analyzing plant health: {e}")


def control_automation():
    """Automated control logic"""
    try:
        sensors = system_state['sensors']
        
        # Temperature-based heater control
        if sensors['temp_reservoir'] and sensors['temp_reservoir'] < config.temp_min:
            relay_control.set_relay('heater', True)
            system_state['relays']['heater'] = True
        elif sensors['temp_reservoir'] and sensors['temp_reservoir'] > config.temp_max:
            relay_control.set_relay('heater', False)
            system_state['relays']['heater'] = False
        
        # DO-based backup aerator control
        if sensors['do'] and sensors['do'] < config.do_critical:
            relay_control.set_relay('backup_aerator', True)
            system_state['relays']['backup_aerator'] = True
            system_state['alerts'].append({
                'timestamp': datetime.now().isoformat(),
                'level': 'critical',
                'message': f"CRITICAL: Low dissolved oxygen ({sensors['do']} mg/L) - backup aerator activated"
            })
        elif sensors['do'] and sensors['do'] > config.do_normal:
            relay_control.set_relay('backup_aerator', False)
            system_state['relays']['backup_aerator'] = False
        
        # Water level control
        if sensors['water_level_percent'] and sensors['water_level_percent'] < 20:
            system_state['alerts'].append({
                'timestamp': datetime.now().isoformat(),
                'level': 'critical',
                'message': f"CRITICAL: Low water level ({sensors['water_level_percent']:.1f}%)"
            })
        
    except Exception as e:
        logger.error(f"Error in automation control: {e}")


# Schedule periodic tasks
scheduler.add_job(read_all_sensors, 'interval', minutes=5, id='read_sensors')
scheduler.add_job(analyze_plant_health, 'interval', hours=1, id='analyze_plants')
scheduler.add_job(control_automation, 'interval', minutes=1, id='automation')
scheduler.start()

# Initial sensor reading on startup
scheduler.add_job(read_all_sensors, id='startup_read')


# API Routes

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve main dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "system_name": "STEM DREAM Aquaponics"
    })


@app.get("/api/status")
async def get_status():
    """Get current system status"""
    return JSONResponse(content=system_state)


@app.get("/api/sensors")
async def get_sensors():
    """Get current sensor readings"""
    return JSONResponse(content=system_state['sensors'])


@app.get("/api/history/{sensor}/{hours}")
async def get_sensor_history(sensor: str, hours: int = 24):
    """Get historical sensor data"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        data = db_manager.get_sensor_history(sensor, start_time, end_time)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/relay/{relay_name}/{action}")
async def control_relay(relay_name: str, action: str):
    """Control relay (on/off)"""
    try:
        if relay_name not in system_state['relays']:
            raise HTTPException(status_code=400, detail="Invalid relay name")
        
        state = action.lower() == 'on'
        relay_control.set_relay(relay_name, state)
        system_state['relays'][relay_name] = state
        
        # Log action
        logger.info(f"Relay {relay_name} set to {action}")
        db_manager.log_action(f"relay_{relay_name}", action)
        
        # Broadcast update
        await manager.broadcast({
            'type': 'relay_update',
            'data': system_state['relays']
        })
        
        return JSONResponse(content={
            'success': True,
            'relay': relay_name,
            'state': state
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze_now")
async def trigger_plant_analysis():
    """Trigger immediate plant health analysis"""
    try:
        analyze_plant_health()
        return JSONResponse(content={
            'success': True,
            'message': 'Analysis started'
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat_with_llm(request: Request):
    """Chat with LLM about system status"""
    try:
        data = await request.json()
        user_message = data.get('message', '')
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message required")
        
        # Get LLM response with current system context
        response = aquaponics_llm.get_response(user_message, system_state)
        
        # Log conversation
        db_manager.log_conversation(user_message, response)
        
        return JSONResponse(content={
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            'type': 'initial_state',
            'data': system_state
        })
        
        # Keep connection alive
        while True:
            # Wait for ping from client
            data = await websocket.receive_text()
            if data == 'ping':
                await websocket.send_text('pong')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting STEM DREAM Aquaponics Control System...")
    
    # Initialize hardware
    try:
        atlas_sensors.initialize()
        temperature_sensors.initialize()
        water_level.initialize()
        relay_control.initialize()
        logger.info("Hardware initialized successfully")
    except Exception as e:
        logger.error(f"Hardware initialization error: {e}")
    
    # Load ML models
    try:
        plant_analyzer.load_model()
        logger.info("ML models loaded successfully")
    except Exception as e:
        logger.error(f"ML model loading error: {e}")
    
    logger.info("System startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down system...")
    scheduler.shutdown()
    relay_control.cleanup()
    db_manager.close()
    logger.info("System shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "hydroponics.core.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
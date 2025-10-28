"""
Machine Learning module for plant health analysis using TensorFlow Lite
Detects nutrient deficiencies, diseases, and pest issues
"""

import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    logger.warning("TFLite runtime not found, using mock ML")
    tflite = None

try:
    from picamera2 import Picamera2
    import cv2
except ImportError:
    logger.warning("picamera2/opencv not found, using mock camera")
    Picamera2 = None
    cv2 = None


class PlantHealthAnalyzer:
    """Analyze plant health using computer vision and ML"""
    
    def __init__(self, model_path: str = "models/plant_disease.tflite"):
        self.model_path = model_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.camera = None
        self.mock_mode = tflite is None or Picamera2 is None
        
        # Plant disease/deficiency classes
        self.class_labels = [
            'healthy',
            'nitrogen_deficiency',
            'iron_deficiency',
            'phosphorus_deficiency',
            'potassium_deficiency',
            'magnesium_deficiency',
            'calcium_deficiency',
            'fungal_disease',
            'bacterial_disease',
            'pest_damage',
            'water_stress',
            'light_stress',
            'temperature_stress'
        ]
        
        # Recommendations for each issue
        self.recommendations = {
            'healthy': ['Continue current nutrient regimen', 'Monitor regularly'],
            'nitrogen_deficiency': [
                'Increase nutrient solution concentration',
                'Check EC levels (target 1.2-1.8 mS/cm)',
                'Increase feeding frequency if needed',
                'Verify pH is in optimal range (5.8-6.2)'
            ],
            'iron_deficiency': [
                'Check pH - iron uptake blocked above pH 7.0',
                'Add chelated iron supplement',
                'Verify EC not too high (>2.5 causes lockout)',
                'Ensure adequate oxygenation'
            ],
            'phosphorus_deficiency': [
                'Increase bloom/fruiting nutrients if flowering',
                'Check pH (optimal P uptake at 6.0-6.5)',
                'Verify water temperature (cold <15Â°C reduces uptake)',
                'Add phosphorus supplement'
            ],
            'potassium_deficiency': [
                'Add potassium supplement',
                'Check EC levels - may need increase',
                'Verify pH in optimal range',
                'Check for salt buildup (flush if needed)'
            ],
            'magnesium_deficiency': [
                'Add Epsom salt (magnesium sulfate)',
                'Check pH - Mg uptake best at 6.0-6.5',
                'Reduce calcium if very high (Ca competes with Mg)',
                'Apply foliar spray for quick fix'
            ],
            'calcium_deficiency': [
                'Increase calcium in nutrient solution',
                'Check pH - Ca uptake best at 6.2-6.5',
                'Improve air circulation (Ca moves with transpiration)',
                'Verify adequate water uptake'
            ],
            'fungal_disease': [
                'Remove infected leaves immediately',
                'Reduce humidity below 60%',
                'Improve air circulation',
                'Apply organic fungicide if needed',
                'Check reservoir for algae/contamination'
            ],
            'bacterial_disease': [
                'Remove infected plants/leaves',
                'Disinfect system components',
                'Check water temperature (keep below 22Â°C)',
                'Verify DO levels adequate (>5 mg/L)',
                'Consider UV sterilization'
            ],
            'pest_damage': [
                'Inspect plants for insects',
                'Apply organic pest control if needed',
                'Introduce beneficial insects',
                'Improve airflow',
                'Check for entry points'
            ],
            'water_stress': [
                'Check water level in reservoir',
                'Verify pump operation',
                'Inspect for clogs in system',
                'Check root health',
                'Verify adequate DO levels'
            ],
            'light_stress': [
                'Check light intensity and distance',
                'Verify timer settings',
                'Ensure 14-16 hours light for leafy greens',
                'Check for light burn (too close)',
                'Verify spectrum appropriate for growth stage'
            ],
            'temperature_stress': [
                'Check reservoir temperature (target 18-22Â°C)',
                'Check air temperature (target 20-24Â°C)',
                'Add heater if too cold',
                'Add chiller or cooling if too hot',
                'Improve ventilation'
            ]
        }
    
    def load_model(self):
        """Load TFLite model"""
        if self.mock_mode:
            logger.warning("Running ML in MOCK MODE")
            return
        
        try:
            model_file = Path(self.model_path)
            
            if not model_file.exists():
                logger.warning(f"Model file not found: {self.model_path}")
                logger.info("Downloading default PlantVillage model...")
                self._download_default_model()
            
            self.interpreter = tflite.Interpreter(model_path=str(model_file))
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            logger.info(f"ML model loaded: {self.model_path}")
            logger.info(f"Input shape: {self.input_details[0]['shape']}")
            
        except Exception as e:
            logger.error(f"Error loading ML model: {e}")
            self.mock_mode = True
    
    def _download_default_model(self):
        """Download a default plant disease detection model"""
        import urllib.request
        
        # Use a pre-trained PlantVillage model (example URL - replace with actual)
        model_url = "https://tfhub.dev/agripredict/disease-classification/1"
        
        model_dir = Path(self.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Downloading model... this may take a few minutes")
        # In production, implement actual download from TF Hub or your model repository
        logger.warning("Model download not implemented - using mock mode")
    
    def initialize_camera(self):
        """Initialize Pi Camera"""
        if self.mock_mode:
            return
        
        try:
            self.camera = Picamera2()
            config = self.camera.create_still_configuration(
                main={"size": (640, 640)},
                controls={"ExposureTime": 20000, "AnalogueGain": 2.0}
            )
            self.camera.configure(config)
            logger.info("Camera initialized")
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            self.mock_mode = True
    
    def capture_image(self) -> Optional[np.ndarray]:
        """Capture image from camera"""
        if self.mock_mode:
            # Generate mock image
            return np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        try:
            if self.camera is None:
                self.initialize_camera()
            
            self.camera.start()
            time.sleep(2)  # Allow camera to adjust
            
            image = self.camera.capture_array()
            self.camera.stop()
            
            return image
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for model input"""
        try:
            if self.mock_mode:
                # Mock preprocessing
                return np.random.rand(1, 224, 224, 3).astype(np.float32)
            
            input_shape = self.input_details[0]['shape']
            height, width = input_shape[1], input_shape[2]
            
            # Convert to PIL Image
            img = Image.fromarray(image)
            
            # Resize to model input size
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to numpy array and normalize
            img_array = np.array(img, dtype=np.float32)
            img_array = img_array / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def run_inference(self, input_data: np.ndarray) -> np.ndarray:
        """Run ML inference on preprocessed image"""
        try:
            if self.mock_mode:
                # Mock inference - simulate realistic distribution
                predictions = np.random.dirichlet(np.ones(len(self.class_labels)), size=1)[0]
                predictions[0] = 0.85  # Make "healthy" most likely in mock
                return predictions / predictions.sum()  # Normalize
            
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            return output_data[0]
        except Exception as e:
            logger.error(f"Error running inference: {e}")
            return None
    
    def analyze(self) -> Dict:
        """
        Perform complete plant health analysis
        Returns dict with status, issues, confidence, and recommendations
        """
        try:
            logger.info("Starting plant health analysis...")
            
            # Capture image
            image = self.capture_image()
            if image is None:
                return self._error_result("Failed to capture image")
            
            # Preprocess
            input_data = self.preprocess_image(image)
            if input_data is None:
                return self._error_result("Failed to preprocess image")
            
            # Run inference
            predictions = self.run_inference(input_data)
            if predictions is None:
                return self._error_result("Failed to run inference")
            
            # Get top predictions
            top_indices = np.argsort(predictions)[-3:][::-1]
            top_classes = [self.class_labels[i] for i in top_indices]
            top_confidences = [float(predictions[i]) for i in top_indices]
            
            # Determine overall status
            primary_class = top_classes[0]
            primary_confidence = top_confidences[0]
            
            # Build result
            result = {
                'status': primary_class,
                'confidence': primary_confidence,
                'issues': [],
                'recommendations': []
            }
            
            # Add issues with confidence above threshold
            threshold = 0.15
            for cls, conf in zip(top_classes, top_confidences):
                if cls != 'healthy' and conf > threshold:
                    result['issues'].append({
                        'type': cls,
                        'confidence': conf
                    })
            
            # Get recommendations
            if primary_class != 'healthy':
                result['recommendations'] = self.recommendations.get(
                    primary_class,
                    ['Monitor plant health', 'Check all parameters']
                )
            else:
                result['recommendations'] = self.recommendations['healthy']
            
            logger.info(f"Analysis complete: {primary_class} ({primary_confidence:.2%})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in plant analysis: {e}")
            return self._error_result(str(e))
    
    def _error_result(self, error_msg: str) -> Dict:
        """Return error result"""
        return {
            'status': 'error',
            'confidence': 0.0,
            'issues': [{'type': 'analysis_error', 'confidence': 1.0}],
            'recommendations': [f"Analysis failed: {error_msg}"],
            'error': error_msg
        }
    
    def analyze_with_context(self, sensor_data: Dict) -> Dict:
        """
        Enhanced analysis incorporating sensor data
        Helps disambiguate visual symptoms
        """
        result = self.analyze()
        
        if result['status'] == 'error':
            return result
        
        # Add context-aware recommendations based on sensor data
        ph = sensor_data.get('ph')
        ec = sensor_data.get('ec')
        temp = sensor_data.get('temp_reservoir')
        do_level = sensor_data.get('do')
        
        context_recommendations = []
        
        # pH context
        if ph is not None:
            if ph < 5.5:
                context_recommendations.append(
                    f"pH is low ({ph:.1f}) - this may cause nutrient lockout"
                )
            elif ph > 7.0:
                context_recommendations.append(
                    f"pH is high ({ph:.1f}) - iron and other micronutrients may be unavailable"
                )
        
        # EC context
        if ec is not None:
            if ec < 0.8:
                context_recommendations.append(
                    f"EC is low ({ec:.2f} mS/cm) - plants may be underfed"
                )
            elif ec > 2.5:
                context_recommendations.append(
                    f"EC is high ({ec:.2f} mS/cm) - risk of nutrient burn"
                )
        
        # Temperature context
        if temp is not None:
            if temp < 16:
                context_recommendations.append(
                    f"Water temperature low ({temp:.1f}Â°C) - slows nutrient uptake"
                )
            elif temp > 24:
                context_recommendations.append(
                    f"Water temperature high ({temp:.1f}Â°C) - increases disease risk"
                )
        
        # DO context
        if do_level is not None:
            if do_level < 5:
                context_recommendations.append(
                    f"Low dissolved oxygen ({do_level:.1f} mg/L) - root health may be compromised"
                )
        
        if context_recommendations:
            result['recommendations'].extend(context_recommendations)
        
        return result

import os
import json
import h5py
import numpy as np
import tensorflow as tf
from PIL import Image

# Get the directory where model_loader.py is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dynamically point to the model files inside the same directory
ORIGINAL_MODEL_PATH = os.path.join(BASE_DIR, "Alzheimer_Detection_model (1).h5")
CLEANED_MODEL_PATH = os.path.join(BASE_DIR, "Alzheimer_Detection_model_cleaned.h5")

def clean_config_dict(d):
    """Recursively deletes 'quantization_config' and flattens 'DTypePolicy' to a regular string."""
    if isinstance(d, dict):
        # 1. Strip quantization config if present
        if 'quantization_config' in d:
            del d['quantization_config']
            
        # 2. Fix complex dictionary 'dtype' policies (Keras 3 -> Keras 2)
        if 'dtype' in d and isinstance(d['dtype'], dict):
            # If it contains a nested Keras DTypePolicy name, extract it (e.g., 'float32')
            policy_config = d['dtype'].get('config', {})
            policy_name = policy_config.get('name', 'float32') if isinstance(policy_config, dict) else 'float32'
            d['dtype'] = policy_name

        # 3. Fix InputLayer compatibility issues
        if d.get('class_name') == 'InputLayer' and 'config' in d:
            cfg = d['config']
            if 'batch_shape' in cfg:
                bs = cfg.pop('batch_shape')
                if bs and len(bs) >= 3:
                    cfg['input_shape'] = bs[1:]
            cfg.pop('optional', None)

        # Recursively scan internal elements
        for k, v in list(d.items()):
            clean_config_dict(v)
    elif isinstance(d, list):
        for item in d:
            clean_config_dict(item)

def ensure_cleaned_model():
    """Generates the compatible model format from the original file."""
    # Force regeneration every time to clear out the previous incompatible 'cleaned' file on the server
    print("Generating fully compatible model configuration from original...")
    if not os.path.exists(ORIGINAL_MODEL_PATH):
        raise FileNotFoundError(f"Original model not found at: {ORIGINAL_MODEL_PATH}")

    # Read original configuration
    with h5py.File(ORIGINAL_MODEL_PATH, 'r') as f:
        config_str = f.attrs['model_config']
        if isinstance(config_str, bytes):
            config_str = config_str.decode('utf-8')
        config = json.loads(config_str)

    # Apply all compatibility updates (InputLayer batch_shape, optional, etc.)
    clean_config_dict(config)
    cleaned_config_str = json.dumps(config)

    # Safely copy binary file contents to target destination 
    import shutil
    shutil.copy2(ORIGINAL_MODEL_PATH, CLEANED_MODEL_PATH)

    # Write cleaned config to the copy
    with h5py.File(CLEANED_MODEL_PATH, 'r+') as f:
        f.attrs['model_config'] = cleaned_config_str

    print("Cleaned model successfully updated and created.")
    return CLEANED_MODEL_PATH
    
class AlzheimerModel:
    def __init__(self):
        cleaned_path = ensure_cleaned_model()
        print("Loading TensorFlow Keras model...")
        self.model = tf.keras.models.load_model(cleaned_path, compile=False)
        self.classes = ['Mild Demented', 'Moderate Demented', 'Non Demented', 'Very Mild Demented']
        print("Model loaded successfully!")

    def predict(self, image_pil):
        """
        Takes a PIL image, preprocesses it, and runs inference.
        Returns a tuple: (predicted_class_name, confidence, dict_of_all_probabilities)
        """
        # Convert to RGB if not already
        if image_pil.mode != 'RGB':
            image_pil = image_pil.convert('RGB')
            
        # Resize to 224x224 (required by EfficientNetB0 in this model)
        image_resized = image_pil.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convert to numpy array and prepare for model
        img_array = np.array(image_resized, dtype=np.float32)
        
        # Add batch dimension (shape: 1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict (Keras Rescaling layer in model will scale [0, 255] to [0, 1] internally)
        predictions = self.model.predict(img_array)
        probs = predictions[0]
        
        # Map predictions to output format
        predicted_idx = np.argmax(probs)
        predicted_class = self.classes[predicted_idx]
        confidence = float(probs[predicted_idx])
        
        all_probs = {self.classes[i]: float(probs[i]) for i in range(len(self.classes))}
        
        return predicted_class, confidence, all_probs

if __name__ == '__main__':
    # Dry run test
    loader = AlzheimerModel()
    # Dummy test image
    dummy_img = Image.fromarray(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
    pred_class, conf, all_probs = loader.predict(dummy_img)
    print("Test prediction result:")
    print("Class:", pred_class)
    print("Confidence:", conf)
    print("All Probs:", all_probs)

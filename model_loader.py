import os
import json
import h5py
import re
import numpy as np
import tensorflow as tf
from PIL import Image

# Get the directory where model_loader.py is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dynamically point to the model files inside the same directory
ORIGINAL_MODEL_PATH = os.path.join(BASE_DIR, "Alzheimer_Detection_model (1).h5")
CLEANED_MODEL_PATH = os.path.join(BASE_DIR, "Alzheimer_Detection_model_cleaned.h5")

def ensure_cleaned_model():
    """Generates the compatible model format from the original file by rewriting the JSON structure."""
    print("Generating fully compatible model configuration from original...")
    if not os.path.exists(ORIGINAL_MODEL_PATH):
        raise FileNotFoundError(f"Original model not found at: {ORIGINAL_MODEL_PATH}")

    # Read original configuration string directly
    with h5py.File(ORIGINAL_MODEL_PATH, 'r') as f:
        config_str = f.attrs['model_config']
        if isinstance(config_str, bytes):
            config_str = config_str.decode('utf-8')

    # Load into an actual Python dictionary structure to mutate safely
    config = json.loads(config_str)

    def clean_node(d):
        """Recursively walks the entire model configuration dictionary tree."""
        if isinstance(d, dict):
            # 1. Clean out the Keras 3 DTypePolicy structures
            if 'dtype' in d:
                if isinstance(d['dtype'], dict):
                    # Extract the type name (e.g., 'float32') out of the Keras 3 metadata dictionary
                    policy_config = d['dtype'].get('config', {})
                    if isinstance(policy_config, dict):
                        d['dtype'] = policy_config.get('name', 'float32')
                    else:
                        d['dtype'] = 'float32'
                elif isinstance(d['dtype'], str) and 'DTypePolicy' in d['dtype']:
                    d['dtype'] = 'float32'

            # 2. Strip quantization configs if they exist
            if 'quantization_config' in d:
                del d['quantization_config']

            # 3. Fix InputLayer compatibility parameters (Keras 3 -> Keras 2)
            if d.get('class_name') == 'InputLayer' and 'config' in d:
                cfg = d['config']
                if 'batch_shape' in cfg:
                    bs = cfg.pop('batch_shape')
                    if bs and len(bs) >= 3:
                        cfg['input_shape'] = bs[1:]
                cfg.pop('optional', None)

            # Continue deep walk
            for k, v in list(d.items()):
                clean_node(v)
        elif isinstance(d, list):
            for item in d:
                clean_node(item)

    # Clean the full configuration structural tree
    clean_node(config)
    cleaned_config_str = json.dumps(config)

    # Safely duplicate binary structural file contents
    import shutil
    shutil.copy2(ORIGINAL_MODEL_PATH, CLEANED_MODEL_PATH)

    # Re-apply the entirely converted structural architecture configuration
    with h5py.File(CLEANED_MODEL_PATH, 'r+') as f:
        f.attrs['model_config'] = cleaned_config_str.encode('utf-8')

    print("Cleaned model successfully updated and created.")
    return CLEANED_MODEL_PATH
class AlzheimerModel:
    def __init__(self):
        cleaned_path = ensure_cleaned_model()
        print("Loading TensorFlow Keras model...")
        
        # Load the updated architecture smoothly
        self.model = tf.keras.models.load_model(cleaned_path, compile=False)
            
        self.classes = ['Mild Demented', 'Moderate Demented', 'Non Demented', 'Very Mild Demented']
        print("Model loaded successfully!")

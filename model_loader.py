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

    # 1. Strip 'quantization_config' completely
    config_str = re.sub(r'"quantization_config"\s*:\s*\{[^}]*\},?', '', config_str)

    # 2. Hard-replace Keras 3 DTypePolicy dictionary blocks with a plain "float32" string
    # This targets blocks like: "dtype": {"module": "keras", "class_name": "DTypePolicy", "config": {"name": "float32"}, ...}
    config_str = re.sub(
        r'"dtype"\s*:\s*\{\s*"module"\s*:\s*"keras"\s*,\s*"class_name"\s*:\s*"DTypePolicy"[^}]*\}\s*\}', 
        '"dtype": "float32"', 
        config_str
    )
    # Also clean up standard DTypePolicy dictionaries without module definitions
    config_str = re.sub(
        r'"dtype"\s*:\s*\{\s*"class_name"\s*:\s*"DTypePolicy"[^}]*\}', 
        '"dtype": "float32"', 
        config_str
    )

    # 3. Load it back into JSON format to modify internal InputLayer properties safely
    config = json.loads(config_str)

    def fix_input_layers(d):
        if isinstance(d, dict):
            if d.get('class_name') == 'InputLayer' and 'config' in d:
                cfg = d['config']
                if 'batch_shape' in cfg:
                    bs = cfg.pop('batch_shape')
                    if bs and len(bs) >= 3:
                        cfg['input_shape'] = bs[1:]
                cfg.pop('optional', None)
            for k, v in list(d.items()):
                fix_input_layers(v)
        elif isinstance(d, list):
            for item in d:
                fix_input_layers(item)

    fix_input_layers(config)
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

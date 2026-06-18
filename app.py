import os
import io
import traceback
from flask import Flask, request, jsonify
from PIL import Image

# Import our model loader helper
from model_loader import AlzheimerModel

app = Flask(__name__, static_folder='static', static_url_path='')

# Global variable to hold the preloaded model
model_instance = None

def get_model():
    global model_instance
    if model_instance is None:
        print("Pre-loading Alzheimer Detection Model...")
        model_instance = AlzheimerModel()
    return model_instance

@app.route('/')
def index():
    """Serve the single-page application frontend."""
    return app.send_static_file('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Accepts an uploaded image file, processes it, 
    and returns model prediction probabilities.
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file uploaded. Please upload an image.'
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Empty filename. Please select a valid image file.'
        }), 400

    try:
        # Load model (ensures it is initialized)
        model = get_model()

        # Read image bytes and open using PIL
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))

        # Run inference
        predicted_class, confidence, all_probs = model.predict(image)

        return jsonify({
            'success': True,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'predictions': all_probs
        })

    except Exception as e:
        print("Error during prediction:")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f"Prediction failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Force model load at startup so users don't wait on first request
    try:
        get_model()
    except Exception as e:
        print(f"CRITICAL: Failed to load model at startup: {e}")
        traceback.print_exc()
        
    print("Starting Flask application on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=False)

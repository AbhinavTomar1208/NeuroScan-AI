# NEUROSCANAI

NEUROSCANAI is an AI-powered diagnostic assistant for Alzheimer's disease detection. It provides a user-friendly web interface for uploading brain MRI scans and delivers classification predictions across four cognitive status categories.

## Project Overview

NEUROSCANAI is built as a lightweight Flask web application with a React-style single-page frontend. It uses a pre-trained TensorFlow/Keras model to analyze MRI images and classify them into the following categories:

- `Non Demented`
- `Very Mild Demented`
- `Mild Demented`
- `Moderate Demented`

The app is designed for research and demonstration purposes and should not be used as a clinical diagnostic tool without medical validation.

## Key Features

- Image upload and drag-and-drop support
- MRI preview with scanline animation
- Quick test sample MRI cards for fast verification
- Backend API for inference using TensorFlow/Keras
- Probability breakdown and confidence score
- Clinical guidance cards for each output class

## Architecture

NEUROSCANAI consists of the following main components:

- `app.py`
  - Flask application that serves the frontend and provides `/api/predict`
  - Accepts image uploads and returns prediction output

- `run.py`
  - Pre-flight dependency check and model setup
  - Launches the Flask server and opens the browser automatically

- `model_loader.py`
  - Loads the Keras model and ensures compatibility
  - Includes logic to clean the model configuration when needed
  - Preprocesses uploaded images for inference

- `static/`
  - `index.html`: frontend UI layout and structure
  - `app.js`: frontend application logic, file upload handling, and API requests
  - `style.css`: app styling and layout rules
  - `samples/`: sample MRI images for quick testing

- Model files
  - `Alzheimer_Detection_model (1).h5`: original trained model
  - `Alzheimer_Detection_model_cleaned.h5`: cleaned copy used for loading reliably

## Requirements

The application requires Python and the following Python packages:

- `flask`
- `tensorflow`
- `keras`
- `h5py`
- `Pillow`

## Installation

1. Create a Python virtual environment (recommended):

```bash
python -m venv venv
```

2. Activate the environment:

- Windows PowerShell:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- Windows CMD:
  ```cmd
  venv\Scripts\activate.bat
  ```

3. Install dependencies:

```bash
pip install flask tensorflow keras h5py pillow
```

## Usage

1. Place the model file `Alzheimer_Detection_model (1).h5` in the project root.
2. Start the application:

```bash
python run.py
```

3. The app will automatically open in your default browser at:

```
http://127.0.0.1:5000
```

4. Upload an MRI image or choose one of the sample MRI cards to run a prediction.

## How the model is loaded

`model_loader.py` includes compatibility logic that removes unsupported metadata entries from the saved Keras model configuration before loading the model. This ensures the model can be loaded consistently across TensorFlow/Keras versions.

## Notes

- The prediction output is a probabilistic classification and should not be interpreted as a medical diagnosis.
- The frontend is designed for demonstration and analysis workflows.
- The project is ideal for AI research, prototyping, and interactive model evaluation.

## Project Structure

```
AlzheimerPred/
├── Alzheimer_Detection_model (1).h5
├── Alzheimer_Detection_model_cleaned.h5
├── README.md
├── app.py
├── model_loader.py
├── run.py
└── static/
    ├── app.js
    ├── index.html
    ├── style.css
    └── samples/
        ├── mild.png
        ├── non_demented.png
        └── very_mild.png
```
=======
# NeuroScan-AI
>>>>>>> 46f80fa19a3c77aee24aed4c39be7111f0fed017

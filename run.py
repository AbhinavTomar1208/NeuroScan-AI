import os
import sys
import time
import webbrowser
import threading

def check_dependencies():
    """Verifies that all required packages are installed."""
    required = ['flask', 'tensorflow', 'keras', 'h5py', 'PIL']
    missing = []
    for pkg in required:
        try:
            if pkg == 'PIL':
                __import__('PIL')
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)
            
    if missing:
        print("\n" + "="*50)
        print("ERROR: Missing required Python packages!")
        print("Please install them using the following command:")
        print(f"pip install {' '.join(missing)}")
        print("="*50 + "\n")
        sys.exit(1)

def open_browser():
    """Opens the web browser to the local server after a brief delay."""
    # Wait for Flask to start up
    time.sleep(2.5)
    url = "http://127.0.0.1:5000"
    print(f"\nOpening web browser to: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    print("Pre-flight check: Verifying dependencies...")
    check_dependencies()
    
    print("Pre-flight check: Checking Keras model...")
    try:
        from model_loader import ensure_cleaned_model
        ensure_cleaned_model()
    except Exception as e:
        print(f"CRITICAL ERROR preparing model: {e}")
        sys.exit(1)
        
    # Start thread to open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("Launching Flask application...")
    from app import app
    app.run(host='127.0.0.1', port=5000, debug=False)

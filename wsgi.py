import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the app.py file directly
import app as app_module

app = app_module.app

if __name__ == "__main__":
    app.run()
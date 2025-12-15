"""
Entry point for Render deployment.
This file allows Render to run the app with: uvicorn main:app
"""
import sys
from pathlib import Path

# Add the current directory to Python path so 'app' module can be imported
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

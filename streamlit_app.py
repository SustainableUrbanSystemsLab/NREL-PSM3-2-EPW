"""
Entry point for Streamlit Cloud deployment.
This file exists in the root for Streamlit Cloud compatibility.
The actual app code is in app/streamlit_app.py.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Import and run the main function
from streamlit_app import main

if __name__ == "__main__":
    main()

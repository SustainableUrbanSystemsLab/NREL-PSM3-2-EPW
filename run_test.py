import sys
from unittest.mock import patch
import streamlit.web.cli as stcli

import app.streamlit_app

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())

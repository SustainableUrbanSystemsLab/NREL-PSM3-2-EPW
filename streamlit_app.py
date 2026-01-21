import base64
import json
import pickle
import uuid
import re
import os
from datetime import datetime
from typing import Optional, Union, Any

import streamlit as st
import pandas as pd

from nrel_psm3_2_epw.assets import download_epw

# --- CONSTANTS ---
ATTRIBUTES = ('air_temperature,clearsky_dhi,clearsky_dni,clearsky_ghi,cloud_type,dew_point,dhi,dni,fill_flag,'
              'ghi,relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,'
              'wind_direction,wind_speed')
INTERVAL = '60'
UTC = 'false'
YOUR_NAME = "John+Doe"
REASON_FOR_USE = 'beta+testing'
YOUR_AFFILIATION = 'aaa'
YOUR_EMAIL = "Joe@Doe.edu"
MAILING_LIST = 'false'
LEAP_YEAR = 'false'
MIN_YEAR = 1998


def _load_api_key() -> Optional[str]:
    """
    Attempts to load the API key from various sources in order of precedence:
    1. streamlit secrets
    2. environment variable
    3. local 'api_key' file
    4. local '.env' file
    """
    # 1. Secrets
    try:
        if st.secrets.get("APIKEY"):
            return st.secrets.get("APIKEY")
    except Exception:
        pass

    # 2. Environment Variable
    api_key = os.environ.get("APIKEY")
    if api_key:
        return api_key

    cwd = os.getcwd()
    
    # 3. api_key file
    api_key_path = os.path.join(cwd, "api_key")
    if os.path.isfile(api_key_path):
        with open(api_key_path, "r") as f:
            return f.readline().strip()

    # 4. .env file
    env_path = os.path.join(cwd, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                if key.strip() == "APIKEY" and value.strip():
                    return value.strip()
    return None


def download_button(object_to_download: Any, 
                    download_filename: str, 
                    button_text: str, 
                    pickle_it: bool = False) -> Optional[str]:
    """
    Generates a link to download the given object_to_download.
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.error(f"Pickling error: {e}")
            return None
    else:
        if isinstance(object_to_download, bytes):
            pass
        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # Check if already bytes
        if isinstance(object_to_download, bytes):
            b64 = base64.b64encode(object_to_download).decode()
        else:
            b64 = base64.b64encode(object_to_download.encode()).decode()
    except Exception as e:
        st.error(f"Encoding error: {e}")
        return None

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub(r'\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br><br>'
    return dl_link


def main():
    st.markdown("""
    # NREL-PSM3-2-EPW  `v3.2.2`

    This script converts climate data from NREL to the EnergyPlus EPW format.  
    If you do not have an API key, please request one [here](https://developer.nrel.gov/signup).
    """)

    # API Key Handling
    default_api_key = _load_api_key()
    api_key_override = st.text_input(
        "Optional: provide your own API key (used if set):",
        value="",
        type="password",
    )
    
    api_key = ""
    api_key_source = "none"
    
    if api_key_override:
        api_key = api_key_override
        api_key_source = "user"
    elif default_api_key:
        api_key = default_api_key
        api_key_source = "default"
        st.caption("Using the default API key from secrets.")

    st.markdown("Please provide _Lat_, _Lon_, _Location_, and _Year_.")

    lat = st.text_input('Lat:', value=33.770)
    lon = st.text_input('Lon:', value=-84.3824)
    location = st.text_input('Location (just used to name the file):', value="Atlanta")
    year = st.text_input('Year (e.g., 2012, tmy, tmy-2024):', value="tmy")

    if st.button('Request from NREL'):
        if not api_key:
            st.error("Please provide a valid API key.")
            st.stop()

        current_year = datetime.now().year
        year_str = str(year).strip()
        
        # Basic Year Validation
        if year_str.isdigit():
            year_int = int(year_str)
            if year_int in (current_year, current_year - 1):
                st.warning(f"NREL does not provide data for the current year {year}. "
                           f"It is also unlikely that there is data availability for {year_int - 1}.")
                st.stop()
            elif year_int < MIN_YEAR:
                st.warning(f"NREL does not provide data for the year {year}. "
                           f"The earliest year data is available for is {MIN_YEAR}.")
                st.stop()
        else:
            if not year_str.lower().startswith(("tmy", "tgy", "tdy")):
                st.warning("Year must be a numeric year (>=1998) or a TMY name like tmy or tmy-2024.")
                st.stop()

        st.info("Requesting data from NREL...")

        try:
            file_name = download_epw(lon, lat, year, location, ATTRIBUTES, INTERVAL, UTC, YOUR_NAME,
                                     api_key, REASON_FOR_USE, YOUR_AFFILIATION, YOUR_EMAIL, MAILING_LIST, LEAP_YEAR)
        except Exception as exc:
            st.error(f"Request failed: {exc}")
            if api_key_source == "default":
                st.info("If this failure is related to the default API key, enter your own key above and retry.")
            st.stop()

        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                s = f.read()
                download_button_str = download_button(s, file_name, 'Download EPW')
                if download_button_str:
                    st.markdown(download_button_str, unsafe_allow_html=True)
                else:
                    st.error("Failed to generate download button.")
        else:
            st.error("Please make sure that NREL is able to deliver data for the location and year your provided.")
        st.stop()


if __name__ == "__main__":
    main()

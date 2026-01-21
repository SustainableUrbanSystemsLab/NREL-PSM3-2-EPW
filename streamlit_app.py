from nrel_psm3_2_epw.assets import download_epw 
import base64
import json
import pickle
import uuid
import re
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Draw a title and some text to the app:
'''
# NREL-PSM3-2-EPW  `v3.2.2`

This script converts climate data from NREL to the EnergyPlus EPW format.  
If you do not have an API key, please request one [here](https://developer.nrel.gov/signup).
'''

def _load_api_key():
    secret_key = None
    try:
        secret_key = st.secrets.get("APIKEY")
    except Exception:
        secret_key = None
    if secret_key:
        return secret_key

    api_key = os.environ.get("APIKEY")
    if api_key:
        return api_key

    cwd = os.getcwd()
    api_key_path = os.path.join(cwd, "api_key")
    if os.path.isfile(api_key_path):
        with open(api_key_path, "r") as api_key_file:
            return api_key_file.readline().strip()

    env_path = os.path.join(cwd, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r") as env_file:
            for line in env_file:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                if key.strip() == "APIKEY" and value.strip():
                    return value.strip()

    return None


default_api_key = _load_api_key()
api_key_override = st.text_input(
    "Optional: provide your own API key (used if set):",
    value="",
    max_chars=None,
    type="password",
)
if api_key_override:
    api_key = api_key_override
    api_key_source = "user"
elif default_api_key:
    api_key = default_api_key
    api_key_source = "default"
else:
    api_key = ""
    api_key_source = "none"

if api_key_source == "default":
    st.caption("Using the default API key from secrets.")

'''
Please provide _Lat_, _Lon_, _Location_, and _Year_.
'''

lat = st.text_input('Lat:', value=33.770, max_chars=None,  type='default')
lon = st.text_input('Lon:', value=-84.3824, max_chars=None,  type='default')
location = st.text_input('Location (just used to name the file):', value="Atlanta", max_chars=None, type='default')
year = st.text_input('Year (e.g., 2012, tmy, tmy-2024):', value="tmy", max_chars=None,  type='default')

attributes = 'air_temperature,clearsky_dhi,clearsky_dni,clearsky_ghi,cloud_type,dew_point,dhi,dni,fill_flag,ghi,' \
             'relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,' \
             'wind_direction,wind_speed'

interval = '60'
utc = 'false'
your_name = "John+Doe"
reason_for_use = 'beta+testing'
your_affiliation = 'aaa'
your_email = "Joe@Doe.edu"
mailing_list = 'false'
leap_year = 'false'


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    """
    Generates a link to download the given object_to_download.

    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.

    Returns:
    -------
    (str): the anchor tag to download object_to_download

    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')

    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

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

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link

if st.button('Request from NREL'):
    if api_key == "":
        st.write("Please provide a valid API key.")
        st.stop()

    current_year = datetime.now().year
    year_str = str(year).strip()
    if year_str.isdigit():
        year_int = int(year_str)
        if year_int in (current_year, current_year - 1):
            st.write(f"NREL does not provide data for the current year {year}. "
                     f"It is also unlikely that there is data availability for {year_int - 1}.")
            st.stop()
        elif year_int < 1998:
            st.write(f"NREL does not provide data for the year {year}. "
                     f"The earliest year data is available for is 1998.")
            st.stop()
    else:
        if not year_str.lower().startswith(("tmy", "tgy", "tdy")):
            st.write("Year must be a numeric year (>=1998) or a TMY name like tmy or tmy-2024.")
            st.stop()

    st.write("Requesting data from NREL...")

    try:
        file_name = download_epw(lon, lat, year, location, attributes, interval, utc, your_name,
                                 api_key, reason_for_use, your_affiliation, your_email, mailing_list, leap_year)
    except Exception as exc:
        st.error(f"Request failed: {exc}")
        if api_key_source == "default":
            st.info("If this failure is related to the default API key, enter your own key above and retry.")
        st.stop()

    if os.path.exists(file_name):
        with open(file_name, 'rb') as f:
            s = f.read()
            download_button_str = download_button(s, file_name, 'Download EPW')
            st.markdown(download_button_str, unsafe_allow_html=True)
    else:
        st.write("Please make sure that NREL is able to deliver data for the location and year your provided.")
    st.stop()

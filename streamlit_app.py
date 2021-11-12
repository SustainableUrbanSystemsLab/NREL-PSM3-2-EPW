from assets import download_epw
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
# NREL-PSM3-2-EPW

This script converts climate data from NREL to the EnergyPlus EPW format.  
If you do not have an API key, feel free to request one [here](https://developer.nrel.gov/signup).
'''

api_key = st.text_input('Please provide your own api key here:',
                        max_chars=None, key="2", type="password")

'''
Please provide _Lat_, _Lon_, _Location_, and _Year_.
'''

lat = st.text_input('Lat:', value=42.434269, max_chars=None, key="2", type='default')
lon = st.text_input('Lon:', value=-76.500354, max_chars=None, key="2", type='default')
location = st.text_input('Location (just used to name the file):', value="Ithaca", max_chars=None, key="2",
                         type='default')
year = st.text_input('Year:', value=2019, max_chars=None, key="2", type='default')

# lat, lon = 42.434269, -76.500354
# location = "Ithaca"
# year = '2019'
attributes = 'air_temperature,clearsky_dhi,clearsky_dni,clearsky_ghi,cloud_type,dew_point,dhi,dni,fill_flag,ghi,' \
             'relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,' \
             'wind_direction,wind_speed,ghuv-280-400,ghuv-295-385'

interval = '60'
utc = 'false'
your_name = "John+Doe"
# api_key_file = open("api_key", 'r')
# api_key = api_key_file.readline()
reason_for_use = 'beta+testing'
your_affiliation = 'aaa'
your_email = "Joe@Doe.edu"
mailing_list = 'false'
leap_year = 'true'


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

    if api_key is not "":

        currentYear = datetime.now().year
        if int(year) == currentYear:
            st.write("NREL does not provide data for the current year " + str(
                year) + ". It is also unlikely that there is data availability for " + str(int(year) - 1) + ".")
            st.stop()
        elif int(year) < 1998:
            st.write("NREL does not provide data for the year " + str(
                year) + ".")
            st.stop()

        st.write("Requesting data from NREL...")

        file_name = download_epw(float(lat), float(lon), int(year), location, attributes, interval, utc, your_name,
                                 api_key,
                                 reason_for_use,
                                 your_affiliation,
                                 your_email, mailing_list, leap_year)

        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                s = f.read()

                download_button_str = download_button(s, file_name,
                                                      'Download EPW')
                st.markdown(download_button_str, unsafe_allow_html=True)

        else:
            st.write("Please make sure that NREL is able to deliver data for the location and year your provided.")

    else:
        st.write("Please provide a valid API key.")
st.stop()

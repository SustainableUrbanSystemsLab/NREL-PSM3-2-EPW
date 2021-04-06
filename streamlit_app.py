import streamlit as st

from assets import download_epw
import base64




# Draw a title and some text to the app:
'''
# NREL-PSB3-2-EPW

Convert climate data from NREL to the EnergyPlus EPW format.
If you do not have an api key yet, feel free to request one [here](https://developer.nrel.gov/signup).
'''

api_key = st.text_input('Please provide your api key here.',  max_chars=None, key="2", type='default')

'''
Please provide Lat, Lon, Location, and Year.
'''

lat = st.text_input('Lat:', value=42.434269, max_chars=None, key="2", type='default')
lon = st.text_input('Lon:', value= -76.500354, max_chars=None, key="2", type='default')
location = st.text_input('Location:', value= "MyLocation", max_chars=None, key="2", type='default')
year = st.text_input('Year:', value = 2019, max_chars=None, key="2", type='default')



#lat, lon = 42.434269, -76.500354
#location = "Ithaca"
#year = '2019'
attributes = 'air_temperature,clearsky_dhi,clearsky_dni,clearsky_ghi,cloud_type,dew_point,dhi,dni,fill_flag,ghi,' \
             'relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,' \
             'wind_direction,wind_speed,ghuv-280-400,ghuv-295-385'

interval = '60'
utc = 'false'
your_name = "John+Doe"
#api_key_file = open("api_key", 'r')
#api_key = api_key_file.readline()
reason_for_use = 'beta+testing'
your_affiliation = 'aaa'
your_email = "Joe@Doe.edu"
mailing_list = 'false'
leap_year = 'true'

epw = None

def get_epw_download_link(file_name):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """

    b64 = base64.b64encode(file_name.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download EPW</a>'
    return href



d = "_"
file_name = str(location) + d + str(lat) + d + str(lon) + d + str(year) + '.epw'



if st.button('Download EPW file'):

    if api_key is not "":
        st.write("Retrieving data from NREL...")
        download_epw(float(lat), float(lon), int(year), location, attributes, interval, utc, your_name, api_key, reason_for_use,
                           your_affiliation,
                           your_email, mailing_list, leap_year)



    tmp_download_link = get_epw_download_link(file_name)
    st.markdown(tmp_download_link, unsafe_allow_html=True)


st.stop()

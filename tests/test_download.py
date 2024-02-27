import os
from pathlib import Path

from nrel_psm3_2_epw.assets import *

import pandas as pd


def test_download_epw():
    lat, lon = 40.755840, -73.982684
    location = "NYC"
    year = '2012'
    attributes = 'air_temperature,clearsky_dhi,clearsky_dni,clearsky_ghi,cloud_type,dew_point,dhi,dni,fill_flag,ghi,' \
                 'relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,' \
                 'wind_direction,wind_speed,ghuv-280-400,ghuv-295-385'

    interval = '60'
    utc = 'false'
    your_name = "John+Doe"

    cwd = Path.cwd()
    api_key_file_path = cwd / Path("api_key")

    api_key = None

    if api_key_file_path.is_file():
        api_key_file = open(api_key_file_path, 'r')
        api_key = api_key_file.readline().rstrip()
    else:
        api_key = os.environ['APIKEY']

    print(api_key)

    reason_for_use = 'beta+testing'
    your_affiliation = 'aaa'
    your_email = "Joe@Doe.edu"
    mailing_list = 'false'
    leap_year = 'true'

    download_epw(lon, lat, int(year), location, attributes, interval, utc, your_name,
                 api_key, reason_for_use, your_affiliation, your_email, mailing_list, leap_year)

    data = epw.EPW()
    data.read("NYC_40.75584_-73.982684_2012.epw")

    #(data.dataframe)

    assert(data.dataframe['Year'][0] == 2012)
    assert((data.dataframe['Atmospheric Station Pressure'] > 31000) & (data.dataframe['Atmospheric Station Pressure'] < 120000)).all()
    assert((data.dataframe['Dry Bulb Temperature'] > -70) & (data.dataframe['Dry Bulb Temperature'] < 70)).all()
    assert((data.dataframe['Dew Point Temperature'] > -70) & (data.dataframe['Dew Point Temperature'] < 70)).all()
    assert((data.dataframe['Relative Humidity'] >= 0) & (data.dataframe['Relative Humidity'] < 110)).all()
    assert(data.dataframe['Global Horizontal Radiation'] >= 0).all()
    assert(data.dataframe['Direct Normal Radiation'] >= 0).all()
    assert(data.dataframe['Diffuse Horizontal Radiation'] >= 0).all()
    assert((data.dataframe['Wind Direction'] >= 0) & (data.dataframe['Relative Humidity'] <= 360)).all()
    assert((data.dataframe['Wind Speed'] >= 0) & (data.dataframe['Wind Speed'] <= 40)).all()
    assert((data.dataframe['Opaque Sky Cover'] >= 0) & (data.dataframe['Opaque Sky Cover'] <= 10)).all()
    assert((data.dataframe['Total Sky Cover'] >= 0) & (data.dataframe['Total Sky Cover'] <= 10)).all()


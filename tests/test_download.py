from nrel_psm3_2_epw.assets import *
from pathlib import Path
import os


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

    if api_key_file_path.is_file():
        api_key_file = open(api_key_file_path, 'r')
        api_key = api_key_file.readline().rstrip()
    else:
        api_key = os.environ['APIKEY']

    reason_for_use = 'beta+testing'
    your_affiliation = 'aaa'
    your_email = "Joe@Doe.edu"
    mailing_list = 'false'
    leap_year = 'true'

    download_epw(lat, lon, year, location, attributes, interval, utc, your_name, api_key, reason_for_use, your_affiliation,
                 your_email, mailing_list, leap_year)

    data = epw.EPW()
    data.read("NYC_40.75584_-73.982684_2012.epw")

    assert(data.dataframe['Year'][0] == 2012)

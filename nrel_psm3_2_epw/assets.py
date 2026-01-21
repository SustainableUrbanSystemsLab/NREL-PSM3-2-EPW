from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from datetime import datetime

import numpy as np
import pandas as pd
import requests

from . import epw


GOES_AGGREGATED_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb-GOES-aggregated-v4-0-0-download.csv"
GOES_TMY_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb-GOES-tmy-v4-0-0-download.csv"


def _sanitize_url(raw_url):
    parts = urlsplit(raw_url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != "api_key"]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _is_tmy_name(value):
    name = str(value).strip().lower()
    return name.startswith(("tmy", "tgy", "tdy"))


def download_epw(lon, lat, year, location, attributes, interval, utc, your_name, api_key, reason_for_use,
                 your_affiliation, your_email, mailing_list, leap_year):
    year_str = str(year).strip()
    year_int = int(year_str) if year_str.isdigit() else None
    is_tmy = _is_tmy_name(year)

    if not is_tmy:
        if year_int is None:
            raise ValueError("Year must be numeric unless using a TMY/TGY/TDY dataset.")
        current_year = datetime.now().year
        if year_int in (current_year, current_year - 1):
            raise Exception("NREL does not provide data for the current year " + str(
                year) + ". It is also unlikely that there is data availability for " + str(year_int - 1) + ".")

    if is_tmy and str(interval) != "60":
        interval = "60"

    url = GOES_TMY_URL if is_tmy else GOES_AGGREGATED_URL

    payload = {
        "names": year,
        "leap_day": leap_year,
        "interval": interval,
        "utc": utc,
        "full_name": your_name,
        "email": your_email,
        "affiliation": your_affiliation,
        "mailing_list": mailing_list,
        "reason": reason_for_use,
        "attributes": attributes,
        "wkt": f"POINT({lon} {lat})",
        "api_key": api_key,
    }

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    r = None
    all_data = None

    try:
        r = requests.request("GET", url, params=payload, headers=headers, timeout=20)
        payload["api_key"] = "REDACTED"
        api_key = None
        if not r.ok:
            safe_url = _sanitize_url(r.url)
            try:
                error_payload = r.json()
            except ValueError:
                error_payload = {"message": r.text.strip()}
            raise RuntimeError(f"NREL request failed ({r.status_code}) for {safe_url}: {error_payload}")

        # Return just the first 2 lines to get metadata:
        all_data = pd.read_csv(r.url)

        if all_data is None:
            raise RuntimeError("Could not retrieve any data")

    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        raise
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        raise
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)
        raise

    data_rows = all_data.shape[0] - 2
    if data_rows <= 0:
        raise RuntimeError("No data rows returned from NREL")

    # Take first row for metadata
    metadata = all_data.iloc[0, :]

    # Return all but first 2 lines of csv to get data:
    df = all_data.iloc[2:, :]
    df.columns = all_data.iloc[1]
    time_columns = ["Year", "Month", "Day", "Hour", "Minute"]
    if is_tmy:
        if not all(col in df.columns for col in time_columns):
            raise RuntimeError("TMY response missing expected timestamp columns")
        time_frame = df[time_columns].apply(pd.to_numeric, errors="coerce")
        datetimes = pd.to_datetime(time_frame, errors="coerce")
        if datetimes.isnull().any():
            raise RuntimeError("Could not parse timestamps from TMY response")
        datetimes = pd.DatetimeIndex(datetimes)
    else:
        datetimes = pd.date_range('01/01/' + str(year_int),
                                  periods=data_rows, freq='h')

    # Set the time index in the pandas dataframe:
    df = df.set_index(datetimes)

    # See metadata for specified properties, e.g., timezone and elevation
    timezone = elevation = location_id = "Could not be retrieved from NREL"
    if metadata is not None:
        timezone, elevation, location_id = metadata[
            'Local Time Zone'], metadata['Elevation'], metadata['Location ID']

    out = epw.EPW()
    out.headers = {
        'LOCATION': [location,
                     'STATE',
                     'COUNTRY',
                     'NREL PSM v4 SOURCE',
                     'XXX',
                     lat,
                     lon,
                     timezone,
                     elevation],
        'DESIGN CONDITIONS': ['1',
                              'This is ficticious header data to make the EPW readable',
                              '',
                              'Heating',
                              '1',
                              '3.8',
                              '4.9',
                              '-3.7',
                              '2.8',
                              '10.7',
                              '-1.2',
                              '3.4',
                              '11.2',
                              '12.9',
                              '12.1',
                              '11.6',
                              '12.2',
                              '2.2',
                              '150',
                              'Cooling',
                              '8',
                              '8.5',
                              '28.3',
                              '17.2',
                              '25.7',
                              '16.7',
                              '23.6',
                              '16.2',
                              '18.6',
                              '25.7',
                              '17.8',
                              '23.9',
                              '17',
                              '22.4',
                              '5.9',
                              '310',
                              '16.1',
                              '11.5',
                              '19.9',
                              '15.3',
                              '10.9',
                              '19.2',
                              '14.7',
                              '10.4',
                              '18.7',
                              '52.4',
                              '25.8',
                              '49.8',
                              '23.8',
                              '47.6',
                              '22.4',
                              '2038',
                              'Extremes',
                              '12.8',
                              '11.5',
                              '10.6',
                              '22.3',
                              '1.8',
                              '34.6',
                              '1.5',
                              '2.3',
                              '0.8',
                              '36.2',
                              '-0.1',
                              '37.5',
                              '-0.9',
                              '38.8',
                              '-1.9',
                              '40.5'],
        'TYPICAL/EXTREME PERIODS': ['6',
                                    'Summer - Week Nearest Max Temperature For Period',
                                    'Extreme',
                                    '8/ 1',
                                    '8/ 7',
                                    'Summer - Week Nearest Average Temperature For Period',
                                    'Typical',
                                    '9/ 5',
                                    '9/11',
                                    'Winter - Week Nearest Min Temperature For Period',
                                    'Extreme',
                                    '2/ 1',
                                    '2/ 7',
                                    'Winter - Week Nearest Average Temperature For Period',
                                    'Typical',
                                    '2/15',
                                    '2/21',
                                    'Autumn - Week Nearest Average Temperature For Period',
                                    'Typical',
                                    '12/ 6',
                                    '12/12',
                                    'Spring - Week Nearest Average Temperature For Period',
                                    'Typical',
                                    '5/29',
                                    '6/ 4'],
        'GROUND TEMPERATURES': ['3',
                                '.5',
                                '',
                                '',
                                '',
                                '10.86',
                                '10.57',
                                '11.08',
                                '11.88',
                                '13.97',
                                '15.58',
                                '16.67',
                                '17.00',
                                '16.44',
                                '15.19',
                                '13.51',
                                '11.96',
                                '2',
                                '',
                                '',
                                '',
                                '11.92',
                                '11.41',
                                '11.51',
                                '11.93',
                                '13.33',
                                '14.60',
                                '15.61',
                                '16.15',
                                '16.03',
                                '15.32',
                                '14.17',
                                '12.95',
                                '4',
                                '',
                                '',
                                '',
                                '12.79',
                                '12.27',
                                '12.15',
                                '12.31',
                                '13.10',
                                '13.96',
                                '14.74',
                                '15.28',
                                '15.41',
                                '15.10',
                                '14.42',
                                '13.60'],
        'HOLIDAYS/DAYLIGHT SAVINGS': ['No', '0', '0', '0'],
        'COMMENTS 1': ['NREL PSM3 DATA'],
        'COMMENTS 2': ['https://bit.ly/NREL--PSM3-2-EPW'],
        'DATA PERIODS': ['1', '1', 'Data', 'Sunday', ' 1/ 1', '12/31']
    }

    # Actual file starts here

    # st.write(df.index)
    epw_df = pd.DataFrame()
    epw_df['Year'] = datetimes.year.astype(int)
    epw_df['Month'] = datetimes.month.astype(int)
    epw_df['Day'] = datetimes.day.astype(int)
    epw_df['Hour'] = datetimes.hour.astype(int) + 1
    epw_df['Minute'] = datetimes.minute.astype(int)
    epw_df['Data Source and Uncertainty Flags'] = "'Created with NREL PSM v4 input data'"

    epw_df['Dry Bulb Temperature'] = df['Temperature'].values.flatten()

    epw_df['Dew Point Temperature'] = df['Dew Point'].values.flatten()

    epw_df['Relative Humidity'] = df['Relative Humidity'].values.flatten()

    epw_df['Atmospheric Station Pressure'] = df['Pressure'].astype(int).multiply(100).values.flatten()
    epw_df['Extraterrestrial Horizontal Radiation'] = 9999
    #
    epw_df['Extraterrestrial Direct Normal Radiation'] = 9999
    #
    epw_df['Horizontal Infrared Radiation Intensity'] = 9999
    #
    epw_df['Global Horizontal Radiation'] = df['GHI'].values.flatten()
    epw_df['Direct Normal Radiation'] = df['DNI'].values.flatten()
    epw_df['Diffuse Horizontal Radiation'] = df['DHI'].values.flatten()

    epw_df['Global Horizontal Illuminance'] = 999999
    epw_df['Direct Normal Illuminance'] = 999999
    epw_df['Diffuse Horizontal Illuminance'] = 999999
    epw_df['Zenith Luminance'] = 9999

    epw_df['Wind Direction'] = df['Wind Direction'].values.flatten()
    epw_df['Wind Speed'] = df['Wind Speed'].values.flatten()

    epw_df['Total Sky Cover'] = df['Cloud Type'].values.flatten()
    # used if Horizontal IR Intensity missing
    epw_df['Opaque Sky Cover'] = df['Cloud Type'].values.flatten()
    #

    epw_df['Visibility'] = 9999
    epw_df['Ceiling Height'] = 99999
    epw_df['Present Weather Observation'] = ''
    #
    epw_df['Present Weather Codes'] = ''
    epw_df['Precipitable Water'] = df['Precipitable Water'].values.flatten()
    epw_df['Aerosol Optical Depth'] = .999
    #
    epw_df['Snow Depth'] = 999
    epw_df['Days Since Last Snowfall'] = 99
    epw_df['Albedo'] = df['Surface Albedo'].values.flatten()
    #

    epw_df['Liquid Precipitation Depth'] = 999
    epw_df['Liquid Precipitation Quantity'] = 99

    out.dataframe = epw_df

    d = "_"
    file_name = str(location) + d + str(lat) + d + \
                str(lon) + d + str(year) + '.epw'

    out.write(file_name)
    print("Success: File", file_name, "written")

    return file_name

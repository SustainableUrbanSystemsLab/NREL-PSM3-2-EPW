import numpy as np
import pandas as pd
import requests
from epw import epw
import sys



def download_epw(lat, lon,year, location,  attributes,  interval, utc, your_name, api_key,reason_for_use, your_affiliation, your_email, mailing_list, leap_year):
    # Declare url string
    url = 'https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?wkt=POINT({lon}%20{lat})&names={year}&leap_day={leap}&interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation={affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&attributes={attr}'.format(
            year=year, lat=lat, lon=lon, leap=leap_year, interval=interval, utc=utc, name=your_name, email=your_email, mailing_list=mailing_list, affiliation=your_affiliation,
            reason=reason_for_use, api=api_key, attr=attributes)

    df = pd.DataFrame()

    try:
        r = requests.get(url, timeout=3)
        r.raise_for_status()
        # Return all but first 2 lines of csv to get data:
        df = pd.read_csv(
                'https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.csv?wkt=POINT({lon}%20{lat})&names={year}&leap_day={leap}&interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation={affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&attributes={attr}'.format(
                        year=year, lat=lat, lon=lon, leap=leap_year, interval=interval, utc=utc, name=your_name, email=your_email, mailing_list=mailing_list, affiliation=your_affiliation,
                        reason=reason_for_use, api=api_key, attr=attributes), skiprows=2)
        # Set the time index in the pandas dataframe:
        df = df.set_index(pd.date_range('1/1/{yr}'.format(yr=year), freq=interval + 'Min', periods=525600 / int(interval)))

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        [print(err) for err in r.json()['errors']]
        sys.exit("There is an issue with the input url")
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    a = epw()
    epw_df = a.dataframe
    a.headers = {'LOCATION'                 : [location,
                                               'XX',
                                               'XX',
                                               'NREL PSM3',
                                               'XXX',
                                               lat,
                                               lon,
                                               'XX',
                                               'XXX'],
                 'DESIGN CONDITIONS'        : ['1',
                                               'Climate Design Data 2009 ASHRAE Handbook',
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
                 'TYPICAL/EXTREME PERIODS'  : ['6',
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
                 'GROUND TEMPERATURES'      : ['3',
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
                 'COMMENTS 1'               : ['NREL PSM3 DATA'],
                 'COMMENTS 2'               : [''],
                 'DATA PERIODS'             : ['1', '1', 'Data', 'Sunday', ' 1/ 1', '12/31']}

    # Actual file starts here

    epw_df['Dry Bulb Temperature'] = df['Temperature'].values.flatten()

    epw_df['Dew Point Temperature'] = df['Dew Point'].values.flatten()

    epw_df['Relative Humidity'] = df['Relative Humidity'].values.flatten()

    epw_df['Atmospheric Station Pressure'] = df['Pressure'].values.flatten()
    epw_df['Extraterrestrial Horizontal Radiation'] = np.array(np.zeros(8760)).astype(int)
    #
    epw_df['Extraterrestrial Direct Normal Radiation'] = np.array(np.zeros(8760)).astype(int)
    #
    epw_df['Horizontal Infrared Radiation Intensity'] = np.array(np.zeros(8760)).astype(int)
    #
    epw_df['Global Horizontal Radiation'] = df['GHI'].values.flatten()
    epw_df['Direct Normal Radiation'] = df['DNI'].values.flatten()
    epw_df['Diffuse Horizontal Radiation'] = df['DHI'].values.flatten()

    epw_df['Global Horizontal Illuminance'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Direct Normal Illuminance'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Diffuse Horizontal Illuminance'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Zenith Luminance'] = np.array(np.zeros(8760)).astype(int)

    epw_df['Wind Direction'] = df['Wind Direction'].values.flatten().astype(int)
    epw_df['Wind Speed'] = df['Wind Speed'].values.flatten()

    epw_df['Total Sky Cover'] = df['Cloud Type'].values.flatten()
    # used if Horizontal IR Intensity missing
    epw_df['Opaque Sky Cover'] = df['Cloud Type'].values.flatten()
    #

    epw_df['Visibility'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Ceiling Height'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Present Weather Observation'] = np.array(np.zeros(8760)).astype(int)
    #
    epw_df['Present Weather Codes'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Precipitable Water'] = df['Precipitable Water'].values.flatten()
    epw_df['Aerosol Optical Depth'] = np.array(np.zeros(8760)).astype(int)
    #
    epw_df['Snow Depth'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Days Since Last Snowfall'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Albedo'] = df['Surface Albedo'].values.flatten()
    #

    epw_df['Liquid Precipitation Depth'] = np.array(np.zeros(8760)).astype(int)
    epw_df['Liquid Precipitation Quantity'] = np.array(np.zeros(8760)).astype(int)

    file_name = str(location) + "_" + str(year) + '.epw'
    a.write(file_name)
    print("Success: File",file_name, "written")

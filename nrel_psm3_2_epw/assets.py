from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from datetime import datetime
import re
from typing import Union, Any

import pandas as pd
import requests

from . import epw
from .constants import GOES_AGGREGATED_URL, GOES_TMY_URL, DEFAULT_HEADERS


def _sanitize_url(raw_url: str) -> str:
    """Removes the api_key from a URL for safe logging."""
    parts = urlsplit(raw_url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != "api_key"]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _is_tmy_name(value: Any) -> bool:
    """Checks if the year value indicates a TMY dataset."""
    name = str(value).strip().lower()
    return name.startswith(("tmy", "tgy", "tdy"))


def download_epw(
    lon: Union[str, float],
    lat: Union[str, float],
    year: Union[str, int],
    location: str,
    attributes: str,
    interval: str,
    utc: str,
    your_name: str,
    api_key: str,
    reason_for_use: str,
    your_affiliation: str,
    your_email: str,
    mailing_list: str,
    leap_year: str,
) -> str:
    """
    Downloads climate data from NREL and converts it to an EPW file.

    Returns:
        str: The filename of the created EPW file.
    """
    year_str = str(year).strip()
    year_int = int(year_str) if year_str.isdigit() else None
    is_tmy = _is_tmy_name(year)

    if not is_tmy:
        if year_int is None:
            raise ValueError("Year must be numeric unless using a TMY/TGY/TDY dataset.")
        current_year = datetime.now().year
        if year_int in (current_year, current_year - 1):
            raise Exception(
                f"NREL does not provide data for the current year {year}. "
                f"It is also unlikely that there is data availability for {year_int - 1}."
            )

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

    headers = {"content-type": "application/x-www-form-urlencoded", "cache-control": "no-cache"}

    try:
        r = requests.request("GET", url, params=payload, headers=headers, timeout=20)
        # Redact API key for safety before potentially logging payload/url in an error
        payload["api_key"] = "REDACTED"

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
        datetimes = pd.date_range(f"01/01/{year_int}", periods=data_rows, freq="h")

    # Set the time index in the pandas dataframe:
    df = df.set_index(datetimes)

    # See metadata for specified properties, e.g., timezone and elevation
    timezone = elevation = "0"
    if metadata is not None:
        timezone = metadata.get("Local Time Zone", "0")
        elevation = metadata.get("Elevation", "0")

    out = epw.EPW()
    out.headers = DEFAULT_HEADERS.copy()

    # Update location-specific headers
    out.headers["LOCATION"] = [
        location,
        "STATE",
        "COUNTRY",
        "NREL PSM v4 SOURCE",
        "XXX",
        str(lat),
        str(lon),
        str(timezone),
        str(elevation),
    ]

    epw_df = pd.DataFrame()
    epw_df["Year"] = datetimes.year.astype(int)
    epw_df["Month"] = datetimes.month.astype(int)
    epw_df["Day"] = datetimes.day.astype(int)
    epw_df["Hour"] = datetimes.hour.astype(int) + 1
    epw_df["Minute"] = datetimes.minute.astype(int)
    epw_df["Data Source and Uncertainty Flags"] = "'Created with NREL PSM v4 input data'"

    epw_df["Dry Bulb Temperature"] = df["Temperature"].values.flatten()
    epw_df["Dew Point Temperature"] = df["Dew Point"].values.flatten()
    epw_df["Relative Humidity"] = df["Relative Humidity"].values.flatten()
    epw_df["Atmospheric Station Pressure"] = df["Pressure"].astype(int).multiply(100).values.flatten()

    # Missing/Placeholder values
    epw_df["Extraterrestrial Horizontal Radiation"] = 9999
    epw_df["Extraterrestrial Direct Normal Radiation"] = 9999
    epw_df["Horizontal Infrared Radiation Intensity"] = 9999

    epw_df["Global Horizontal Radiation"] = df["GHI"].values.flatten()
    epw_df["Direct Normal Radiation"] = df["DNI"].values.flatten()
    epw_df["Diffuse Horizontal Radiation"] = df["DHI"].values.flatten()

    epw_df["Global Horizontal Illuminance"] = 999999
    epw_df["Direct Normal Illuminance"] = 999999
    epw_df["Diffuse Horizontal Illuminance"] = 999999
    epw_df["Zenith Luminance"] = 9999

    epw_df["Wind Direction"] = df["Wind Direction"].values.flatten()
    epw_df["Wind Speed"] = df["Wind Speed"].values.flatten()

    epw_df["Total Sky Cover"] = df["Cloud Type"].values.flatten()
    epw_df["Opaque Sky Cover"] = df["Cloud Type"].values.flatten()

    epw_df["Visibility"] = 9999
    epw_df["Ceiling Height"] = 99999
    epw_df["Present Weather Observation"] = ""
    epw_df["Present Weather Codes"] = ""
    epw_df["Precipitable Water"] = df["Precipitable Water"].values.flatten()
    epw_df["Aerosol Optical Depth"] = 0.999
    epw_df["Snow Depth"] = 999
    epw_df["Days Since Last Snowfall"] = 99
    epw_df["Albedo"] = df["Surface Albedo"].values.flatten()
    epw_df["Liquid Precipitation Depth"] = 999
    epw_df["Liquid Precipitation Quantity"] = 99

    out.dataframe = epw_df

    d = "_"

    # Sanitize location: replace non-alphanumeric characters with underscores
    safe_location = re.sub(r"[^a-zA-Z0-9]", "_", str(location))

    # Format lat/lon to 2 decimal places if possible
    try:
        lat_str = f"{float(lat):.2f}"
    except (ValueError, TypeError):
        lat_str = str(lat)

    try:
        lon_str = f"{float(lon):.2f}"
    except (ValueError, TypeError):
        lon_str = str(lon)

    current_year = datetime.now().year
    file_name = f"{safe_location}{d}{lat_str}{d}{lon_str}{d}{str(year)}{d}{current_year}.epw"

    out.write(file_name)
    print("Success: File", file_name, "written")

    return file_name

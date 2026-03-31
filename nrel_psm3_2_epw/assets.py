import io
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from datetime import datetime
import re
from typing import Union, Any

import pandas as pd
import requests
from . import epw
from .constants import GOES_AGGREGATED_URL, GOES_TMY_URL, DEFAULT_HEADERS

# Bolt Optimization: Maintain a global session to reuse TCP connections
_session = requests.Session()


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
        # Bolt Optimization: Use the session object to reuse the underlying TCP/TLS connection.
        # This speeds up repeated requests to the NREL API by avoiding repeated handshakes.
        r = _session.request("GET", url, params=payload, headers=headers, timeout=20)
        # Redact API key for safety before potentially logging payload/url in an error
        payload["api_key"] = "REDACTED"

        if not r.ok:
            safe_url = _sanitize_url(r.url)
            try:
                error_payload = r.json()
            except ValueError:
                error_payload = {"message": r.text.strip()}
            raise RuntimeError(f"NREL request failed ({r.status_code}) for {safe_url}: {error_payload}")

        # Parse the downloaded content instead of requesting the URL again
        # This prevents pandas from making a second HTTP request for the same data

        # Bolt Optimization:
        # Instead of parsing the entire CSV in one go, which causes pandas to infer
        # all columns as string `object` dtypes due to the first metadata row, we
        # parse the metadata and actual dataset separately. This allows pandas to
        # use highly optimized C parsing to natively infer the correct numeric types
        # (int64/float64) for the dataset, massively speeding up DataFrame construction
        # and downstream calculations.
        metadata_df = pd.read_csv(io.BytesIO(r.content), nrows=1)
        df = pd.read_csv(io.BytesIO(r.content), skiprows=2)

        if df is None or metadata_df is None:
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

    data_rows = df.shape[0]
    if data_rows <= 0:
        raise RuntimeError("No data rows returned from NREL")

    # Take first row for metadata
    metadata = metadata_df.iloc[0, :]

    time_columns = ["Year", "Month", "Day", "Hour", "Minute"]
    if not all(col in df.columns for col in time_columns):
        raise RuntimeError("NREL response missing expected timestamp columns")

    # Bolt Optimization:
    # Both TMY and aggregated APIs return native time columns natively parsed as int64 via `skiprows=2`.
    # By extracting these values directly, we completely bypass synthetic `pd.date_range` generation
    # and expensive property extractions (`.year`, `.month`, etc.) on the pandas DatetimeIndex, saving CPU cycles.
    try:
        # Using `.to_numpy(dtype=int)` directly safely validates and casts the series to raw numpy arrays
        # much faster than `df[time_columns].astype(int)`.
        year_vals = df["Year"].to_numpy(dtype=int)
        month_vals = df["Month"].to_numpy(dtype=int)
        day_vals = df["Day"].to_numpy(dtype=int)
        hour_vals = df["Hour"].to_numpy(dtype=int)
        minute_vals = df["Minute"].to_numpy(dtype=int)
    except ValueError:
        raise RuntimeError("Could not parse timestamps from NREL response")

    # Bolt Optimization: Avoid setting the DatetimeIndex on the pandas DataFrame
    # since we immediately extract raw `.values` below. This saves a full copy
    # of the 8760xN DataFrame.

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

    # Bolt Optimization:
    # Avoid pandas `.to_numpy()` and pandas `.multiply()` overhead during DataFrame construction.
    # Using underlying numpy `.values` directly, computing operations on the numpy arrays,
    # and preventing implicit dataframe copying via `copy=False` further halves construction time.
    # Furthermore, using `.values` on `pd.DatetimeIndex` properties avoids expensive pandas dispatch and cast overhead.
    # Bolt Optimization: The "Pressure" array is natively inferred as int64. We remove .astype(int) to avoid redundant array duplication.
    epw_df = pd.DataFrame(
        {
            "Year": year_vals,
            "Month": month_vals,
            "Day": day_vals,
            "Hour": hour_vals + 1,
            "Minute": minute_vals,
            "Data Source and Uncertainty Flags": "'Created with NREL PSM v4 input data'",
            "Dry Bulb Temperature": df["Temperature"].values,
            "Dew Point Temperature": df["Dew Point"].values,
            "Relative Humidity": df["Relative Humidity"].values,
            "Atmospheric Station Pressure": (df["Pressure"].values * 100),
            "Extraterrestrial Horizontal Radiation": 9999,
            "Extraterrestrial Direct Normal Radiation": 9999,
            "Horizontal Infrared Radiation Intensity": 9999,
            "Global Horizontal Radiation": df["GHI"].values,
            "Direct Normal Radiation": df["DNI"].values,
            "Diffuse Horizontal Radiation": df["DHI"].values,
            "Global Horizontal Illuminance": 999999,
            "Direct Normal Illuminance": 999999,
            "Diffuse Horizontal Illuminance": 999999,
            "Zenith Luminance": 9999,
            "Wind Direction": df["Wind Direction"].values,
            "Wind Speed": df["Wind Speed"].values,
            "Total Sky Cover": df["Cloud Type"].values,
            "Opaque Sky Cover": df["Cloud Type"].values,
            "Visibility": 9999,
            "Ceiling Height": 99999,
            "Present Weather Observation": "",
            "Present Weather Codes": "",
            "Precipitable Water": df["Precipitable Water"].values,
            "Aerosol Optical Depth": 0.999,
            "Snow Depth": 999,
            "Days Since Last Snowfall": 99,
            "Albedo": df["Surface Albedo"].values,
            "Liquid Precipitation Depth": 999,
            "Liquid Precipitation Quantity": 99,
        },
        copy=False,
    )

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

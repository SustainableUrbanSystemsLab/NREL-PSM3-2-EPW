import os
from datetime import datetime

import pytest

from nrel_psm3_2_epw import epw
from nrel_psm3_2_epw.assets import download_epw


def test_download_epw(tmp_path, monkeypatch):
    api_key = os.environ.get("APIKEY")
    if not api_key:
        pytest.skip("APIKEY not set")

    lat, lon = 40.755840, -73.982684
    location = "NYC"
    year = "tmy"
    attributes = (
        "air_temperature,clearsky_dhi,clearsky_dni,clearsky_ghi,cloud_type,dew_point,dhi,dni,fill_flag,ghi,"
        "relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,"
        "wind_direction,wind_speed"
    )

    interval = "60"
    utc = "false"
    your_name = "John+Doe"

    reason_for_use = "beta+testing"
    your_affiliation = "aaa"
    your_email = "Joe@Doe.edu"
    mailing_list = "false"
    leap_year = "false"

    monkeypatch.chdir(tmp_path)
    download_epw(
        lon,
        lat,
        year,
        location,
        attributes,
        interval,
        utc,
        your_name,
        api_key,
        reason_for_use,
        your_affiliation,
        your_email,
        mailing_list,
        leap_year,
    )

    # Find the generated EPW file (filename format changed with refactoring)
    epw_files = list(tmp_path.glob("*.epw"))
    assert len(epw_files) == 1, f"Expected 1 EPW file, found {len(epw_files)}: {epw_files}"
    epw_file = epw_files[0]

    data = epw.EPW()
    data.read(epw_file)

    assert data.dataframe.shape[0] == 8760
    assert data.dataframe["Year"].between(1998, datetime.now().year).all()
    assert (
        (data.dataframe["Atmospheric Station Pressure"] > 31000)
        & (data.dataframe["Atmospheric Station Pressure"] < 120000)
    ).all()
    assert ((data.dataframe["Dry Bulb Temperature"] > -70) & (data.dataframe["Dry Bulb Temperature"] < 70)).all()
    assert ((data.dataframe["Dew Point Temperature"] > -70) & (data.dataframe["Dew Point Temperature"] < 70)).all()
    assert ((data.dataframe["Relative Humidity"] >= 0) & (data.dataframe["Relative Humidity"] < 110)).all()
    assert (data.dataframe["Global Horizontal Radiation"] >= 0).all()
    assert (data.dataframe["Direct Normal Radiation"] >= 0).all()
    assert (data.dataframe["Diffuse Horizontal Radiation"] >= 0).all()
    assert ((data.dataframe["Wind Direction"] >= 0) & (data.dataframe["Relative Humidity"] <= 360)).all()
    assert ((data.dataframe["Wind Speed"] >= 0) & (data.dataframe["Wind Speed"] <= 40)).all()
    assert ((data.dataframe["Opaque Sky Cover"] >= 0) & (data.dataframe["Opaque Sky Cover"] <= 10)).all()
    assert ((data.dataframe["Total Sky Cover"] >= 0) & (data.dataframe["Total Sky Cover"] <= 10)).all()

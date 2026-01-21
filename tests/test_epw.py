import pandas as pd

from nrel_psm3_2_epw import epw


def test_epw_read_write_roundtrip(tmp_path):
    names = [
        "Year",
        "Month",
        "Day",
        "Hour",
        "Minute",
        "Data Source and Uncertainty Flags",
        "Dry Bulb Temperature",
        "Dew Point Temperature",
        "Relative Humidity",
        "Atmospheric Station Pressure",
        "Extraterrestrial Horizontal Radiation",
        "Extraterrestrial Direct Normal Radiation",
        "Horizontal Infrared Radiation Intensity",
        "Global Horizontal Radiation",
        "Direct Normal Radiation",
        "Diffuse Horizontal Radiation",
        "Global Horizontal Illuminance",
        "Direct Normal Illuminance",
        "Diffuse Horizontal Illuminance",
        "Zenith Luminance",
        "Wind Direction",
        "Wind Speed",
        "Total Sky Cover",
        "Opaque Sky Cover",
        "Visibility",
        "Ceiling Height",
        "Present Weather Observation",
        "Present Weather Codes",
        "Precipitable Water",
        "Aerosol Optical Depth",
        "Snow Depth",
        "Days Since Last Snowfall",
        "Albedo",
        "Liquid Precipitation Depth",
        "Liquid Precipitation Quantity",
    ]

    row0 = {name: idx for idx, name in enumerate(names)}
    row1 = {name: idx + 1 for idx, name in enumerate(names)}
    row0["Year"] = 2020
    row1["Year"] = 2021

    frame = pd.DataFrame([row0, row1], columns=names)

    out = epw.EPW()
    out.headers = {
        "LOCATION": ["City", "State"],
        "DATA PERIODS": ["1"],
    }
    out.dataframe = frame

    file_path = tmp_path / "sample.epw"
    out.write(file_path)

    loaded = epw.EPW()
    loaded.read(file_path)

    assert loaded.headers["LOCATION"] == ["City", "State"]
    assert loaded.dataframe.shape == (2, len(names))
    assert loaded.headers["LOCATION"] == ["City", "State"]
    assert loaded.dataframe.shape == (2, len(names))
    assert loaded.dataframe["Year"].tolist() == [2020, 2021]


def test_epw_read_handles_empty_lines(tmp_path):
    # Manually create a file with empty lines in the header
    file_path = tmp_path / "empty_lines.epw"
    with open(file_path, "w") as f:
        f.write("LOCATION,City,State\n")
        f.write("\n")  # Empty line to trigger the 'if not row: continue' check
        f.write("DATA PERIODS,1\n")
        f.write("2020,1,1,1,0,SOURCE,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n")

    loaded = epw.EPW()
    loaded.read(file_path)

    assert loaded.headers["LOCATION"] == ["City", "State"]
    assert loaded.headers["DATA PERIODS"] == ["1"]
    assert not loaded.dataframe.empty

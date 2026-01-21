import pandas as pd
import pytest
import requests

from nrel_psm3_2_epw import assets


class DummyResponse:
    def __init__(self, ok, url, status_code=200, json_data=None, json_error=None, text=""):
        self.ok = ok
        self.url = url
        self.status_code = status_code
        self._json_data = json_data
        self._json_error = json_error
        self.text = text

    def json(self):
        if self._json_error:
            raise self._json_error
        return self._json_data


def _build_all_data(row_count, include_time_columns=True, bad_time=False):
    columns = [
        "Local Time Zone",
        "Elevation",
        "Location ID",
        "Year",
        "Month",
        "Day",
        "Hour",
        "Minute",
        "Temperature",
        "Dew Point",
        "Relative Humidity",
        "Pressure",
        "GHI",
        "DNI",
        "DHI",
        "Wind Direction",
        "Wind Speed",
        "Cloud Type",
        "Precipitable Water",
        "Surface Albedo",
    ]
    if not include_time_columns:
        columns = [col for col in columns if col not in {"Year", "Month", "Day", "Hour", "Minute"}]

    metadata = {col: "" for col in columns}
    metadata["Local Time Zone"] = -5
    metadata["Elevation"] = 20
    metadata["Location ID"] = 123

    header_row = {col: col for col in columns}

    data_rows = []
    for idx in range(row_count):
        row = {col: 0 for col in columns}
        row.update({
            "Temperature": 20 + idx,
            "Dew Point": 10 + idx,
            "Relative Humidity": 50,
            "Pressure": 1013,
            "GHI": 200,
            "DNI": 500,
            "DHI": 100,
            "Wind Direction": 180,
            "Wind Speed": 3,
            "Cloud Type": 1,
            "Precipitable Water": 1.5,
            "Surface Albedo": 0.2,
        })
        if include_time_columns:
            if bad_time and idx == 0:
                row.update({"Year": "bad", "Month": "bad", "Day": "bad", "Hour": "bad", "Minute": "bad"})
            else:
                row.update({"Year": 2012, "Month": 1, "Day": 1, "Hour": idx % 24, "Minute": 0})
        data_rows.append(row)

    return pd.DataFrame([metadata, header_row] + data_rows, columns=columns)


def _mock_read_csv(all_data):
    def _reader(*_args, **_kwargs):
        return all_data.copy()

    return _reader


def test_sanitize_url_removes_api_key():
    url = "https://example.com/data?api_key=secret&names=2012"
    sanitized = assets._sanitize_url(url)
    assert "api_key" not in sanitized
    assert "names=2012" in sanitized


@pytest.mark.parametrize("value,expected", [
    ("tmy", True),
    ("TMY-2024", True),
    ("tgy-2024", True),
    ("tdy-2024", True),
    ("2012", False),
])
def test_is_tmy_name(value, expected):
    assert assets._is_tmy_name(value) is expected


def test_download_epw_rejects_non_numeric_year():
    with pytest.raises(ValueError):
        assets.download_epw(0, 0, "not-a-year", "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_rejects_current_year():
    current_year = str(assets.datetime.now().year)
    with pytest.raises(Exception):
        assets.download_epw(0, 0, current_year, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_non_ok_json(monkeypatch):
    response = DummyResponse(
        ok=False,
        url="https://example.com/data?api_key=secret&names=2012",
        status_code=400,
        json_data={"errors": ["bad request"]},
    )

    monkeypatch.setattr(assets.requests, "request", lambda *args, **kwargs: response)

    with pytest.raises(RuntimeError) as exc:
        assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")

    assert "api_key" not in str(exc.value)


def test_download_epw_non_ok_non_json(monkeypatch):
    response = DummyResponse(
        ok=False,
        url="https://example.com/data?api_key=secret",
        status_code=404,
        json_error=ValueError("no json"),
        text="Not Found",
    )

    monkeypatch.setattr(assets.requests, "request", lambda *args, **kwargs: response)

    with pytest.raises(RuntimeError) as exc:
        assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")

    assert "Not Found" in str(exc.value)


def test_download_epw_request_connection_error(monkeypatch):
    def _raise(*_args, **_kwargs):
        raise requests.exceptions.ConnectionError("fail")

    monkeypatch.setattr(assets.requests, "request", _raise)

    with pytest.raises(requests.exceptions.ConnectionError):
        assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_request_timeout_error(monkeypatch):
    def _raise(*_args, **_kwargs):
        raise requests.exceptions.Timeout("fail")

    monkeypatch.setattr(assets.requests, "request", _raise)

    with pytest.raises(requests.exceptions.Timeout):
        assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_request_other_error(monkeypatch):
    def _raise(*_args, **_kwargs):
        raise requests.exceptions.RequestException("fail")

    monkeypatch.setattr(assets.requests, "request", _raise)

    with pytest.raises(requests.exceptions.RequestException):
        assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_no_data_rows(monkeypatch):
    all_data = _build_all_data(0)

    response = DummyResponse(ok=True, url="https://example.com/data")
    monkeypatch.setattr(assets.requests, "request", lambda *args, **kwargs: response)
    monkeypatch.setattr(assets.pd, "read_csv", _mock_read_csv(all_data))

    with pytest.raises(RuntimeError, match="No data rows"):
        assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_read_csv_none(monkeypatch):
    response = DummyResponse(ok=True, url="https://example.com/data")
    monkeypatch.setattr(assets.requests, "request", lambda *args, **kwargs: response)
    monkeypatch.setattr(assets.pd, "read_csv", lambda *_args, **_kwargs: None)

    with pytest.raises(RuntimeError, match="Could not retrieve any data"):
        assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_tmy_missing_time_columns(monkeypatch):
    all_data = _build_all_data(2, include_time_columns=False)

    response = DummyResponse(ok=True, url="https://example.com/data")
    monkeypatch.setattr(assets.requests, "request", lambda *args, **kwargs: response)
    monkeypatch.setattr(assets.pd, "read_csv", _mock_read_csv(all_data))

    with pytest.raises(RuntimeError, match="missing expected timestamp columns"):
        assets.download_epw(0, 0, "tmy", "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_tmy_bad_time(monkeypatch):
    all_data = _build_all_data(2, include_time_columns=True, bad_time=True)

    response = DummyResponse(ok=True, url="https://example.com/data")
    monkeypatch.setattr(assets.requests, "request", lambda *args, **kwargs: response)
    monkeypatch.setattr(assets.pd, "read_csv", _mock_read_csv(all_data))

    with pytest.raises(RuntimeError, match="Could not parse timestamps"):
        assets.download_epw(0, 0, "tmy", "Loc", "ghi", "60", "false",
                            "Name", "key", "reason", "aff", "email", "false", "false")


def test_download_epw_tmy_interval_coerced(monkeypatch, tmp_path):
    all_data = _build_all_data(2, include_time_columns=True)

    captured = {}

    def _fake_request(_method, _url, params=None, **_kwargs):
        captured["params"] = params
        return DummyResponse(ok=True, url="https://example.com/data")

    monkeypatch.setattr(assets.requests, "request", _fake_request)
    monkeypatch.setattr(assets.pd, "read_csv", _mock_read_csv(all_data))
    monkeypatch.chdir(tmp_path)

    assets.download_epw(0, 0, "tmy", "Loc", "ghi", "30", "false",
                        "Name", "key", "reason", "aff", "email", "false", "false")

    assert captured["params"]["interval"] == "60"
    assert (tmp_path / "Loc_0_0_tmy.epw").exists()


def test_download_epw_numeric_year_success(monkeypatch, tmp_path):
    all_data = _build_all_data(3, include_time_columns=True)

    captured = {}

    def _fake_request(_method, url, params=None, **_kwargs):
        captured["url"] = url
        captured["params"] = params
        return DummyResponse(ok=True, url="https://example.com/data")

    monkeypatch.setattr(assets.requests, "request", _fake_request)
    monkeypatch.setattr(assets.pd, "read_csv", _mock_read_csv(all_data))
    monkeypatch.chdir(tmp_path)

    assets.download_epw(0, 0, 2012, "Loc", "ghi", "60", "false",
                        "Name", "key", "reason", "aff", "email", "false", "false")

    assert captured["url"] == assets.GOES_AGGREGATED_URL
    assert (tmp_path / "Loc_0_0_2012.epw").exists()

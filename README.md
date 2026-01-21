# NREL-PSM3-2-EPW
 A script that writes out epw files from NREL Physical Solar Model (PSM) v3.2.2

# Demo

- [Link to demo](https://nrel-psm3-2-epw.streamlit.app/)

# How to use locally

- Create a virtual environment and install dependencies with uv:
  - `uv venv .venv`
  - `uv sync --extra dev`
- Place your [API key](https://developer.nrel.gov/signup/) in a file called `api_key` in the tests directory or export it as `APIKEY`.
- Make adjustments to `tests/test_download.py` and run the file or run tests with `uv run pytest`.
- For GOES TMY data, use `names` like `tmy`, `tmy-2024`, `tgy-2024`, or `tdy-2024`. Numeric years use the GOES aggregated dataset.

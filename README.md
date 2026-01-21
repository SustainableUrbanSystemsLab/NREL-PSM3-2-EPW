# NREL-PSM3-2-EPW

[![Build-Test](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/actions/workflows/build-test.yml/badge.svg)](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/actions/workflows/build-test.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nrel-psm3-2-epw.streamlit.app/)
[![Version](https://img.shields.io/badge/version-v4.0.0-blue)](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/releases)



A script and Streamlit app that writes out EPW files from NREL Physical Solar Model (PSM) v3.2.2 (and v4.0.0 API).

## Features

-   **EPW Conversion**: Converts NREL solar data to EnergyPlus Weather format.
-   **Streamlit App**: User-friendly interface for downloading data.
-   **Secure**: API keys are managed via Streamlit secrets and verified with hash checks.
-   **Modern Stack**: Built with `uv` for dependency management and `ruff` for code quality.

## Project Structure

-   `app/`: Contains the Streamlit application code.
    -   `streamlit_app.py`: Main entry point.
    -   `.streamlit/secrets.toml`: (Not committed) Stores your API key.
-   `nrel_psm3_2_epw/`: Core transformation logic.
-   `tests/`: Unit tests (100% coverage).

## How to Run Locally

1.  **Install dependencies with uv**:
    ```bash
    uv sync --extra dev
    ```

2.  **Configure API Key**:
    -   Create `app/.streamlit/secrets.toml`:
        ```toml
        APIKEY = "YOUR_NREL_API_KEY"
        ```
    -   *Note: The app verifies the default API key integrity.*

3.  **Run the App**:
    ```bash
    uv run streamlit run app/streamlit_app.py
    ```
    *(Windows users can use `run_streamlit.bat`)*

4.  **Run Tests**:
    ```bash
    uv run pytest
    ```

5.  **Lint & Format**:
    ```bash
    uv run ruff check --fix .
    uv run ruff format .
    ```

## Demo

-   [Link to demo](https://nrel-psm3-2-epw.streamlit.app/)

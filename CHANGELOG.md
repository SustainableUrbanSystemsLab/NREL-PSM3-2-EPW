# CHANGELOG


## v0.2.0 (2026-03-11)

### Features

- Read version dynamically from package metadata
  ([`cf2d01a`](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/commit/cf2d01aef82a394dc1cf8d3e64106b2ca1e59f26))

Replace hardcoded "4.0.0" version in the Streamlit UI and User-Agent header with the installed
  package version via importlib.metadata. This ensures the displayed version stays in sync with
  semantic-release.

https://claude.ai/code/session_01SqjYWGRjhsP5CdjNCVyqRQ


## v0.1.0 (2026-03-11)

### Bug Fixes

- Use standard python build in semantic release
  ([`b5822b1`](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/commit/b5822b1ee44c3e16597bf536afbb362e416f4914))

The python-semantic-release GitHub Action runs in its own Docker container where uv is not
  available. Replace `uv build` with `pip install build && python -m build` which works in the
  container.

https://claude.ai/code/session_01SqjYWGRjhsP5CdjNCVyqRQ

### Chores

- Add semantic release workflow and configuration
  ([`12a81da`](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/commit/12a81da9ed5391f4710f056b919bbbc11791f2ce))

Add python-semantic-release to project dependencies and configure it in pyproject.toml to handle
  automatic version bumping and release creation when merging to main. Also add a new GitHub Actions
  workflow for this purpose.

Co-authored-by: kastnerp <1919773+kastnerp@users.noreply.github.com>

### Features

- Add resources for visualizing EPW files online
  ([`14675a6`](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/commit/14675a6c501bcde0eba9200cdbcb2457a744b038))

Adds links to EPWvis and CBE Clima Tool after a successful EPW file download to help users visualize
  their data.

Co-authored-by: kastnerp <1919773+kastnerp@users.noreply.github.com>

- Add reverse geocoding to streamlit map
  ([`e4fdc35`](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/commit/e4fdc35967f02882ecd2584d1c21c75a913f1b6f))

- Added `requests` dependency to fetch location names from OpenStreetMap Nominatim API. -
  Implemented `get_location_name` with `@st.cache_data` to optimize Streamlit reruns. - Updated the
  map interaction to automatically populate the 'Location' input with the clicked location's name.

Co-authored-by: google-labs-jules[bot] <161369871+google-labs-jules[bot]@users.noreply.github.com>

- **ui**: Add visual feedback and disabled state to NREL request button
  ([`d2532b9`](https://github.com/SustainableUrbanSystemsLab/NREL-PSM3-2-EPW/commit/d2532b9ff0975fe0b09f9b9934c08f8e49d76fab))

Co-authored-by: kastnerp <1919773+kastnerp@users.noreply.github.com>

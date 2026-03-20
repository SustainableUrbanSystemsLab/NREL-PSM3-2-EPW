## 2024-05-23 - Avoid premature optimization
**Learning:** Avoid premature optimization of cold paths and optimizations that make code unreadable.
**Action:** Measure first, optimize second. Keep code readable.

## 2026-03-06 - Double HTTP Requests Anti-Pattern
**Learning:** Found an anti-pattern where an HTTP request is made using `requests.get` to validate parameters and then `pandas.read_csv(r.url)` is called with the resulting URL. This causes pandas to silently make a second full HTTP request to download the exact same data, wasting bandwidth, latency, and API limits.
**Action:** When a library like pandas accepts a URL or a file-like object, pass `io.BytesIO(response.content)` from the validated `requests.Response` object instead of the URL string to prevent redundant network calls.

## 2026-03-07 - Pandas DataFrame Initialization Optimization
**Learning:** Initializing a pandas DataFrame column-by-column after creating an empty DataFrame `pd.DataFrame()` is highly inefficient due to repeated internal re-allocations. Furthermore, using `.values.flatten()` on columns can trigger unnecessary memory copies compared to `.to_numpy()`.
**Action:** When constructing a new DataFrame from existing series or arrays, initialize it with a single dictionary `pd.DataFrame({"col": data})`. Additionally, prefer `.to_numpy()` over `.values.flatten()` for extracting raw array values without copying. This can lead to a 4x speedup during dataframe construction.

## 2026-03-08 - Pandas DataFrame Further Memory Initialization Optimization
**Learning:** While using a single dictionary for `pd.DataFrame(...)` initialization is faster than column-by-column, using pandas series methods like `.to_numpy()` or `.astype(int).multiply(100).to_numpy()` still incurs overhead from pandas series method dispatching. Directly accessing the underlying NumPy array using `.values` and performing NumPy-level operations (e.g., `df["Pressure"].values.astype(int) * 100`) avoids this. Moreover, using `copy=False` in the `pd.DataFrame` constructor prevents redundant data copying from the input dictionary arrays.
**Action:** When speed is critical during DataFrame construction from other pandas columns, use `.values` and perform mathematical operations at the NumPy array level, and include `copy=False` in the `pd.DataFrame(...)` constructor. This can halve construction time compared to `.to_numpy()`.

## 2026-03-09 - Pandas read_csv with mixed string/numeric column typing bottleneck
**Learning:** Found a major performance bottleneck where parsing a CSV file that has string metadata rows at the top along with the numeric dataset forces pandas to infer all dataset columns as `object` (string) dtypes. This completely nullifies pandas' numeric C-level vectorization and significantly slows down DataFrame construction and numerical operations.
**Action:** When working with CSVs containing leading metadata rows (like the NREL API), use `pd.read_csv` twice. First with `nrows=1` to get metadata, and second with `skiprows=2` to read the dataset natively as `float64`/`int64`. This restores pandas' numeric inference and leads to >2x performance gains.

## 2026-03-12 - Pandas DatetimeIndex Property Overhead
**Learning:** Accessing properties like `.year`, `.month`, `.hour` on a `pd.DatetimeIndex` and calling `.astype(int)` returns a pandas `Index` (or Series) object and incurs significant pandas dispatch overhead during repeated operations or DataFrame construction.
**Action:** Append `.values` (e.g., `datetimes.year.values`) when extracting these properties. This yields a raw NumPy `int32` array immediately, completely avoiding the `.astype(int)` cast and pandas dispatch overhead, speeding up array creation by ~25-30%.

## 2024-03-13 - Optimize EPW File Parsing by Removing Redundant I/O Passes
**Learning:** `EPW.read()` originally iterated through the file twice using `csv.reader` (once for headers, once for the data start index) before handing off to `pd.read_csv`. For large EPW files (8760+ rows), Python-level CSV iteration overhead can be a bottleneck.
**Action:** When parsing files that require metadata extraction before vectorized loading, extract all necessary metadata (headers, first data row index) in a single Python pass. Passing the pre-computed `skiprows` index directly to `pd.read_csv` halves the preliminary iteration overhead.

## 2026-03-14 - Unused DataFrame Re-indexing Overhead
**Learning:** Calling `df.set_index()` right before constructing a new DataFrame using `df["Col"].values` creates an entirely unnecessary, complete memory copy of the original 8760-row DataFrame. Furthermore, redundant cast operations like `.astype(float).astype(int)` inside the inner loop double the cast time.
**Action:** When mapping DataFrame values to a new DataFrame using `.values`, avoid modifying the original DataFrame structure (like setting indexes) unless the index is strictly required for alignment or subsequent vectorized operations. Also, since `read_csv` correctly infers numerical data types after bypassing metadata rows, redundant `.astype(float)` casts on numerical columns should be removed to speed up execution.

## 2026-03-15 - Unnecessary pandas datetime parsing overhead
**Learning:** For TMY datasets, using `pd.to_datetime` and `pd.DatetimeIndex` on the `Year`, `Month`, `Day`, `Hour`, `Minute` columns is an unnecessary overhead, because the DataFrame is loaded natively via C-engine with correct numeric types. The timestamp validation can be performed using `.astype(int)`, which validates and correctly formats everything in a fraction of the time.
**Action:** When time columns in a pandas DataFrame are already available as integer columns (e.g. from `skiprows=2` loading), bypass `pd.to_datetime` entirely and directly use `.values` on the numeric columns or `.astype(int).values` when some level of verification is needed. This skips the significant overhead of pandas' datetime dispatch mechanisms and datetime index creation.

## 2026-03-17 - Prevent `st_folium` from triggering full app reruns
**Learning:** By default, `streamlit-folium` returns a full dictionary of map states (including `bounds`, `zoom`, `center`). This causes the entire Streamlit Python script to unnecessarily rerun every time the user pans or zooms the map in the browser, wasting significant server CPU and causing UI lag. Furthermore, instantiating `folium.Map(...)` inside the render function creates new HTML representations and forces the frontend to rebuild the map iframe.
**Action:** Always add `returned_objects=["last_clicked"]` (or other strictly needed keys) to `st_folium` to limit websocket state updates to actual interactions. Additionally, wrap the `folium.Map` instantiation in an `@st.cache_resource` function so the iframe state is preserved across unrelated app interactions.

## 2026-03-22 - Pandas to_csv overhead
**Learning:** For relatively simple DataFrame-to-CSV writes without custom headers or index constraints, `pandas.to_csv()` involves heavy string formatting overhead. My benchmarks demonstrated that extracting raw numpy arrays via `df.values.tolist()` and passing them to the built-in python `csvwriter.writerows()` can cut the write time by more than half (e.g., from ~92ms to ~54ms per 8760x35 EPW table).
**Action:** When speed is critical and the CSV format allows, replace `df.to_csv(...)` with the standard Python library `csv.writer` and `csvwriter.writerows(df.values.tolist())`. Note this applies mostly when appending data to an already opened file descriptor with existing manual headers.

## 2026-03-22 - HTTP Keep-Alive for API Requests
**Learning:** Re-instantiating `requests.request()` for every API call does not take advantage of HTTP keep-alive, meaning a full TCP connection and TLS handshake are required every time. By utilizing a global `requests.Session()` within the module, we can keep the connection open, resulting in more than a 2x reduction in latency for repeated requests to the same server (from ~431ms down to ~218ms).
**Action:** When making multiple or repeated HTTP requests to the same domain (especially when TLS is involved), always use a `requests.Session()` to pool the underlying connection.

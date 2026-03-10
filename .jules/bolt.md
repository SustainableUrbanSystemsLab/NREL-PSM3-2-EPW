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

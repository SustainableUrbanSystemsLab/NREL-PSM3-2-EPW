content = """    # Update lat/lon from map click if available
    if map_data and map_data.get("last_clicked"):
        default_lat = map_data["last_clicked"]["lat"]
        default_lon = map_data["last_clicked"]["lng"]

        # Reverse geocode the location
        loc_name = get_location_name(default_lat, default_lon)
        if loc_name != "Unknown Location":
            default_location = loc_name
"""

replace = """    # Update lat/lon from map click if available
    if map_data and map_data.get("last_clicked"):
        default_lat = map_data["last_clicked"]["lat"]
        default_lon = map_data["last_clicked"]["lng"]

        # Reverse geocode the location
        loc_name = get_location_name(default_lat, default_lon)
        if loc_name != "Unknown Location":
            default_location = loc_name

        # UX Improvement: Provide subtle toast feedback when a new location is clicked on the map
        click_id = f"{default_lat}-{default_lon}"
        if st.session_state.get("last_map_click") != click_id:
            st.session_state["last_map_click"] = click_id
            if loc_name != "Unknown Location":
                st.toast(f"Location updated to **{loc_name}**", icon="📍")
            else:
                st.toast(f"Location updated to coordinates: {default_lat:.4f}, {default_lon:.4f}", icon="📍")
"""

with open("app/streamlit_app.py", "r") as f:
    orig = f.read()

new_content = orig.replace(content, replace)

with open("app/streamlit_app.py", "w") as f:
    f.write(new_content)

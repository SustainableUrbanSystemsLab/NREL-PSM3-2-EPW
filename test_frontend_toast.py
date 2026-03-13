from playwright.sync_api import sync_playwright


def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        page.wait_for_timeout(3000)

        # Streamlit folium usually embeds the map in an iframe
        iframe_element = page.locator("iframe[title='streamlit_folium.st_folium']").first
        iframes = page.frames
        for frame in iframes:
            if "localhost" in frame.url or "127.0.0.1" in frame.url:  # Find the right iframe
                try:
                    frame.locator(".leaflet-container").click(position={"x": 200, "y": 200})
                    break
                except Exception:
                    pass

        # Wait for the toast to appear
        page.wait_for_selector("[data-testid='stToast']", timeout=10000)
        page.screenshot(path="verification_toast3.png")
        browser.close()


if __name__ == "__main__":
    verify_frontend()

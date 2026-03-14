from playwright.sync_api import sync_playwright, expect
import time

def test_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")

        # wait for app to load
        page.wait_for_selector("text=NREL-PSM3-2-EPW")

        # Find the Year input field and fill it with an invalid value
        year_input = page.locator("input[aria-label='Year']")
        year_input.fill("1997")
        year_input.press("Enter")

        # Wait a moment for Streamlit to rerender
        time.sleep(2)

        # Take a screenshot
        page.screenshot(path="verification.png")
        browser.close()

if __name__ == "__main__":
    test_frontend()

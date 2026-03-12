import os
from playwright.sync_api import sync_playwright

def test_validation_ux():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the Streamlit app
            page.goto("http://localhost:8501")

            # Wait for the app to load
            page.wait_for_selector("text=NREL-PSM3-2-EPW")

            # Find the Year input field and fill it with an invalid year
            year_input = page.locator('input[aria-label="Year"]')
            year_input.fill("1990")
            year_input.press("Enter")

            # Wait a moment for Streamlit to rerun
            page.wait_for_timeout(2000)

            # Check if the "Request from NREL" button is disabled
            button = page.locator('button', has_text="Request from NREL").first

            # Take a screenshot showing the button state
            # Hover over the button to show the tooltip if possible
            button.hover(force=True)
            page.wait_for_timeout(1000)

            # Make sure we have a directory for verification
            os.makedirs("/home/jules/verification", exist_ok=True)

            page.screenshot(path="/home/jules/verification/validation_ux3.png")
            print("Screenshot taken at /home/jules/verification/validation_ux3.png")

        except Exception as e:
            print(f"Error during verification: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_validation_ux()

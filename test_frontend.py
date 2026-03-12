from playwright.sync_api import sync_playwright

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        page.wait_for_timeout(5000)
        page.screenshot(path="verification.png")
        browser.close()

if __name__ == "__main__":
    verify_frontend()

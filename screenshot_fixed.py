from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        page.goto("http://localhost:8501")
        page.wait_for_timeout(5000)
        page.screenshot(path="screenshot_fixed.png")
        browser.close()

run()

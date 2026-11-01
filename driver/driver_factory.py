from playwright.sync_api import sync_playwright, Browser, Page, Playwright

class DriverFactory:
    @staticmethod
    def create_driver(browser_name: str, _headless: bool = True):
        """
        Returns: (page, playwright) tuple for proper cleanup
        """
        playwright = sync_playwright().start()
        
        browser_name = browser_name.lower()
        
        if browser_name == "chrome":
            browser = playwright.chromium.launch(headless=_headless)
        elif browser_name in ["edge", "msedge"]:
            browser = playwright.chromium.launch(headless=_headless, channel="msedge")
        elif browser_name == "firefox":
            browser = playwright.firefox.launch(headless=_headless)
        else:
            playwright.stop()
            raise ValueError(f"Browser '{browser_name}' is not supported.")

        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        return page, playwright 
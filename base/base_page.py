import logging
from playwright.sync_api import Page, Locator
from typing import Optional

class BasePage:
    """
    Base Page Object с встроенным логгером.
    Все Page Objects наследуются от этого класса.
    """
    
    def __init__(self, page: Page, logger: logging.Logger):
        """
        Args:
            page: Playwright Page instance
            logger: Logger instance from test fixture
        """
        self.page = page
        self.logger = logger
    
    def navigate(self, url: str):
        """Navigate to URL with logging"""
        self.logger.info(f"📍 Navigating to: {url}")
        self.page.goto(url)
        self.logger.debug(f"✓ Page loaded: {self.page.url}")
    
    def click_element(self, selector: str, description: str = None):
        """Click element with logging"""
        desc = description or selector
        self.logger.info(f"🖱️ Clicking: {desc}")
        
        try:
            self.page.click(selector)
            self.logger.debug(f"✓ Clicked successfully: {desc}")
        except Exception as e:
            self.logger.error(f"❌ Failed to click: {desc}")
            self.logger.error(f"Error: {str(e)}")
            raise
    
    def fill_input(self, selector: str, text: str, description: str = None):
        """Fill input field with logging"""
        desc = description or selector
        self.logger.info(f"⌨️ Filling '{desc}' with: {text}")
        
        try:
            self.page.fill(selector, text)
            self.logger.debug(f"✓ Filled successfully: {desc}")
        except Exception as e:
            self.logger.error(f"❌ Failed to fill: {desc}")
            raise
    
    def get_text(self, selector: str, description: str = None) -> str:
        """Get element text with logging"""
        desc = description or selector
        self.logger.debug(f"📖 Reading text from: {desc}")
        
        try:
            text = self.page.locator(selector).text_content()
            self.logger.debug(f"✓ Text retrieved: '{text}'")
            return text
        except Exception as e:
            self.logger.error(f"❌ Failed to get text from: {desc}")
            raise
    
    def wait_for_element(self, selector: str, timeout: int = 30000, description: str = None):
        """Wait for element with logging"""
        desc = description or selector
        self.logger.debug(f"⏳ Waiting for element: {desc} (timeout: {timeout}ms)")
        
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.logger.debug(f"✓ Element appeared: {desc}")
        except Exception as e:
            self.logger.error(f"❌ Element did not appear: {desc}")
            raise
    
    def take_screenshot(self, name: str):
        """Take screenshot with logging"""
        self.logger.info(f"📸 Taking screenshot: {name}")
        screenshot_path = f"screenshots/{name}.png"
        self.page.screenshot(path=screenshot_path)
        self.logger.debug(f"✓ Screenshot saved: {screenshot_path}")
        return screenshot_path
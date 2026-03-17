
import logging
from base.base_page import BasePage
from playwright.sync_api import Page


LOGIN_URL = "https://signin.ebay.com/signin/"

class LoginPage(BasePage):
    
    def __init__(self, page: Page, logger: logging.Logger):
        super().__init__(page, logger)   

    def login(self, username, password ):
        self.logger.info(f"🔐 Logging in as: {username}")
        self.navigate(self.LOGIN_URL)
        
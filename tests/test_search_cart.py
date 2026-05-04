import pytest
import allure
from pages.login_page import LoginPage
from utils.config_reader import ConfigReader

@allure.feature("eBay Search")
@allure.story("Search with price filter")
def test_search_items_under_price(page):

    page.logger.info("="*60)
    page.logger.info("TEST: Search items under price")
    page.logger.info("="*60)
    
    username = ConfigReader.get_ebay_username()
    password = ConfigReader.get_ebay_password()


    login_page = LoginPage(page, page.logger)
    
    # Navigate to eBay
    login_page.login(username,password)
    
    
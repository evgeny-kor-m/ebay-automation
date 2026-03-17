import pytest
import allure
from pages.login_page import LoginPage

@allure.feature("eBay Search")
@allure.story("Search with price filter")
def test_search_items_under_price(page):

    page.logger.info("="*60)
    page.logger.info("TEST: Search items under price")
    page.logger.info("="*60)
    

    login_page = LoginPage(page, page.logger)
    
    # Navigate to eBay
    login_page.login()
    
    
import pytest
import allure
from pages.search_page import SearchPage

@allure.feature("eBay Search")
@allure.story("Search with price filter")
def test_search_items_under_price(page):
    """
    Test: Search for items under specific price
    
    Args:
        page: Playwright page fixture with attached logger
    """
    # page.logger уже доступен из fixture
    page.logger.info("="*60)
    page.logger.info("TEST: Search items under price")
    page.logger.info("="*60)
    
    # Создаём Page Object с логгером
    search_page = SearchPage(page, page.logger)
    
    # Navigate to eBay
    search_page.navigate("https://www.ebay.com")
    
    # Search for shoes
    search_page.search_for("shoes")
    
    # Apply price filter
    search_page.apply_price_filter(max_price=220)
    
    # Get results
    urls = search_page.get_search_results(limit=5)
    
    # Assertions
    assert len(urls) > 0, "No search results found"
    page.logger.info(f"✅ Test passed: Found {len(urls)} results")
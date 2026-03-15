from base.base_page import BasePage
from playwright.sync_api import Page
import logging

class SearchPage(BasePage):
    """
    Page Object для страницы поиска eBay.
    Наследует логгер от BasePage.
    """
    
    # Локаторы
    SEARCH_INPUT = "#gh-ac"
    SEARCH_BUTTON = "#gh-btn"
    PRICE_MIN_INPUT = "input[name='_udlo']"
    PRICE_MAX_INPUT = "input[name='_udhi']"
    PRICE_SUBMIT = "button[aria-label='Submit price range']"
    SEARCH_RESULTS = ".s-item"
    RESULT_TITLE = ".s-item__title"
    RESULT_PRICE = ".s-item__price"
    RESULT_LINK = ".s-item__link"
    NEXT_PAGE_BUTTON = "a.pagination__next"
    
    def __init__(self, page: Page, logger: logging.Logger):
        """
        Args:
            page: Playwright Page instance
            logger: Logger from test fixture
        """
        super().__init__(page, logger)  # ← Передаём в BasePage
        self.logger.info("🔍 SearchPage initialized")
    
    def search_for(self, query: str):
        """Perform search with logging"""
        self.logger.info(f"🔎 Searching for: '{query}'")
        
        self.fill_input(self.SEARCH_INPUT, query, "Search input")
        self.click_element(self.SEARCH_BUTTON, "Search button")
        
        # Wait for results
        self.wait_for_element(self.SEARCH_RESULTS, description="Search results")
        self.logger.info(f"✓ Search completed for: '{query}'")
    
    def apply_price_filter(self, max_price: int, min_price: int = 0):
        """Apply price filter if available"""
        self.logger.info(f"💰 Applying price filter: ${min_price} - ${max_price}")
        
        try:
            # Check if price filter exists
            if self.page.locator(self.PRICE_MAX_INPUT).is_visible():
                if min_price > 0:
                    self.fill_input(self.PRICE_MIN_INPUT, str(min_price), "Min price")
                
                self.fill_input(self.PRICE_MAX_INPUT, str(max_price), "Max price")
                self.click_element(self.PRICE_SUBMIT, "Submit price filter")
                
                self.logger.info(f"✓ Price filter applied: ${min_price}-${max_price}")
            else:
                self.logger.warning("⚠️ Price filter not available on this page")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not apply price filter: {str(e)}")
    
    def get_search_results(self, limit: int = 5) -> list:
        """
        Extract search results URLs
        
        Args:
            limit: Maximum number of results to extract
            
        Returns:
            List of product URLs
        """
        self.logger.info(f"📋 Extracting up to {limit} search results")
        
        results = []
        items = self.page.locator(self.SEARCH_RESULTS).all()
        
        self.logger.debug(f"Found {len(items)} items on page")
        
        for i, item in enumerate(items[:limit]):
            try:
                link = item.locator(self.RESULT_LINK).get_attribute("href")
                title = item.locator(self.RESULT_TITLE).text_content()
                price = item.locator(self.RESULT_PRICE).text_content()
                
                results.append(link)
                self.logger.debug(f"  [{i+1}] {title} - {price}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to extract item {i+1}: {str(e)}")
        
        self.logger.info(f"✓ Extracted {len(results)} results")
        return results
    
    def has_next_page(self) -> bool:
        """Check if next page button exists"""
        try:
            is_visible = self.page.locator(self.NEXT_PAGE_BUTTON).is_visible()
            self.logger.debug(f"Next page button visible: {is_visible}")
            return is_visible
        except:
            return False
    
    def go_to_next_page(self):
        """Navigate to next page"""
        self.logger.info("➡️ Going to next page")
        self.click_element(self.NEXT_PAGE_BUTTON, "Next page button")
        self.wait_for_element(self.SEARCH_RESULTS, description="Next page results")
---
name: write-page-object
description: Write a new Page Object class following the project's POM architecture
---

# Write Page Object

## Purpose

Create a new page object class that models user interactions with a specific page/component of the eBay application.

## Template

```python
import logging
import allure
from base.base_page import BasePage

class {PageName}(BasePage):
    """Models interactions with the {page description}"""
    
    # Define locators as class-level constants
    ELEMENT_LOCATOR = "css_selector_or_xpath"
    BUTTON_LOCATOR = "css_selector_or_xpath"
    
    def __init__(self, page, logger: logging.Logger):
        super().__init__(page, logger)
    
    @allure.step("Perform action")
    def perform_action(self, parameter: str) -> str:
        """
        Perform a specific user action
        
        Args:
            parameter: Description of parameter
            
        Returns:
            Result of action
        """
        self.logger.info(f"Performing action with parameter: {parameter}")
        self.click_element(self.ELEMENT_LOCATOR, "Element description")
        return self.get_text(self.ELEMENT_LOCATOR)
```

## Key Points

1. **Locators**: Use CSS selectors preferentially, XPath as fallback
2. **Methods**: Each method = one logical user action
3. **Logging**: Add descriptive messages via `self.logger`
4. **Allure Steps**: Decorate user action methods with `@allure.step()`
5. **Reuse BasePage**: Leverage existing methods: `click_element()`, `fill_input()`, `get_text()`, `wait_for_element()`, `navigate()`

## Example

```python
class SearchResultsPage(BasePage):
    """Models the eBay search results page"""
    
    PRICE_FILTER_INPUT = "[data-testid='price-filter-min']"
    APPLY_FILTER_BUTTON = "button:has-text('Apply')"
    RESULT_ITEMS = ".s-item"
    
    @allure.step("Apply price filter")
    def apply_price_filter(self, min_price: str, max_price: str):
        self.fill_input(self.PRICE_FILTER_INPUT, min_price, "Min price")
        self.click_element(self.APPLY_FILTER_BUTTON, "Apply filter")
        self.wait_for_element(self.RESULT_ITEMS, description="Results loaded")
```

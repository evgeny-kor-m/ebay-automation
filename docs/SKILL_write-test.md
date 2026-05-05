---
name: write-test
description: Write a new test following the project's pytest conventions
---

# Write Test

## Purpose

Create a new test file or test function following project conventions.

## Template

```python
import pytest
import allure
from pages.your_page import YourPage
from utils.config_reader import ConfigReader

@allure.feature("Feature Name")
@allure.story("Specific scenario")
def test_feature_behavior(page):
    """Test description explaining what is being tested"""
    
    page.logger.info("=" * 60)
    page.logger.info("TEST: {test description}")
    page.logger.info("=" * 60)
    
    # Arrange
    your_page = YourPage(page, page.logger)
    
    # Act
    your_page.perform_action()
    
    # Assert
    assert page.locator("selector").is_visible()
```

## Key Conventions

1. **Naming**: `test_` prefix + descriptive name (`test_user_can_login`, `test_price_filter_works`)
2. **Scope**: Test function scope = 1 test scenario
3. **Fixture**: `page` fixture provides Playwright Page with attached logger
4. **Allure**: Use `@allure.feature()` and `@allure.story()` decorators
5. **Logging**: Use `page.logger.info()`, `.debug()`, `.error()`, `.warning()`
6. **Pattern**: Arrange → Act → Assert
7. **Location**: Files in `tests/` directory with `test_*.py` naming

## Example

```python
import allure
from pages.login_page import LoginPage
from utils.config_reader import ConfigReader

@allure.feature("Authentication")
@allure.story("User login")
def test_user_can_login_with_valid_credentials(page):
    """Verify user can login with valid eBay credentials"""
    
    page.logger.info("=" * 60)
    page.logger.info("TEST: User login with valid credentials")
    page.logger.info("=" * 60)
    
    # Arrange
    username = ConfigReader.get_ebay_username()
    password = ConfigReader.get_ebay_password()
    login_page = LoginPage(page, page.logger)
    
    # Act
    login_page.login(username, password)
    
    # Assert
    assert page.locator("[data-testid='user-profile']").is_visible()
    page.logger.info("Login successful - user profile visible")
```

## Running Tests

```bash
pytest tests/test_your_feature.py::test_feature_behavior
pytest tests/test_your_feature.py -n 3  # parallel
pytest --browser firefox tests/test_your_feature.py  # specify browser
pytest --alluredir=reports/allure-results  # with Allure reporting
```

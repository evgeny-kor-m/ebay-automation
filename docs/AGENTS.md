# eBay Automation - AI Agent Instructions

## Project Overview

This is a **Playwright-based test automation framework** for eBay web application testing. It implements the **Page Object Model (POM)** architecture with parallel test execution, comprehensive logging, and Allure reporting.

**Stack**: Python 3.11+, pytest, Playwright, pytest-xdist, Allure Reports

## Architecture & Directory Structure

### Core Directories

- **`tests/`** — Test files following `test_*.py` naming convention
  - `conftest.py` — Pytest configuration, fixtures, hooks, and test lifecycle management
- **`pages/`** — Page Object classes that model UI interactions (inherit from `BasePage`)
  - `login_page.py` — Example page object for login functionality
- **`base/`** — Base classes and utilities
  - `base_page.py` — Abstract page class with common methods (`click_element`, `fill_input`, `wait_for_element`, `navigate`, etc.)
- **`driver/`** — Browser driver management
  - `driver_factory.py` — Creates and manages Playwright browser instances (Chrome, Firefox, Edge)
- **`config/`** — Configuration files
  - `appsettings.json` — Environment settings, timeouts, logging, browser settings, file paths
- **`data/`** — Test data
  - `test_data.yaml` — YAML-based test data for parameterized tests
- **`utils/`** — Helper utilities
  - `config_reader.py` — Reads appsettings.json and environment variables
  - `logger_setup.py` — Test logging configuration
  - `allure_manager.py` — Allure report management
  - `helper.py` — Common helper functions
- **`reports/`** — Generated test reports (Allure HTML reports and logs)

## Key Patterns & Conventions

### Page Object Model (POM)

All page objects inherit from `BasePage` and follow this pattern:

```python
from base.base_page import BasePage
from utils.logger_setup import LoggerManager

class MyPage(BasePage):
    # Define locators as class attributes
    SEARCH_INPUT = "input[placeholder='Search items']"
    SEARCH_BUTTON = "[data-testid='search-btn']"
    
    def search_items(self, query: str):
        self.fill_input(self.SEARCH_INPUT, query, "Search input")
        self.click_element(self.SEARCH_BUTTON, "Search button")
```

### Test Structure

Tests follow the Arrange-Act-Assert (AAA) pattern with Allure decorators:

```python
import allure
from pages.login_page import LoginPage

@allure.feature("eBay Feature")
@allure.story("Specific scenario")
def test_feature(page):  # 'page' fixture provides Page object with logger
    page.logger.info("Test description")
    
    # Arrange
    login_page = LoginPage(page, page.logger)
    
    # Act
    login_page.login(username, password)
    
    # Assert
    assert page.locator("selector").is_visible()
```

### Configuration Access

Configuration is centralized in `appsettings.json` and accessed via `ConfigReader`:

```python
from utils.config_reader import ConfigReader

username = ConfigReader.get_ebay_username()
base_url = ConfigReader.get_value("BaseUrl")
timeout = ConfigReader.get_value("Timeouts", {}).get("DefaultTimeout")
```

### Logging in Tests

Every test receives a logger via the `page` fixture. Use it for debugging:

```python
page.logger.info("User action description")
page.logger.debug("Detailed debug info")
page.logger.error("Error occurred")
page.logger.warning("Warning")
```

## Common Commands

### Setup Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
playwright install
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_search_cart.py

# Run specific test
pytest tests/test_search_cart.py::test_search_items_under_price

# Parallel execution (3 workers)
pytest -n 3

# Specify browser (chromium, firefox, webkit)
pytest --browser firefox

# Generate Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Test with Different Browsers

```bash
# Single browser
pytest --browser chrome

# Multiple browsers (runs each test in all browsers)
pytest --browser chrome --browser firefox

# Run in headless mode (default)
pytest  # controlled by appsettings.json "Headless": true
```

## Important Notes for Agents

### When Writing New Tests

1. **Test Naming**: Use `test_` prefix and descriptive names
2. **Page Objects**: Create page objects for each page/section of the app
3. **Assertions**: Use Playwright assertions (`.is_visible()`, `.is_enabled()`, etc.)
4. **Error Handling**: Leverage `BasePage` methods which include error logging
5. **Allure Decorators**: Add `@allure.feature()` and `@allure.story()` for better reporting
6. **Logging**: Use `page.logger` extensively for debugging and traceability

### When Creating Page Objects

1. Define locators as class-level constants (CSS selectors or XPath)
2. Inherit from `BasePage` for common methods (`click_element`, `fill_input`, `wait_for_element`, etc.)
3. Add description parameter to `BasePage` methods for better logging
4. Each method should represent a logical user action
5. Pass logger to parent class via `super().__init__(page, logger)`

### Known Configuration Issues

- **Browser**: Ensure browser is installed via `playwright install {browser_name}`
- **Headless Mode**: Configured in `appsettings.json` → `BrowserSettings.Headless`
- **Timeouts**: Default timeout is `30000ms` (30s), navigation is `60000ms` — adjust in appsettings.json
- **Viewport**: Fixed at 1920x1080 in `driver_factory.py`
- **Environment Variables**: `.env` file should contain eBay credentials (referenced by `ConfigReader`)

### Debugging Tips

1. Check logs in `reports/logs/` directory
2. Allure reports available in `reports/RUN_*/allure-reports/`
3. Use `page.logger.debug()` for detailed troubleshooting
4. Enable video recording in appsettings.json for test failures
5. Parallel execution with `-n` flag requires isolated sessions per worker

### Test Lifecycle

- `pytest_configure()` — Runs before all tests (setup logging, folders)
- `page` fixture (function scope) — Creates browser/page for each test, attaches logger
- `pytest_unconfigure()` — Runs after all tests (generates Allure reports)

## Code Style

- **Import Organization**: Standard library → Third-party → Local imports
- **Docstrings**: Add docstrings to page object methods
- **Type Hints**: Use type hints for function parameters and returns
- **Error Messages**: Be descriptive in log messages and assertion failures

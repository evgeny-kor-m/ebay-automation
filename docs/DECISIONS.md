# Architecture Decisions

### D1. Browser creation.
A naming conflict between `pytest-playwright` and my custom `page` fixture caused `--browser` to be ignored. I removed the plugin and implemented a `DriverFactory` with YAML-based run profiles (`config/profiles/*.yaml`), each defining the browser, channel, and remote address. Adding a browser now requires only a new profile file.

### D2. Currency: 
forced to USD (ebay.com + US shipping region). Fix the currency for comparison against the budget (using a single currency).

### D3. We’re excluding the "$20 to $40" price range.
The range does not have a definitive price, skip the card and write this in the log.

### D4. Subtotal => Total
"Total = subtotal excluding shipping" means that in the code, we should look at the "Subtotal" line, not the "Total" line.
Shipping is not controlled by our code, and no address is defined for the guest; the task allows the use of the subtotal.

### D5. Auth. 
Real eBay logins cannot be automated (due to CAPTCHA, 2FA, and bot detection). The default mode is "Guest," where scenarios (such as searching or using the shopping cart) run without logging in. Alternatively, there is a "StorageState" option: a session—manually saved once—is injected into the browser. The mode is selected in the configuration, with implementation handled via the Strategy pattern.

### D6. Browser versions. 
Playwright is tied to its own browser builds; you cannot select a specific version. Versions are accessed via channels: `chrome` (stable) and `chrome-beta` (two versions of Chrome), plus `msedge` and `firefox`. If you need precise version numbers, you must use Selenium Grid or Moon — this can be considered either a bonus or a limitation.

### D7. Reporting. 
Test execution only generates allure-results, reports are viewed separately via make report (Allure CLI in WSL, accessible through Windows browser at localhost). Removed AllureManager with hardcoded Windows paths and PowerShell dependencies. The same command now works locally and in CI.

### D8 Code. Broken Selector
(e.g., an XPath expression with an unclosed bracket) —  proceed to the next locator, but log the issue as an ERROR.

### D9. Screenshot upon failure. 
SmartLocator does not take a screenshot; instead, it raises an `ElementNotFoundError` (containing the name and all attempted locators). Screenshots and traces are collected by a test-failure hook in `conftest.py` — one screenshot per failure, with no duplicates. If the flow itself catches the error and continues (for example, by skipping an item), the flow takes the screenshot.

### D10. Code element.py
Extract UI elements into immutable `@dataclasses` with validation in `__post_init__`. This ensures thread safety during parallel execution and adheres to the "fail-fast" principle: if an element is created without a fallback locator or contains a duplicate, the framework will fail immediately upon initialization—before wasting time launching the browser.

### D11. Test strategy
Unit tests only for code with logic where a bug is costly to find via e2e:
Element, exceptions, SmartLocator, retry, parse_price.
Pages and flows are covered by e2e. Coverage is a tool, not a target.
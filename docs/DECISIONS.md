
### D1. Browser creation.
A naming conflict between `pytest-playwright` and my custom `page` fixture caused `--browser` to be ignored. I removed the plugin and implemented a `DriverFactory` with YAML-based run profiles (`config/profiles/*.yaml`), each defining the browser, channel, and remote address. Adding a browser now requires only a new profile file.

### D2. Currency: forced to USD (ebay.com + US shipping region)

### D3. We’re excluding the "$20 to $40" price range.

### D4. "Total = subtotal excluding shipping" means that in the code, we should look at the "Subtotal" line, not the "Total" line.

### D5. Auth. 
Real eBay logins cannot be automated (due to CAPTCHA, 2FA, and bot detection). The default mode is "Guest," where scenarios (such as searching or using the shopping cart) run without logging in. Alternatively, there is a "StorageState" option: a session—manually saved once—is injected into the browser. The mode is selected in the configuration, with implementation handled via the Strategy pattern.

### D6. Browser versions. 
Playwright is tied to its own browser builds; you cannot select a specific version. Versions are accessed via channels: `chrome` (stable) and `chrome-beta` (two versions of Chrome), plus `msedge` and `firefox`. If you need precise version numbers, you must use Selenium Grid or Moon — this can be considered either a benefit or a limitation.

### D7. Reporting. 
Test execution only generates allure-results, reports are viewed separately via make report (Allure CLI in WSL, accessible through Windows browser at localhost). Removed AllureManager with hardcoded Windows paths and PowerShell dependencies. The same command now works locally and in CI.


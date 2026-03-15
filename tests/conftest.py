import datetime
import pytest
import allure
import os
from driver.driver_factory import DriverFactory
from utils.config_reader import ConfigReader
from utils.logger_setup import LoggerManager

run_logger = None
root_run_path = None

def init_test_folders():
    global root_run_path

    paths = ConfigReader.get_value("Paths", {})
    base_dir = paths.get("BasetDir")
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    run_folder_name = f"RUN_{timestamp}"

    root_run_path = os.path.join(os.getcwd(), base_dir, run_folder_name)

    for key, value in paths.items():
        if key in ["BasetDir", "LogFileName"]:
            continue
        folder_path = os.path.join(root_run_path, value)
        os.makedirs(folder_path, exist_ok=True)
    
    

def pytest_configure(config):
    global run_logger, root_run_path
    
    init_test_folders()
    run_logger = LoggerManager.setup_main_logger(root_run_path)
    
    run_logger.info(f"Testing structure created: {root_run_path}")
    
    

    run_logger.info("\n" + "="*50)
    run_logger.info("PYTEST: All tests execution started")
    run_logger.info(f"ENVIRONMENT: {ConfigReader.get_value('Environment', 'Testing')}")
    run_logger.info("="*50)
    
    
@pytest.fixture(scope="function")
def page(request):
    global root_run_path
    
    test_name = request.node.name
    browser_name = ConfigReader.get_browser()
    headless = ConfigReader.get_headless()
    
    # Create test logger
    test_logger, log_path = LoggerManager.get_test_logger(root_run_path, test_name)
    
    run_logger.info(f"--- RUN TEST: {test_name} ---")
    test_logger.info(f"Init browser: {browser_name} (Headless: {headless})")
    
    # Create browser page
    driver_page, playwright = DriverFactory.create_driver(browser_name, headless)
    
    # ✅ ATTACH LOGGER TO PAGE
    driver_page.logger = test_logger
    
    yield driver_page
    
    run_logger.info(f"--- END TEST: {test_name} ---")
    driver_page.context.browser.close()
    playwright.stop()
    
    # Attach log to Allure
    if os.path.exists(log_path):
        with open(log_path, "rb") as f:
            allure.attach(
                f.read(),
                name=f"Logs-{test_name}",
                attachment_type=allure.attachment_type.TEXT
            )

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            global root_run_path
            screenshot_dir = os.path.join(root_run_path, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            screenshot_path = os.path.join(screenshot_dir, f"{item.name}_failed.png")
            page.screenshot(path=screenshot_path)
            
            allure.attach(
                page.screenshot(),
                name="Screenshot on Failure",
                attachment_type=allure.attachment_type.PNG
            )
            run_logger.error(f"Test Failure: {item.name}. Screenshot: {screenshot_path}")

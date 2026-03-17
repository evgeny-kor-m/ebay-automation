import datetime
import pytest
import allure
import os
from driver.driver_factory import DriverFactory
from utils.config_reader import ConfigReader
from utils.helper import file
from utils.logger_setup import LoggerManager
from utils.allure_manager import AllureManager

run_logger = None


def init_test_folders():
    # paths = ConfigReader.get_value("Paths", {})
    # base_dir = paths.get("BasetDir")
   
    # timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # run_folder_name = f"RUN_{timestamp}"
    # root_run_path = os.path.join(os.getcwd(), base_dir, run_folder_name)

    # for key, value in paths.items():
    #     if key in ["BasetDir", "LogFileName"]:
    #         continue
    #     folder_path = os.path.join(root_run_path, value)
    #     os.makedirs(folder_path, exist_ok=True)
    
    paths = ConfigReader.get_value("Paths", {})
    base_dir = paths.get("BasetDir")

    for key, value in paths.items():
        if key in ["BasetDir", "LogFileName"]:
            continue
        folder_path = os.path.join(base_dir, value)
        os.makedirs(folder_path, exist_ok=True)
    

def pytest_configure(config):
    """Hook is executed before all tests start"""
    global run_logger

    init_test_folders()
    run_logger = LoggerManager.setup_main_logger()

    run_logger.info("="*50)
    run_logger.info("PYTEST: All tests execution started")
    run_logger.info(f"ENVIRONMENT: {ConfigReader.get_value('Environment', 'Testing')}")
    run_logger.info("="*50)

def pytest_unconfigure(config):
    """Hook is executed after all tests finish"""
    global run_logger

    prepare_reports()
    try:
        run_logger.info("="*50)
        run_logger.info("PYTEST: All test execution finished")
        run_logger.info("="*50)
    except ValueError:
        run_logger.warning("log file already closed by pytest")
        pass   
    
@pytest.fixture(scope="function")
def page(request):
    global run_logger

    test_name = request.node.name
    browser_name = ConfigReader.get_browser()
    headless = ConfigReader.get_headless()
    
    # Create test logger
    test_logger, log_path = LoggerManager.get_test_logger(test_name)
    
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
    global run_logger

    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot_dir = os.path.join(ConfigReader.get_base_dir(), ConfigReader.get_value("Paths.Screenshots", "screenshots"))
            os.makedirs(screenshot_dir, exist_ok=True)
            
            screenshot_path = os.path.join(screenshot_dir, f"{item.name}_failed.png")
            page.screenshot(path=screenshot_path)
            
            allure.attach(
                page.screenshot(),
                name="Screenshot on Failure",
                attachment_type=allure.attachment_type.PNG
            )
            run_logger.error(f"Test Failure: {item.name}. Screenshot: {screenshot_path}")

def prepare_reports():
    global run_logger

    base_dir = ConfigReader.get_base_dir()
    results_dir = os.path.join(base_dir, "allure-results")
    report_dir = os.path.join(base_dir, "allure-report")

    AllureManager.generate_report(results_dir, report_dir)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    run_folder_name = f"RUN_{timestamp}"
    root_run_path = os.path.join(os.getcwd(), base_dir, run_folder_name)

    file.move_folder_contents(base_dir, root_run_path)
    run_logger.info(f"Testing structure created: {root_run_path}")

    archived_report_dir = os.path.join(root_run_path, "allure-report")

    if ConfigReader.get_value("Allure.AutoOpen", True):
        AllureManager.open_report(archived_report_dir) 


def pytest_runtest_setup(item):
    """Hook: before each test setup"""
    print(f" [HOOK] Test setup: {item.name}")

def pytest_runtest_teardown(item):
    """Hook: after each test teardown"""
    print(f" [HOOK] Test completion: {item.name}")

def pytest_collection_modifyitems(items):
    """Hook: after collecting all tests"""
    print(f"\n[HOOK] Tests collected: {len(items)}")

def pytest_sessionfinish(session, exitstatus):
    print("\n[HOOK] Session finish: Preparing reports and archiving...")
    # prepare_reports()
    





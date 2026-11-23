"""Fixtures for integration tests: real headless Chromium, no network.

Pages are filled with page.set_content(), so tests are offline and deterministic.
"""

import pytest
from playwright.sync_api import sync_playwright


# Module scope: one Chromium launch per test file (launch is the slow part);
# isolation between tests is provided by a fresh context in html_page.
@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def html_page(browser):
    """Fresh isolated page per test; any network request is aborted."""
    # New context per test: no cookies/storage/DOM leak between tests.
    context = browser.new_context()
    # Abort every request: content comes only from set_content(), never the network.
    context.route("**/*", lambda route: route.abort())
    page = context.new_page()
    yield page
    context.close()

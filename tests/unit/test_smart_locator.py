"""Unit tests for core.smart_locator.SmartLocator. No network, no browser.

Page/Locator are replaced by minimal stubs (FakeRoot/FakeLocator).
Tests against real Playwright live in
tests/integration/test_smart_locator_playwright.py.
"""

import logging

import pytest
from playwright.sync_api import Error as PlaywrightError

from core.element import Element
from core.smart_locator import SmartLocator

TIMEOUT_MS = 500
LOGGER_NAME = "test.smart_locator"

BROKEN = "div[data-testid='buy']]"
WORKING = "//button[text()='Buy It Now']"
# First line is what Playwright puts before the multi-line "Call log".
BROKEN_REASON = (
    f'Locator.wait_for: Unexpected token "]" while parsing css selector "{BROKEN}".'
)


class FakeLocator:
    """Stands in for a Playwright Locator; `.first` returns itself.

    Implements only what SmartLocator.find_element calls:
    `root.locator(selector).first.wait_for(state=..., timeout=...)`.
    No DOM and no browser: the outcome of `wait_for` is preconfigured.
    """

    def __init__(
        self, selector: str, calls: list, error: Exception | None = None
    ) -> None:
        # Kept so the test can tell which locator was tried.
        self.selector = selector
        # Call log shared with FakeRoot: records the order of attempts.
        self._calls = calls
        # What wait_for raises: None = "element found",
        # PlaywrightError = broken selector / not found.
        self._error = error

    @property
    def first(self) -> "FakeLocator":
        # Real `.first` narrows to the first match; a stub is already one element.
        return self

    def wait_for(self, state: str, timeout: int) -> None:
        # Record the attempt first, so failed attempts are logged too.
        self._calls.append((self.selector, state, timeout))
        if self._error is not None:
            raise self._error
        # No error: the element "reached" the requested state.


class FakeRoot:
    """Stands in for a Page: `locator(selector)` returns a preconfigured FakeLocator.

    Built from a {selector: error_or_None} map that sets each locator's outcome.
    """

    def __init__(self, errors: dict[str, Exception | None]) -> None:
        # One log for all locators, so the test can assert order and count of attempts.
        self.calls: list[tuple[str, str, int]] = []
        self._locators = {
            sel: FakeLocator(sel, self.calls, err) for sel, err in errors.items()
        }

    def locator(self, selector: str) -> FakeLocator:
        # An unknown selector raises KeyError: the test fails loudly, not silently.
        return self._locators[selector]


@pytest.fixture
def smart_locator(caplog) -> SmartLocator:
    """SmartLocator under test, with its own logger captured by caplog."""
    # Capture everything from DEBUG up for this logger only, so tests can assert
    # the DEBUG/INFO/WARNING/ERROR records SmartLocator writes.
    caplog.set_level(logging.DEBUG, logger=LOGGER_NAME)
    # Short timeout: per-locator wait (ms); stubs don't wait, keeps failures fast.
    return SmartLocator(timeout_ms=TIMEOUT_MS, logger=logging.getLogger(LOGGER_NAME))


def test_broken_first_selector_falls_back_to_second_and_logs_error(
    smart_locator, caplog
):
    """#1 (fakes) Broken #1 raises playwright.Error -> ERROR with reason, found via #2."""
    element = Element("buy button", (BROKEN, WORKING))
    syntax_error = PlaywrightError(
        f"{BROKEN_REASON}\nCall log:\n  - waiting for locator(...)"
    )
    root = FakeRoot({BROKEN: syntax_error, WORKING: None})

    found = smart_locator.find_element(root, element)

    # Found via #2, after exactly one attempt per locator, in order.
    assert found is root.locator(WORKING)
    assert root.calls == [
        (BROKEN, "visible", TIMEOUT_MS),
        (WORKING, "visible", TIMEOUT_MS),
    ]

    # ERROR for #1 names the element, the position, the selector and the reason,
    # without the multi-line Call log.
    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(errors) == 1
    message = errors[0].getMessage()
    assert "[buy button]" in message
    assert "#1/2" in message
    assert BROKEN in message
    assert BROKEN_REASON in message
    assert "Call log" not in message

    # The fallback hit is reported so the broken primary gets fixed.
    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert any("fallback #2/2" in w and WORKING in w for w in warnings)

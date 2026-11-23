import pytest
from core.exceptions import ElementNotFoundError, FrameworkError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

VALID_LOCATORS = ("[data-testid='x']", "//button[text()='Go']")


# --- ElementNotFoundError --------------------------------------------------

# even if `tried` is passed as a list, internally it is stored as a tuple
# The element name and the tried locators are included in the error as attributes.
def test_element_not_found_stores_name_and_tried_as_tuple():
    err = ElementNotFoundError("search button", list(VALID_LOCATORS))
    assert err.name == "search button"
    assert err.tried == VALID_LOCATORS
    assert isinstance(err.tried, tuple)

# checks that: ElementNotFoundError — a subclass of FrameworkError
# in the code (for example, in a flow or a hook), can catch any of our errors with a single line.
# except FrameworkError as e:     # will catch:  ElementNotFoundError, BotChallengeDetected, CurrencyMismatchError
def test_element_not_found_is_framework_error():
    assert isinstance(ElementNotFoundError("x", VALID_LOCATORS), FrameworkError)


def test_element_not_found_is_not_playwright_timeout():
    # Retry is keyed on Playwright timeouts; this error must never be retried.

    err = ElementNotFoundError("x", VALID_LOCATORS)
    
    # Part 1 — "Is our error a type of Playwright timeout?" expect "no."
    assert not isinstance(err, PlaywrightTimeoutError) 

    # Part 2 — Simulation of what retry will do
    with pytest.raises(ElementNotFoundError):          # (3) outside, we expect get our error here   
        try:
            raise err                                  # (1) we raise our error
        except PlaywrightTimeoutError:                 # (2) the "retry" mechanism catches ONLY timeouts, if it catches our error, FAIL the test
            pytest.fail("ElementNotFoundError was caught as Playwright TimeoutError")

# Check: The error message contains the element name and each locator that was tried.
def test_element_not_found_message_lists_name_and_all_locators():
    message = str(ElementNotFoundError("search button", VALID_LOCATORS))
    assert "search button" in message
    for loc in VALID_LOCATORS:
        assert loc in message

"""Unit tests for core.smart_locator.SmartLocator. No network.

Two groups:
- fakes: Page/Locator replaced by minimal stubs, no browser at all;
- real Playwright: headless chromium + page.set_content(), all requests aborted.
"""

import logging

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from core.element import Element
from core.exceptions import ElementNotFoundError
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
    """Stands in for a Playwright Locator; `.first` returns itself."""

    def __init__(
        self, selector: str, calls: list, error: Exception | None = None
    ) -> None:
        self.selector = selector
        self._calls = calls
        self._error = error

    @property
    def first(self) -> "FakeLocator":
        return self

    def wait_for(self, state: str, timeout: int) -> None:
        self._calls.append((self.selector, state, timeout))
        if self._error is not None:
            raise self._error


class FakeRoot:
    """Stands in for a Page: `locator(selector)` returns a preconfigured FakeLocator."""

    def __init__(self, errors: dict[str, Exception | None]) -> None:
        self.calls: list[tuple[str, str, int]] = []
        self._locators = {
            sel: FakeLocator(sel, self.calls, err) for sel, err in errors.items()
        }

    def locator(self, selector: str) -> FakeLocator:
        return self._locators[selector]


@pytest.fixture
def smart_locator(caplog) -> SmartLocator:
    caplog.set_level(logging.DEBUG, logger=LOGGER_NAME)
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


# --- real Playwright (headless chromium, set_content, no network) ----------


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def html_page(browser):
    """Fresh isolated page per test; any network request is aborted."""
    context = browser.new_context()
    context.route("**/*", lambda route: route.abort())
    page = context.new_page()
    yield page
    context.close()


def _records(caplog, level: int) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno == level]


BUTTON_HTML = "<button id='go' data-testid='go'>Go</button>"
MISSING_CSS = "[data-testid='missing']"


def test_real_first_locator_found_logs_debug(smart_locator, html_page, caplog):
    """#2 First locator matches -> returned, DEBUG 'OK via #1/2', no WARNING/ERROR."""
    html_page.set_content(BUTTON_HTML)
    element = Element("go button", ("[data-testid='go']", "//button[text()='Go']"))

    found = smart_locator.find_element(html_page, element)

    assert found.get_attribute("id") == "go"
    assert any("OK via #1/2" in m for m in _records(caplog, logging.DEBUG))
    assert _records(caplog, logging.WARNING) == []
    assert _records(caplog, logging.ERROR) == []


def test_real_fallback_to_second_logs_warning(smart_locator, html_page, caplog):
    """#3 #1 misses, #2 matches -> INFO for #1, one WARNING 'fallback #2/2', no ERROR."""
    html_page.set_content(BUTTON_HTML)
    element = Element("go button", (MISSING_CSS, "//button[text()='Go']"))

    found = smart_locator.find_element(html_page, element)

    assert found.get_attribute("id") == "go"
    assert any("not found via #1/2" in m for m in _records(caplog, logging.INFO))
    warnings = _records(caplog, logging.WARNING)
    assert len(warnings) == 1
    assert "fallback #2/2" in warnings[0]
    assert _records(caplog, logging.ERROR) == []


def test_real_broken_xpath_logs_error_and_falls_back(smart_locator, html_page, caplog):
    """#4 #1 is invalid XPath '//button[' -> one ERROR with reason, found via #2."""
    html_page.set_content(BUTTON_HTML)
    broken = "//button["
    element = Element("go button", (broken, "[data-testid='go']"))

    found = smart_locator.find_element(html_page, element)

    assert found.get_attribute("id") == "go"
    errors = _records(caplog, logging.ERROR)
    assert len(errors) == 1
    assert "#1/2" in errors[0]
    assert broken in errors[0]
    assert "not a valid XPath expression" in errors[0]
    assert "Call log" not in errors[0]
    assert any("fallback #2/2" in w for w in _records(caplog, logging.WARNING))


def test_real_none_found_raises_element_not_found(smart_locator, html_page, caplog):
    """#5 Nothing matches -> ElementNotFoundError with name and tried == locators."""
    html_page.set_content(BUTTON_HTML)
    element = Element("missing", (MISSING_CSS, "//button[text()='Nope']"))

    with pytest.raises(ElementNotFoundError) as exc_info:
        smart_locator.find_element(html_page, element)

    assert exc_info.value.name == "missing"
    assert exc_info.value.tried == element.locators
    assert any("all 2 locator(s) failed" in m for m in _records(caplog, logging.ERROR))


def test_real_hidden_element_depends_on_state(smart_locator, html_page):
    """#6 display:none -> not found for state='visible', found for state='attached'."""
    html_page.set_content(
        "<button id='hidden' data-testid='hidden' style='display:none'>Hidden</button>"
    )
    element = Element(
        "hidden button", ("[data-testid='hidden']", "//button[text()='Hidden']")
    )

    with pytest.raises(ElementNotFoundError):
        smart_locator.find_element(html_page, element, state="visible")

    found = smart_locator.find_element(html_page, element, state="attached")
    assert found.get_attribute("id") == "hidden"


CARDS_HTML = """
<div class="card" data-testid="card" id="card-a">
  <span class="title">Item A</span><span class="price" data-testid="price">$10.00</span>
</div>
<div class="card" data-testid="card" id="card-b">
  <span class="title">Item B</span><span class="price" data-testid="price">$20.00</span>
</div>
"""
# Playwright auto-detects XPath only for "//" or ".."; ".//" is parsed as CSS.
# Inside a scoped locator, "//" is already relative to the scope.
PRICE_XPATH = "//span[contains(@class, 'price')]"
PRICE = Element("price", ("[data-testid='price']", PRICE_XPATH))
PRICE_VIA_XPATH_FALLBACK = Element("price", (MISSING_CSS, PRICE_XPATH))


def _card_b(smart_locator, page):
    return smart_locator.find_element(
        page, Element("card B", ("#card-b", "//div[.//span[text()='Item B']]"))
    )


def test_real_root_scopes_search_to_its_card(smart_locator, html_page):
    """#7 root=card B: CSS price is card B's own ($20), not the first on page ($10)."""
    html_page.set_content(CARDS_HTML)
    card_b = _card_b(smart_locator, html_page)

    # Control: from the page, the first price on the page is card A's.
    assert smart_locator.find_element(html_page, PRICE).text_content() == "$10.00"
    # Scoped to card B, its own price is returned, not the neighbour's.
    assert smart_locator.find_element(card_b, PRICE).text_content() == "$20.00"


def test_real_root_scopes_xpath_fallback_to_its_card(smart_locator, html_page):
    """#8 root=card B: '//' XPath fallback stays inside the card, returns $20."""
    html_page.set_content(CARDS_HTML)
    card_b = _card_b(smart_locator, html_page)

    found = smart_locator.find_element(card_b, PRICE_VIA_XPATH_FALLBACK)

    assert found.text_content() == "$20.00"

"""Integration tests for core.smart_locator.SmartLocator against real Playwright.

Headless chromium + page.set_content(), all network requests aborted
(browser/html_page fixtures live in tests/integration/conftest.py).
The stub-based test lives in tests/unit/test_smart_locator.py.
"""

import logging

import pytest
from playwright.sync_api import Locator

from core.element import Element
from core.exceptions import ElementNotFoundError
from core.smart_locator import SmartLocator

TIMEOUT_MS = 500
LOGGER_NAME = "test.smart_locator"


@pytest.fixture
def smart_locator(caplog) -> SmartLocator:
    caplog.set_level(logging.DEBUG, logger=LOGGER_NAME)
    return SmartLocator(timeout_ms=TIMEOUT_MS, logger=logging.getLogger(LOGGER_NAME))


def _records(caplog, level: int) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno == level]


BUTTON_HTML = "<button id='go' data-testid='go'>Go</button>"
MISSING_CSS = "[data-testid='missing']"


def test_real_first_locator_found_logs_debug(smart_locator, html_page, caplog):
    """#2 First locator matches -> returned, DEBUG 'OK via #1/2', no WARNING/ERROR."""
    html_page.set_content(BUTTON_HTML)
    element = Element("go button", ("[data-testid='go']", "//button[text()='Go']"))

    found = smart_locator.find_element(html_page, element)

    # The right DOM element is returned (the real button, not just "something").
    assert found.get_attribute("id") == "go"
    # Success via the primary locator is logged at DEBUG only.
    assert any("OK via #1/2" in m for m in _records(caplog, logging.DEBUG))
    # Happy path is silent: no fallback warning ...
    assert _records(caplog, logging.WARNING) == []
    # ... and no broken-selector error.
    assert _records(caplog, logging.ERROR) == []


def test_real_fallback_to_second_logs_warning(smart_locator, html_page, caplog):
    """#3 #1 misses, #2 matches -> INFO for #1, one WARNING 'fallback #2/2', no ERROR."""
    html_page.set_content(BUTTON_HTML)
    element = Element("go button", (MISSING_CSS, "//button[text()='Go']"))

    found = smart_locator.find_element(html_page, element)

    # Found via #2: the same button as in #2.
    assert found.get_attribute("id") == "go"
    # #1 simply didn't match (timeout) -> INFO, not ERROR: the selector is valid.
    assert any("not found via #1/2" in m for m in _records(caplog, logging.INFO))
    warnings = _records(caplog, logging.WARNING)
    # Exactly one WARNING: the fallback hit, so the primary gets fixed.
    assert len(warnings) == 1
    # The WARNING names which fallback worked.
    assert "fallback #2/2" in warnings[0]
    # A missing element is not a broken selector: no ERROR.
    assert _records(caplog, logging.ERROR) == []


def test_real_broken_xpath_logs_error_and_falls_back(smart_locator, html_page, caplog):
    """#4 #1 is invalid XPath '//button[' -> one ERROR with reason, found via #2."""
    html_page.set_content(BUTTON_HTML)
    broken = "//button["
    element = Element("go button", (broken, "[data-testid='go']"))

    found = smart_locator.find_element(html_page, element)

    # A broken #1 doesn't stop the search: found via #2.
    assert found.get_attribute("id") == "go"
    errors = _records(caplog, logging.ERROR)
    # Exactly one ERROR: for the broken #1 only (no "all failed" error).
    assert len(errors) == 1
    # The ERROR says which locator is broken (position) ...
    assert "#1/2" in errors[0]
    # ... shows the selector itself ...
    assert broken in errors[0]
    # ... and the real reason from Playwright.
    assert "not a valid XPath expression" in errors[0]
    # Only the first line of the reason: the multi-line Call log is cut off.
    assert "Call log" not in errors[0]
    # The fallback hit is still reported as a WARNING.
    assert any("fallback #2/2" in w for w in _records(caplog, logging.WARNING))


def test_real_none_found_raises_element_not_found(smart_locator, html_page, caplog):
    """#5 Nothing matches -> ElementNotFoundError with name and tried == locators."""
    html_page.set_content(BUTTON_HTML)
    element = Element("missing", (MISSING_CSS, "//button[text()='Nope']"))

    # No locator matched -> ElementNotFoundError (not a Playwright timeout).
    with pytest.raises(ElementNotFoundError) as exc_info:
        smart_locator.find_element(html_page, element)

    # The exception names the element ...
    assert exc_info.value.name == "missing"
    # ... and lists every locator that was tried, in order.
    assert exc_info.value.tried == element.locators
    # A final ERROR summarises the failure with the number of locators.
    assert any("all 2 locator(s) failed" in m for m in _records(caplog, logging.ERROR))


def test_real_hidden_element_depends_on_state(smart_locator, html_page):
    """#6 display:none -> not found for state='visible', found for state='attached'."""
    html_page.set_content(
        "<button id='hidden' data-testid='hidden' style='display:none'>Hidden</button>"
    )
    element = Element(
        "hidden button", ("[data-testid='hidden']", "//button[text()='Hidden']")
    )

    # In the DOM but display:none -> never becomes visible -> not found.
    with pytest.raises(ElementNotFoundError):
        smart_locator.find_element(html_page, element, state="visible")

    # The same element with state="attached" is found: `state` is passed through.
    found = smart_locator.find_element(html_page, element, state="attached")
    # And it is the hidden button itself.
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

    # The "//" XPath fallback searched inside card B ($20), not the whole page
    # (which would return card A's $10 first).
    assert found.text_content() == "$20.00"


LIST_HTML = """
<ul id="results" data-testid="results">
  <li class="item" data-testid="item">Item A</li>
  <li class="item" data-testid="item">Item B</li>
  <li class="item" data-testid="item">Item C</li>
</ul>
"""
# Same list + a neighbouring list with 2 more cards of the same kind.
LIST_WITH_NEIGHBOURS_HTML = (
    LIST_HTML
    + """
<ul id="sponsored" data-testid="sponsored">
  <li class="item" data-testid="item">Ad X</li>
  <li class="item" data-testid="item">Ad Y</li>
</ul>
"""
)
ITEM_XPATH = "//li[contains(@class, 'item')]"
ITEM = Element("result item", ("[data-testid='item']", ITEM_XPATH))
ITEM_VIA_XPATH_FALLBACK = Element("result item", (MISSING_CSS, ITEM_XPATH))
RESULTS_LIST = Element("results list", ("#results", "//ul[@data-testid='results']"))
OWN_ITEMS = ["Item A", "Item B", "Item C"]


def test_real_find_all_returns_all_matches(smart_locator, html_page, caplog):
    """#9 Three cards -> find_all returns a Locator with count() == 3."""
    html_page.set_content(LIST_HTML)

    items = smart_locator.find_all(html_page, ITEM)

    # A Locator (not a list), so callers can still chain .nth()/.count().
    assert isinstance(items, Locator)
    # All matches, not narrowed to .first.
    assert items.count() == 3
    # And they are exactly the three cards, in DOM order.
    assert items.all_text_contents() == OWN_ITEMS
    # Found via the primary locator -> DEBUG only.
    assert any("OK via #1/2" in m for m in _records(caplog, logging.DEBUG))
    # Happy path: no fallback warning.
    assert _records(caplog, logging.WARNING) == []


def test_real_find_all_fallback_to_second_logs_warning(smart_locator, html_page, caplog):
    """#10 #1 misses, #2 matches -> count() == 3, one WARNING 'fallback #2/2'."""
    html_page.set_content(LIST_HTML)

    items = smart_locator.find_all(html_page, ITEM_VIA_XPATH_FALLBACK)

    # The fallback XPath returns all three cards, not just the first.
    assert items.count() == 3
    # #1 simply didn't match -> INFO.
    assert any("not found via #1/2" in m for m in _records(caplog, logging.INFO))
    warnings = _records(caplog, logging.WARNING)
    # Exactly one WARNING for the fallback hit ...
    assert len(warnings) == 1
    # ... naming the fallback that worked.
    assert "fallback #2/2" in warnings[0]
    # A missing element is not a broken selector: no ERROR.
    assert _records(caplog, logging.ERROR) == []


def test_real_find_all_none_found_raises_element_not_found(
    smart_locator, html_page, caplog
):
    """#11 Nothing matches -> ElementNotFoundError (not an empty Locator)."""
    html_page.set_content(LIST_HTML)
    element = Element("missing items", (MISSING_CSS, "//li[text()='Nope']"))

    # No locator matched -> error, not a silent count() == 0.
    with pytest.raises(ElementNotFoundError) as exc_info:
        smart_locator.find_all(html_page, element)

    # The exception names the element ...
    assert exc_info.value.name == "missing items"
    # ... and lists every locator that was tried, in order.
    assert exc_info.value.tried == element.locators
    # A final ERROR summarises the failure.
    assert any("all 2 locator(s) failed" in m for m in _records(caplog, logging.ERROR))


def test_real_find_all_root_counts_only_inside_container(smart_locator, html_page):
    """#12 root=results list: only its 3 cards are counted, not the neighbours."""
    html_page.set_content(LIST_WITH_NEIGHBOURS_HTML)
    container = smart_locator.find_element(html_page, RESULTS_LIST)

    # Control: page-wide there are 5 cards (3 own + 2 neighbours).
    assert smart_locator.find_all(html_page, ITEM).count() == 5

    items = smart_locator.find_all(container, ITEM)
    # Scoped to the container: only its own 3 cards.
    assert items.count() == 3
    # And they are the container's cards, no "Ad X"/"Ad Y".
    assert items.all_text_contents() == OWN_ITEMS

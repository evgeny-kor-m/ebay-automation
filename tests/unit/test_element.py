"""Unit tests for core.element.Element and core.exceptions. No browser, no network."""

import dataclasses

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.element import Element
from core.exceptions import ElementNotFoundError, FrameworkError

VALID = ("[data-testid='x']", "//button[text()='Go']")


# --- valid Element ---------------------------------------------------------


def test_valid_element_keeps_fields():
    el = Element("search button", VALID)
    assert el.name == "search button"
    assert el.locators == VALID


def test_valid_element_accepts_more_than_two_locators():
    locators = VALID + ("button#gh-btn",)
    assert Element("search button", locators).locators == locators


# --- validation errors ---------------------------------------------------


@pytest.mark.parametrize("name", ["", "   "], ids=["empty", "whitespace"])
def test_empty_name_rejected(name):
    with pytest.raises(ValueError, match="name is required"):
        Element(name, VALID)


def test_list_instead_of_tuple_rejected():
    with pytest.raises(TypeError, match="must be a tuple"):
        Element("x", list(VALID))


@pytest.mark.parametrize("locators", [None, 5], ids=["none", "int"])
def test_non_iterable_locators_rejected_with_clear_message(locators):
    with pytest.raises(TypeError, match="'x': locators must be a tuple"):
        Element("x", locators)


def test_string_instead_of_tuple_rejected():
    # A common typo: ("#a") is a str, not a 1-tuple.
    with pytest.raises(TypeError, match="must be a tuple"):
        Element("x", "#a")


@pytest.mark.parametrize("locators", [(), ("#a",)], ids=["zero", "one"])
def test_fewer_than_two_locators_rejected(locators):
    with pytest.raises(ValueError, match="at least 2 locators"):
        Element("x", locators)


@pytest.mark.parametrize("bad", ["", "   "], ids=["empty", "whitespace"])
def test_empty_locator_rejected(bad):
    with pytest.raises(ValueError, match="empty locator"):
        Element("x", ("#a", bad))


def test_duplicate_locators_rejected():
    with pytest.raises(ValueError, match="duplicate locators"):
        Element("x", ("#a", "#a"))


def test_duplicate_locators_differing_only_by_whitespace_rejected():
    with pytest.raises(ValueError, match="duplicate locators"):
        Element("x", ("#a", "#a "))


def test_non_string_name_rejected_with_type_error():
    with pytest.raises(TypeError, match="Element name must be a string"):
        Element(None, VALID)


def test_non_string_locator_rejected_with_type_error_naming_element():
    with pytest.raises(TypeError, match="'search button'"):
        Element("search button", ("#a", None))


# --- immutability ----------------------------------------------------------


@pytest.mark.parametrize("attr, value", [("name", "other"), ("locators", ("#b", "#c"))])
def test_element_is_frozen(attr, value):
    el = Element("x", VALID)
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(el, attr, value)


# --- ElementNotFoundError --------------------------------------------------


def test_element_not_found_stores_name_and_tried_as_tuple():
    err = ElementNotFoundError("search button", list(VALID))
    assert err.name == "search button"
    assert err.tried == VALID
    assert isinstance(err.tried, tuple)


def test_element_not_found_is_framework_error():
    assert isinstance(ElementNotFoundError("x", VALID), FrameworkError)


def test_element_not_found_is_not_playwright_timeout():
    # Retry is keyed on Playwright timeouts; this error must never be retried.
    err = ElementNotFoundError("x", VALID)
    assert not isinstance(err, PlaywrightTimeoutError)
    with pytest.raises(ElementNotFoundError):
        try:
            raise err
        except PlaywrightTimeoutError:
            pytest.fail("ElementNotFoundError was caught as Playwright TimeoutError")


def test_element_not_found_message_lists_name_and_all_locators():
    message = str(ElementNotFoundError("search button", VALID))
    assert "search button" in message
    for loc in VALID:
        assert loc in message

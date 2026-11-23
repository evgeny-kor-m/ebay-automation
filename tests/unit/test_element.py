"""Unit tests for core.element.Element. No browser, no network."""

import dataclasses

import pytest

from core.element import Element

VALID_LOCATORS = ("[data-testid='x']", "//button[text()='Go']")


# --- valid Element ---------------------------------------------------------


def test_valid_element_keeps_fields():
    el = Element("search button", VALID_LOCATORS)
    assert el.name == "search button"
    assert el.locators == VALID_LOCATORS


# The requirement is "at least 2," which means 3 should also be acceptable.
def test_valid_element_accepts_more_than_two_locators():
    locators = VALID_LOCATORS + ("button#gh-btn",)
    assert Element("search button", locators).locators == locators


# --- validation errors ---------------------------------------------------

# Run	 parameter  value	 signature
# 1: 	 name       ""	     empty
# 2: 	 name       "   "	 whitespace
# --results----------------------------------------
# tests/unit/test_element.py::test_empty_name_rejected[empty name] PASSED  [ 50%]
# tests/unit/test_element.py::test_empty_name_rejected[whit spaces] PASSED [100%]


@pytest.mark.parametrize("name", ["", "   "], ids=["empty name", "whit spaces"])
def test_empty_name_rejected(name):
    with pytest.raises(ValueError, match="name is required"):
        Element(name, VALID_LOCATORS)


def test_list_instead_of_tuple_rejected():
    with pytest.raises(TypeError, match="must be a tuple"):
        Element("x", list(VALID_LOCATORS))


# non_iterable - not collection
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


# Two runs: the second locator is empty "" or consists of only spaces " ".
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
        Element(None, VALID_LOCATORS)


def test_non_string_locator_rejected_with_type_error_naming_element():
    with pytest.raises(TypeError, match="'search button'"):
        Element("search button", ("#a", None))


# --- immutability ----------------------------------------------------------
# After creation an Element cannot be changed (frozen=True).


@pytest.mark.parametrize(
    "attr, value",  # parameters
    [("name", "other"), ("locators", ("#b", "#c"))],  # values
    ids=["changing-name", "changing-locators"],
)  # ids
def test_element_is_frozen(attr, value):
    el = Element("x", VALID_LOCATORS)
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(
            el, attr, value
        )  # the same as el.name = "other" / el.locators = ("#b", "#c")

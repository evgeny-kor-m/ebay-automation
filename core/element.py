"""Element: a UI element described as data — a name plus fallback locators."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Element:
    """Immutable description of a UI element.

    Holds no logic for finding: SmartLocator does that (SRP).
    Validated on creation, so a page with an invalid Element fails on import.
    """

    name: str
    locators: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Element name is required (used in logs).")
        if not isinstance(self.locators, tuple):
            raise TypeError(
                f"Element '{self.name}': locators must be a tuple, "
                f"got {type(self.locators).__name__}."
            )
        if len(self.locators) < 2:
            raise ValueError(
                f"Element '{self.name}' needs at least 2 locators for fallback, "
                f"got {len(self.locators)}."
            )
        if any(not loc.strip() for loc in self.locators):
            raise ValueError(f"Element '{self.name}' has an empty locator.")
        if len(set(self.locators)) != len(self.locators):
            raise ValueError(
                f"Element '{self.name}' has duplicate locators: a duplicate is a fake fallback."
            )

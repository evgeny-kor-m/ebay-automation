import logging

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.element import Element
from core.exceptions import ElementNotFoundError


class SmartLocator:
    """Finds an Element by trying its locators in order (fallback)."""
    def __init__(self, timeout_ms: int, logger: logging.Logger) -> None:
        if timeout_ms <= 0:
            raise ValueError(f"timeout_ms must be positive, got {timeout_ms}.")
        self.timeout_ms = timeout_ms  # Timeout for 1 Locator
        self.logger = logger

    def find_element(
        self, root: Page | Locator, element: Element, state: str = "visible"
    ) -> Locator:
        """Return the first locator of `element` that reaches `state`.

        Tries locators in order, one attempt each (attempts = number of locators).
        Raises ElementNotFoundError if none matched.
        """
        total = len(element.locators)

        for attempt, loc in enumerate(element.locators, start=1):
            candidate = root.locator(loc).first
            try:
                candidate.wait_for(state=state, timeout=self.timeout_ms)
            except PlaywrightTimeoutError:
                self.logger.info(
                    f"[{element.name}] not found via #{attempt}/{total}: {loc}"
                )
                continue
            except PlaywrightError as e:
                reason = str(e).splitlines()[0]
                self.logger.error(
                    f"[{element.name}] broken selector #{attempt}/{total}: {loc} — {reason}"
                )
                continue

            if attempt == 1:
                self.logger.debug(f"[{element.name}] OK via #1/{total}: {loc}")
            else:
                self.logger.warning(
                    f"[{element.name}] OK via fallback #{attempt}/{total}: {loc} "
                    f"(primary locator is broken — update it)"
                )
            return candidate

        self.logger.error(f"[{element.name}] not found, all {total} locator(s) failed")
        raise ElementNotFoundError(element.name, element.locators)

    # def find_all(self, root: Page | Locator, element: Element) -> Locator: ...
    # def exists(self, root: Page | Locator, element: Element) -> bool: ...

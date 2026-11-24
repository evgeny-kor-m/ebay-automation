import logging

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.element import Element
from core.exceptions import ElementNotFoundError


class SmartLocator:
    """Finds an Element by trying its locators in order (fallback)."""

    def __init__(self, timeout_ms: int, logger: logging.Logger) -> None:
        """Configure the search.

        Args:
            timeout_ms: wait budget for ONE locator, in ms (not for the whole
                element: the worst case is timeout_ms * number of locators).
            logger: receives one record per attempt (DEBUG/INFO/WARNING/ERROR).

        Raises:
            ValueError: if timeout_ms is not positive.
        """
        if timeout_ms <= 0:
            raise ValueError(f"timeout_ms must be positive, got {timeout_ms}.")
        self.timeout_ms = timeout_ms  # Timeout for 1 Locator
        self.logger = logger

    def _resolve(
        self, root: Page | Locator, element: Element, state: str = "visible"
    ) -> Locator:
        """Return the Locator of the first selector whose first match reaches `state`.

        Each selector of `element.locators` is tried once, in order, searching
        inside `root` (Page or a scoping Locator). Per attempt it logs:
        - DEBUG: found via the primary (#1) selector;
        - WARNING: found via a fallback selector (primary needs fixing);
        - INFO: selector timed out (element absent or not in `state`);
        - ERROR: selector is invalid (playwright.Error), first line of the reason.
        The returned Locator is NOT narrowed to `.first`; it may match many elements.

        Raises:
            ElementNotFoundError: no selector matched; carries name and all locators.
        """
        total = len(element.locators)
        for attempt, loc in enumerate(element.locators, start=1):
            matches = root.locator(loc)
            try:
                matches.first.wait_for(state=state, timeout=self.timeout_ms)
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
            return matches

        self.logger.error(f"[{element.name}] not found, all {total} locator(s) failed")
        raise ElementNotFoundError(element.name, element.locators)

    def find_element(
        self, root: Page | Locator, element: Element, state: str = "visible"
    ) -> Locator:
        """Return the first locator of `element` that reaches `state`.

        Tries locators in order, one attempt each (attempts = number of locators).
        Raises ElementNotFoundError if none matched.
        """
        return self._resolve(root, element, state).first

    def find_all(
        self, root: Page | Locator, element: Element, state: str = "visible"
    ) -> Locator:
        """Return a Locator for ALL matches of the first working locator of `element`.

        Same fallback as find_element, but the result is not narrowed to `.first`
        (e.g. for a list of search results). Only the first match is waited for
        `state`; the others are not checked.
        Raises ElementNotFoundError if none matched.
        """
        return self._resolve(root, element, state)

    # def exists(self, root: Page | Locator, element: Element) -> bool: ...

"""Framework-specific exceptions.

Separate types let the framework react differently to different failures:
- retry repeats only environment errors (Playwright timeouts, network),
  never ElementNotFoundError: if no locator matched, repeating won't help;
- reports show a clear reason instead of a generic "Timeout 30000ms exceeded".
"""

from collections.abc import Sequence


class FrameworkError(Exception):
    """Base class for all errors raised by this framework."""


class ElementNotFoundError(FrameworkError):
    """All locators of an Element failed (fallback exhausted).

    Deliberately NOT a subclass of Playwright's TimeoutError:
    retry is configured on timeouts and must not repeat this error.
    """

    def __init__(self, name: str, tried: Sequence[str]) -> None:
        self.name = name
        self.tried = tuple(tried)
        locators = "\n".join(f"  #{i} {loc}" for i, loc in enumerate(self.tried, 1))
        super().__init__(
            f"Element '{name}' not found, tried {len(self.tried)} locator(s):\n{locators}"
        )


class BotChallengeDetected(FrameworkError):
    """eBay showed a CAPTCHA / 'Pardon our interruption' page instead of content."""

    def __init__(self, url: str, marker: str) -> None:
        self.url = url
        self.marker = marker
        super().__init__(f"Bot challenge detected at {url} ({marker})")


class CurrencyMismatchError(FrameworkError):
    """Price is not in the expected currency (decision D2: USD only)."""

    def __init__(self, price_text: str, expected: str = "USD") -> None:
        self.price_text = price_text
        self.expected = expected
        super().__init__(f"Expected price in {expected}, got {price_text!r}")

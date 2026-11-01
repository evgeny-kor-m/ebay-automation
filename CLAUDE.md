# eBay E2E Automation

An E2E framework for eBay built with Playwright and pytest (Python 3.12). It covers searching with price filtering, adding items to the cart, and verifying the total amount. This is a test assignment; architecture is prioritized over the number of test cases.

## Commands
- Unit tests: `pytest tests/unit -q`
- E2E tests: `pytest tests/e2e --profile chrome`
- Parallel execution: `pytest tests/e2e -n 4 --profile chrome`
- Import validation: `pytest --collect-only -q`

## Architecture
Layer structure and dependency flow (circular imports are prohibited):
`tests` → `flows` → `pages` → `core`; `utils` is accessible to all layers.

- `core/` — Infrastructure layer, agnostic to eBay: includes `Element`, `SmartLocator`, retry logic, `BasePage`, and custom exceptions.
- `pages/` — Page Object Model (POM): contains only `Element` definitions and atomic actions. No business logic.
- `flows/` — Implements the 4 functions required by the assignment: authentication, search, cart operations, and assertions. Contains business logic such as pagination, price filtering, and variant selection.
- `utils/` — Utilities including `config_reader`, `logger_setup`, and price handling (e.g., `parse_price` returning a `Decimal`).
- `driver/` — Handles browser instantiation based on profiles defined in `config/profiles/*.yaml`.
- `tests/` — Interact only with `flows/` and `data/`. They have no knowledge of specific locators.

## Rules
- Every UI component must be defined as an `Element(name, locators)`, requiring at least 2 locators based on *different* attributes (e.g., `data-*` attributes, CSS selectors, or XPath based on text content). Hardcoded string selectors outside of `Element` definitions are prohibited.
- Fallback mechanisms (iterating through multiple locators) and retry logic (handling environmental instability) are distinct processes. `ElementNotFoundError` should not trigger a retry.
- Monetary values ​​must be handled exclusively using `Decimal`; never use `float`.
- Wait conditions must be based on the state of the element. - `time.sleep` and `wait_for_timeout` are prohibited.
- No `except Exception: pass` blocks.
- Configuration, URLs, and timeouts must come from `config/`; do not hardcode them.

## What to avoid
- Do not weaken or remove assertions just to make a test pass. If a test fails, identify the cause and report it.
- Do not modify `core/` without an explicit request.
- Do not add dependencies without prior approval.
- Do not touch files outside the scope of the assigned task.
- Do not perform `commit` or `push` operations — these are handled by a human.

## Process
Before making any changes, outline the affected files and wait for confirmation.
Each step should result in a small diff. After applying changes, run the relevant tests.
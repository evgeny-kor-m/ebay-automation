# eBay E2E Automation

An E2E framework for eBay built with Playwright and pytest (Python 3.12). It covers searching with price filtering, adding items to the cart, and verifying the total amount. This is a test assignment; architecture is prioritized over the number of test cases.

## Status
Refactoring in progress. The Architecture section describes the TARGET structure.
Many modules in `core/`, `flows/`, `tests/` are still empty stubs.
Before referring to a file or function, verify it exists and is implemented.
`--profile` is not implemented yet: the browser is still taken from `config/appsettings.json`.

## Decisions
Architectural decisions are in `docs/DECISIONS.md` (D1–D7). Follow them; do not re-decide.
Key ones: own DriverFactory + YAML profiles (no pytest-playwright), USD only,
price ranges are skipped, cart check uses subtotal, Guest auth by default,
reports via `make report`.

## Commands
- Unit tests: `pytest tests/unit -q` (or `make unit`)
- E2E tests: `pytest tests/e2e --profile chrome` (planned, `--profile` not implemented yet)
- Parallel execution: `pytest tests/e2e -n 4 --profile chrome` (planned)
- Import validation: `pytest --collect-only -q`
- Allure report of the last run: `make report` / `make report-all`

## Architecture
Layer structure and dependency flow (circular imports are prohibited):
`tests` → `flows` → `pages` → `core`; `utils` is accessible to all layers.

- `core/` — Infrastructure layer, agnostic to eBay: `Element`, `SmartLocator`, retry logic, `BasePage`, custom exceptions.
- `pages/` — Page Object Model: only `Element` definitions and atomic actions. No business logic.
- `flows/` — The 4 functions required by the assignment: authentication, search, cart operations, assertions. Business logic lives here: pagination, price filtering, variant selection.
- `utils/` — `config_reader`, `logger_setup`, price handling (`parse_price` returning `Decimal`).
- `driver/` — Browser instantiation based on profiles in `config/profiles/*.yaml`.
- `tests/` — Use only `flows/` and `data/`. No knowledge of locators.

## Rules
- Every UI element is an `Element(name, locators)` with at least 2 locators based on *different* attributes (`data-*`, CSS, XPath by text). String selectors outside `Element` are prohibited.
- Fallback (iterating locators) and retry (environment instability) are separate mechanisms. `ElementNotFoundError` must not trigger a retry.
- Money is handled only as `Decimal`, never `float`.
- Waits are based on element state; `time.sleep` and `wait_for_timeout` are prohibited.
- No `except Exception: pass`.
- Configuration, URLs and timeouts come from `config/`; never hardcode them.
- Secrets only from `.env`; never in code, logs or reports.
- Use `git mv` to move files (preserves history).
- Preserve LF line endings; never rewrite whole files just to change a few lines.

## What to avoid
- Do not weaken or remove assertions to make a test pass. If a test fails, find the cause and report it.
- Do not modify `core/` without an explicit request.
- Do not add dependencies without prior approval.
- Do not touch files outside the scope of the task.
- Do not `commit` or `push` — a human does that.

## Process
Before making changes, list the affected files and wait for confirmation.
Each step = a small diff. After changes, run the relevant tests.
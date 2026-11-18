# AI Issues

## 2026-11-01 — Architecture Description
Error: The "Files in Repo" table incorrectly listed `core/*` and `flows/*` as implemented layers (showing 0 rows/files) — this description was taken from `CLAUDE.md` rather than the actual codebase.
Discovery: Identified via `ls` + `wc -l` checks. The agent acknowledged the error once presented with the facts.
Conclusion: Always verify the agent’s claims regarding the state of the repository using actual commands.

## 2026-11-01 — cleanup (0.2)
The agent itself detected a side effect (CRLF→LF conversions bloated the diff) and rolled it back.
Removed a dead hook—beyond the scope of the prompt—with an explicit explanation.
Lesson: the repo contains mixed line endings → added `.gitattributes`.

## 2026-11-17 — Exception pickling
The agent identified an issue: exceptions with a custom `__init__` method cannot be reconstructed via `pickle` (which is correct),
and it claimed this poses a risk to `xdist` (an overstatement). Upon further investigation, I checked the `xdist`/`execnet` source code
and ran a test: `xdist` transmits reports as strings and does not use `pickle`.
Conclusion: Always verify findings with facts; the agent may exaggerate the potential consequences.

### 2026-11-18 — SmartLocator real-browser tests
Fixed a test bug where Playwright treated .//span as CSS instead of XPath (only // and .. are recognized as XPath, and // inside a Locator is already relative). Added test 6b specifically for fallback XPath. Verified and added rule to CLAUDE.md
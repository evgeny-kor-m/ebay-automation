# AI Issues

## 2026-11-01 — Architecture Description
Error: The "Files in Repo" table incorrectly listed `core/*` and `flows/*` as implemented layers (showing 0 rows/files) — this description was taken from `CLAUDE.md` rather than the actual codebase.
Discovery: Identified via `ls` + `wc -l` checks. The agent acknowledged the error once presented with the facts.
Conclusion: Always verify the agent’s claims regarding the state of the repository using actual commands.

## 2026-11-01 — cleanup (0.2)
The agent itself detected a side effect (CRLF→LF conversions bloated the diff) and rolled it back.
Removed a dead hook—beyond the scope of the prompt—with an explicit explanation.
Lesson: the repo contains mixed line endings → added `.gitattributes`.
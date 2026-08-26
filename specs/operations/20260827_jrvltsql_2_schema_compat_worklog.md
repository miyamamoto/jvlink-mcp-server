# jvlink-mcp-server / jrvltsql 2.0 schema compatibility worklog

## Start state — 2026-08-27

- Objective: validate and repair `jvlink-mcp-server` against the stable
  `jrvltsql 2.0.0` database contract, including runtime database access,
  schema descriptions, SQL examples, installation documentation, and the
  parent-release synchronization workflow.
- Minimal scope: this repository only. Do not modify the registered JV-Link
  runtime, Wine prefix, service identity, collector database, or KPS feature
  and model jobs. All PostgreSQL probes are read-only.
- Repository: `miyamamoto/jvlink-mcp-server`.
- Worktree: `/home/keiba/scratch/20260827_jvlink_mcp_jrvltsql_2_check`.
- Branch: `fix/jrvltsql-2-schema-compat-20260827`.
- Base and initial HEAD: `42d522b38809378a16690be7d81c055735245855`
  (`origin/master`).
- Current public release: `jvlink-mcp-server v0.6.0`.
- Upstream release under test: `jrvltsql v2.0.0`, annotated tag target
  `4d3a89b382bb0a0b788d68093bc16f0f8dd950f5`.
- Implementation model: Codex directly; no delegated coding session.

## Initial observations

- GitHub has no open pull request. The latest ten scheduled `Sync with
  jrvltsql` runs failed after all 68 selected unit tests passed. The workflow
  attempted to commit and tag directly on protected `master`; GitHub rejected
  it because changes must pass through a pull request and required checks.
- `.github/jrvltsql_version.txt` still records `v1.6.0`. The workflow tests
  only this repository's mocks and does not install the detected upstream
  release or exercise an upstream-generated database.
- Exact-base local non-live suite: `187 passed, 8 skipped`; the only warning is
  the unsupported pytest option `collect_ignore_glob`.
- A read-only probe against the development PostgreSQL database written by
  exact `jrvltsql 2.0.0` found two concrete compatibility defects:
  1. PostgreSQL returns unquoted table identifiers in lower case. `get_tables`
     returns `nl_se`, while `get_table_schema("NL_SE")` performs a
     case-sensitive whitelist comparison and rejects the documented table.
  2. High-level APIs use SQLite/DuckDB `?` parameter markers with pg8000.
     Parameterized favorite, jockey, frame, horse-history, and sire queries
     fail on PostgreSQL. A parameter-free frame query and raw SELECT work.
- The same database has 130 public tables and positive `NL_RA`, `NL_SE`, and
  `NL_UM` counts. Dangerous DML was rejected before database execution.
- Static surfaces contain older assumptions, including `jrvltsql v1.6`, the
  claim that all columns are text, legacy logical table names in feature SQL,
  and claims that jrvltsql writes DuckDB. These require a bounded source-of-
  truth audit against stable 2.0.0 before editing.

## Validation and STOP conditions

- Add the smallest failing regression coverage before production fixes and
  record the exact base failure.
- Required closure: SQLite and PostgreSQL unit/integration behavior, actual
  PostgreSQL 2.0.0 read-only probes, MCP stdio initialization/list/call,
  package build, full non-live suite, exact-SHA review, CI, zero unresolved
  threads, and clean worktree.
- Stop on any database mutation, provider acquisition, credential exposure,
  collector identity drift, failed executed CI step, or a schema fact that
  cannot be established from the exact upstream release/database.

## Next safe action

Commit and push this start record, open a draft PR, then inventory every
runtime and public reference to the old schema before writing the minimal red
tests.

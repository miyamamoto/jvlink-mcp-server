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

Freeze the aggregated candidate, commit and push it to PR #22, then run the
repository's workflow-equivalent checks and one final exact-SHA review. Do not
change the development collector or either PostgreSQL database.

## Audit and red-first evidence — 2026-08-27

- The exact upstream 2.0.0 DDL was re-read from tag target
  `4d3a89b382bb0a0b788d68093bc16f0f8dd950f5`. Its executable `SCHEMAS`
  registry contains 80 JRA tables and every table has a primary key. The MCP
  static resource exposes only 70 JRA tables and many of their key definitions
  are from an older generation.
- A compact red-first run was made before production changes:
  `pytest -q tests/test_additional_coverage.py::TestConnectionPostgreSQL
  tests/test_jrvltsql_2_contract.py` -> `22 failed`.
- The failures independently bind four grouped regressions:
  1. qmark parameters reached pg8000 unchanged instead of `%s`;
  2. PostgreSQL lower-case catalog names were not canonicalized and documented
     upper-case names were rejected;
  3. representative changed keys in both static schema surfaces disagreed
     with 2.0.0;
  4. the parent sync still pushed and tagged protected `master` directly,
     did not install the detected jrvltsql release, and public feature examples
     referenced retired logical table names.
- This is a batched repair after collecting the related findings; no
  production source was changed during the red run.

## Aggregated implementation and validation — 2026-08-27

- Added an executable 80-table JRA contract pinned to stable `jrvltsql 2.0.0`
  (`4d3a89b382bb0a0b788d68093bc16f0f8dd950f5`) and applied it to both schema
  resources. The generated upstream SQLite schema and MCP metadata now agree
  on all table names and primary-key columns.
- Fixed PostgreSQL catalog-name canonicalization and converted unquoted qmark
  parameters to pg8000 `%s` markers. The connection remains read-only.
- Replaced retired logical feature SQL/table identifiers with physical 2.0
  identifiers; removed four ignored legacy executable query suites that were
  not collected by pytest and failed against the current package.
- Corrected package/install surfaces: version `0.7.0`, exact upstream sync
  lock, packaged feature data, Python dependency bounds, installer guidance,
  and protected-branch-safe parent release PR workflow.
- Hardened the updater with installed-package version fallback, PEP 440
  comparison, user-cache state, and a fail-closed installed-wheel manual
  update response. Its new negative regressions were observed red before the
  repair (unknown/invalid version and installed-wheel git-update paths).

### JRA-only scope correction

- A read-only examination of the existing NAR surface showed that it had been
  inferred from JRA table names and did not match the separate provider's
  physical schema. The user then confirmed that this MCP is not intended to
  support NAR.
- Added a single public-surface regression first. Before removal it failed with
  `{'nar_favorite_performance', 'nar_horse_history', 'nar_jockey_stats'}` still
  registered.
- A second same-root negative was added after the mixed-provider development
  PostgreSQL revealed 43 physical NAR tables through generic discovery. Before
  the filter it failed with `['NL_RA', 'NL_RA_NAR']` instead of the JRA-only
  list. Generic schema access, SQL execution, and the SQL validator now reject
  NAR physical identifiers while ordinary JRA SELECT queries remain green.
- Removed NAR MCP tools, resources, high-level APIs, schema entries, venue
  constants, query templates, sample-data paths, live probes, and active
  documentation. The wheel must expose JRA only; NAR remains the responsibility
  of its separate provider stack.

### Completed evidence on the uncommitted aggregate

- Focused contract suite: `92 passed`.
- Full default Python 3.11 suite: `183 passed, 8 skipped`.
- Fresh isolated Python 3.12.11 suite: `183 passed, 8 skipped`.
- Upstream-generated 80-table SQLite MCP stdio smoke: 22 tools, 6 resources,
  zero NAR surface, `NL_SE` 103 columns, and successful favorite analysis.
- Development PostgreSQL read-only MCP stdio smoke: 130 physical database
  tables, exactly 80 JRA tables exposed by the MCP, `NL_SE` 103 columns,
  successful positive-row favorite analysis, zero NAR tools/tables, and an
  explicit NAR query rejected. No database mutation or collector action was
  performed.
- Fresh wheel/sdist build succeeded. Isolated Python 3.12 wheel install reports
  metadata/package/updater version `0.7.0`, 22 tools, 80 static JRA tables, and
  zero NAR runtime-source hits.
- `git diff --check` passes. Repository-wide Ruff currently reports 65
  pre-existing style findings and is not configured as the repository test
  gate; no bulk formatting change is included in this iteration.

## Aggregated PR review repair — 2026-08-27

- Six actionable review findings were collected before changing the candidate:
  parent-sync version surfaces/post-update validation, a Markdown fence,
  unconfirmed result filtering, PostgreSQL dollar-quoted strings, case-folded
  column descriptions, and cross-family schema-map pollution.
- The first compact regression run on candidate
  `779e4d4f1d4062fd9d47906dceca7e5688d0f9d3` failed exactly five grouped
  assertions (`5 failed, 21 passed`): lower-case PostgreSQL column description,
  dollar-quoted question marks, incomplete sync workflow, polluted family maps,
  and the public result-query/fence contract.
- After the documentation failure exposed the same `KakuteiJyuni IS NOT NULL`
  condition in executable query surfaces, the existing contract test was
  minimally extended across those surfaces. It failed first on
  `data/feature_importance.json`, proving that the executable/public examples
  still admitted unconfirmed `KakuteiJyuni = 0` rows.
- The batched repair now preserves PostgreSQL dollar-quoted text while adapting
  actual qmark parameters, performs case-insensitive description lookup,
  applies the 80-table contract only after the three family maps are combined,
  and uniformly requires `KakuteiJyuni > 0` for result analysis.
- The parent-sync proposal now updates every version/contract surface, records
  the exact upstream commit, regenerates `uv.lock`, and runs the full suite plus
  a package build on the mutated tree before it can commit or push a PR.
- Post-repair compact result: `26 passed`; `git diff --check` passes. Full
  candidate validation then passed on both supported interpreters: Python 3.11
  and isolated Python 3.12.11 each reported `186 passed, 8 skipped`.
- The mutated workflow parses as YAML, and a fresh `0.7.0` wheel and sdist both
  build successfully. Actual PostgreSQL smoke, PR-thread closure, and the final
  exact-SHA gate remain pending.
- The review repair was committed as code candidate
  `00052aa8bb0baf6d1f7b9b5073a4915f1eadcdf9`. Its read-only MCP stdio probe
  against the mixed-provider development PostgreSQL passed: 22 tools, exactly
  80 exposed JRA tables, no exposed NAR table, 103 `NL_SE` columns, a positive
  confirmed-result count, and explicit `NL_RA_NAR` rejection. The first two
  harness attempts were discarded: one sourced a non-shell env file and one
  used the container port instead of the published host port; neither changed
  the database, and the successful probe loaded dotenv without logging values.
- PR-thread closure and the final exact-SHA CI/review gate remain pending.

## Final exact-SHA review follow-up — 2026-08-27

- CI passed on `23aedcb7931e654cf10b3c0a7d888ec085175b36`, the seven prior review
  threads were answered/resolved, and one final Codex review was requested.
- That review found two distinct P2 regressions. Both were reproduced red
  before production changes (`2 failed`): an installed wheel beneath an
  unrelated tagged checkout inherited the host repository's `v99.0.0`, and
  the distance suitability feature-rate example lacked a confirmed-result
  predicate.
- The batched repair treats Git metadata as authoritative only when
  `PROJECT_ROOT` is itself a source checkout (`pyproject.toml` plus `.git`);
  installed distributions use package metadata instead. All feature examples
  that derive win rates now require `KakuteiJyuni > 0`, including distance,
  popularity, and sire groupings.
- Focused post-repair result: `44 passed`. A final commit, both full Python
  suites, CI, thread closure, and clean exact-SHA gate remain pending.

## Second final-review closure — 2026-08-27

- The exact `70419fb33d445caa613d4bb320eece8ad2dcefc0` review identified two
  remaining P2 classes: the automated upstream gate checked only table/primary
  key identity, and the NAR guard searched literals/comments/aliases instead of
  physical table-reference positions.
- Both compact regressions were confirmed red before production changes
  (`2 failed`): a schema with `NL_SE.KakuteiJyuni TEXT` and no `Ninki` returned
  no errors, while `SELECT 'NL_RA_NAR' AS source FROM NL_RA` raised the NAR
  rejection.
- The upstream contract now validates the SQLite names/types of the columns
  directly consumed by public high-level APIs in `NL_RA`, `NL_SE`, and `NL_UM`,
  in addition to the complete 80-table primary-key registry. A freshly
  downloaded official `jrvltsql v2.0.0` wheel generated a new 80-table SQLite
  database and passed the expanded validator.
- NAR rejection now lexes `FROM`/`JOIN` table positions after masking SQL
  string/dollar literals and comments. Direct physical NAR references still
  fail; the same token in a result literal, alias, or comment remains valid.
- Focused post-repair result: `39 passed`. Final full suites, commit, CI,
  review/thread closure, and release gate remain pending.
- Before accepting that repair, a bounded self-review exercised PostgreSQL's
  legal nested block comments. The first implementation accepted a physical
  NAR table after `/* outer /* nested */ still outer */`; the added regression
  failed red. Block-comment masking now tracks nesting depth, and the focused
  JRA-only/schema/connection selection remains green (`39 passed`).

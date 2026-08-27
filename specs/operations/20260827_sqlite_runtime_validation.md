# SQLite runtime validation — 2026-08-27

## Scope and identity

- Purpose: create a durable SQLite input and verify the released JRA-only MCP
  through the actual stdio protocol. No PostgreSQL, collector, Wine prefix,
  provider identity, or credential state is modified.
- Repository: `miyamamoto/jvlink-mcp-server`.
- Worktree: `/home/keiba/scratch/20260827_jvlink_mcp_sqlite_validation`.
- Branch: `ops/sqlite-runtime-validation-20260827`.
- Base: `89c94e0b19274543d37ea35ff44267dcb31f6564`.
- Production release: `v0.7.0`, annotated-tag target
  `89c94e0b19274543d37ea35ff44267dcb31f6564`.

## Database materialization

- Read-only source: the fresh provider SQLite generated during the jrvltsql
  2.0.0 release validation. Before copying it reported 80 tables, zero
  NAR-shaped tables, `NL_RA=72`, `NL_SE=943`, `integrity_check=ok`, and zero
  foreign-key violations.
- Durable destination:
  `/home/keiba/.local/share/jvlink-mcp-server/data/keiba.db`.
- The destination was created with SQLite's online backup API rather than a
  byte copy. It was closed in `DELETE` journal mode so the runtime depends on a
  single database file rather than retained WAL sidecars.
- Final destination evidence: 50,511,872 bytes, SHA-256
  `dc6554324cd5f40a59c3ba9818b3166c9a88af583ff69c42e35fc666e77be9ee`,
  `integrity_check=ok`, 80 tables, zero NAR-shaped tables, `NL_RA=72`, and
  `NL_SE=943`. `NL_RA` covers the provider dates 2026-08-22 through
  2026-08-23. This is a functional real-provider validation database, not a
  claim of historical completeness.

## Installed runtime and configuration

- Runtime path:
  `/home/keiba/.local/share/jvlink-mcp-server/runtime-v0.7.0/.venv`.
- Python: 3.12.11. Installed package: `jvlink-mcp-server==0.7.0` directly from
  tag `v0.7.0`; PEP 610 provenance resolves to exact merge
  `89c94e0b19274543d37ea35ff44267dcb31f6564`.
- Stable launcher: `/home/keiba/.local/bin/jvlink-mcp-sqlite`.
- Non-secret environment reference:
  `/home/keiba/.config/jvlink-mcp-server/sqlite.env`.
- Codex config `/home/keiba/.codex/config.toml` now registers
  `mcp_servers.jvlink` with the stable launcher. The TOML parses successfully.
  MCP discovery is process-start scoped, so a new Codex session is required to
  observe the added server.

## Runtime verification

- Direct installed-package probe exposed 22 tools, 6 resources, and exactly 80
  JRA tables. The read-only query over `NL_RA` returned 72 rows with dates
  2026-08-22 through 2026-08-23.
- An independent MCP client initialized the launcher over stdio, listed 22
  tools and 6 resources, observed zero `nar_` tools, invoked the public
  `keiba_data_search` tool, and received the SQLite `NL_RA` count of 72 without
  an MCP error.
- The first client call deliberately attempted the internal Python function
  name `execute_safe_query`; stdio correctly reported that it is not a public
  tool. Listing the protocol surface identified the registered public name
  `keiba_data_search`, after which the paired call passed.

## Adjacent finding and follow-up

- The released MCPB manifest still advertises historical names such as
  `execute_safe_query`, while the actual FastMCP registrations expose
  `keiba_data_search`, `favorite_performance`, and the remaining 20 tool names.
  Runtime clients use `tools/list`, so the installed stdio server and SQLite
  query path are functional; the static bundle metadata is nevertheless stale.
- Treat the manifest mismatch as a separate minimal patch iteration. Add one
  red-first contract comparing generated manifest tool names with actual MCP
  registrations, update the manifest generator, and publish a patch release
  only after exact-SHA tests/review/CI. Do not alter the validated SQLite file
  while fixing metadata.

## Next safe command and stop conditions

- Next safe validation after starting a new Codex session: list MCP tools for
  `jvlink`, then call `keiba_data_search` with
  `SELECT COUNT(*) AS races FROM NL_RA` and require 72.
- Stop if the destination hash changes unexpectedly, SQLite integrity is not
  `ok`, the tool list contains a `nar_` prefix, or the installed package
  provenance is not the exact v0.7.0 merge above.

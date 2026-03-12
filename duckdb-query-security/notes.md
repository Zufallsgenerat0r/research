# Research Notes: DuckDB Query Security for Untrusted Users

## Setup
- DuckDB v1.5.0 installed via pip on Linux
- All experiments run against in-memory databases (`:memory:`) unless noted

## Key Findings

### 1. Read-only connections (`read_only=True`)
- **Works for file-based databases only.** In-memory databases cannot be opened read-only (raises `CatalogException`).
- `access_mode='READ_ONLY'` cannot be changed at runtime — must be set at connection time.
- Blocks: INSERT, UPDATE, DELETE, CREATE TABLE, DROP TABLE, ALTER TABLE, CREATE INDEX.
- Does NOT block: SELECT, CTEs, aggregations, window functions, etc.
- **Limitation:** Not useful for sandboxing in-memory analytical queries since you can't open `:memory:` as read-only. More relevant when exposing a pre-built database file.

### 2. File/network access restrictions
- `enable_external_access` (default: `true`) — master switch for all file/network I/O.
- When `false`, blocks: `read_csv`, `read_parquet`, `COPY TO`, `ATTACH` (file), `INSTALL`, `LOAD`.
- `allowed_paths` — list of specific files whitelisted even when external access is off.
  - Type: `VARCHAR[]` — must use list syntax: `SET allowed_paths=['/path/to/file']`
  - Description from duckdb_settings: "List of files that are ALWAYS allowed to be queried - even when enable_external_access is false"
- `allowed_directories` — list of directory prefixes whitelisted.
  - Same semantics as `allowed_paths` but for directory trees.
- **CRITICAL ORDER DEPENDENCY:** `allowed_paths` and `allowed_directories` MUST be set BEFORE `enable_external_access=false`. DuckDB raises `InvalidInputException` if you try to set them after.
- Path traversal (`../`) is properly blocked.
- `allowed_extensions` does NOT exist in v1.5.0 — the setting is called `allow_community_extensions` (boolean).

### 3. Configuration locking (`lock_configuration=true`)
- Once set, prevents ALL `SET` commands including trying to set `lock_configuration=false`.
- This is irreversible for the lifetime of the connection.
- Must be the LAST setting configured — set everything else first, then lock.
- Prevents: changing threads, memory_limit, enable_external_access, allow_community_extensions, etc.
- Does NOT prevent: DDL (CREATE TABLE), DML (INSERT), queries, PRAGMA reads.

### 4. Resource limits
- `threads` (default: number of CPU cores) — limits worker threads.
- `memory_limit` (default: 80% of system RAM) — limits DuckDB's memory usage.
- `max_temp_directory_size` (default: 90% of available disk) — limits spill-to-disk.
- All three can be locked via `lock_configuration`.

### 5. Query timeouts via `connection.interrupt()`
- DuckDB has no built-in query timeout setting.
- `connection.interrupt()` can be called from another thread to cancel a running query.
- Raises `duckdb.InterruptException` in the thread running the query.
- Connection remains usable after interrupt — no need to reconnect.
- `threading.Timer` provides a clean implementation pattern.
- Works on: long SELECT queries, recursive CTEs, cross joins, etc.

### 6. Attack vectors tested
- **File exfiltration** (`read_csv('/etc/passwd')`): BLOCKED by `enable_external_access=false`
- **File write** (`COPY TO '/tmp/evil'`): BLOCKED by `enable_external_access=false`
- **Extension install** (`INSTALL httpfs`): BLOCKED by `enable_external_access=false`
- **Extension load** (`LOAD httpfs`): BLOCKED by `enable_external_access=false`
- **Attach external DB** (`ATTACH '/tmp/evil.db'`): BLOCKED by `enable_external_access=false`
- **Config escape** (`SET enable_external_access=true`): BLOCKED by `lock_configuration=true`
- **Path traversal** (`'../etc/passwd'`): BLOCKED by DuckDB's path resolution
- **CPU DoS** (recursive CTE bomb): Mitigated by `connection.interrupt()` timeout
- **Memory DoS** (huge allocations): Mitigated by `memory_limit`
- **Disk DoS** (spill files): Mitigated by `max_temp_directory_size`
- **Attach :memory:**: ALLOWED (harmless — just creates another in-memory database)
- **CREATE MACRO**: ALLOWED (harmless — only affects the in-memory session)
- **PRAGMA reads** (`PRAGMA version`): ALLOWED (read-only, low risk)
- **duckdb_settings()**: ALLOWED (shows configuration, low sensitivity)

### 7. Correct configuration order
The order of SET commands matters:
1. `SET allowed_paths=[...]` and `SET allowed_directories=[...]` (if needed)
2. `SET enable_external_access=false`
3. `SET threads=N`, `SET memory_limit='...'`, `SET max_temp_directory_size='...'`
4. `SET allow_community_extensions=false`
5. `SET lock_configuration=true` (MUST BE LAST)

### 8. Gotchas discovered
- `allowed_paths` requires `VARCHAR[]` type — string value causes cast error
- `allowed_paths` cannot be passed via config dict to `duckdb.connect()` — must use SQL SET
- `read_only=True` on `:memory:` raises an error, not a silent no-op
- `enable_external_access` cannot be toggled at runtime (only set once before first use)
- `allowed_extensions` doesn't exist — the setting is `allow_community_extensions`
- Memory limit displays as MiB (e.g., "244.1 MiB" for 256MB input)

# DuckDB Query Security: Sandboxing Untrusted User Queries

<!-- AI-GENERATED-NOTE -->
> [!NOTE]
> This is an AI-generated research report. All text and code in this report was created by an LLM (Large Language Model). For more information on how these reports are created, see the [main research repository](https://github.com/simonw/research).
<!-- /AI-GENERATED-NOTE -->

## Overview

This investigation explores how to safely run DuckDB queries from untrusted users. DuckDB provides several built-in security mechanisms that, when layered together, create a robust sandbox for executing arbitrary SQL against in-memory or controlled datasets.

**DuckDB version tested:** 1.5.0

## Security Layers

### 1. Read-Only Connections

```python
con = duckdb.connect("database.duckdb", read_only=True)
```

| Feature | Details |
|---------|---------|
| **What it blocks** | INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, and all other DDL/DML |
| **What it allows** | SELECT, CTEs, aggregations, window functions, joins |
| **Limitation** | Only works with file-based databases; `:memory:` cannot be read-only |
| **Use case** | Exposing a pre-built database file to users for querying |

### 2. File & Network Access Restrictions

```python
con = duckdb.connect(":memory:")
# Optional: whitelist specific paths BEFORE disabling external access
con.execute("SET allowed_directories=['/data/user_uploads']")
con.execute("SET allowed_paths=['/data/shared/lookup.csv']")
# Disable all external access
con.execute("SET enable_external_access=false")
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enable_external_access` | bool | `true` | Master switch for all file/network I/O |
| `allowed_paths` | VARCHAR[] | `[]` | Specific files accessible even when external access is off |
| `allowed_directories` | VARCHAR[] | `[]` | Directory trees accessible even when external access is off |

**What gets blocked** when `enable_external_access=false`:
- `read_csv()`, `read_parquet()`, `read_json()` — all file readers
- `COPY ... TO` — file writes
- `ATTACH '/path/to/db'` — external database access
- `INSTALL` / `LOAD` — extension management
- HTTP/S3 access via extensions

**Critical ordering requirement:** `allowed_paths` and `allowed_directories` **must** be set **before** `enable_external_access=false`. DuckDB will reject changes to these settings once external access is disabled.

### 3. Configuration Locking

```python
con.execute("SET lock_configuration=true")
```

Once locked, **all** `SET` commands are rejected, including attempts to unlock. This prevents users from bypassing any security settings via SQL injection of `SET` commands.

Must be the **last** setting you configure.

### 4. Resource Limits

```python
con.execute("SET threads=2")
con.execute("SET memory_limit='256MB'")
con.execute("SET max_temp_directory_size='512MB'")
```

| Setting | Default | Description |
|---------|---------|-------------|
| `threads` | CPU core count | Maximum worker threads |
| `memory_limit` | ~80% of system RAM | Maximum memory usage |
| `max_temp_directory_size` | ~90% of available disk | Maximum spill-to-disk usage |

### 5. Query Timeouts

DuckDB has no built-in timeout setting, but `connection.interrupt()` can be called from a timer thread:

```python
import threading
import duckdb

con = duckdb.connect(":memory:")
timer = threading.Timer(5.0, con.interrupt)
timer.start()
try:
    result = con.execute(long_running_query)
    timer.cancel()
except duckdb.InterruptException:
    print("Query timed out")
```

The connection remains usable after an interrupt — no reconnection needed.

## Recommended Configuration Order

```
1. SET allowed_paths=[...]           # (optional) whitelist files
2. SET allowed_directories=[...]     # (optional) whitelist dirs
3. SET enable_external_access=false  # kill all external I/O
4. SET allow_community_extensions=false
5. SET threads=N                     # limit CPU
6. SET memory_limit='256MB'          # limit RAM
7. SET max_temp_directory_size='512MB' # limit disk
8. SET lock_configuration=true       # MUST BE LAST — locks everything
```

## Production Wrapper: `SandboxedDuckDB`

The [`sandboxed_duckdb.py`](sandboxed_duckdb.py) module provides a ready-to-use wrapper class:

```python
from sandboxed_duckdb import SandboxedDuckDB, QueryTimeoutError

with SandboxedDuckDB(
    timeout=10.0,
    memory_limit="256MB",
    threads=2,
    allowed_directories=["/data/uploads"],
) as db:
    # Load user's data
    db.execute("CREATE TABLE data AS SELECT * FROM read_csv('/data/uploads/file.csv')")

    # Run user's query safely
    try:
        result = db.execute(user_query).fetchall()
    except QueryTimeoutError:
        print("Query took too long")
    except duckdb.PermissionException:
        print("Query tried to access restricted resources")
```

### Features
- Automatic configuration of all security layers in correct order
- Query timeout via `connection.interrupt()` with `threading.Timer`
- Custom `QueryTimeoutError` exception for timeout handling
- Context manager support (`with` statement)
- Connection reuse after timeouts
- Optional path/directory whitelisting

Also includes `run_sandboxed_query()` for one-shot queries:

```python
from sandboxed_duckdb import run_sandboxed_query

rows = run_sandboxed_query(
    "SELECT * FROM data WHERE x > 10",
    timeout=5.0,
    setup_queries=["CREATE TABLE data AS SELECT range AS x FROM range(100)"],
)
```

## Attack Vectors Tested

| Attack | Mitigation | Result |
|--------|-----------|--------|
| Read `/etc/passwd` via `read_csv()` | `enable_external_access=false` | BLOCKED |
| Write files via `COPY TO` | `enable_external_access=false` | BLOCKED |
| Install malicious extension | `enable_external_access=false` | BLOCKED |
| Attach external database | `enable_external_access=false` | BLOCKED |
| Re-enable access via `SET` | `lock_configuration=true` | BLOCKED |
| Path traversal (`../`) | DuckDB path resolution | BLOCKED |
| CPU exhaustion (recursive CTE) | `connection.interrupt()` timeout | MITIGATED |
| Memory exhaustion | `memory_limit` | MITIGATED |
| Disk exhaustion (spill files) | `max_temp_directory_size` | MITIGATED |

## Files

| File | Description |
|------|-------------|
| `sandboxed_duckdb.py` | Production-ready `SandboxedDuckDB` wrapper class with self-tests |
| `demo_01_read_only.py` | Demo: read-only connections |
| `demo_02_external_access.py` | Demo: file/network access restrictions and path whitelisting |
| `demo_03_config_locking.py` | Demo: configuration locking |
| `demo_04_query_timeout.py` | Demo: query timeouts via `connection.interrupt()` |
| `demo_05_resource_limits.py` | Demo: thread, memory, and disk limits |
| `notes.md` | Detailed research notes and findings |

## Known CVEs

| CVE | Versions | Description |
|-----|----------|-------------|
| CVE-2024-41672 | <= 1.0.0 | `sniff_csv()` bypassed `enable_external_access=false` to read filesystem content. Fixed in 1.1.0. |
| CVE-2025-59037 | npm 1.3.3 | Supply chain attack on npm packages (not an engine vulnerability). Fixed in 1.3.4+. |
| CVE-2024-9264 | N/A | Grafana SQL injection via DuckDB (Grafana bug, not DuckDB). |

DuckDB's own documentation warns: these settings "cannot provide complete protection against all attack vectors." For robust security, **combine with OS/container-level sandboxing** (seccomp, namespaces, Docker with restricted capabilities).

## Remaining Considerations

- **SQL injection in the application layer**: The sandbox protects DuckDB, but your application must still use parameterized queries to prevent SQL injection when building queries from user input.
- **Information leakage**: `duckdb_settings()` and `PRAGMA version` are accessible and reveal configuration details. For high-security environments, consider wrapping queries to filter these.
- **Denial of service via result size**: A query like `SELECT * FROM range(1000000000)` produces huge output. Consider adding application-level `LIMIT` enforcement or result-size caps.
- **No per-query memory limits**: `memory_limit` is per-connection, not per-query. One expensive query can consume the entire budget.
- **`connection.interrupt()` reliability**: Not instantaneous — DuckDB must process at least one tuple chunk first. There are open GitHub issues (#15925, #10699) about unreliable interrupt and occasional race-condition crashes. For critical deployments, add a hard process-kill fallback.
- **OS-level sandboxing**: For maximum security, run DuckDB inside a container or process sandbox (seccomp, namespaces) in addition to the DuckDB-level settings.

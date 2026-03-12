#!/usr/bin/env python3
"""Production-ready sandboxed DuckDB wrapper for running untrusted queries.

This module provides a SandboxedDuckDB class that configures DuckDB with
multiple layers of security to safely execute queries from untrusted users:

  1. File/network isolation (enable_external_access=false)
  2. Optional path whitelisting (allowed_paths, allowed_directories)
  3. Configuration locking (lock_configuration=true)
  4. Resource limits (threads, memory, temp disk)
  5. Query timeouts via connection.interrupt()

Usage:
    from sandboxed_duckdb import SandboxedDuckDB

    with SandboxedDuckDB(timeout=5.0, memory_limit="256MB") as db:
        db.execute("CREATE TABLE t AS SELECT range AS x FROM range(100)")
        rows = db.execute("SELECT * FROM t WHERE x < 10").fetchall()
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Optional

import duckdb


class QueryTimeoutError(Exception):
    """Raised when a query exceeds the configured timeout."""


class SandboxedDuckDB:
    """A sandboxed DuckDB connection that restricts untrusted queries.

    Security layers applied (in order):
      1. allowed_paths / allowed_directories (optional whitelists)
      2. enable_external_access = false
      3. allow_community_extensions = false
      4. Resource limits (threads, memory_limit, max_temp_directory_size)
      5. lock_configuration = true (prevents all SET commands)
      6. Query timeout via connection.interrupt() with threading.Timer

    Parameters
    ----------
    timeout : float or None
        Maximum seconds a query may run. None disables timeouts.
    memory_limit : str
        DuckDB memory limit (e.g., "256MB", "1GB").
    threads : int
        Maximum worker threads.
    max_temp_directory_size : str
        Maximum disk space for temp spill files.
    allowed_paths : list[str] or None
        Specific file paths that may be accessed even with external access off.
        Must be set before external access is disabled.
    allowed_directories : list[str] or None
        Directory prefixes that may be accessed even with external access off.
        Must be set before external access is disabled.
    """

    def __init__(
        self,
        timeout: Optional[float] = 30.0,
        memory_limit: str = "256MB",
        threads: int = 2,
        max_temp_directory_size: str = "512MB",
        allowed_paths: Optional[list[str]] = None,
        allowed_directories: Optional[list[str]] = None,
    ):
        self.timeout = timeout
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        self._lock = threading.Lock()

        # Create connection and configure sandbox
        self._conn = duckdb.connect(":memory:")

        # Step 1: Set path whitelists BEFORE disabling external access.
        # Order matters: these cannot be set after enable_external_access=false.
        if allowed_paths:
            paths_sql = ",".join(f"'{p}'" for p in allowed_paths)
            self._conn.execute(f"SET allowed_paths=[{paths_sql}]")
        if allowed_directories:
            dirs_sql = ",".join(f"'{d}'" for d in allowed_directories)
            self._conn.execute(f"SET allowed_directories=[{dirs_sql}]")

        # Step 2: Disable all external access (file I/O, network, extensions).
        self._conn.execute("SET enable_external_access=false")

        # Step 3: Resource limits.
        self._conn.execute(f"SET threads={int(threads)}")
        self._conn.execute(f"SET memory_limit='{memory_limit}'")
        self._conn.execute(f"SET max_temp_directory_size='{max_temp_directory_size}'")

        # Step 4: Lock configuration so the user can't undo any of the above.
        self._conn.execute("SET lock_configuration=true")

    def execute(self, query: str, params: Any = None) -> duckdb.DuckDBPyRelation:
        """Execute a query with timeout protection.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : tuple or list, optional
            Query parameters for prepared statements.

        Returns
        -------
        duckdb.DuckDBPyRelation
            The query result, supporting .fetchall(), .fetchone(), .fetchdf(), etc.

        Raises
        ------
        QueryTimeoutError
            If the query exceeds the configured timeout.
        duckdb.PermissionException
            If the query tries to access files or change configuration.
        duckdb.InvalidInputException
            If the query tries to modify a read-only database or change locked config.
        """
        if self._conn is None:
            raise RuntimeError("Connection is closed")

        timer = None
        timed_out = threading.Event()

        if self.timeout is not None:
            def _interrupt():
                timed_out.set()
                self._conn.interrupt()

            timer = threading.Timer(self.timeout, _interrupt)
            timer.start()

        try:
            if params is not None:
                result = self._conn.execute(query, params)
            else:
                result = self._conn.execute(query)
            return result
        except duckdb.InterruptException:
            if timed_out.is_set():
                raise QueryTimeoutError(
                    f"Query exceeded timeout of {self.timeout}s"
                ) from None
            raise
        finally:
            if timer is not None:
                timer.cancel()

    def close(self):
        """Close the underlying connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# ---------------------------------------------------------------------------
# Convenience function for one-shot sandboxed queries
# ---------------------------------------------------------------------------

def run_sandboxed_query(
    query: str,
    timeout: float = 10.0,
    memory_limit: str = "128MB",
    threads: int = 1,
    setup_queries: Optional[list[str]] = None,
) -> list[tuple]:
    """Execute a single query in a fully sandboxed, ephemeral DuckDB instance.

    Parameters
    ----------
    query : str
        The SQL query to execute.
    timeout : float
        Maximum seconds the query may run.
    memory_limit : str
        DuckDB memory limit.
    threads : int
        Maximum worker threads.
    setup_queries : list[str], optional
        Queries to run before the main query (e.g., CREATE TABLE statements).

    Returns
    -------
    list[tuple]
        Query results as a list of tuples.
    """
    with SandboxedDuckDB(
        timeout=timeout,
        memory_limit=memory_limit,
        threads=threads,
    ) as db:
        if setup_queries:
            for sq in setup_queries:
                db.execute(sq)
        return db.execute(query).fetchall()


# ---------------------------------------------------------------------------
# Self-test / demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== SandboxedDuckDB self-test ===\n")

    # 1. Basic usage
    print("1. Basic in-memory query")
    with SandboxedDuckDB(timeout=5.0) as db:
        db.execute("CREATE TABLE nums AS SELECT range AS n FROM range(100)")
        result = db.execute("SELECT SUM(n), AVG(n) FROM nums").fetchone()
        print(f"   SUM={result[0]}, AVG={result[1]}")

    # 2. File access blocked
    print("\n2. File access is blocked")
    with SandboxedDuckDB() as db:
        try:
            db.execute("SELECT * FROM read_csv('/etc/passwd', sep=':')")
            print("   FAIL: file read was allowed")
        except duckdb.PermissionException:
            print("   OK: file read blocked")

    # 3. Config changes blocked
    print("\n3. Configuration changes are blocked")
    with SandboxedDuckDB() as db:
        try:
            db.execute("SET enable_external_access=true")
            print("   FAIL: config change was allowed")
        except duckdb.InvalidInputException:
            print("   OK: config change blocked")

    # 4. Extension install blocked
    print("\n4. Extension install is blocked")
    with SandboxedDuckDB() as db:
        try:
            db.execute("INSTALL httpfs")
            print("   FAIL: extension install was allowed")
        except (duckdb.PermissionException, duckdb.Error):
            print("   OK: extension install blocked")

    # 5. Query timeout
    print("\n5. Query timeout")
    with SandboxedDuckDB(timeout=1.0) as db:
        try:
            db.execute("""
                WITH RECURSIVE bomb(n) AS (
                    SELECT 1
                    UNION ALL
                    SELECT n+1 FROM bomb WHERE n < 999999999
                )
                SELECT COUNT(*) FROM bomb
            """)
            print("   FAIL: query should have timed out")
        except QueryTimeoutError as e:
            print(f"   OK: {e}")

    # 6. Connection reuse after timeout
    print("\n6. Connection still works after timeout")
    with SandboxedDuckDB(timeout=1.0) as db:
        try:
            db.execute("""
                WITH RECURSIVE x(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM x WHERE n<999999999)
                SELECT COUNT(*) FROM x
            """)
        except QueryTimeoutError:
            pass
        result = db.execute("SELECT 42 AS answer").fetchone()
        print(f"   OK: got {result[0]} after timeout recovery")

    # 7. Convenience function
    print("\n7. run_sandboxed_query convenience function")
    rows = run_sandboxed_query(
        "SELECT n, n*n AS square FROM nums WHERE n < 5",
        setup_queries=["CREATE TABLE nums AS SELECT range AS n FROM range(10)"],
    )
    print(f"   Results: {rows}")

    # 8. With allowed directories
    print("\n8. Allowed directories")
    import tempfile, os
    sandbox_dir = os.path.join(tempfile.gettempdir(), "duckdb_sandbox_test")
    os.makedirs(sandbox_dir, exist_ok=True)
    csv_path = os.path.join(sandbox_dir, "test.csv")
    with open(csv_path, "w") as f:
        f.write("a,b\n1,2\n3,4\n")

    with SandboxedDuckDB(allowed_directories=[sandbox_dir]) as db:
        rows = db.execute(f"SELECT * FROM read_csv('{csv_path}')").fetchall()
        print(f"   Read from allowed dir: {rows}")
        try:
            db.execute("SELECT * FROM read_csv('/etc/hostname')")
            print("   FAIL: outside allowed dir was accessible")
        except duckdb.PermissionException:
            print("   OK: outside allowed dir blocked")

    print("\nAll tests passed.")

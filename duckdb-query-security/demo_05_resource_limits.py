#!/usr/bin/env python3
"""Demo 5: Resource limits in DuckDB.

Shows how to constrain CPU and memory usage to prevent resource exhaustion
from untrusted queries.
"""
import duckdb


def demo_thread_limit():
    """Limit the number of threads DuckDB uses."""
    print("=== Thread limits ===")
    con = duckdb.connect(":memory:")

    # Check default
    default = con.execute("SELECT current_setting('threads')").fetchone()[0]
    print(f"  Default threads: {default}")

    # Set to a lower value
    con.execute("SET threads=2")
    current = con.execute("SELECT current_setting('threads')").fetchone()[0]
    print(f"  After SET threads=2: {current}")

    # Can also set to 1 for fully serial execution
    con.execute("SET threads=1")
    current = con.execute("SELECT current_setting('threads')").fetchone()[0]
    print(f"  After SET threads=1: {current}")

    con.close()


def demo_memory_limit():
    """Limit the amount of memory DuckDB can use."""
    print("\n=== Memory limits ===")
    con = duckdb.connect(":memory:")

    # Check default
    default = con.execute("SELECT current_setting('memory_limit')").fetchone()[0]
    print(f"  Default memory_limit: {default}")

    # Set a lower limit
    con.execute("SET memory_limit='256MB'")
    current = con.execute("SELECT current_setting('memory_limit')").fetchone()[0]
    print(f"  After SET memory_limit='256MB': {current}")

    # Try to exceed the limit
    try:
        # Create a table that tries to use a lot of memory
        con.execute("""
            CREATE TABLE big AS
            SELECT range AS id,
                   repeat('x', 1000) AS payload
            FROM range(5000000)
        """)
        cnt = con.execute("SELECT COUNT(*) FROM big").fetchone()[0]
        print(f"  Large table created: {cnt} rows (fit in memory)")
    except duckdb.OutOfMemoryException as e:
        print(f"  Out of memory (expected with limit): {type(e).__name__}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")

    con.close()


def demo_temp_directory_limit():
    """Limit the size of temporary files DuckDB can create."""
    print("\n=== Temp directory size limit ===")
    con = duckdb.connect(":memory:")

    # Check default
    default = con.execute(
        "SELECT current_setting('max_temp_directory_size')"
    ).fetchone()[0]
    print(f"  Default max_temp_directory_size: {default}")

    # Set a limit - when memory is exhausted, DuckDB spills to disk.
    # This limits how much disk it can use.
    con.execute("SET max_temp_directory_size='512MB'")
    current = con.execute(
        "SELECT current_setting('max_temp_directory_size')"
    ).fetchone()[0]
    print(f"  After SET: {current}")

    con.close()


def demo_combined_limits():
    """Show the recommended combination of resource limits."""
    print("\n=== Combined resource limits ===")
    con = duckdb.connect(":memory:")

    con.execute("SET threads=2")
    con.execute("SET memory_limit='256MB'")
    con.execute("SET max_temp_directory_size='512MB'")

    # Lock so the user can't change them
    con.execute("SET lock_configuration=true")

    print("  Resource limits set and locked:")
    for setting in ["threads", "memory_limit", "max_temp_directory_size"]:
        val = con.execute(f"SELECT current_setting('{setting}')").fetchone()[0]
        print(f"    {setting} = {val}")

    # Verify they can't be changed
    try:
        con.execute("SET threads=64")
        print("  Change after lock: ALLOWED (unexpected)")
    except duckdb.InvalidInputException:
        print("\n  Attempt to change threads: BLOCKED (good)")

    con.close()


if __name__ == "__main__":
    demo_thread_limit()
    demo_memory_limit()
    demo_temp_directory_limit()
    demo_combined_limits()
    print("\nDone.")

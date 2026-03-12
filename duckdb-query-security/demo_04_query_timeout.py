#!/usr/bin/env python3
"""Demo 4: Query timeouts via connection.interrupt() with a timer thread.

DuckDB doesn't have a built-in query timeout setting, but connection.interrupt()
can be called from another thread to cancel a running query. This demo shows
how to implement reliable query timeouts.
"""
import duckdb
import threading
import time


def demo_basic_interrupt():
    """Basic interrupt: cancel a long-running query."""
    print("=== Basic interrupt ===")
    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE big AS SELECT range AS id FROM range(10000000)")

    def interrupt_after(conn, delay):
        time.sleep(delay)
        conn.interrupt()

    # Start a timer that will interrupt after 1 second
    timer = threading.Thread(target=interrupt_after, args=(con, 1.0))
    timer.start()

    start = time.time()
    try:
        # Cross join of 10M rows = very expensive
        con.execute(
            "SELECT COUNT(*) FROM big t1, big t2 WHERE t1.id = t2.id + 1"
        )
        elapsed = time.time() - start
        print(f"  Query completed in {elapsed:.2f}s (wasn't slow enough to interrupt)")
    except duckdb.InterruptException:
        elapsed = time.time() - start
        print(f"  Query interrupted after {elapsed:.2f}s")

    timer.join()
    con.close()


def demo_timeout_context_manager():
    """A reusable timeout context manager pattern."""
    print("\n=== Timeout context manager ===")

    class QueryTimeout:
        """Context manager that interrupts a DuckDB connection after a timeout."""

        def __init__(self, connection, timeout_seconds):
            self.connection = connection
            self.timeout = timeout_seconds
            self._timer = None

        def __enter__(self):
            self._timer = threading.Timer(self.timeout, self.connection.interrupt)
            self._timer.start()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._timer is not None:
                self._timer.cancel()
            # Don't suppress exceptions
            return False

    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE data AS SELECT range AS x FROM range(10000000)")

    # Fast query - completes before timeout
    with QueryTimeout(con, timeout_seconds=5.0):
        result = con.execute("SELECT SUM(x) FROM data").fetchone()
        print(f"  Fast query result: {result[0]}")

    # Slow query - gets interrupted
    try:
        with QueryTimeout(con, timeout_seconds=0.5):
            con.execute("""
                WITH RECURSIVE bomb(n) AS (
                    SELECT 1
                    UNION ALL
                    SELECT n + 1 FROM bomb WHERE n < 1000000000
                )
                SELECT COUNT(*) FROM bomb
            """)
            print("  Slow query completed (unexpected)")
    except duckdb.InterruptException:
        print("  Slow query timed out after 0.5s (expected)")

    # Connection is still usable after interrupt
    result = con.execute("SELECT 'still working' AS status").fetchone()
    print(f"  After interrupt: {result[0]}")

    con.close()


def demo_interrupt_recursive_cte():
    """Show that interrupt works on recursive CTEs (common DoS vector)."""
    print("\n=== Interrupting recursive CTE ===")
    con = duckdb.connect(":memory:")

    timer = threading.Timer(1.0, con.interrupt)
    timer.start()

    start = time.time()
    try:
        con.execute("""
            WITH RECURSIVE counter(n) AS (
                SELECT 1
                UNION ALL
                SELECT n + 1 FROM counter WHERE n < 999999999
            )
            SELECT MAX(n) FROM counter
        """)
    except duckdb.InterruptException:
        elapsed = time.time() - start
        print(f"  Recursive CTE interrupted after {elapsed:.2f}s")

    timer.cancel()
    con.close()


if __name__ == "__main__":
    demo_basic_interrupt()
    demo_timeout_context_manager()
    demo_interrupt_recursive_cte()
    print("\nDone.")

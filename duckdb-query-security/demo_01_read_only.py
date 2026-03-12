#!/usr/bin/env python3
"""Demo 1: Read-only connections in DuckDB.

Shows how read_only=True prevents all write operations on file-based databases.
Note: in-memory databases cannot be opened in read-only mode.
"""
import duckdb
import os
import tempfile

DB_PATH = os.path.join(tempfile.gettempdir(), "demo_readonly.duckdb")


def setup_database():
    """Create a database with sample data."""
    if os.path.exists(DB_PATH):
        os.unlink(DB_PATH)
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE TABLE users (id INT, name VARCHAR, email VARCHAR)")
    con.execute(
        "INSERT INTO users VALUES "
        "(1, 'Alice', 'alice@example.com'), "
        "(2, 'Bob', 'bob@example.com')"
    )
    con.close()
    print(f"Created database at {DB_PATH}")


def demo_read_only():
    """Demonstrate read-only connection behavior."""
    con = duckdb.connect(DB_PATH, read_only=True)

    # SELECT works fine
    print("\n--- Reads succeed ---")
    rows = con.execute("SELECT * FROM users ORDER BY id").fetchall()
    for row in rows:
        print(f"  {row}")

    # Aggregations, CTEs, subqueries all work
    result = con.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()
    print(f"  Count: {result[0]}")

    # All write operations are blocked
    print("\n--- Writes are blocked ---")
    write_operations = [
        ("INSERT", "INSERT INTO users VALUES (3, 'Charlie', 'c@example.com')"),
        ("UPDATE", "UPDATE users SET name='ALICE' WHERE id=1"),
        ("DELETE", "DELETE FROM users WHERE id=1"),
        ("CREATE TABLE", "CREATE TABLE evil (x INT)"),
        ("DROP TABLE", "DROP TABLE users"),
        ("ALTER TABLE", "ALTER TABLE users ADD COLUMN age INT"),
        ("CREATE INDEX", "CREATE INDEX idx ON users(name)"),
    ]
    for label, sql in write_operations:
        try:
            con.execute(sql)
            print(f"  {label}: ALLOWED (unexpected!)")
        except duckdb.InvalidInputException as e:
            print(f"  {label}: BLOCKED")

    con.close()


def demo_inmemory_readonly_fails():
    """In-memory databases cannot be opened read-only."""
    print("\n--- In-memory read-only is not supported ---")
    try:
        duckdb.connect(":memory:", read_only=True)
        print("  Connected (unexpected!)")
    except duckdb.CatalogException as e:
        print(f"  Cannot open in-memory DB as read-only: {e}")


if __name__ == "__main__":
    setup_database()
    demo_read_only()
    demo_inmemory_readonly_fails()

    # Cleanup
    os.unlink(DB_PATH)
    print("\nDone.")

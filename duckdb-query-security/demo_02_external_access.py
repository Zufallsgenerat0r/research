#!/usr/bin/env python3
"""Demo 2: File and network access restrictions in DuckDB.

Shows how enable_external_access, allowed_paths, and allowed_directories
control what files the database engine can read and write.
"""
import duckdb
import os
import tempfile

SANDBOX_DIR = os.path.join(tempfile.gettempdir(), "duckdb_sandbox")


def setup_test_files():
    """Create test files for the demo."""
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    with open(os.path.join(SANDBOX_DIR, "sales.csv"), "w") as f:
        f.write("product,quantity,price\n")
        f.write("Widget,100,9.99\n")
        f.write("Gadget,50,24.99\n")
    print(f"Created test files in {SANDBOX_DIR}")


def demo_disable_all_external_access():
    """Disable all file/network operations."""
    print("\n=== 1. Disable ALL external access ===")
    con = duckdb.connect(":memory:")
    con.execute("SET enable_external_access=false")

    blocked_ops = [
        ("Read CSV", f"SELECT * FROM read_csv('{SANDBOX_DIR}/sales.csv')"),
        ("Read Parquet", "SELECT * FROM read_parquet('/data/file.parquet')"),
        ("COPY TO", "COPY (SELECT 1) TO '/tmp/out.csv'"),
        ("ATTACH DB", "ATTACH '/tmp/test.duckdb' AS ext"),
        ("INSTALL ext", "INSTALL httpfs"),
        ("LOAD ext", "LOAD httpfs"),
    ]
    for label, sql in blocked_ops:
        try:
            con.execute(sql)
            print(f"  {label}: ALLOWED (unexpected)")
        except (duckdb.PermissionException, duckdb.Error) as e:
            print(f"  {label}: BLOCKED")

    # In-memory operations still work
    con.execute("CREATE TABLE t AS SELECT 42 AS answer")
    result = con.execute("SELECT * FROM t").fetchone()
    print(f"  In-memory query: {result} (always works)")
    con.close()


def demo_allowed_paths():
    """Use allowed_paths to whitelist specific files."""
    print("\n=== 2. allowed_paths: whitelist specific files ===")
    csv_path = os.path.join(SANDBOX_DIR, "sales.csv")
    con = duckdb.connect(":memory:")

    # IMPORTANT: Set allowed_paths BEFORE disabling external access
    con.execute(f"SET allowed_paths=['{csv_path}']")
    con.execute("SET enable_external_access=false")

    # Whitelisted file works
    try:
        rows = con.execute(f"SELECT * FROM read_csv('{csv_path}')").fetchall()
        print(f"  Read whitelisted file: OK ({len(rows)} rows)")
    except duckdb.PermissionException:
        print("  Read whitelisted file: BLOCKED (unexpected)")

    # Other files are blocked
    try:
        con.execute("SELECT * FROM read_csv('/etc/hostname')")
        print("  Read /etc/hostname: ALLOWED (unexpected)")
    except duckdb.PermissionException:
        print("  Read /etc/hostname: BLOCKED (good)")

    con.close()


def demo_allowed_directories():
    """Use allowed_directories to whitelist directory prefixes."""
    print("\n=== 3. allowed_directories: whitelist directory trees ===")
    con = duckdb.connect(":memory:")

    # IMPORTANT: Set before disabling external access
    con.execute(f"SET allowed_directories=['{SANDBOX_DIR}']")
    con.execute("SET enable_external_access=false")

    # Any file under the allowed directory works
    csv_path = os.path.join(SANDBOX_DIR, "sales.csv")
    try:
        rows = con.execute(f"SELECT * FROM read_csv('{csv_path}')").fetchall()
        print(f"  Read from allowed dir: OK ({len(rows)} rows)")
    except duckdb.PermissionException:
        print("  Read from allowed dir: BLOCKED (unexpected)")

    # Can also write to allowed directory
    out_path = os.path.join(SANDBOX_DIR, "output.csv")
    try:
        con.execute("CREATE TABLE t AS SELECT 1 AS x, 2 AS y")
        con.execute(f"COPY t TO '{out_path}'")
        print(f"  Write to allowed dir: OK")
    except duckdb.PermissionException:
        print("  Write to allowed dir: BLOCKED")

    # Path traversal is blocked
    try:
        con.execute(
            f"SELECT * FROM read_csv('{SANDBOX_DIR}/../etc/passwd')"
        )
        print("  Path traversal: ALLOWED (bad!)")
    except duckdb.PermissionException:
        print("  Path traversal: BLOCKED (good)")

    # Outside the allowed directory is blocked
    try:
        con.execute("SELECT * FROM read_csv('/etc/hostname')")
        print("  Outside allowed dir: ALLOWED (bad!)")
    except duckdb.PermissionException:
        print("  Outside allowed dir: BLOCKED (good)")

    con.close()


def demo_ordering_matters():
    """Show that allowed_paths must be set BEFORE disabling external access."""
    print("\n=== 4. ORDERING MATTERS ===")
    con = duckdb.connect(":memory:")
    con.execute("SET enable_external_access=false")

    try:
        con.execute(f"SET allowed_paths=['{SANDBOX_DIR}/sales.csv']")
        print("  Set allowed_paths after disable: OK (unexpected)")
    except duckdb.InvalidInputException as e:
        print("  Set allowed_paths after disable: BLOCKED")
        print("  Error: Cannot change allowed_paths when external access is disabled")
        print("  -> You MUST set allowed_paths BEFORE SET enable_external_access=false")

    con.close()


if __name__ == "__main__":
    setup_test_files()
    demo_disable_all_external_access()
    demo_allowed_paths()
    demo_allowed_directories()
    demo_ordering_matters()
    print("\nDone.")

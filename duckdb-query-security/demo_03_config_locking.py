#!/usr/bin/env python3
"""Demo 3: Configuration locking in DuckDB.

Shows how lock_configuration=true prevents users from changing ANY setting,
making the security configuration tamper-proof.
"""
import duckdb


def demo_without_locking():
    """Without locking, a user can re-enable external access."""
    print("=== Without lock_configuration ===")
    con = duckdb.connect(":memory:")
    con.execute("SET enable_external_access=false")

    # User can just turn it back on... by reconnecting or via SET
    # (In practice, SET enable_external_access cannot be changed at runtime,
    #  but other settings like threads, memory_limit CAN be changed.)
    try:
        con.execute("SET threads=16")
        r = con.execute("SELECT current_setting('threads')").fetchone()
        print(f"  Changed threads to: {r[0]} (no protection)")
    except Exception as e:
        print(f"  Change threads: BLOCKED - {e}")

    con.close()


def demo_with_locking():
    """With locking, NO configuration changes are possible."""
    print("\n=== With lock_configuration ===")
    con = duckdb.connect(":memory:")

    # Set all security settings first
    con.execute("SET enable_external_access=false")
    con.execute("SET threads=2")
    con.execute("SET memory_limit='256MB'")

    # THEN lock the configuration
    con.execute("SET lock_configuration=true")
    print("  Configuration locked.")

    # Now try to change things
    attempts = [
        ("enable_external_access", "SET enable_external_access=true"),
        ("lock_configuration", "SET lock_configuration=false"),
        ("threads", "SET threads=16"),
        ("memory_limit", "SET memory_limit='8GB'"),
        ("allow_community_extensions", "SET allow_community_extensions=true"),
    ]
    for setting, sql in attempts:
        try:
            con.execute(sql)
            print(f"  Change {setting}: ALLOWED (unexpected!)")
        except duckdb.InvalidInputException:
            print(f"  Change {setting}: BLOCKED (good)")

    # Queries still work fine
    con.execute("CREATE TABLE t AS SELECT generate_series AS x FROM generate_series(1, 100)")
    result = con.execute("SELECT AVG(x) FROM t").fetchone()
    print(f"\n  Queries still work: AVG = {result[0]}")

    # Verify settings are intact
    print("\n  Current settings:")
    for s in ["enable_external_access", "threads", "memory_limit", "lock_configuration"]:
        r = con.execute(f"SELECT current_setting('{s}')").fetchone()
        print(f"    {s} = {r[0]}")

    con.close()


def demo_recommended_setup_order():
    """Show the recommended order for setting up a locked sandbox."""
    print("\n=== Recommended setup order ===")
    con = duckdb.connect(":memory:")

    # Step 1: Set allowed paths/dirs (if needed)
    # con.execute("SET allowed_directories=['/data/user123']")

    # Step 2: Disable external access
    con.execute("SET enable_external_access=false")

    # Step 3: Set resource limits
    con.execute("SET threads=2")
    con.execute("SET memory_limit='256MB'")

    # Step 4: Disable community extensions
    con.execute("SET allow_community_extensions=false")

    # Step 5: LAST - lock everything
    con.execute("SET lock_configuration=true")

    print("  Setup complete. Configuration is now immutable.")
    print("  Order: allowed_paths -> external_access -> limits -> lock")
    con.close()


if __name__ == "__main__":
    demo_without_locking()
    demo_with_locking()
    demo_recommended_setup_order()
    print("\nDone.")

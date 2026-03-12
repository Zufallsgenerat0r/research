Evaluating how to securely sandbox untrusted SQL queries in DuckDB, this project systematically tests and combines DuckDB’s built-in security features—including read-only database modes, external file/network access restrictions, configuration locking, resource limits, and connection timeouts—to mitigate risks like filesystem access, extension abuse, and resource exhaustion. The ready-to-use [`SandboxedDuckDB`](sandboxed_duckdb.py) wrapper class automates these settings in the correct order and provides a robust framework for safely executing user queries within controlled Python applications. Key attack vectors such as unauthorized file reads/writes, extension loading, and resource exhaustion were empirically tested and confirmed blocked or mitigated under these controls (DuckDB 1.5.0). The study emphasizes the importance of combining DuckDB’s in-process protections with OS- or container-level sandboxing for robust security.

Key findings:
- Enforcing `enable_external_access=false` with prior path/directory whitelisting effectively blocks external file/network access.
- Configuration locking (`lock_configuration=true`) prevents privilege escalation or security setting bypass through SQL injection.
- There is no built-in query timeout, but reliable timeouts are implemented via `connection.interrupt()` and a host-side timer (though some reliability issues remain).
- Application-level controls are still needed for SQL injection prevention, information leakage, and large result set limits.
- For production use, see [`sandboxed_duckdb.py`](sandboxed_duckdb.py) (project repo) for a securely wrapped interface. 

DuckDB project: https://duckdb.org/  
SandboxedDuckDB: [`sandboxed_duckdb.py`](sandboxed_duckdb.py)

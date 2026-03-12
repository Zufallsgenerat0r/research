# Research projects carried out by AI tools

Each directory in this repo is a separate research project carried out by an LLM tool. Every single line of text and code was written by an LLM.

*Times shown are in UTC.*

<!--[[[cog
import os
import re
import subprocess
import pathlib
from datetime import datetime, timezone

# Model to use for generating summaries
MODEL = "github/gpt-4.1"

# Get all subdirectories with their first commit dates
research_dir = pathlib.Path.cwd()
subdirs_with_dates = []

for d in research_dir.iterdir():
    if d.is_dir() and not d.name.startswith('.'):
        # Get the date of the first commit that touched this directory
        try:
            result = subprocess.run(
                ['git', 'log', '--diff-filter=A', '--follow', '--format=%aI', '--reverse', '--', d.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse first line (oldest commit)
                date_str = result.stdout.strip().split('\n')[0]
                commit_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                subdirs_with_dates.append((d.name, commit_date))
            else:
                # No git history, use directory modification time
                subdirs_with_dates.append((d.name, datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)))
        except Exception:
            # Fallback to directory modification time
            subdirs_with_dates.append((d.name, datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)))

# Print the heading with count
print(f"## {len(subdirs_with_dates)} research projects\n")

# Sort by date, most recent first
subdirs_with_dates.sort(key=lambda x: x[1], reverse=True)

for dirname, commit_date in subdirs_with_dates:
    folder_path = research_dir / dirname
    readme_path = folder_path / "README.md"
    summary_path = folder_path / "_summary.md"

    date_formatted = commit_date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M')

    # Get GitHub repo URL
    github_url = None
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            origin = result.stdout.strip()
            # Convert SSH URL to HTTPS URL for GitHub
            if origin.startswith('git@github.com:'):
                origin = origin.replace('git@github.com:', 'https://github.com/')
            if origin.endswith('.git'):
                origin = origin[:-4]
            github_url = f"{origin}/tree/main/{dirname}"
    except Exception:
        pass

    # Extract title from first H1 header in README, fallback to dirname
    title = dirname
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            for readme_line in f:
                if readme_line.startswith('# '):
                    title = readme_line[2:].strip()
                    break

    if github_url:
        print(f"### [{title}]({github_url}#readme) ({date_formatted})\n")
    else:
        print(f"### {title} ({date_formatted})\n")

    # Check if summary already exists
    if summary_path.exists():
        # Use cached summary
        with open(summary_path, 'r') as f:
            description = f.read().strip()
            if description:
                print(description)
            else:
                print("*No description available.*")
    elif readme_path.exists():
        # Generate new summary using llm command
        prompt = """Summarize this research project concisely. Write just 1 paragraph (3-5 sentences) followed by an optional short bullet list if there are key findings. Vary your opening - don't start with "This report" or "This research". Include 1-2 links to key tools/projects. Be specific but brief. No emoji."""
        result = subprocess.run(
            ['llm', '-m', MODEL, '-s', prompt],
            stdin=open(readme_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            error_msg = f"LLM command failed for {dirname} with return code {result.returncode}"
            if result.stderr:
                error_msg += f"\nStderr: {result.stderr}"
            raise RuntimeError(error_msg)
        if result.stdout.strip():
            description = result.stdout.strip()
            print(description)
            # Save to cache file
            with open(summary_path, 'w') as f:
                f.write(description + '\n')
        else:
            raise RuntimeError(f"LLM command returned no output for {dirname}")
    else:
        print("*No description available.*")

    print()  # Add blank line between entries

# Add AI-generated note to all project README.md files
# Note: we construct these marker strings via concatenation to avoid the HTML comment close sequence
AI_NOTE_START = "<!-- AI-GENERATED-NOTE --" + ">"
AI_NOTE_END = "<!-- /AI-GENERATED-NOTE --" + ">"
AI_NOTE_CONTENT = """> [!NOTE]
> This is an AI-generated research report. All text and code in this report was created by an LLM (Large Language Model). For more information on how these reports are created, see the [main research repository](https://github.com/simonw/research)."""

for dirname, _ in subdirs_with_dates:
    folder_path = research_dir / dirname
    readme_path = folder_path / "README.md"

    if not readme_path.exists():
        continue

    content = readme_path.read_text()

    # Check if note already exists
    if AI_NOTE_START in content:
        # Replace existing note
        pattern = re.escape(AI_NOTE_START) + r'.*?' + re.escape(AI_NOTE_END)
        new_note = f"{AI_NOTE_START}\n{AI_NOTE_CONTENT}\n{AI_NOTE_END}"
        new_content = re.sub(pattern, new_note, content, flags=re.DOTALL)
        if new_content != content:
            readme_path.write_text(new_content)
    else:
        # Add note after first heading (# ...)
        lines = content.split('\n')
        new_lines = []
        note_added = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if not note_added and line.startswith('# '):
                # Add blank line, then note, then blank line
                new_lines.append('')
                new_lines.append(AI_NOTE_START)
                new_lines.append(AI_NOTE_CONTENT)
                new_lines.append(AI_NOTE_END)
                note_added = True

        if note_added:
            readme_path.write_text('\n'.join(new_lines))

]]]-->
## 2 research projects

### [DuckDB Query Security: Sandboxing Untrusted User Queries](https://github.com/Zufallsgenerat0r/research/tree/main/duckdb-query-security#readme) (2026-03-12 16:48)

Evaluating how to securely sandbox untrusted SQL queries in DuckDB, this project systematically tests and combines DuckDB’s built-in security features—including read-only database modes, external file/network access restrictions, configuration locking, resource limits, and connection timeouts—to mitigate risks like filesystem access, extension abuse, and resource exhaustion. The ready-to-use [`SandboxedDuckDB`](sandboxed_duckdb.py) wrapper class automates these settings in the correct order and provides a robust framework for safely executing user queries within controlled Python applications. Key attack vectors such as unauthorized file reads/writes, extension loading, and resource exhaustion were empirically tested and confirmed blocked or mitigated under these controls (DuckDB 1.5.0). The study emphasizes the importance of combining DuckDB’s in-process protections with OS- or container-level sandboxing for robust security.

Key findings:
- Enforcing `enable_external_access=false` with prior path/directory whitelisting effectively blocks external file/network access.
- Configuration locking (`lock_configuration=true`) prevents privilege escalation or security setting bypass through SQL injection.
- There is no built-in query timeout, but reliable timeouts are implemented via `connection.interrupt()` and a host-side timer (though some reliability issues remain).
- Application-level controls are still needed for SQL injection prevention, information leakage, and large result set limits.
- For production use, see [`sandboxed_duckdb.py`](sandboxed_duckdb.py) (project repo) for a securely wrapped interface. 

DuckDB project: https://duckdb.org/  
SandboxedDuckDB: [`sandboxed_duckdb.py`](sandboxed_duckdb.py)

### [Works in Progress Magazine: Author & Topic Analysis](https://github.com/Zufallsgenerat0r/research/tree/main/worksinprogress-focus#readme) (2026-03-12 14:44)

Automated analysis of [Works in Progress](https://worksinprogress.co/) magazine reveals strong editorial and topical cohesion around ideas of human advancement, with 116 cataloged articles spanning 72 authors and 28 topics since its 2020 founding. Output has grown steadily, particularly in 2024–25 (up to 10 articles per issue), and while the editorial team contributes regularly, most writers are one-time contributors from a broad pool of academics and journalists. Signature subject areas include housing/urban planning, policy, and science/innovation, with viral topics like the "Housing Theory of Everything" setting the magazine apart within the broader genre of progress studies. Visualizations and scripts were generated using [`analyze_and_visualize.py`](#), built from a structured dataset (`wip_data.py`).

Key findings:
- Housing, policy, and science/innovation are the most distinctive and frequently covered themes.
- Interdisciplinary approaches are common; top authors write across multiple categories.
- The majority of contributors have authored only one article, reflecting a diverse and rotating pool.
- See the [Works in Progress archive](https://worksinprogress.co/archive/) for source material reference.

<!-- [[[end]]] -->

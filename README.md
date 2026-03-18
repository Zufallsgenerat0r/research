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
## 10 research projects

### [Latest Major Release of Python Pydantic](https://github.com/Zufallsgenerat0r/research/tree/main/pydantic-latest-release#readme) (2026-03-18 13:08)

Pydantic v2 marks a major evolution in Python data validation by shifting all validation and serialization logic to the Rust-powered [`pydantic-core`](https://github.com/pydantic/pydantic-core), enabling dramatic speedups (5–50x) and improved modularity. The new architecture centers on a structured schema dict that bridges the Python and Rust components, allowing for extensible yet efficient model validation. Key features include the `TypeAdapter` for validating arbitrary types, strict mode for disabling automatic type coercion, improved JSON Schema handling, and a new dict-based model configuration. Migration from v1 involved sweeping API changes but is facilitated by in-place compatibility shims and the [`bump-pydantic`](https://github.com/pydantic/bump-pydantic) automation tool. Looking ahead, v3 is planned as a refinement-focused release, promising stability and cleanup without major disruptions.

**Key findings:**
- Validation and serialization logic moved to Rust (`pydantic-core`), greatly boosting performance.
- v2 introduced core schema architecture and tree-based validator composition for extensibility.
- Strict mode, `TypeAdapter`, modern JSON Schema, and dict-based configs improve developer experience.
- Migration aided by compatibility layer and automated tools; v3 will phase out v1 shims and focus on polish, with minimal API churn.

### [Security Review: Dimowner/AudioRecorder](https://github.com/Zufallsgenerat0r/research/tree/main/security-review-audiorecorder#readme) (2026-03-16 13:26)

The security analysis of Dimowner/AudioRecorder (https://github.com/Dimowner/AudioRecorder), an open-source offline Android audio app, reveals a strong design focus on limiting remote attack vectors but exposes several serious vulnerabilities in local file handling and app security. Critical issues include an overly broad FileProvider configuration, multiple SQL injection risks, and signing credentials mistakenly checked into version control. High-severity concerns span path traversal, unprotected broadcast receivers, excessive logging, and insufficient input validation, all of which could facilitate privilege escalation or data exposure. Immediate remediation is advised on FileProvider restrictions, SQL query parameterization, exclusion of credentials from source control, and tightening receiver/export settings to reduce attack surface.

**Key Findings**
- FileProvider exposes whole external storage, risking data leaks.
- SQL queries are vulnerable to injection; parameterization needed.
- App signing credentials are in version control; must be removed and rotated.
- Broadcast receivers and widget are exported without proper protection.
- Log output and file operations lack validation, further increasing risk.
- Recommendations detailed for each risk; see SQL injection guidance at https://developer.android.com/training/data-storage/sqlite#InsertData (Android documentation).

### [Recreating "Order From Chaos" Visualizations](https://github.com/Zufallsgenerat0r/research/tree/main/order-from-chaos-viz#readme) (2026-03-13 21:31)

Inspired by Max Cooper's *Order From Chaos* video and Maxime Causeret's original Houdini-based techniques, this project systematically recreates four core generative visualization methods using accessible Python tools. Techniques implemented include the Gray-Scott reaction-diffusion system, differential growth algorithms, particle-driven ripples in flow fields, and procedural organism simulations with flocking behaviors—all rendered with scientific libraries like NumPy, SciPy, and Matplotlib. Outputs closely match the biological and emergent visuals in the original video, offering static, reproducible results suitable for further artistic or scientific exploration.  
To deepen fidelity or create real-time versions, users may explore [Blender Geometry Nodes](https://www.blender.org/features/geometry-nodes/) or [Processing / p5.js](https://p5js.org/), while GPU acceleration enables high-resolution, interactive simulations.

**Key Findings:**
- Python can replicate advanced generative art methods originally built in Houdini using standard scientific libraries.
- Reaction-diffusion, differential growth, and particle-in-flow field algorithms offer a diverse toolkit for procedural biomorphic visualization.
- Static reproductions are possible, though real-time and higher complexity require specialized tools or GPU acceleration.

### [Open Source Alternatives to Slack: Deployment, Security & Maintainability](https://github.com/Zufallsgenerat0r/research/tree/main/slack-alternatives#readme) (2026-03-13 18:05)

Evaluating five leading open source Slack alternatives—Mattermost, Rocket.Chat, Zulip, Element/Matrix (Synapse), and Revolt (Stoat)—this study analyzed deployment options, security posture, maturity, and maintainability. **Mattermost** emerges as the best fit for compliance-focused enterprises with its robust admin tooling and support, although some key features are paywalled; **Zulip** stands out for those prioritizing fully open source solutions with its Apache 2.0 license, threaded discussions, and outstanding contributor community. **Element/Matrix** offers unmatched end-to-end encryption and federation for privacy-critical use cases, but introduces the most operational complexity. Rocket.Chat remains a feature-rich option for technically adept teams wary of licensing nuances, while Revolt (Stoat) is best left to casual Discord-like communities due to its weak security posture. For more details, see the official repositories: [Mattermost](https://github.com/mattermost/mattermost), [Zulip](https://github.com/zulip/zulip), and [Matrix/Element](https://github.com/matrix-org/synapse).

**Key findings:**
- Zulip is the only top-tier, fully open source (Apache 2.0) platform with no proprietary features or code.
- Element/Matrix is the sole platform with default end-to-end encryption and true federation, but demands the most technical effort to deploy and maintain.
- Mattermost and Rocket.Chat provide enterprise features and support, but both have key features restricted to proprietary tiers.
- Revolt (Stoat) lacks mature security practices, limiting its suitability to informal, community-based use.

### [CO2 Impact of Food in Germany](https://github.com/Zufallsgenerat0r/research/tree/main/german-food-co2-impact#readme) (2026-03-12 23:19)

Food production and consumption in Germany account for about 25% of national greenhouse gas emissions, with the average diet generating approximately 2,000 kg CO2-equivalent per person annually. Meat and dairy together contribute roughly 70% of food-related emissions, far outpacing other categories such as grains and vegetables. Switching dietary patterns to flexitarian, vegetarian, or vegan can reduce emissions by 30-53%, though even the vegan diet remains above the level needed to meet Germany’s climate targets; systemic changes, such as agricultural reform and reducing food waste, are required. The CO2 footprint varies widely between foods, with beef and lamb being especially high, while plant-based foods like root vegetables and legumes are much lower; additionally, eating seasonal or minimally processed foods reduces emissions, but transport (except air freight) generally plays a secondary role.

Key tools and data files for this research include the [IFEU 2020 study](https://www.ifeu.de/fileadmin/uploads/Reinhardt-Gaertner-Wagner-2020-Environmental-footprints-of-food-products-and-dishes-in-Germany-ifeu-2020.pdf) and the [food_co2_analysis.py Python script](README.md).

**Key findings:**
- Beef/lamb >10x more CO2-intensive than most plant foods
- Meat and dairy are the largest contributors to dietary emissions
- Dietary shifts (flexitarian, vegetarian, vegan) significantly reduce emissions but alone are insufficient for climate targets
- Seasonality and minimal processing matter more than food miles; air freight is a major exception
- About 30% of emissions gap is due to food waste and energy use in retail/cooking

### [ZimaOS App Update Mechanism: How It Works](https://github.com/Zufallsgenerat0r/research/tree/main/zimaos-update-mechanism#readme) (2026-03-12 21:44)

ZimaOS, an open-source NAS OS by IceWhale Technology, employs two robust update mechanisms: app updates managed via [CasaOS-AppManagement](https://github.com/IceWhaleTech/CasaOS-AppManagement) (Go service, Docker Compose-based) and system OTA updates powered by [RAUC](https://rauc.io/) using an A/B partition approach. App updates involve catalog refreshes, digest comparisons for images (especially those tagged `:latest`), and atomic replacement with backup/rollback patterns, all triggered through dashboard UI or API endpoints. System updates use signed `.raucb` bundles, written to the inactive partition and boot-switched upon success, with automatic rollback if a new slot fails. Developer workflow is tightly tied to Docker Compose conventions and app store metadata, but is limited by Buildroot's lack of a package manager and potential system/container breakages after upgrades.

**Key findings:**
- App update detection is cached for 1 hour and relies on Docker manifest digest comparison for `:latest` tags.
- System updates via RAUC are atomic, signed, and managed at the partition level, ensuring boot fallback.
- Limitations include no traditional package manager, only Docker extensions, UI/CLI discrepancies, and developer gotchas around compose file handling and third-party integrations.
- Repeated system upgrades have caused existing containers to fail, and certain hardware features (e.g., GPU passthrough) remain unreliable due to Buildroot’s design.
- See [ZimaOS adaptation guide](https://www.zimaspace.com/docs/zimaos/Build-Apps) for app development specifics.

### [ZimaOS Developer Experience: Gotchas, Limitations, and Practical Guide](https://github.com/Zufallsgenerat0r/research/tree/main/zimaos-developer-experience#readme) (2026-03-12 21:44)

ZimaOS, developed from the open-source CasaOS, is a NAS operating system built on Buildroot with a Docker-centric application model and simplified web UI. Developers face several notable challenges: custom apps share a project name, `.env` files are unsupported in the UI, app store installs can't be edited, and system-level access is severely limited by the Buildroot base (no package manager, driver installs, or file system flexibility). Migration from CasaOS requires a fresh install, and frequent ZimaOS updates or paid-tier changes have triggered compatibility, GPU passthrough, and storage visibility issues. Docker Compose files need to follow strict metadata conventions (`x-casaos`) for App Store integration, and several network and storage gotchas—like host access from containers and Samba share mounting—require workarounds or are simply unsupported.

**Key findings:**
- You can create and install apps via the [web UI](https://www.zimaspace.com/docs/zimaos/Build-Apps), CLI, or by submitting to the [App Store](https://github.com/IceWhaleTech/CasaOS-AppStore) (compose files must use strict `x-casaos` metadata).
- Buildroot base means there is no package manager—extensions are only possible through Docker.
- Multiple custom apps via UI collide (same project name), `.env` support is missing, and app updates can break both drivers and app configs.
- Network and storage integrations (host access, mounting, and multi-partition disks) are limited; only storage managed through ZimaOS is visible in the UI.
- GPU passthrough and driver support are inconsistent and easily broken by updates, with no straightforward fix.

For app developers, the most critical gotchas are the lack of `.env` support, project name collisions, non-editable App Store app configs, fragile update behavior, and strict Compose file requirements.

### [ZimaOS Research Report](https://github.com/Zufallsgenerat0r/research/tree/main/zimaos-research#readme) (2026-03-12 21:44)

ZimaOS is a Buildroot-based, standalone NAS operating system developed by IceWhale Technology, expanding upon the CasaOS platform to deliver advanced storage (RAID/ZFS/Btrfs), optimized hardware support, and robust OTA updates through the RAUC mechanism. Unlike CasaOS—which is a Docker-centric software layer for third-party Linux systems—ZimaOS comes as a full OS image, enabling seamless system-level management, VM provisioning, and enhanced security on supported x86-64 devices. The ecosystem revolves around a Docker-based app store ([CasaOS-AppStore](https://github.com/IceWhaleTech/CasaOS-AppStore)), customizable Compose manifests, and extensible API endpoints for comprehensive lifecycle operations. Notably, ZimaOS introduced a paid tier (CE vs Plus Edition), and its update infrastructure carefully separates system updates (via A/B partitions and RAUC) from manually triggered app updates, prioritizing reliability over automation. For developers, the platform offers granular control through [CasaOS-AppManagement](https://github.com/IceWhaleTech/CasaOS-AppManagement) API and a clear architecture of Go microservices behind a unified Vue.js frontend.

**Key Findings:**
- ZimaOS supports advanced storage (RAID, ZFS, Btrfs) and VM management, going beyond CasaOS's scope.
- System updates use RAUC with A/B partitions for rollback safety, while app updates are strictly manual and version-pinned.
- App ecosystem is modular, Docker Compose-driven, and extensible via official and third-party app stores.
- The architecture relies on microservices (Go) with all APIs exposed through a secure gateway, with configuration kept in `/etc/casaos/`.
- Paid Plus Edition removes limits on disks, apps, and users, reflecting a new business model as of v1.5.0+ (2025).

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

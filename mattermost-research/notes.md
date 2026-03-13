# Mattermost Research Notes

## 2026-03-13 - Research Session

### Goal
Research Mattermost as an open source Slack alternative across four dimensions:
1. Overview (license, language, architecture)
2. How to run it (self-hosting, managed options)
3. Security (CVEs, audits, encryption, compliance)
4. Maintainability (GitHub stats, community, activity)

### Research Log

#### Sources Consulted
- Mattermost official website (mattermost.com)
- Mattermost official documentation (docs.mattermost.com)
- GitHub repository (github.com/mattermost/mattermost)
- CVEDetails (cvedetails.com) - 403 blocked, used search snippets
- OpenCVE (app.opencve.io) - 403 blocked, used search snippets
- Mattermost Handbook (handbook.mattermost.com)
- HackerOne / Bugcrowd pages
- Crunchbase, PitchBook, Getlatka for company data
- endoflife.date for release lifecycle data
- Multiple third-party analysis sites

#### Key Findings

**Licensing**: Open-core model. Source code is AGPL v3, compiled releases are MIT. Enterprise features under commercial license. "Mattermost Entry" is new free tier with server-wide limitations. User limits being lowered progressively (community fork "Mostlymatter" removes limits).

**Tech Stack**: Go backend (38.9%), TypeScript/React frontend (49.7%), PostgreSQL/MySQL databases. React Native mobile apps, Electron desktop apps.

**CVE Count**: Could not get exact total from CVEDetails (page blocked). CVEDetails lists 1,192 versions in CVE/CPE data. OpenCVE has ~25 pages of results suggesting 400-500+ total CVEs. Mattermost is its own CNA. High volume of CVEs in 2024-2025 including critical ones (CVSS 9.9).

**Company**: Founded 2016, $70.6M total funding, 156-162 employees, $33.1M revenue in 2024, 800+ customers. Backed by Battery Ventures, Redpoint, Y Combinator.

**GitHub**: 35.8k stars, 8.4k forks, 534 watchers, 539 open issues, 287 open PRs. Monthly release cadence on the 16th.

**Compliance**: SOC 2 Type II, ISO 27001 certified. Supports HIPAA, CMMC, GDPR compliance (deployment-dependent). No direct FedRAMP authorization but supports IL4/IL5 deployments.

**Encryption**: TLS in transit (AES-256 with 2048-bit RSA). At rest relies on external disk/database encryption (LUKS, TDE, etc.) - no built-in application-level encryption at rest by design (to preserve search functionality).

**Bug Bounty**: Transitioned from HackerOne to Bugcrowd (November 2025). Active responsible disclosure program. 30-day embargo on details after fix.

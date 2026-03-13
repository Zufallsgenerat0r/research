# Research Notes: Open Source Slack Alternatives

## Goal
Research open source alternatives to Slack — how to run them, security posture, and maintainability.

## Alternatives Investigated
- Mattermost
- Rocket.Chat
- Zulip
- Element (Matrix/Synapse)
- Revolt (now Stoat)

---

## Research Log

### 2026-03-13 — Research conducted

#### Sources used
- Web searches for each platform covering: overview, architecture, deployment, security CVEs, GitHub stats
- Official documentation sites for each project
- CVE databases (cvedetails.com, GitHub Security Advisories)
- GitHub repositories for contributor/star counts

#### Key findings

**Mattermost**: Most enterprise-ready. Go+React stack, ~34k GitHub stars. Has had several critical CVEs in 2025 including path traversal leading to RCE (CVE-2025-4981) and Boards plugin SQL injection (CVSS 9.9). Open core model with MIT-licensed community edition. Backed by Mattermost Inc. Docker/K8s/bare-metal deployment options.

**Rocket.Chat**: TypeScript/Node.js + MongoDB. ~45k GitHub stars, 1190 contributors. MIT license base but enterprise features under proprietary license. 50 total CVEs tracked since 2018 including SSRF and stored XSS in 2024. Strong community with GSoC participation. Docker/K8s deployment.

**Zulip**: Python/Django backend. ~22k+ stars, 1500+ contributors, 500+ commits/month. Apache 2.0 license — fully open source with no proprietary tiers. Unique threaded topic model. Fewer critical CVEs than competitors. Backed by Kandra Labs. Ubuntu/Debian/Docker deployment.

**Element/Matrix**: Decentralized protocol (Matrix). Synapse (Python/Twisted+Rust) is primary server. ~3.3k stars on current repo (migrated). AGPL v3 license. End-to-end encryption built in (Megolm/Olm). BSI-funded security audit found no critical issues. Federation protocol CVEs in 2025. Docker Compose or bare metal deployment.

**Revolt/Stoat**: Rust backend + TypeScript frontend. ~2.3k stars on main repo. AGPL v3 license. Rebranded to Stoat in late 2025. More Discord-like than Slack-like. Self-hosted version is stripped of some features. Smallest/least mature project of the five. Minimum 2 vCPU/2GB RAM for self-hosting.

#### Observations
- All five can be self-hosted with Docker
- Mattermost and Rocket.Chat have the most enterprise features and corporate backing
- Zulip is the most genuinely open source (Apache 2.0, no proprietary tier)
- Element/Matrix is the only truly decentralized/federated option
- Revolt/Stoat is aimed more at Discord users than Slack users
- Security track records vary — all have had CVEs, but response times and disclosure practices are generally good across the board

# Zulip Research Notes

## Research Started: 2026-03-13

### Plan
- Overview: license, language, architecture
- Deployment: Docker, K8s, bare metal, managed hosting
- Security: CVEs, audits, encryption, SSO, compliance
- Maintainability: GitHub stats, community, releases, bus factor

---

## Key Findings

### Overview
- Apache 2.0 license, 100% open source (no open-core)
- Backend: Python (Django + Tornado), Frontend: TypeScript/Handlebars, Mobile: Flutter
- Architecture: Nginx frontend -> Django (business logic) + Tornado (real-time/long-polling), PostgreSQL, Redis, memcached
- Founded 2012, acquired by Dropbox 2014, open-sourced late 2015
- Kandra Labs (founded 2016 by Tim Abbott) stewards the project
- Unique feature: topic-based threading within channels

### Deployment
- Standard install: Ubuntu 22.04/24.04, Debian 12/13
- Docker: official docker-compose and Helm charts
- Kubernetes: Helm chart available but multi-replica not straightforward
- Min requirements: 2GB RAM, 10GB disk (SSD recommended)
- Cloud hosting: Free tier (10k messages), Standard $8/mo, Plus $12/mo per user
- Self-hosted plans: Free, Basic $3.50/mo, Business $8/mo, Enterprise custom

### Security
- 28 total CVEs on CVEDetails (as of research date)
- Recent CVEs mostly medium severity (XSS, access control issues)
- Encryption: at rest and in transit
- SSO: SAML, OpenID Connect, Microsoft Entra ID, LDAP, SCIM provisioning
- HackerOne private vulnerability disclosure program
- No evidence of SOC 2 certification or formal third-party pen testing
- No ISO 27001 certification found
- Latest security release: 11.5 fixing CVE-2026-24050

### Maintainability
- ~24,800 GitHub stars
- 1,500+ contributors, 99+ with 100+ commits each
- 500+ commits/month
- Two major releases per year (10.0 Mar 2025, 11.0 Aug 2025, 12.0 expected early 2026)
- Active in GSoC for 10 consecutive years
- 185K words of contributor documentation
- Corporate backing: Kandra Labs (no VC, funded by founder + ~$1M NSF grants)
- Tim Abbott is the lead developer/CEO - key person dependency
- Sponsors 2,000+ organizations with free hosting

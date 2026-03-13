# Rocket.Chat Research Notes

## Research Started: 2026-03-13

### Plan
- Overview: license, language, architecture
- Deployment: Docker, K8s, bare metal, managed hosting
- Security: CVEs, audits, encryption, SSO, compliance
- Maintainability: GitHub stats, community, activity, bus factor

---

## Key Findings

### Overview
- TypeScript/Node.js with MongoDB backend
- License: MIT for core, but enterprise features under proprietary Rocket.Chat Enterprise Edition (EE) license
- Some concerns from FOSS community about EE code being mixed into the codebase
- Founded 2015 by Gabriel Engel and Rodrigo Do Nascimento

### GitHub Stats (as of March 2026)
- 44,866 stars, 13,376 forks, 1,190 contributors, 2,342 open issues

### Funding
- Total raised: ~37-48M USD over 4 rounds from 15 investors
- Latest: Series A-II, 10M, September 2023
- ~180 employees

### CVEs
- 50 total CVEs (2018-2025)
- Most severe: CVSS 7.5 (NoSQL injection, SAML issues)

### Security Certifications
- ISO 27001 certified (June 2023 - June 2026)
- SOC 2 Type II attested
- HackerOne VDP program, E2EE available

### Deployment
- Docker (most popular), Kubernetes (Helm charts), Launchpad CLI
- Minimum: 1 vCPU, 2GB RAM, 40GB storage for <=50 users

### Release Cadence
- ~monthly releases, 2 LTS releases per year
- Latest: v8.0.0-rc.3 (Jan 7, 2026)

### Pricing
- Community: Free, Starter: Free (50 users), Pro: 8/user/month, Enterprise: Custom

### Concerns
- License mixing (MIT + proprietary EE in same codebase)
- LDAP/SAML/custom OAuth require premium plan
- Community edition limited to 1,000 users

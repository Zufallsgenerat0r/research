# Rocket.Chat: Open Source Slack Alternative -- Research Report

**Date:** 2026-03-13

---

## 1. Overview

### What Is Rocket.Chat?

Rocket.Chat is an open-source communications platform for team messaging, video conferencing, and omnichannel customer support. It positions itself as a self-hostable alternative to Slack, Microsoft Teams, and Discord, with a particular focus on organizations with strict data sovereignty and compliance requirements (government, defense, healthcare, finance).

**Founded:** 2015 by Gabriel Engel and Rodrigo Do Nascimento (Wilmington, US)

**Corporate Backing:** Rocket.Chat Technologies Corp. is a private company with approximately 180 employees. They have raised between $37M and $48M (sources vary) across 4 funding rounds from 15 investors. Key investors include Valor Capital Group, New Enterprise Associates, and Monashees. The latest round was a $10M Series A-II in September 2023.

### Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | TypeScript / Node.js |
| Database | MongoDB (replica set recommended) |
| Extensions | TypeScript via Apps Engine |
| Desktop App | Electron |
| Mobile App | React Native |

### License

Rocket.Chat uses a **dual-license model**:

- **Core / Community:** MIT License -- permissive, no copyleft obligations
- **Enterprise features:** Proprietary "Rocket.Chat Enterprise Edition (EE)" license, which restricts use and distribution

**Important caveat:** The FOSS community has raised concerns that enterprise-licensed code is mixed into the same codebase as MIT-licensed code, and in some cases FOSS code depends on non-FOSS code. The mobile application codebase has a similar structure where the enterprise license is nested in subdirectories. This means the project is not fully open-source in practice despite marketing claims.

### Pricing Tiers

| Plan | Price | Limits |
|------|-------|--------|
| Community | Free | Self-hosted, no advanced features, no official support |
| Starter | Free | Up to 50 users, 100 omnichannel contacts, some premium features |
| Pro | $8/user/month (annual) | Up to 500 users |
| Enterprise | Custom | Unlimited, full feature set, dedicated support |

---

## 2. How to Run It

### Self-Hosting Options

**Docker (Most Popular Method)**
- Docker Compose deployment with automatic MongoDB container provisioning
- Runs on Ubuntu, CentOS, Debian, and other major Linux distributions
- For production: MongoDB should be deployed separately as a replica set
- Simplest path to getting started

**Kubernetes**
- Official Helm charts available
- Requires kubectl v1.21+ and Helm v3
- Supports microservices architecture for individual service scaling
- StorageClass required for Persistent Volumes
- Best for organizations with existing Kubernetes expertise

**Launchpad (CLI)**
- Automated Kubernetes deployment with guided steps
- Applies best-practice defaults, built-in monitoring
- Verifies dependencies (MongoDB, S3 storage, ingress, certificates)

**Other**
- AWS EC2 deployments supported
- DigitalOcean 1-Click install available

### System Requirements

| Scale | vCPU | RAM | Storage |
|-------|------|-----|---------|
| Up to 50 concurrent users | 1 | 2 GB | 40 GB |

- **Database:** MongoDB replica set (3 members) strongly recommended for HA
- **File Storage:** Amazon S3, Google Cloud Storage, or MinIO recommended (GridFS not recommended)
- **Supported MongoDB versions:** Must be on a supported version; v8.0.0 dropped MongoDB 5.0 and 6.0 support, requiring MongoDB 8.2

### Managed Hosting Options

**Official Rocket.Chat Cloud:**

| Tier | Description |
|------|-------------|
| Standard Cloud | Single-tenant workspace in shared cluster, no SLA |
| Premium Cloud | Isolated workspace with pre-allocated resources, enhanced support |
| Dedicated Private Cloud | Dedicated hardware, custom regional hosting, K8s nodes, MongoDB Atlas HA |

Built on Docker/Kubernetes on AWS. Daily/twice-daily/hourly backups. 24/7 monitoring.

**Third-Party Managed Hosting:**
- Stellar Hosted (European cloud, GDPR-focused)
- AlphaNodes (German cloud servers)
- Railway (~$5-15/month base)
- Kamatera, Hostinger (VPS options)

---

## 3. Security

### Known CVEs

**Total: 50 CVEs** (January 2018 through June 2025)

Note: CVEDetails tracks Rocket.Chat under two separate vendor IDs (17468 and 16681), so both must be checked for a complete picture.

**Highest-severity CVEs (CVSS 7.5+):**

| CVE | CVSS | Description |
|-----|------|-------------|
| CVE-2021-22911 | 7.5 | Unauthenticated NoSQL injection leading to potential RCE (v3.11-3.13) |
| CVE-2021-22910 | 7.5 | Sanitization vulnerability, NoSQL injection leading to potential RCE |
| CVE-2020-29594 | 7.5 | SAML login mishandling |
| CVE-2017-1000493 | 7.5 | NoSQL injection, admin account takeover (v0.59 and prior) |

**Common vulnerability types found:**
- Cross-site scripting (XSS) -- stored and DOM-based
- NoSQL injection (some leading to RCE)
- Server-Side Request Forgery (SSRF)
- Authentication bypass (2FA bypass via CAS)
- Denial of Service (DoS)
- Prototype pollution (escalatable to RCE)
- Information disclosure

**Recent (2024-2025) CVEs:**
- CVE-2025-5892: ReDoS in IRC server module (CVSS 4.0)
- CVE-2024-47048: Stored XSS in marketplace app descriptions
- CVE-2024-46935: Denial of Service
- CVE-2024-46934: DOM-based XSS via UpdateOTRAck
- CVE-2024-45621: Stored XSS in Electron desktop app via PDF links
- CVE-2024-39713: SSRF via Twilio webhook (before v6.10.1)

### Security Audit History and Certifications

| Certification | Status | Details |
|---------------|--------|---------|
| ISO 27001 | Certified | Valid June 2023 - June 2026, audited by QMS Brasil, renewed annually |
| SOC 2 Type II | Attested | Audited by Prescient Assurance |
| SOC 2 Type I | Attested | Previously achieved |

- Annual internal audits per ISO 27001 framework
- Third-party vendor assessments conducted
- The certification process began in 2019; first audit in April 2020

### Encryption

- **In transit:** TLS/HTTPS (standard)
- **End-to-End Encryption (E2EE):** Available for channels -- can create encrypted rooms and encrypt existing rooms. As of late 2025, a unified v2 encryption model was introduced across platforms with strengthened password requirements and authenticated encryption for new data
- **At rest:** Depends on deployment infrastructure (database-level encryption via MongoDB, storage-level encryption via cloud provider)

### SSO / Authentication

| Method | Availability |
|--------|-------------|
| LDAP | Premium plans only |
| SAML | Premium plans only |
| Custom OAuth / OpenID Connect | Premium plans only |
| Two-Factor Authentication (2FA) | All plans |
| Basic OAuth (Google, GitHub, etc.) | All plans |

Note: LDAP is being rewritten in TypeScript. Previously contributed community code for LDAP/SAML/OAuth may no longer be compatible.

### Compliance

Rocket.Chat claims support for:
- HIPAA (with proper configuration: encryption, audit logging, access controls, BAAs)
- GDPR
- FINRA
- FedRAMP
- CCPA

### Vulnerability Disclosure Program

- **HackerOne:** Rocket.Chat runs a Vulnerability Disclosure Program (VDP) at [hackerone.com/rocket_chat](https://hackerone.com/rocket_chat)
- This appears to be a VDP (responsible disclosure) rather than a paid bug bounty
- All vulnerabilities are assigned CVE identifiers
- Public disclosure occurs 30 days after a patch is released
- Security details are initially withheld, then elaborated in the next version release notes

---

## 4. Maintainability

### GitHub Statistics (as of March 2026)

| Metric | Value |
|--------|-------|
| Stars | 44,866 |
| Forks | 13,376 |
| Contributors | 1,190 |
| Open Issues | 2,342 |

### Release Cadence

- **Frequency:** Approximately monthly minor releases
- **LTS:** 2 Long-Term Support releases per year (~every 6 months)
- **Support window:** Each release supported for approximately 6 months
- **Latest stable:** December 5, 2025 (supported until May 31, 2026)
- **Latest pre-release:** v8.0.0-rc.3 (January 7, 2026)
- **Desktop releases:** January 6, 2026 (Electron app)
- **Mobile releases:** Active development through late 2024 / early 2025

### Project Activity (2025-2026)

The project remains actively developed:

- Regular monthly releases across server, desktop, and mobile platforms
- Active Google Summer of Code participation: 19 projects in GSoC 2025 (record-breaking), preparing for GSoC 2026
- 710+ contributors and mentors active in GSoC 2025 channels
- 2026 roadmap publicly shared (roadmap reveal event March 3, 2026)
- Apps Engine repository archived November 2025 and merged into main monorepo (consolidation, not abandonment)
- Focus areas for 2025-2026: ML/AI projects, Attribute-Based Access Control (ABAC), unified E2EE v2, voice calling improvements

### Community

- **GitHub:** 44.8k stars, highly active issue tracker
- **Community server:** Open Rocket.Chat instance for community discussion
- **Forums:** Active at forums.rocket.chat
- **GSoC community:** 800+ participants for 2026 season
- **Documentation:** Comprehensive docs at docs.rocket.chat covering deployment, administration, development, and API reference
- **Stack Overflow, Reddit, Twitter:** Active presence monitored by community management team
- **Third-party communities:** Cloudron, DigitalOcean, Ubuntu Snap

### Bus Factor

**Moderate-to-Good.** Key factors:

- **Corporate backing:** ~180-employee company (Rocket.Chat Technologies Corp.) with $37-48M in funding
- **1,190 contributors** on GitHub, though core development is primarily driven by the company's ~48-person engineering team
- **Risk:** The project is heavily dependent on the company's financial health. If the company were to fail, community continuation would be possible (MIT-licensed core) but challenging given the mixed licensing model
- **Mitigating factors:** Large contributor base, active GSoC pipeline, MIT license on core code, strong community engagement
- **Concerns:** The project direction and most active development comes from the company rather than independent contributors, making it more of a corporate open source project than a community-driven one

### Documentation Quality

- **Official docs:** Comprehensive, well-organized at docs.rocket.chat
- **Coverage:** Deployment guides, API reference, admin guides, developer docs, security documentation
- **Handbooks:** Internal processes are publicly documented at handbook.rocket.chat
- **Gaps:** Community-reported issues suggest some areas (especially advanced deployment configurations) could use more depth
- **Interactive courses and quizzes** available through the community platform

---

## Summary Assessment

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Maturity | High | 10+ years old, well-established |
| Feature completeness | High | Messaging, video, omnichannel, E2EE, federation |
| Self-hosting ease | Medium | Docker is straightforward; production HA requires expertise |
| Security posture | Good | ISO 27001, SOC 2 Type II, HackerOne VDP, regular patching |
| CVE history | Moderate concern | 50 CVEs total, including some high-severity RCE-capable vulnerabilities |
| Open source purity | Mixed | MIT core but EE code mixed in; LDAP/SAML/OAuth require paid plans |
| Community health | Strong | 44.8k stars, 1.19k contributors, active GSoC, monthly releases |
| Corporate sustainability | Moderate | ~180 employees, $37-48M raised, but no recent large funding rounds |
| Documentation | Good | Comprehensive official docs, public handbooks |

### Key Risks

1. **Mixed licensing** -- enterprise features intertwined with open-source code may create confusion and limit the value of the free tier
2. **Financial dependency** -- project health is closely tied to the company financial viability; no major funding round since September 2023
3. **Feature gating** -- critical security features (LDAP, SAML) are locked behind paid plans
4. **CVE history** -- multiple high-severity vulnerabilities discovered, including RCE-capable NoSQL injections

### Key Strengths

1. **Data sovereignty** -- full self-hosting with Docker or Kubernetes
2. **Compliance certifications** -- ISO 27001, SOC 2 Type II, HIPAA/GDPR/FedRAMP support
3. **Active development** -- monthly releases, 2026 roadmap published, strong GSoC participation
4. **Large community** -- one of the largest open-source chat platforms by GitHub stars
5. **Flexible deployment** -- Docker, Kubernetes, cloud hosting, or managed third-party hosting

---

## Sources

- [Rocket.Chat GitHub Repository](https://github.com/RocketChat/Rocket.Chat)
- [Rocket.Chat Official Documentation](https://docs.rocket.chat/)
- [Rocket.Chat Pricing](https://www.rocket.chat/pricing)
- [Rocket.Chat Security and Compliance](https://www.rocket.chat/platform/secure)
- [Rocket.Chat ISO 27001 Announcement](https://www.rocket.chat/press-releases/rocket-chat-is-now-iso-27001-certified)
- [Rocket.Chat SOC 2 Type II Announcement](https://www.rocket.chat/blog/rocket-chat-achieves-soc-2-r-type-ii-attestation)
- [CVEDetails -- Rocket.Chat Vulnerabilities](https://www.cvedetails.com/vulnerability-list/vendor_id-17468/Rocket.chat.html)
- [HackerOne -- Rocket.Chat VDP](https://hackerone.com/rocket_chat)
- [Rocket.Chat Deployment Guide](https://docs.rocket.chat/docs/deploy-rocketchat)
- [Rocket.Chat System Requirements](https://docs.rocket.chat/docs/system-requirements)
- [Rocket.Chat Release Lifecycle](https://docs.rocket.chat/docs/releaselifecycle)
- [Rocket.Chat Security Advisories](https://docs.rocket.chat/docs/rocketchat-security-fixes-updates-and-advisories)
- [Rocket.Chat Community](https://www.rocket.chat/community)
- [IsItReallyFOSS -- Rocket.Chat](https://isitreallyfoss.com/projects/rocket-chat/)
- [Rocket.Chat GSoC 2026](https://github.com/RocketChat/google-summer-of-code/blob/main/google-summer-of-code-2026.md)
- [Rocket.Chat 2026 Roadmap](https://forums.rocket.chat/t/rocket-chat-roadmap-review-2026/22727)
- [End-of-Life Tracking](https://endoflife.date/rocket-chat)
- [Rocket.Chat on Crunchbase](https://www.crunchbase.com/organization/rocket-chat)

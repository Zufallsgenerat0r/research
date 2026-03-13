# Zulip: Open Source Slack Alternative - Research Report

**Date:** 2026-03-13

---

## 1. Overview

**Zulip** is an open-source team chat platform with a unique topic-based threading model that combines the immediacy of chat with the organizational structure of email. It was created in 2012 by Jeff Arnold, Waseem Daher, Jessica McKellar, and Tim Abbott.

### History

- **2012:** Founded as Zulip, Inc.
- **2014:** Acquired by Dropbox while still in private beta
- **Late 2015:** Dropbox released Zulip as open-source software
- **2016:** Tim Abbott founded Kandra Labs to steward Zulip's development
- **2017:** Launched Zulip Cloud (hosted) and enterprise support offerings
- **2025:** Project celebrated its 10th anniversary as open source

### License

- **Apache License 2.0** - fully permissive open-source license
- **100% open source** with no "open-core" restrictions. All features are available in the self-hosted version
- No proprietary enterprise-only features locked behind a paywall

### Programming Languages & Technology Stack

| Component | Technology |
|-----------|------------|
| Backend / Application Server | Python (Django framework) |
| Real-time Event System | Python (Tornado - async) |
| Frontend Web App | TypeScript, Handlebars templates |
| Backend Templates | Jinja2 |
| Mobile Apps (iOS/Android) | Flutter (Dart) |
| Desktop Client | TypeScript (Electron) |
| Terminal Client | Python |
| Database | PostgreSQL (14-18 supported) |
| Caching | Redis, memcached |
| Web Server / Reverse Proxy | Nginx |

### Architecture

Zulip uses a multi-component architecture:

1. **Nginx** serves as the front-end web server, handling static assets and proxying to Django and Tornado
2. **Django** handles the main business logic, API endpoints, authentication, and most HTTP requests
3. **Tornado** maintains tens of thousands of long-lived (long-polling) connections for real-time event/message delivery
4. **PostgreSQL** is the primary data store
5. **Redis** and **memcached** provide caching layers
6. **RabbitMQ** handles message queuing for background tasks

The system supports **multi-realm (multi-tenant)** hosting, where a single server can host multiple organizations on separate subdomains.

---

## 2. How to Run It

### Self-Hosting Options

#### Standard Installation (Bare Metal / VM)

**Supported operating systems:**
- Ubuntu 22.04, Ubuntu 24.04
- Debian 12, Debian 13

The standard installer expects a dedicated machine and installs system packages (nginx, PostgreSQL, Redis) via apt. Recommended approach for most deployments.

#### Docker

- Official Docker image with `docker-compose` configuration
- Helm charts for Kubernetes deployments
- Moderately increases installation/maintenance/upgrade effort vs. standard installer
- Does **not** support docker-rootless or uDocker (requires root for ulimit settings)
- Migration between Docker and standard installation is supported via backup tools

#### Kubernetes

- Helm chart available in the `docker-zulip` repository
- Not designed for easy horizontal scaling of application server containers
- Running multiple zulip application server replicas requires deep knowledge of Zulip internals

#### Pre-built Cloud Images

- Pre-built images for DigitalOcean and Render

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 2 GB | 4 GB (if building containers) |
| Disk | 10 GB (SSD) | More for larger deployments |
| Network (Inbound) | Port 443 (HTTPS) | Port 25 if using email integration |
| Network (Outbound) | Ports 80, 443 (HTTP/S) | Port 587 (SMTP) |

**Additional requirements:**
- SSL certificate for your domain
- Domain name (e.g., `zulip.example.com`)
- SMTP credentials for outgoing email

### Managed Hosting (Zulip Cloud)

| Plan | Price (Monthly) | Price (Annual) | Key Features |
|------|----------------|----------------|--------------|
| **Free** | $0 | $0 | 10,000 message search history; push notifications for up to 10 users |
| **Standard** | $8/user/mo | $6.67/user/mo | Unlimited history, full feature set |
| **Plus** | $12/user/mo | $10/user/mo | SAML/SCIM support, premium features |

### Self-Hosted Plans

| Plan | Price |
|------|-------|
| **Free** | $0 (community edition) |
| **Basic** | $3.50/user/mo |
| **Business** | $6.67/user/mo (annual) / $8/user/mo (monthly) |
| **Enterprise** | Custom pricing |

Sponsorships available for open-source projects, non-profits, education, and academic research (2,000+ organizations sponsored). An 85%+ discount is offered for non-workplace users.

---

## 3. Security

### Known CVEs

As of March 2026, Zulip has **28 total CVEs** listed on CVEDetails. The majority are medium-severity issues (CVSS scores typically 4-6 range). Notable recent CVEs include:

| CVE | Year | Severity | Description |
|-----|------|----------|-------------|
| CVE-2026-24050 | 2026 | - | Fixed in Zulip Server 11.5 |
| CVE-2025-52559 | 2025 | - | Stored XSS in group/channel names (fixed in 10.4 and 11.5) |
| CVE-2025-47930 | 2025 | - | Security issue fixed in 10.3 |
| CVE-2025-31478 | 2025 | - | Auth backend bypass fixed in 10.2 |
| CVE-2024-56136 | 2024 | - | Email address information leak in multi-org setups |
| CVE-2024-27286 | 2024 | - | Incorrect access preservation when moving messages between streams |
| CVE-2023-32678 | 2023 | - | Removed users retained edit/delete access on private streams |
| CVE-2022-21706 | 2022 | - | Reusable invitation link could join wrong organization |

**Assessment:** The CVE count of 28 over approximately 10 years of active development is moderate and in line with similar-scale projects. Most vulnerabilities are access control and XSS issues rather than critical RCE or data breach vectors. The project has been responsive in issuing patches.

### Security Audit History

- **No evidence of formal third-party security audits, penetration tests, or SOC 2 certification** was found
- Zulip's security model relies on:
  - Full open-source transparency (anyone can audit the codebase)
  - HackerOne private vulnerability disclosure program (bug bounty)
  - Rigorous internal code review processes
  - Comprehensive automated test suites with complete coverage of security-sensitive code paths
  - Statically typed Python with extensive linting to prevent common security bugs

### Encryption

| Type | Status |
|------|--------|
| **In Transit** | Yes - TLS/HTTPS enforced |
| **At Rest** | Yes - customer data encrypted at rest |
| **E2E for Push Notifications** | Server support added (mobile app support pending) |

### Authentication & SSO

Zulip supports a wide range of authentication methods:

- **SAML** (Okta, OneLogin, Azure AD / Entra ID, Keycloak, Auth0)
- **OpenID Connect**
- **Microsoft Entra ID** (Azure AD)
- **LDAP** integration with sync
- **SCIM** provisioning (user and group lifecycle management)
- **Google** and **GitHub** OAuth
- **SAML Single Logout** supported
- **REMOTE_USER** SSO for existing SSO setups
- Strong password requirements via zxcvbn password strength checker
- Credential rotation supported

**Note:** SAML and SCIM on Zulip Cloud require the Plus plan.

### Compliance Certifications

- **No SOC 2 Type I or Type II certification** found
- **No ISO 27001 certification** found
- **No FedRAMP or HIPAA certifications** found
- The security controls in place (encryption, access controls, audit logging, SSO) are aligned with SOC 2 Trust Services Criteria, but formal certification has not been publicly documented

### Vulnerability Disclosure Program

- **HackerOne** private bug bounty program
- Security team reachable at `security@zulip.com`
- Formal CVE assignment for all confirmed vulnerabilities
- Public disclosure on the Zulip blog with credit to reporters
- Security releases published for current and previous major release series

---

## 4. Maintainability

### GitHub Statistics

| Metric | Value |
|--------|-------|
| **GitHub Stars** (zulip/zulip) | ~24,800 |
| **Total Contributors** | 1,500+ |
| **Major Contributors** (100+ commits) | 99+ |
| **Commits per Month** | 500+ |
| **Desktop Client Stars** | ~950 |
| **Terminal Client Stars** | ~820 |
| **Docker Image Stars** | ~724 |
| **Flutter Mobile Stars** | ~429 |

### Release Cadence

Zulip follows a **two major releases per year** cadence with security/maintenance patch releases between majors:

| Version | Release Date | Notes |
|---------|-------------|-------|
| 12.0 | Expected early 2026 | Currently in development (12.0-dev+git) |
| 11.5 | Early 2026 | Latest stable; security fix CVE-2026-24050 |
| 11.0 | August 2025 | 76 contributors since 10.0 |
| 10.0 | March 2025 | 121 contributors since 9.0 |
| 9.0 | July 2024 | - |

Security and patch releases (e.g., 10.1, 10.2, 10.3, 10.4) are issued as needed between major releases.

### Community & Activity (2025-2026)

- **Highly active project** with consistent 500+ commits/month
- **10 consecutive years** participating in Google Summer of Code (14 GSoC participants in 2025)
- Recognized as a **GetApp 2025 Category Leader** for collaboration
- **2,000+ organizations** sponsored with free Zulip Cloud Standard hosting
- Active development community with public Zulip chat for contributors
- Many GSoC participants become long-term contributors and core team members

### Documentation Quality

- **185,000+ words** of contributor documentation
- Comprehensive production deployment docs
- Architecture overview documentation
- API documentation with changelog
- Release lifecycle documentation
- Security model documentation
- The documentation is widely regarded as exceptionally thorough for an open-source project

### Bus Factor Analysis

**Strengths:**
- 99+ contributors with 100+ commits each distributes knowledge broadly
- Extensive documentation (185K words) captures institutional knowledge
- Active GSoC pipeline feeds new contributors into the core team
- Community is "unusual in how many people outside the core team have made major contributions"

**Risks:**
- **Tim Abbott** is the founder, lead developer, and CEO of Kandra Labs -- he is the single most critical person to the project
- **Kandra Labs** employs the core development team but has no VC backing and modest funding (~$1M in NSF grants + founder funding + community donations)
- The company is funded through Zulip Cloud revenue, GitHub Sponsors, Patreon, and Open Collective -- sustainability depends on these revenue streams
- Critical subsystems (Tornado real-time system, authentication, etc.) may have concentrated knowledge among a small number of Kandra Labs employees

### Corporate Backing

| Aspect | Detail |
|--------|--------|
| **Steward Company** | Kandra Labs, Inc. |
| **Founded** | April 2016 |
| **CEO / Lead Developer** | Tim Abbott |
| **Headquarters** | San Francisco, CA |
| **Funding** | Founder-funded + ~$1M in NSF SBIR grants (2017, 2018) |
| **VC Backing** | None (privately held, no outside investors) |
| **Revenue Sources** | Zulip Cloud subscriptions, enterprise support, GitHub Sponsors, Patreon, Open Collective |
| **Ownership** | Privately held |

---

## Summary Assessment

| Dimension | Rating | Notes |
|-----------|--------|-------|
| **Openness** | Excellent | Apache 2.0, 100% open source, no open-core restrictions |
| **Deployment Flexibility** | Good | Standard install, Docker, Helm/K8s, managed cloud; horizontal scaling is limited |
| **Security Posture** | Good | 28 CVEs over 10 years, active HackerOne program, encryption at rest/in transit, broad SSO support; lacks formal certifications (SOC 2, ISO 27001) |
| **Community Health** | Excellent | 24.8K stars, 1,500+ contributors, 500+ commits/month, 10 years of GSoC |
| **Documentation** | Excellent | 185K+ words of contributor docs, comprehensive production docs |
| **Corporate Sustainability** | Moderate Risk | Small company (Kandra Labs), no VC funding, heavy reliance on Tim Abbott; mitigated by large contributor base and open-source transparency |
| **Release Maturity** | Good | Predictable twice-yearly cadence, responsive security patches |

---

## Sources

- [Zulip Official Website](https://zulip.com/)
- [Zulip GitHub Repository](https://github.com/zulip/zulip)
- [Zulip Security Page](https://zulip.com/security/)
- [Zulip Architecture Overview](https://github.com/zulip/zulip/blob/main/docs/overview/architecture-overview.md)
- [Zulip Deployment Options](https://zulip.readthedocs.io/en/stable/production/deployment.html)
- [Zulip Requirements and Scalability](https://zulip.readthedocs.io/en/stable/production/requirements.html)
- [Zulip Authentication Methods](https://zulip.readthedocs.io/en/latest/production/authentication-methods.html)
- [Zulip Plans and Pricing](https://zulip.com/plans/)
- [Zulip History](https://zulip.com/history/)
- [Zulip Team Page](https://zulip.com/team/)
- [Zulip CVEs on CVEDetails](https://www.cvedetails.com/vulnerability-list/vendor_id-16270/Zulip.html)
- [Zulip 10.0 Release Announcement](https://blog.zulip.com/2025/03/20/zulip-10-0-released/)
- [Zulip 11.0 Release Announcement](https://blog.zulip.com/2025/08/13/zulip-11-0-released/)
- [Zulip 10th Anniversary Blog Post](https://blog.zulip.com/2025/11/24/zulip-ten-years/)
- [Zulip Version History / Changelog](https://zulip.readthedocs.io/en/latest/overview/changelog.html)
- [Zulip Docker Repository](https://github.com/zulip/docker-zulip)
- [Zulip Wikipedia](https://en.wikipedia.org/wiki/Zulip)
- [ALMtoolbox Zulip Overview (2026)](https://www.almtoolbox.com/blog/zulip-chat-overview/)

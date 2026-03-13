# Mattermost: Research Report as an Open Source Slack Alternative

**Date:** 2026-03-13

---

## 1. Overview

### What Is Mattermost?

Mattermost is an open-core, self-hostable team messaging and collaboration platform positioned as a privacy-focused alternative to Slack and Microsoft Teams. It provides channels, direct messages, file sharing, audio/screen sharing, workflow automation (Playbooks), and integrations with DevOps tools. It is visually similar to Slack, which eases migration.

Founded in 2016 by Corey Hulen and Ian Tien, Mattermost, Inc. is headquartered in Palo Alto, California. The company targets organizations with strict data sovereignty requirements: defense, government, financial services, and critical infrastructure.

**Key facts:**
- **Website:** [mattermost.com](https://mattermost.com)
- **GitHub:** [github.com/mattermost/mattermost](https://github.com/mattermost/mattermost)
- **Current version:** v11.4.x (as of March 2026)
- **Over 800,000 workspaces worldwide**
- **800+ enterprise customers** including NASA, Nasdaq, Samsung, SAP, European Parliament, and the U.S. Air Force

### License Model

Mattermost uses an **open-core** licensing model with multiple layers:

| Component | License |
|---|---|
| Source code (main repo) | **AGPL v3** (GNU Affero General Public License) |
| Compiled monthly releases | **MIT License** |
| Admin tools, templates, webapp | **Apache License v2.0** |
| Enterprise features (`server/enterprise/`) | **Mattermost Source Available License** (non-FOSS) |
| Enterprise Edition binary | **Commercial license** (prohibits reverse engineering) |

Derivative works of the open source code base must use AGPL v3. However, compiled releases distributed by Mattermost, Inc. are MIT-licensed, which is much more permissive.

**Important caveat:** Mattermost Entry (the free tier) now has progressive user limits. Starting limits were 5,000 users (warning) / 11,000 users (hard limit), being lowered toward 1,000 users. A community soft fork called [Mostlymatter](https://framasoft.org) by Framasoft removes these limits.

### Programming Languages and Tech Stack

| Component | Technology |
|---|---|
| **Server/Backend** | Go (38.9% of codebase) |
| **Web App/Frontend** | TypeScript + React (49.7% TypeScript, 6.1% JavaScript) |
| **Mobile Apps** | React Native (iOS and Android) |
| **Desktop Apps** | Electron (Windows, macOS, Linux) |
| **Styling** | SCSS (2.7%) |
| **Database** | PostgreSQL (primary), MySQL (supported) |
| **Web Server/Proxy** | NGINX (recommended) |
| **Search** | Built-in PostgreSQL full-text search; optional Elasticsearch/OpenSearch |

### Architecture

- **Single binary deployment** — the server runs as a single Linux binary
- **RESTful API** — all client-server communication via REST API
- **Modular plugin system** — extensible via plugins, webhooks, and apps
- **Horizontal scaling** — supports cluster-based deployment for high availability
- **Database-backed** — PostgreSQL or MySQL; supports Amazon Aurora
- **File storage** — local filesystem, NFS, or S3-compatible object storage
- **Containerizable** — Docker and Kubernetes supported natively

---

## 2. How to Run It

### Self-Hosting Options

#### Docker (Simplest)
- **Officially supported on Linux only** (macOS/Windows for dev/test only)
- Requires Docker Engine and Docker Compose v1.28+
- Creates two containers (app + database) with optional NGINX reverse proxy
- **Not recommended for HA** — lacks automatic failover, shared storage, and load balancing
- Best for: small teams, evaluation, development

#### Kubernetes (Production/HA)
- Supported on self-hosted clusters and managed services (EKS, AKS, GKE, DigitalOcean, etc.)
- Requires Helm v3.13.0+
- Mattermost provides a Kubernetes Operator for deployment management
- NGINX Operator recommended regardless of platform
- Supports CloudNative PG operator for in-cluster PostgreSQL
- Best for: production deployments requiring high availability

#### Bare Metal / VM
- Install directly on Linux (Ubuntu, Debian, RHEL, etc.)
- Single binary + PostgreSQL + NGINX
- Manual configuration of HA clustering if needed

### System Requirements

| Users | vCPUs | RAM | Storage |
|---|---|---|---|
| 250-500 | 2 cores | 4 GB | 45-90 GB |
| 500-1,000 | 4 cores | 8 GB | 90-180 GB |
| 1,000-2,000 | 4-8 cores | 16-32 GB | 180-360 GB |
| 10,000-20,000 | 4-8 cores | 16-32 GB | Min 4 GB SSD + additional servers for HA |

**Database:** PostgreSQL recommended. MySQL supported but MariaDB v10+ is **not** supported. Amazon Aurora PostgreSQL compatible.

### Managed Hosting / Cloud Options

| Option | Description | Pricing Model |
|---|---|---|
| **Mattermost Entry** (Free) | Self-hosted, all Enterprise features with server-wide limits (10,000 message history, user caps) | Free |
| **Mattermost Professional** | Self-hosted with SSO, advanced permissions | $10/user/month |
| **Mattermost Enterprise** | HA, clustering, advanced compliance, Premier Support eligible | Custom pricing (contact sales) |
| **Third-party: Elestio** | Managed hosting across 8 cloud providers (Hetzner, AWS, DigitalOcean, etc.) | Usage-based (hourly) |
| **Third-party: Runateam** | Fully managed Mattermost hosting | 14-day free trial |
| **Third-party: AccuWeb** | VPS hosting with Mattermost pre-installed | Flat pricing VPS plans |

**Note:** Mattermost discontinued its own cloud hosting offering. GitLab began removing Mattermost from the GitLab Omnibus package in 2025, and SSO was removed from Team Edition starting in v11.

---

## 3. Security

### Encryption

**In Transit:**
- TLS encryption on all data transmissions between clients and server
- AES-256 with 2048-bit RSA
- TLS also available between Mattermost server and SMTP email server
- Default SAML signature algorithm updated from SHA-1 to SHA-256 in v11
- Supports AES-192-GCM and AES-256-GCM encryption for SAML (v10.9+)

**At Rest:**
- **No built-in application-level encryption at rest** — this is by design to preserve search and compliance features
- Relies on external disk/database-level encryption: LUKS (Linux), BitLocker (Windows), PostgreSQL TDE
- S3 server-side encryption supported (Enterprise) with Amazon S3-managed keys
- Organizations are expected to handle encryption at rest at the infrastructure level

### SSO / SAML / Authentication

- **SAML 2.0** support (Mattermost acts as Service Provider)
- **Officially supported IdPs:** Okta, OneLogin, Microsoft ADFS
- **Community-tested IdPs:** Azure AD/Entra ID, Keycloak, PingFederate, DUO, SimpleSAMLphp, miniOrange
- **OpenID Connect (OIDC)** support
- **MFA:** TOTP-based MFA for self-hosted; leverages IdP MFA when using SAML/OIDC (CAC/PIV supported)
- **Certificate-based authentication (CBA)** — experimental
- **Enterprise Mobile Management (EMM)** support
- Account lockout after configurable failed login attempts
- **Note:** GitLab SSO removed from Team Edition in v11

### Known CVEs

Mattermost has a **high volume of CVEs**, which reflects both the size/complexity of the software and the fact that Mattermost acts as its own **CVE Numbering Authority (CNA)**, proactively assigning CVEs.

- **Estimated total:** 400-500+ CVEs across all time (based on ~25 pages of results on OpenCVE)
- **CVEDetails** lists 1,192 Mattermost Server versions included in CVE/CPE data
- **2024-2025 saw particularly high CVE volume**, estimated at 200-300+ combined

**Notable Critical CVEs (2025):**

| CVE | Severity | Description |
|---|---|---|
| CVE-2025-25279 | Critical (CVSS 9.9) | Boards plugin — arbitrary file read / SQL injection |
| CVE-2025-20051 | Critical | Boards plugin — arbitrary file read |
| CVE-2025-24490 | Critical | Boards plugin — SQL injection |
| CVE-2025-12419 | Critical | OAuth state token validation failure — account takeover |
| CVE-2025-12421 | Critical | SSO code exchange — account takeover |
| CVE-2025-4981 | High | Archive extractor path traversal — RCE |
| CVE-2025-11777 | High | Authorization bypass in Add Channel Member API |

**Common vulnerability categories:** authorization/permission bypasses, information disclosure, DoS, SQL injection, XSS/CSRF, OAuth/authentication flaws, arbitrary file read/write, and remote code execution.

### Security Audit History

- Mattermost undergoes **multiple rounds of penetration testing and security analysis** by internal teams, deploying organizations, and the global security research community
- **Red Team / Penetration Testing** conducted against company and product infrastructure
- **Automated code security analysis** on all production repositories
- **SOC 2 Type II** audit completed (report available to licensed customers via Trust Center)
- Publicly available documentation **does not name specific third-party audit firms** or publish detailed audit reports

### Compliance Certifications

| Certification | Status |
|---|---|
| **SOC 2 Type II** | Certified |
| **ISO 27001** | Certified |
| **HIPAA** | Deployment guidance provided (not directly certified; self-hosted model means org is responsible) |
| **FedRAMP** | Not directly authorized; supports IL4/IL5 deployments and air-gapped environments |
| **CMMC 2.0** | Detailed guidance on mapping features to CMMC Level 2 controls |
| **GDPR** | Compliant features provided (data retention, export, right to deletion) |
| **CCPA** | Commitment stated |
| **EAR/ECCN** | Enterprise Edition classified ECCN 5D002 with ENC license exception |

### Vulnerability Disclosure Program

- **Bug bounty program** via [Bugcrowd](https://bugcrowd.com/engagements/mattermost-mbb-public) (transitioned from HackerOne in November 2025)
- Monetary rewards for responsibly disclosed vulnerabilities
- **48-hour acknowledgment** of vulnerability reports on business days
- **30-day embargo** on public disclosure details after fix availability
- Testing allowed on personal instances and the community test server (non-disruptive only)
- Vulnerabilities scored per **CVSS 3.1**
- Security updates announced 30 days after patch availability
- **Security Updates page:** [mattermost.com/security-updates](https://mattermost.com/security-updates/)

---

## 4. Maintainability

### GitHub Statistics (as of March 2026)

| Metric | Value |
|---|---|
| **Stars** | ~35,800 |
| **Forks** | ~8,400 |
| **Watchers** | 534 |
| **Open Issues** | 539 |
| **Open Pull Requests** | 287 |
| **Contributors (main repo)** | ~290 active in past year; 1,000+ all-time contributors acknowledged |
| **Community contributors (all projects)** | 4,000+ (per Mattermost marketing) |
| **Last commit** | 2026-02-09 (at time of initial search) |

### Release Cadence

- **Monthly releases** on the 16th of each month
- **Extended Support Releases (ESR):** every 9 months (changed from 6 months in August 2025), supported for 12 months (increased from 9)
- **Current ESR:** v10.11 (August 2025, supported through August 2026)
- **Next ESR:** v11.7 (May 2026, supported through May 2027)
- **Security patches** backported to previous 3 monthly releases and all supported ESRs

**Recent release timeline:**

| Version | Date |
|---|---|
| v11.4 | 2026-02-16 |
| v11.3 | 2026-01-16 |
| v11.2 | 2025-12-16 |
| v11.1 | 2025-11-14 |
| v11.0 | 2025-10-16 |
| v10.12 | 2025-09-16 |
| v10.11 ESR | 2025-08-16 |
| Desktop v6.1.0 | 2026-03-02 |

### Community Size

- **Mattermost Community Server** hosts thousands of active users, contributors, and Mattermost staff
- **Discussion Forum:** [forum.mattermost.com](https://forum.mattermost.com) — active community support
- **800,000+ workspaces** deployed worldwide
- **700,000+ translations** contributed by community
- **1,000+ open source projects on GitHub** referenced Mattermost (as of 2018)
- Community soft fork "Mostlymatter" by Framasoft exists (removes user limits)

### Documentation Quality

- **Comprehensive official docs** at [docs.mattermost.com](https://docs.mattermost.com) covering deployment, administration, security, compliance, and API reference
- **Mattermost Handbook** at [handbook.mattermost.com](https://handbook.mattermost.com) — open company handbook with internal processes
- **API documentation** with RESTful endpoints fully documented
- **Deployment guides** for Docker, Kubernetes, bare metal
- **Security guides** including CMMC compliance mapping
- Documentation actively maintained with the product release cycle

### Project Activity (2025-2026)

The project remains **very active** as of early 2026:
- Monthly releases continuing on schedule
- Desktop app v6.1.0 released March 2, 2026
- GitHub plugin v2.6.0 released February 9, 2026
- Active development of AI features ("Intelligent Mission Environment")
- Expansion into sovereign cloud deployments (Finland defense sector, August 2025)
- Azure Secret/Top Secret cloud development announced at AFCEA West 2025
- ESR lifecycle adjustment indicates maturing enterprise focus

### Bus Factor

**Moderate to Good.** Mitigating and risk factors:

- **Corporate backing:** Mattermost, Inc. with 156-162 employees, 54 engineers
- **$70.6M in total funding** from Battery Ventures, Redpoint, S28 Capital, Y Combinator
- **$33.1M revenue in 2024** (up from $20.7M in 2023) — growing and viable
- **~290 contributors** active in the past year on the main repo
- **AGPL-licensed source code** means the community can fork and continue development if the company fails
- **Community fork already exists** (Mostlymatter by Framasoft)
- **Risk:** Most core development is done by Mattermost employees; community contributions are significant but not dominant
- **Risk:** No known acquisition or IPO plans; reliance on continued venture/revenue funding

### Corporate Backing

| Metric | Value |
|---|---|
| **Company** | Mattermost, Inc. |
| **Founded** | 2016 |
| **HQ** | Palo Alto, California |
| **Founders** | Corey Hulen, Ian Tien |
| **Employees** | 156-162 |
| **Engineering team** | 54 |
| **Total funding** | $70.6M (3 rounds) |
| **Last round** | Series B, $50.4M (June 2019) |
| **Key investors** | Battery Ventures, Redpoint, S28 Capital, Y Combinator |
| **Revenue (2024)** | $33.1M |
| **Revenue (2023)** | $20.7M |
| **Customers** | 800+ (NASA, Nasdaq, Samsung, SAP, U.S. Air Force, European Parliament) |

---

## Summary Assessment

| Dimension | Rating | Notes |
|---|---|---|
| **Maturity** | High | 10+ years of development, v11.x, monthly releases |
| **Self-hosting ease** | Moderate | Docker is straightforward; production HA requires Kubernetes expertise |
| **Security posture** | Mixed | Active vulnerability management and bug bounty, but high CVE volume; no application-level encryption at rest |
| **Compliance** | Strong | SOC 2 Type II, ISO 27001; supports HIPAA/CMMC/GDPR deployments |
| **Community** | Large | 35.8k GitHub stars, active forum, but core development is company-driven |
| **Corporate viability** | Good | Growing revenue ($33M), strong defense/government customer base |
| **Longevity risk** | Low-Medium | AGPL license protects community; no funding since 2019 but revenue growing |
| **Documentation** | Excellent | Comprehensive docs, open handbook, active maintenance |

---

## Sources

- [Mattermost Official Site](https://mattermost.com)
- [Mattermost Documentation](https://docs.mattermost.com)
- [GitHub: mattermost/mattermost](https://github.com/mattermost/mattermost)
- [Mattermost Security Page](https://mattermost.com/security/)
- [Mattermost Security Updates](https://mattermost.com/security-updates/)
- [Mattermost Pricing](https://mattermost.com/pricing/)
- [Mattermost Editions and Offerings](https://docs.mattermost.com/product-overview/editions-and-offerings.html)
- [Mattermost Certifications and Compliance](https://docs.mattermost.com/product-overview/certifications-and-compliance.html)
- [Mattermost Encryption Options](https://docs.mattermost.com/deployment-guide/encryption-options.html)
- [Mattermost Release Policy](https://docs.mattermost.com/product-overview/release-policy.html)
- [Mattermost SAML Documentation](https://docs.mattermost.com/administration-guide/onboard/sso-saml.html)
- [Mattermost Software/Hardware Requirements](https://docs.mattermost.com/deployment-guide/software-hardware-requirements.html)
- [Mattermost Deploy on Kubernetes](https://docs.mattermost.com/deployment-guide/server/deploy-kubernetes.html)
- [Mattermost Deploy with Containers](https://docs.mattermost.com/deployment-guide/server/deploy-containers.html)
- [Mattermost Bug Bounty (Bugcrowd)](https://bugcrowd.com/engagements/mattermost-mbb-public)
- [Mattermost Vulnerability Disclosure](https://mattermost.com/security-vulnerability-report/)
- [Mattermost Handbook - Security](https://handbook.mattermost.com/operations/security/product-security/product-vulnerability-process)
- [CVEDetails - Mattermost](https://www.cvedetails.com/vendor/21455/Mattermost.html)
- [OpenCVE - Mattermost](https://app.opencve.io/cve/?vendor=mattermost)
- [Mattermost on Crunchbase](https://www.crunchbase.com/organization/mattermost)
- [Mattermost Revenue Data (Getlatka)](https://getlatka.com/companies/mattermost)
- [Mattermost End of Life Dates](https://endoflife.date/mattermost)
- [Mattermost Open Source Community](https://mattermost.com/community/)
- [Is Mattermost Really FOSS?](https://isitreallyfoss.com/projects/mattermost/)
- [Cibersafety - Mattermost Vulnerabilities 2025](https://cibersafety.com/en/mattermost-vulnerabilities-cve-2025/)
- [Qualys - Mattermost Critical CVEs 2025](https://threatprotect.qualys.com/2025/02/25/mattermost-releases-fixes-for-critical-vulnerabilities-cve-2025-25279-cve-2025-20051-cve-2025-24490/)
- [Slack vs Mattermost (wz-it.com)](https://wz-it.com/en/blog/slack-vs-mattermost/)

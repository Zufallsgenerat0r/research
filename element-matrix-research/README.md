# Element / Matrix as an Open-Source Slack Alternative

**Research Date:** 2026-03-13

---

## 1. Overview

### What Is It?

**Element** is an open-source, real-time communication client (web, desktop, mobile) built on the **Matrix protocol**. It is the leading client for Matrix and positions itself as a privacy-focused, federated alternative to Slack, Microsoft Teams, and Discord.

- **Element** was formerly known as **Riot** (and before that, **Vector**)
- **Matrix** is the underlying open standard/protocol for decentralized, federated real-time communication
- **Synapse** is the reference Matrix homeserver implementation
- The project was created in 2014 by Matthew Hodgson and Amandine Le Pape while at Amdocs

### The Matrix Protocol

Matrix defines a set of open APIs for decentralized communication. Key architectural concepts:

| Concept | Description |
|---------|-------------|
| **Rooms** | Virtual spaces where clients exchange events (messages, state changes) |
| **Events** | The fundamental unit of data; rooms are modeled as a partially-ordered graph of events |
| **Federation** | Homeservers replicate room data between each other via the Server-Server API over HTTPS with public key authentication |
| **Eventual Consistency** | Matrix optimizes for Availability and Partition tolerance (AP in CAP theorem) |
| **Bridging** | Allows connecting to external systems (IRC, Slack, Discord, etc.) |

Key APIs:
- **Client-Server API** -- how clients talk to homeservers
- **Server-Server (Federation) API** -- how homeservers talk to each other
- **Application Service API** -- for bridges and bots

The full specification is at [spec.matrix.org](https://spec.matrix.org/latest/).

### Programming Languages

| Component | Language(s) | Notes |
|-----------|-------------|-------|
| **Synapse** (homeserver) | Python (Twisted) + Rust | Reference implementation; Rust compiler required to build |
| **Dendrite** (homeserver) | Go | Second-generation; now in **maintenance mode** (security fixes only) |
| **Conduit** (homeserver) | Rust | Lightweight alternative; community-maintained |
| **Element Web** | TypeScript | Uses matrix-js-sdk |
| **Element iOS/Android (Element X)** | Swift / Kotlin | Uses matrix-rust-sdk |
| **matrix-rust-sdk** | Rust | Core SDK powering newer clients |
| **vodozemac** | Rust | Replacement for libolm (crypto library) |

### Architecture

```
Users <-> Element Client <-> Homeserver (Synapse) <-> Federation <-> Other Homeservers
                                |
                          PostgreSQL/SQLite
                                |
                    Matrix Authentication Service (MAS)
                                |
                         OIDC / SSO Provider
```

- Frontend: Element apps (web, desktop, iOS, Android)
- Backend: Synapse homeserver + PostgreSQL (recommended) or SQLite
- Auth: Matrix Authentication Service (MAS) for OIDC-native auth, or legacy Synapse auth
- Calls: Element Call (WebRTC-based, uses LiveKit for SFU)
- Encryption: Olm (1:1) and Megolm (group) via vodozemac or libolm

### Licensing

| Component | License | Notes |
|-----------|---------|-------|
| Synapse | **AGPLv3** (or Element Commercial License) | Changed from Apache 2.0 in late 2023 |
| Element Web/Desktop | **AGPLv3** (or Element Commercial License) | Same change |
| Element iOS/Android | **AGPLv3** | Same change |
| Client SDKs (matrix-js-sdk, matrix-rust-sdk, etc.) | **Apache 2.0** | Deliberately kept permissive to drive adoption |
| Element Server Suite (ESS) | Enterprise license (commercial) | Separate from AGPL |

The AGPL license requires anyone who modifies and deploys the software to release their modifications as open source -- or purchase a commercial license from Element ("Build" subscription).

---

## 2. How to Run It

### Self-Hosting Options

#### Option A: Element Server Suite Community (Recommended by Element)
- **Method:** Helm charts on Kubernetes (K3s, microk8s, KinD, or existing cluster)
- **Includes:** Synapse + Matrix Authentication Service + Element Call (LiveKit) + Element Web
- **Supports:** Matrix 2.0 features, up to ~100 users
- **License:** AGPLv3 (free for non-commercial community use)
- **Minimum Requirements:** 2 CPUs, 2 GB RAM
- **Repo:** [element-hq/ess-helm](https://github.com/element-hq/ess-helm)

#### Option B: Docker Compose (Traditional)
- **Method:** Docker Compose with Synapse + Element Web + PostgreSQL + reverse proxy
- **Best for:** Homelabs, small teams, simple setups
- **Requirements:** 1-2 vCPU, 2-4 GB RAM
- **Guides:** [selfhosthero.com](https://selfhosthero.com/guide-self-host-matrix-synapse-with-element-client/), [cyberhost.uk](https://cyberhost.uk/element-matrix-setup/)

#### Option C: Docker Demo (Experimentation Only)
- **Method:** `element-docker-demo` Docker Compose project
- **Best for:** Quick Matrix 2.0 experimentation; **not for production**
- **Repo:** [element-hq/element-docker-demo](https://github.com/element-hq/element-docker-demo)

#### Option D: Bare Metal / Package Manager
- Synapse provides Debian packages and PyPI packages
- Requires manual setup of PostgreSQL, reverse proxy (nginx/caddy), TLS, TURN server (coturn)

### System Requirements

| Server | Small (<50 users) | Medium (50-500 users) | Large (500+ users) |
|--------|-------------------|----------------------|-------------------|
| **Synapse** | 2 vCPU, 2-4 GB RAM, PostgreSQL | 4 vCPU, 8 GB RAM, PostgreSQL | 8+ vCPU, 16+ GB RAM, PostgreSQL, worker mode |
| **Dendrite** | 1 vCPU, ~100-200 MB RAM | Not well-tested at scale | Not recommended for production |

**Important notes on Synapse scaling:**
- SQLite is only suitable for testing; PostgreSQL is required for any real deployment
- Joining large federated rooms (e.g., Matrix HQ with thousands of members) significantly increases resource usage
- Synapse supports "worker" mode for horizontal scaling of specific functions
- Federation can be resource-intensive; closed federations use fewer resources

### Managed Hosting Options

| Option | Description | Pricing |
|--------|-------------|---------|
| **Element Cloud** (EMS) | Managed hosting by Element | ~$3/monthly active user (contact sales for current pricing) |
| **Element Enterprise Cloud** | Dedicated hosting, 500+ users | ~$4/MAU + enterprise features |
| **Element Starter** | Free self-hosted ESS | Up to 200 users, free |
| **ESS Community** | Free self-hosted Kubernetes deployment | Up to ~100 users, AGPLv3 |
| **Third-party** (Elest.io, etc.) | Community managed hosting | Varies |

---

## 3. Security

### Known CVEs (2023-2025)

A total of approximately **14+ CVEs** have been published for Matrix Synapse across 2023-2025. Key categories:

**2025 (3 known):**
| CVE | Severity | Description |
|-----|----------|-------------|
| CVE-2025-30355 | High | Federation DoS; **exploited in the wild**. Fixed in v1.127.1 |
| CVE-2025-49090 | High | State resolution vulnerability; coordinated multi-server fix (room version 12) |
| CVE-2025-61672 | Medium | Device key validation issue degrading federation |

**2024 (6 known):**
| CVE | Severity | Description |
|-----|----------|-------------|
| CVE-2024-37303 | Medium | Unauthenticated remote media download |
| CVE-2024-31208 | High | V2 state resolution DoS (high CPU + memory) |
| CVE-2024-52815 | Medium | Memory amplification via multipart/form-data |
| CVE-2024-52805 | Medium | Sliding Sync room state leakage |
| CVE-2024-53863 | Medium | Thumbnail generation with arbitrary image formats |
| CVE-2024-52816 | Medium | Malformed federation invite breaks /sync |

**2023 (5 known):**
| CVE | Description |
|-----|-------------|
| CVE-2023-32323 | Federation-exploitable bugs |
| CVE-2023-42453 | Forged read receipts |
| CVE-2023-45129 | Malicious server ACL DoS |
| CVE-2023-41335 | Temporary plaintext password storage |
| CVE-2023-43796 | Remote user enumeration via cached device info |

**Assessment:** The CVE rate is moderate and consistent with an actively-maintained project handling complex federation. Most vulnerabilities are DoS or information leakage rather than remote code execution. The one actively-exploited CVE (CVE-2025-30355) was a federation DoS, not a data breach.

### Security Audit History

| Year | Auditor | Scope | Key Findings |
|------|---------|-------|-------------|
| 2016 | **NCC Group** | Olm/Megolm protocols + libolm | Unknown key-share attack in Megolm; several implementation issues |
| 2022+ | **Least Authority** | vodozemac (Rust Olm/Megolm) | Implementation-level cryptographic issues |
| 2022+ | Matrix.org (internal) | Series of core library audits | Ongoing |
| 2023-2024 | Academic researchers | Formal cryptographic analysis | Confirmed Megolm forward secrecy limitations; Olm pre-key signing requirements |

### End-to-End Encryption (E2EE)

**Current implementation:** Olm (1:1 ratchet, based on Signal's Double Ratchet) + Megolm (group ratchet)

**Strengths:**
- E2EE enabled by default for private rooms
- Cross-signing and device verification supported
- Key backup and recovery mechanisms
- vodozemac (Rust) replacing deprecated libolm (C/C++)

**Known Limitations:**
- **Megolm lacks strong forward secrecy** for group messages -- compromising a key allows decryption of past messages in that session
- **Metadata is not encrypted** -- sender identity, device info, timestamps visible to homeserver operators
- **libolm still widely used** -- only 3 of 16 surveyed Matrix clients use vodozemac (19% adoption)
- **No post-compromise security** in Megolm
- **MLS (Messaging Layer Security)** is the planned next-generation protocol but is reportedly years away from implementation

**Upcoming (April 2026):** Only verified devices will be able to send/receive E2EE messages in Element, improving trust model.

### Encryption at Rest

Synapse does **not** provide native database encryption at rest. Options:
- PostgreSQL Transparent Data Encryption (TDE)
- Filesystem-level encryption (LUKS, dm-crypt)
- Cloud provider disk encryption (AWS RDS, Azure, GCP)

This is an infrastructure-layer concern, not application-layer.

### SSO / Authentication

| Method | Status |
|--------|--------|
| **OIDC** (OpenID Connect) | Fully supported; the strategic direction via MAS |
| **SAML 2.0** | Supported in legacy Synapse auth; **not supported in MAS** (requires bridge like Dex) |
| **CAS** | Supported in legacy Synapse auth |
| **LDAP** | Supported via MAS or legacy auth |
| **MFA** | Delegated to the upstream Identity Provider |

**Matrix Authentication Service (MAS)** is the new recommended auth layer, OIDC-native. Organizations using SAML must bridge through Dex, Authentik, or similar.

### Compliance Certifications

| Certification | Status |
|---------------|--------|
| **ISO/IEC 27001:2022** | Certified (information security management) |
| **Cyber Essentials Plus** | Certified (UK government cybersecurity scheme) |
| **ISO/IEC 5230 (OpenChain)** | Compliant (open-source license compliance) |
| **GDPR** | Supported via self-hosting / data sovereignty |
| **HIPAA** | Possible with appropriate self-hosting configuration (no explicit certification found) |

### Vulnerability Disclosure Program

- **Email:** security@matrix.org
- **Response time:** Within 5 business days
- **Fix timeline:** 90 days (120 days for complex issues)
- **Delayed disclosure:** Up to 30 additional days for especially disruptive vulnerabilities
- **Recognition:** Security Hall of Fame at matrix.org
- **Bug bounty:** No formal bounty program from the Foundation; individual organizations building on Matrix may offer bounties

---

## 4. Maintainability

### GitHub Repository Statistics

| Repository | Stars | Forks | Contributors | Open Issues | Language | License |
|-----------|-------|-------|-------------|-------------|----------|---------|
| **element-hq/element-web** | ~12,800 | ~2,500 | ~70+ active | ~3,555 | TypeScript | AGPL-3.0 |
| **element-hq/synapse** | ~3,840 | ~484 | ~127 | ~1,831 | Python + Rust | AGPL-3.0 |
| **matrix-org/synapse** (archived) | ~11,800 | ~2,100 | -- | -- | Python | Apache 2.0 |
| **matrix-org/dendrite** | ~5,600+ | ~800+ | -- | -- | Go | Apache 2.0 |

Note: The star count split between matrix-org/synapse (archived, 11.8k) and element-hq/synapse (3.8k) reflects the 2024 repo transfer. Combined, Synapse has ~15.6k stars historically.

### Release Cadence

- **Synapse:** **2-week release cycle** (Tuesday releases, RC the week before)
- **Element Web:** **2-week release cycle**
- **Element X (mobile):** Regular releases (frequency not pinned to exact schedule)
- **ESS Helm:** Active releases tracked at [element-hq/ess-helm](https://github.com/element-hq/ess-helm/releases)
- **LTS versions:** Released every 6 months for enterprise customers with backported security fixes

### Community Size

| Metric | Value | Source/Date |
|--------|-------|-------------|
| Total Matrix accounts | ~115 million | Oct 2023 |
| Matrix network users | 80M+ | Element user guide page |
| Known deployments | 80,000+ | Element user guide page |
| matrix.org DAU | 250,000+ | Early 2024 |
| Countries deploying Matrix (govt) | 25+ | End of 2025 |
| Matrix Conference 2025 attendees | 300+ from 20+ countries | Sep 2025 |

### Project Activity (2025-2026)

The project is **actively maintained** as of March 2026:
- Regular 2-week release cycles for both Synapse and Element Web
- Active security response (multiple CVE fixes in 2025, coordinated room version 12 release)
- Matrix 2.0 features being shipped (Sliding Sync, native OIDC, Element Call)
- Element X (next-gen mobile client based on matrix-rust-sdk) under active development
- FOSDEM 2026 presentations on Element Web's future
- Matrix Conference 2025 showed strong government adoption momentum

### Bus Factor & Corporate Backing

**Element (the company):**
- Founded 2017 (as New Vector Ltd), spun out of Amdocs
- HQ: London, UK
- Total funding: ~$48M+ (Series A + Series B led by Protocol Labs, Metaplanet)
- Key investors: Protocol Labs, Metaplanet (Jaan Tallinn/Skype), Automattic, Notion, Amdocs Ventures
- Element employees contribute >90% of core Matrix server and SDK code
- Revenue: ~$3.6M in 2024 (per one source; enterprise contracts may not be fully reflected)
- Team size: ~62 employees (per one source, may be outdated)

**Matrix.org Foundation:**
- UK non-profit Community Interest Company (CIC) governing the Matrix spec
- Revenue: $561K in 2024 (nearly doubled from prior year)
- Operating costs: ~$1.2M/year
- Deficit: $356K in 2024
- **Financial crisis in Feb 2025**: needed $100K urgently to avoid shutting down bridges
- 20 funding organizational members (DINUM/France, Rocket.Chat, Automattic/Beeper, Gematik)
- Half of budget now covered by funding members (moving toward independence from Element)
- Most Foundation staff are Element employees on contract

**Bus Factor Assessment:**
- **High dependency on Element:** Element contributes >90% of core code and employs most Foundation staff
- **Foundation financial fragility:** The Foundation's 2025 financial crisis highlights sustainability risks
- **Mitigating factors:** Growing government adoption (France, Germany, EU), 20 organizational members, open specification allows alternative implementations
- **Dendrite maintenance mode** reduces homeserver implementation diversity
- The AGPL license change was partly motivated by organizations using Matrix without contributing back

### Documentation Quality

- **Official docs:** [matrix-org.github.io/synapse](https://matrix-org.github.io/synapse/latest/) (comprehensive)
- **Matrix spec:** [spec.matrix.org](https://spec.matrix.org/latest/) (detailed, well-structured)
- **Element docs:** [docs.element.io](https://docs.element.io/) (ESS deployment guides)
- **Community resources:** Active Matrix rooms (#synapse:matrix.org, #matrix-dev:matrix.org), community guides
- **Quality assessment:** Documentation is generally good for deployment and configuration. The spec itself is thorough. Third-party guides are abundant due to community size.

### Notable Government / Enterprise Adopters

| Organization | Country | Use Case |
|-------------|---------|----------|
| DINUM / Tchap | France | 5.5M civil servants |
| BWI (German military) | Germany | Armed forces communications |
| Dataport | Germany | Education and public admin |
| Gematik (Ti-Messenger) | Germany | Healthcare real-time communication |
| ZenDiS / openDesk | Germany | Government office suite |
| European Commission | EU | Inter-governmental communication |
| Mozilla | USA | Community communication |

---

## Summary Assessment

### Strengths
- **True federation and data sovereignty** -- unique among Slack alternatives
- **Strong E2EE by default** -- critical for government/regulated industries
- **Active development** with 2-week release cycles
- **Massive adoption** -- 80M+ users, 25+ government deployments
- **Open specification** -- not locked to a single vendor
- **Rich feature set** -- threads, reactions, voice/video calls, spaces, bridges

### Weaknesses
- **Resource-heavy** -- Synapse can consume significant RAM/CPU, especially with large federated rooms
- **Foundation financial fragility** -- sustainability concerns for the nonprofit governing the spec
- **High dependency on Element** -- >90% of core code from one company
- **Encryption limitations** -- Megolm lacks forward secrecy; MLS adoption years away
- **AGPL license** -- may deter some commercial adopters vs. Apache/MIT
- **Complexity** -- federation, encryption, and multiple components increase operational overhead vs. simpler alternatives like Mattermost

### Comparison Context
- **vs. Mattermost:** Mattermost is simpler to deploy, has $130M+ in VC, but lacks true federation and has per-seat pricing for advanced features
- **vs. Rocket.Chat:** Rocket.Chat is simpler, supports some federation, is a Foundation member, but less mature E2EE
- **vs. Slack/Teams:** Element offers data sovereignty and no vendor lock-in, but requires more operational investment

---

## Sources

- [Element Official Site](https://element.io)
- [Matrix.org](https://matrix.org)
- [Matrix Specification](https://spec.matrix.org/latest/)
- [element-hq/synapse on GitHub](https://github.com/element-hq/synapse)
- [element-hq/element-web on GitHub](https://github.com/element-hq/element-web)
- [matrix-org/dendrite on GitHub](https://github.com/matrix-org/dendrite)
- [element-hq/ess-helm on GitHub](https://github.com/element-hq/ess-helm)
- [Matrix Synapse CVE Details](https://www.cvedetails.com/vulnerability-list/vendor_id-2044/product_id-54323/Matrix-Synapse.html)
- [Matrix Security Disclosure Policy](https://matrix.org/security-disclosure-policy/)
- [Element Blog: AGPL License Change](https://element.io/blog/element-to-adopt-agplv3/)
- [Element Blog: Sustainable Licensing](https://element.io/blog/sustainable-licensing-at-element-with-agpl/)
- [Matrix.org Blog: Foundation at a Crossroads (Feb 2025)](https://matrix.org/blog/2025/02/crossroads/)
- [Matrix.org Blog: 2025 Holiday Special](https://matrix.org/blog/2025/12/24/matrix-holiday-special/)
- [Element Pricing](https://element.io/en/pricing)
- [NCC Group Olm Audit (2016)](https://matrix.org/blog/2016/11/21/matrixs-olm-end-to-end-encryption-security-assessment-released-and-implemented-cross-platform-on-riot-at-last/)
- [Practically-exploitable Cryptographic Vulnerabilities in Matrix](https://nebuchadnezzar-megolm.github.io/)
- [Wire: Why Olm and Megolm Fail EU Data Privacy Standards](https://wire.com/en/blog/olm-megolm-eu-data-privacy-risk)
- [Matrix Protocol: Comprehensive Systematic Mapping Study (Springer, 2025)](https://link.springer.com/article/10.1186/s13677-025-00829-7)
- [TechCrunch: Element raises $30M (2021)](https://techcrunch.com/2021/07/27/element-a-messaging-app-built-on-the-decentralized-matrix-protocol-raises-30m/)
- [The Register: Matrix Leaps 60M Users (2022)](https://www.theregister.com/2022/07/15/matrix_grows/)
- [The Stack: Matrix hits 115M Users (2023)](https://www.thestack.technology/matrix-protocol-users-2023/)

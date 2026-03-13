# Element / Matrix Research Notes

## Research Log

### 2026-03-13: Initial Research

**Objective:** Evaluate Element (Matrix client) and Matrix/Synapse server as an open-source Slack alternative.

#### Search Strategy
- Used web searches across multiple dimensions: overview/architecture, self-hosting, security, maintainability
- Targeted specific GitHub repos, CVE databases, official documentation, and news sources
- Cross-referenced multiple sources for accuracy on numbers

#### Key Findings

**Overview & Architecture:**
- Matrix is an open protocol (spec at spec.matrix.org), introduced 2014, v1.0 in June 2019
- Element is the primary client (formerly Riot, formerly Vector), built by Element company (formerly New Vector Ltd)
- Synapse is the reference homeserver: Python/Twisted + Rust
- Dendrite was the next-gen Go homeserver but is now in **maintenance mode** (security fixes only)
- License changed from Apache 2.0 to AGPLv3 in late 2023 for Synapse and Element apps
- Client SDKs (matrix-rust-sdk, matrix-js-sdk, etc.) remain Apache 2.0
- Synapse repo moved from matrix-org/synapse (archived Apr 2024, ~11.8k stars) to element-hq/synapse (~3.8k stars as of Mar 2026)

**Self-Hosting:**
- Multiple deployment paths: ESS Community (Helm/K8s), Docker Compose, bare metal
- ESS Community: min 2 CPUs, 2GB RAM, Kubernetes required, up to 100 users, AGPLv3
- Traditional Docker Compose: 1-2 vCPU, 2-4 GB RAM for Synapse + Element Web
- Dendrite: as low as ~100MB RAM for small deployments but maintenance-mode only
- Managed hosting: Element Matrix Services (EMS) from $3-4/MAU (may be outdated pricing)
- Element Starter: free self-hosted ESS for up to 200 users

**Security:**
- ~14+ CVEs across 2023-2025, mostly federation abuse and DoS
- CVE-2025-30355 was exploited in the wild (federation DoS)
- CVE-2025-49090 was a high-severity state resolution vulnerability requiring coordinated release
- NCC Group audited Olm/Megolm in 2016; Least Authority audited vodozemac (Rust replacement)
- Olm/Megolm have known limitations: Megolm lacks strong forward secrecy, metadata exposure
- Only 3 of 16 Matrix clients use vodozemac; 10 still use deprecated libolm
- MLS (Messaging Layer Security) is planned but years away
- No native encryption at rest in Synapse; relies on infrastructure-level encryption
- SSO: Synapse supports SAML/OIDC/CAS; MAS (new auth service) is OIDC-only, needs bridge for SAML
- Certifications: ISO 27001:2022, Cyber Essentials Plus, ISO/IEC 5230 (OpenChain)
- Vulnerability disclosure via security@matrix.org, 90-day fix timeline, Security Hall of Fame

**Maintainability:**
- element-web: ~12.8k stars, TypeScript, AGPL-3.0, 2-week release cycle
- element-hq/synapse: ~3.8k stars, 127 contributors, 1,831 open issues, 2-week release cycle
- matrix-org/synapse (archived): ~11.8k stars, 2.1k forks
- Matrix network: 80M+ users, 80K+ deployments, 115M accounts reported Oct 2023
- matrix.org homeserver: 250K+ daily active users
- Element company: raised ~$48M+ total, spun out of Amdocs, HQ in London
- Matrix.org Foundation: nonprofit governing the spec, nearly doubled revenue in 2024 ($561K), but $356K deficit
- Foundation financial crisis in Feb 2025: needed $100K urgently, $610K to break even
- 20 funding organizational members including DINUM (France), Rocket.Chat, Automattic/Beeper, Gematik
- 25+ countries deploying Matrix for digital sovereignty
- Matrix Conference 2025: 300+ participants from 20+ countries, 10+ governments

**Concerns Noted:**
- Foundation financial sustainability is a real risk (bus factor concern)
- Dendrite in maintenance mode reduces homeserver diversity
- License change to AGPL may deter some adopters
- Synapse resource consumption can be significant at scale
- Encryption limitations (forward secrecy, metadata) are well-documented academic concerns
- Wire (competitor) published critical analysis of Olm/Megolm EU compliance

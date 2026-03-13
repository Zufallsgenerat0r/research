# Revolt (Stoat) - Open Source Slack/Discord Alternative: Research Report

**Date:** 2026-03-13

---

## 1. Overview

### What Is It?

[Revolt](https://revolt.chat) is an open-source chat platform launched in 2021 as a privacy-focused alternative to Discord. It replicates Discord's familiar server/channel model while offering open-source transparency and self-hosting capabilities. In late 2025, the project was legally compelled to rebrand to **Stoat** (stoat.chat), though the codebase and team remain the same.

### License

- **Core backend and web client:** GNU Affero General Public License v3.0 (AGPLv3)
- **Python wrapper (revolt.py):** MIT License
- **Caveat -- Semi-Open-Source:** Several important components are proprietary or use non-FOSS licenses:
  - Admin control panel (new version: AGPLv3 with proprietary components; old version: FUTO license)
  - Automod / platform moderation tools
  - Server discovery feature (FUTO license)
  - Built-in image hosting service
  - Some source code lives on a separate GitLab instance that is not prominently linked
- The self-hosted version **lags behind** the official instance and is stripped of proprietary features

### Programming Language & Architecture

| Component | Language/Tech | Description |
|-----------|--------------|-------------|
| Backend (revolt-delta) | **Rust** | REST API server |
| Events (revolt-bonfire) | **Rust** | WebSocket events server |
| File Server (revolt-autumn) | **Rust** | File upload/storage |
| Proxy (revolt-january) | **Rust** | Media proxy server |
| Tenor Proxy (revolt-gifbox) | **Rust** | GIF proxy |
| Push Daemon (revolt-pushd) | **Rust** | Push notifications |
| Web Client (Revite) | **TypeScript/Preact** | Browser-based UI |
| Desktop Client | **Electron/JavaScript** | Desktop wrapper |
| Voice/Video | **Rust + LiveKit (WebRTC)** | Real-time communication |

**Infrastructure dependencies:**
- **MongoDB** -- primary database
- **Redis** (or KeyDB/Valkey) -- caching and pub/sub
- **RabbitMQ** -- message broker (added in recent versions)

The architecture is **microservices-based**, with each component running as a separate service, typically orchestrated via Docker Compose.

---

## 2. How to Run It

### Self-Hosting via Docker (Primary Method)

**Minimum system requirements:**
- 2 vCPUs
- 2 GB RAM
- Ubuntu 20.04+ recommended (used in production)
- Docker and Docker Compose

**Network requirements:**
- Ports 80 and 443 (HTTP/HTTPS)
- Ports 7881/tcp and 50000-50100/udp (voice/video via LiveKit)

**Quick start:**
```bash
git clone https://github.com/stoatchat/self-hosted
cd self-hosted
# Configure Revolt.toml and .env.web with your domain
docker compose up -d
```

**Important caveats:**
- **amd64 only** -- backend and bonfire images are only available for amd64
- **ARM support** is limited; KeyDB may not work (use Redis or Valkey instead)
- Older CPUs may need MongoDB pinned to version 4.4
- Docker bypasses ufw firewall rules -- databases may be publicly accessible if ports are open
- As of Feb 2026, secrets are loaded from `secrets.env`; migration from older setups requires manual secret copying
- Caddy (default reverse proxy) does not support WebRTC without significant configuration changes

### Bare Metal

Not officially supported or documented. The backend services can be compiled from source using Cargo (Rust toolchain), but this path is undocumented and unsupported.

### Managed Hosting Options

| Provider | Starting Price | Notes |
|----------|---------------|-------|
| **Elestio** | ~$10/month | 8 cloud providers (Hetzner, DO, AWS, etc.), auto TLS, backups, ISO 27001/SOC2/GDPR compliant, free trial ($20 credits) |
| **OctaByte** | Contact for pricing | Fully managed, 350+ open-source apps catalog |

### Self-Hosting Limitations

- The self-hosted version **is not feature-complete** compared to the official instance
- Missing: admin panel, automod, server discovery, built-in image hosting
- Staff reportedly **do not provide support** for self-hosting issues
- Documentation has been criticized as incomplete; community-written guides fill some gaps
- Described as "a bit of a RAM hog"

---

## 3. Security

### Known Vulnerabilities & Advisories

No formal CVEs have been assigned to Revolt/Stoat in public databases (NVD/MITRE). However, the project has disclosed several security issues through its own channels:

| Date | Issue | Severity |
|------|-------|----------|
| Dec 2024 | January proxy service causing heavy load via recursive calls (DoS vector) | Medium |
| Feb 2025 | Webhook tokens freely accessible to users with read permissions | Medium-High |
| Feb 2025 | Nearby message fetch requests could be crafted to retrieve entire message history | Medium-High |
| May 2025 | Attempted extortion incident; led to improved password security | Incident response |

### Vulnerability Disclosure Process

- **GitHub:** Create a draft security advisory on the relevant repository under the stoatchat org
- **Email:** security@revolt.chat (response within a few days)
- No formal bug bounty program was found

### Encryption

- **In transit:** TLS (standard HTTPS); Elestio managed hosting auto-generates and renews certificates
- **At rest:** No documented at-rest encryption for self-hosted deployments
- **End-to-end encryption (E2EE):** **NOT implemented.** Listed on the roadmap as milestone 0.6.0 for DMs and group chats. Has been "coming soon" for years. Server-side channels would not get E2EE. This is a significant gap for a privacy-focused platform.

### SSO / OIDC / SAML

- **NOT supported.** No native SSO, OIDC, or SAML integration exists.
- Frequently requested by the self-hosting community ("SSO is a must for self hosted chats")
- Discussed as a potential future plugin/extension, but no implementation timeline
- No integration with identity providers like Authentik, Keycloak, etc.

### Authentication Features

- Email + password authentication
- TOTP-based multi-factor authentication (MFA) supported
- Breached password detection via Have I Been Pwned (HIBP) database (added May 2025)
- Authentication handled by the **Authifier** library

### Privacy

- No ads, no trackers, no data sales
- Based in Europe, GDPR-compliant
- Minimal data collection (email, hashed password, username)
- Open-source code allows auditing (with the semi-open-source caveats noted above)

---

## 4. Maintainability

### GitHub Metrics

| Repository | Stars | Forks | Contributors |
|------------|-------|-------|-------------|
| Main discussion (revoltchat/revolt) | ~2,300 | -- | -- |
| Backend (stoatchat/stoatchat) | ~1,800-2,000 | ~115 | ~65 |
| Self-hosted | ~1,700 | -- | -- |
| Web client (Revite) | ~827 | ~184 | ~71 |
| Desktop client | ~1,000 | -- | -- |
| Voice server | ~120 | -- | -- |

**Total commits:** 1,396+ on main backend repo (as of Jan 2026)

### Release Cadence

- Latest version: **v0.10.2** (January 2026)
- The project is still **pre-1.0**, indicating it has not reached what the team considers a stable/mature release
- Releases appear to come in irregular intervals rather than on a fixed schedule

### Community Size

- **Registered users:** 1,000,000+ (as of early 2026)
  - 500,000 by late 2024
  - Crossed 1M during the Discord age verification exodus (Feb 2026)
- **Search interest:** 9,900% spike for "Stoat" + 4,100% for "Revolt" during the Feb 2026 Discord controversy
- Growth has been highly event-driven (Discord bans in Russia/Turkey, Discord ToS changes, age verification rollout)
- The infrastructure has struggled to handle sudden user surges

### Key Maintainers

- **@insertish (Jen)** -- lead developer
- **@DeclanChidlow** -- core maintainer
- Small core team; the project has stated goals of onboarding more maintainers

### Documentation Quality

- **Developer docs:** https://developers.stoat.chat/ -- covers API, bots, and contributing
- **Self-hosting docs:** Present but criticized as incomplete; community members have requested comprehensive guides
- **Wiki:** https://wiki.revolt.chat/ -- covers transparency reports, incidents, project vision
- **Third-party docs:** DeepWiki, community GitHub gists, and Codeberg guides supplement official docs
- Overall assessment: **Functional but sparse**, especially for self-hosting and advanced configuration

### Project Activity (2025-2026)

The project is **actively developed** but has a small core team:
- Rebrand from Revolt to Stoat completed (Oct 2025)
- Infrastructure updates for self-hosted deployments (Feb 2026)
- Ongoing backend development in Rust
- Active community ecosystem with third-party bots, clients (iOS/macOS "Paws"), Helm charts
- Responding to security incidents (May 2025 extortion, Feb 2025 advisories)
- Handling massive growth surges from Discord migration waves

### Maturity Assessment

| Factor | Rating | Notes |
|--------|--------|-------|
| Age | Moderate | Founded 2021, ~5 years old |
| Version | Pre-1.0 | v0.10.x suggests significant work remains |
| Core team size | Small | 2-3 primary maintainers |
| User base | Growing | 1M+ registered, but active users unknown |
| Enterprise readiness | Low | No SSO, no E2EE, limited admin tools for self-hosted |
| Infrastructure stability | Moderate | Servers have buckled under growth surges |
| Bus factor | Concerning | Very small core team, lead developer has expressed mixed views on open source |
| Ecosystem | Growing | Active bot/library community in multiple languages |

---

## 5. Summary & Risk Assessment

### Strengths
- Familiar Discord-like UX with very low learning curve
- Rust backend delivers good performance
- Privacy-first philosophy, GDPR-compliant, European-based
- Active development and growing community
- Docker-based self-hosting available
- TOTP MFA and breached password detection

### Weaknesses / Risks
- **Semi-open-source**: Key components are proprietary; self-hosted version is feature-incomplete
- **No E2EE**: Despite marketing privacy, end-to-end encryption remains unimplemented after years on the roadmap
- **No SSO/OIDC/SAML**: Critical gap for enterprise/organizational use
- **Small core team**: High bus factor risk; lead developer has expressed ambivalence about open source
- **Self-hosting is second-class**: Unsupported by staff, lagging behind official instance, incomplete docs
- **Pre-1.0 maturity**: Not yet considered stable by the project's own versioning
- **Infrastructure fragility**: Has repeatedly struggled with growth surges
- **MongoDB dependency**: SSPL-licensed, raises concerns for strict FOSS environments

### Comparison Context
For organizations needing a self-hosted chat platform with enterprise features, **Matrix/Element** or **Rocket.Chat** offer more mature SSO integration, encryption, and self-hosting support. Revolt/Stoat is better positioned for community/social use cases where Discord-like UX is the priority and enterprise security requirements are less stringent.

---

## Sources

- [Stoat/Revolt Official Site](https://stoat.chat/)
- [Stoat GitHub Organization](https://github.com/stoatchat)
- [Revolt GitHub Organization (redirects to stoatchat)](https://github.com/revoltchat)
- [Stoat Self-Hosted Repository](https://github.com/stoatchat/self-hosted)
- [Stoat Developer Documentation](https://developers.stoat.chat/)
- [Revolt Team Wiki](https://wiki.revolt.chat/)
- [Revolt Review 2026 - European Purpose](https://europeanpurpose.com/tool/revolt)
- [Elestio Managed Hosting](https://elest.io/open-source/revolt)
- [OctaByte Managed Hosting](https://octabyte.io/fully-managed-open-source-services/applications/live-chat/revolt/)
- [OpenAlternative - Revolt Chat](https://openalternative.co/revolt-chat)
- [Firethering - Is Stoat the New Discord?](https://firethering.com/is-stoat-the-new-discord-the-open-source-platform-thousands-are-switching-to/)
- [WebProNews - The Great Discord Exodus](https://www.webpronews.com/the-great-discord-exodus-why-thousands-of-users-are-crashing-an-obscure-chat-platform-called-stoat/)
- [Windows Central - Discord Alternative Search Spike](https://www.windowscentral.com/software-apps/discord-alternative-search-10000-percent-stoat)
- [Privacy Guides Discussion - Revolt is now Stoat](https://discuss.privacyguides.net/t/revolt-is-now-stoat/32176)
- [Mathium05 Blog - What's the deal with Revolt/Stoat?](https://blog.fermi.chat/discordAlts/revolt/)
- [Libre Self-hosted - Revolt Project](https://libreselfhosted.com/project/revolt/)
- [DeepWiki - Self-Hosted Documentation](https://deepwiki.com/revoltchat/self-hosted)
- [Revolt Wiki - Stoat Timeline](https://wiki.rvlt.gg/index.php/Stoat_Timeline)
- [VPN Tier Lists - Self-Host Guide 2026](https://vpntierlists.com/blog/self-host-discord-alternative-matrix-stoat-2026)

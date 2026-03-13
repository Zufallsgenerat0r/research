# Revolt.chat Research Notes

## Research started: 2026-03-13

### Plan
- Overview: license, language, architecture
- Self-hosting: Docker, bare metal, requirements, managed hosting
- Security: CVEs, encryption, SSO, vulnerability disclosure
- Maintainability: stars, contributors, releases, community, docs, activity

---

## Key Findings

### Rebrand
- Revolt rebranded to Stoat in late 2025 due to legal necessity (cease and desist)
- GitHub org moved from revoltchat to stoatchat
- Same team, same codebase, new name

### Architecture
- Backend: Rust (microservices: delta/API, bonfire/events, autumn/files, january/proxy, gifbox/tenor, pushd/push)
- Frontend: TypeScript (Preact-based web client called Revite)
- Desktop: Electron
- Database: MongoDB
- Cache/messaging: Redis (or KeyDB/Valkey)
- Voice: WebRTC via LiveKit
- License: AGPL v3 for core components, but some components use FUTO license or are proprietary

### Semi-Open-Source Concerns
- Admin panel, automod, server discovery, built-in image hosting are proprietary
- Self-hosted version lags behind official instance
- Some code on GitLab (not well-linked), some proprietary repos
- MongoDB dependency raises FOSS purity concerns

### Self-Hosting
- Docker is the primary deployment method
- Minimum: 2 vCPUs, 2 GB RAM
- Ports: 80, 443 (web), 7881/tcp + 50000-50100/udp (voice)
- amd64 only for backend/bonfire images
- ARM: limited support, may need Redis/Valkey instead of KeyDB
- Staff reportedly do not support self-hosting issues

### Managed Hosting
- Elestio: from ~$10/month, 8 cloud providers
- OctaByte: fully managed, pricing on their site

### Security
- No known CVEs in public databases
- Security advisories: webhook token exposure (Feb 2025), message history fetch bypass (Feb 2025), January service DoS via recursion (Dec 2024)
- May 2025: attempted extortion incident, led to improved password checks (HIBP integration)
- E2EE: NOT implemented, on roadmap (milestone 0.6.0) for DMs/group chats only
- SSO/OIDC: NOT implemented, community-requested feature, no timeline
- MFA: TOTP supported
- Vulnerability disclosure: GitHub security advisories or security@revolt.chat

### Maintainability
- ~2.3k stars (discussion repo), ~1.8k stars (main backend), ~1.7k (self-hosted), ~1k (desktop)
- ~65 contributors on backend, ~71 on web client
- Latest version: v0.10.2 (Jan 2026)
- 1,396+ commits to main repo
- 500k users by late 2024, 1M+ users by early 2026
- Major growth spike from Discord age verification controversy (Feb 2026)
- Documentation: developers.stoat.chat exists but self-hosting docs criticized as incomplete
- Lead maintainers: @insertish (Jen), @DeclanChidlow

### Maturity Assessment
- Founded 2021, ~5 years old
- Still pre-1.0 (v0.10.x)
- Active development but small core team
- Rapid user growth straining infrastructure
- Missing enterprise features (SSO, E2EE, admin tools for self-hosted)

### Sources Consulted
- Web searches across: stoat.chat, GitHub (revoltchat/stoatchat orgs), developers.stoat.chat
- Community discussions: Privacy Guides, Lobsters, Lemmy, HN
- Third-party analysis: blog.fermi.chat, firethering.com, europeanpurpose.com
- Managed hosting: elest.io, octabyte.io

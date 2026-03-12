# ZimaOS Developer Experience Research - Working Notes

## Research Date: 2026-03-12

## Search Strategy
1. Searched for "ZimaOS developer guide" and "ZimaOS custom app" documentation
2. Searched for "ZimaOS docker compose" gotchas and issues across GitHub and forums
3. Searched for "CasaOS custom app" development tutorials and guides
4. Searched ZimaOS community forums (community.zimaspace.com), Reddit, and GitHub Issues
5. Searched for "ZimaOS app store submission" process
6. Searched for known limitations, quirks, and version compatibility issues
7. Investigated IceWhaleTech GitHub repos (ZimaOS, CasaOS, CasaOS-AppStore)
8. Searched for GPU passthrough, network/storage gotchas, and Buildroot limitations

## Key Sources Found

### Official Documentation
- ZimaOS Build Apps Manual: https://www.zimaspace.com/docs/zimaos/Build-Apps (returned 403 on fetch, but search snippets had details)
- ZimaOS OpenAPI Live Preview: https://www.zimaspace.com/docs/zimaos/OpenAPI-Live-Preview
- Docker App Paths: https://www.zimaspace.com/docs/zimaos/How-to-understand-Docker-App's-paths-On-ZimaOS
- CasaOS-AppStore CONTRIBUTING.md: https://github.com/IceWhaleTech/CasaOS-AppStore/blob/main/CONTRIBUTING.md

### GitHub Issues (most impactful)
- #328 - All customized containers share same project name
- #195 - No .env file support in Docker Compose Web UI
- #196 - UI mismatch when using Portainer/Dockge
- #271 - Unable to update Docker apps via UI
- #288 - Apps not starting after update to v1.4.4-1
- #272 - Apps not started after boot (exit code 137)
- #294 - LAN Storage fails to parse Samba/CIFS with share path
- #117 - Request for APT package manager (denied - Buildroot limitation)
- #167 - GPU passthrough request for ZVM
- #178 - NVIDIA GPU not recognized
- #225 - NVIDIA Driver/VA-API issues after update
- #343 - Cannot mount more than one partition per disk
- #229 - Update from 1.3.3 to 1.4.1 stuck at 0%
- #422 - In-place upgrade from CasaOS not supported

### Community Forum Posts
- Cannot build custom app from Docker Compose (v1.4.3): https://community.zimaspace.com/t/solved-cannot-build-custom-app-import-from-docker-compose/5977
- Edit docker compose after installing app: https://community.zimaspace.com/t/edit-docker-compose-after-installing-app/7897
- Docker daemon errors after upgrade: https://community.zimaspace.com/t/solved-after-zimaos-upgrade-v1-4-3-i-am-getting-cannot-connect-to-docker-daemon-errors/5649
- Settings reset bug: https://community.zimaspace.com/t/zimaos-settings-resets-every-now-and-then/4966
- Package manager not supported: https://community.zimaspace.com/t/package-manager-not-supported/3960
- GPU passthrough inconsistency: https://community.zimaspace.com/t/gpu-passthrough-issue-nvidia-visible-in-zimaos-jellyfin-but-missing-in-stremio-container/8080
- v1.5.0 beta quality issues: https://community.zimaspace.com/t/version-1-5-0-beta-working-pretty-bad/5947
- Docker registry polling every 30s: https://community.zimaspace.com/t/zimaos-queries-registry-1-docker-io-every-30-seconds/6271

### External Coverage
- ZimaOS 1.5.0 goes paid - community backlash: https://www.notebookcheck.net/ZimaOS-1-5-0-goes-paid-community-reacts-with-dissapointment.1122850.0.html
- LowEndSpirit discussion: https://lowendspirit.com/discussion/9872/anyone-tried-zimaos-zimaspace-nas-os-from-casaos-devs

## Key Learnings

### Buildroot is the root cause of many limitations
ZimaOS is built on Buildroot, not a standard Linux distro. This means:
- No apt, yum, or any package manager
- No mount.cifs available from command line
- Cannot install additional drivers after the fact
- Cannot install additional system-level tools
- All extensions must go through Docker containers

### The CasaOS heritage creates confusion
- ZimaOS evolved from CasaOS but apps aren't 100% compatible
- CasaOS-AppStore apps may not work on ZimaOS
- The docker-compose format uses x-casaos extension fields
- Migration from CasaOS requires CasaOS >= 0.4.4
- No in-place upgrade path from CasaOS to ZimaOS

### The "simplified" UI is a double-edged sword
- Great for beginners, limiting for power users
- Cannot edit docker-compose YAML after App Store installation
- No .env file support
- Custom containers all share the same project name
- Containers managed outside ZimaOS UI display incorrectly

### Version 1.5.0 was a turning point
- Introduced paid licensing (Plus tier at $29 lifetime)
- Free tier limited to 10 apps, 4 disks, 3 users
- Community backlash was significant
- Some features moved from free to premium

### Update process is fragile
- Updates can overwrite user customizations
- Some version upgrades break running apps (exit code 137)
- Settings may reset after power cycles (reported in v1.4.0+)
- v1.3.3 -> v1.4.1 upgrade got stuck at 0%
- Docker daemon errors reported after v1.4.3 upgrade

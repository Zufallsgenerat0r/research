ZimaOS, developed from the open-source CasaOS, is a NAS operating system built on Buildroot with a Docker-centric application model and simplified web UI. Developers face several notable challenges: custom apps share a project name, `.env` files are unsupported in the UI, app store installs can't be edited, and system-level access is severely limited by the Buildroot base (no package manager, driver installs, or file system flexibility). Migration from CasaOS requires a fresh install, and frequent ZimaOS updates or paid-tier changes have triggered compatibility, GPU passthrough, and storage visibility issues. Docker Compose files need to follow strict metadata conventions (`x-casaos`) for App Store integration, and several network and storage gotchas—like host access from containers and Samba share mounting—require workarounds or are simply unsupported.

**Key findings:**
- You can create and install apps via the [web UI](https://www.zimaspace.com/docs/zimaos/Build-Apps), CLI, or by submitting to the [App Store](https://github.com/IceWhaleTech/CasaOS-AppStore) (compose files must use strict `x-casaos` metadata).
- Buildroot base means there is no package manager—extensions are only possible through Docker.
- Multiple custom apps via UI collide (same project name), `.env` support is missing, and app updates can break both drivers and app configs.
- Network and storage integrations (host access, mounting, and multi-partition disks) are limited; only storage managed through ZimaOS is visible in the UI.
- GPU passthrough and driver support are inconsistent and easily broken by updates, with no straightforward fix.

For app developers, the most critical gotchas are the lack of `.env` support, project name collisions, non-editable App Store app configs, fragile update behavior, and strict Compose file requirements.

ZimaOS, an open-source NAS OS by IceWhale Technology, employs two robust update mechanisms: app updates managed via [CasaOS-AppManagement](https://github.com/IceWhaleTech/CasaOS-AppManagement) (Go service, Docker Compose-based) and system OTA updates powered by [RAUC](https://rauc.io/) using an A/B partition approach. App updates involve catalog refreshes, digest comparisons for images (especially those tagged `:latest`), and atomic replacement with backup/rollback patterns, all triggered through dashboard UI or API endpoints. System updates use signed `.raucb` bundles, written to the inactive partition and boot-switched upon success, with automatic rollback if a new slot fails. Developer workflow is tightly tied to Docker Compose conventions and app store metadata, but is limited by Buildroot's lack of a package manager and potential system/container breakages after upgrades.

**Key findings:**
- App update detection is cached for 1 hour and relies on Docker manifest digest comparison for `:latest` tags.
- System updates via RAUC are atomic, signed, and managed at the partition level, ensuring boot fallback.
- Limitations include no traditional package manager, only Docker extensions, UI/CLI discrepancies, and developer gotchas around compose file handling and third-party integrations.
- Repeated system upgrades have caused existing containers to fail, and certain hardware features (e.g., GPU passthrough) remain unreliable due to Buildroot’s design.
- See [ZimaOS adaptation guide](https://www.zimaspace.com/docs/zimaos/Build-Apps) for app development specifics.

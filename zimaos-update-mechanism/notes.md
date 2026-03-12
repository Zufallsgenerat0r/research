# ZimaOS/CasaOS Update Mechanism Research Notes

## Objective
Research how app updates are triggered in ZimaOS/CasaOS, including:
- App update logic in CasaOS-AppManagement
- App store mechanisms in CasaOS-AppStore
- System/firmware update mechanisms (RAUC, OTA)

## Research Log

### Step 1: Initial setup
- Created working folder
- Launched parallel research agents to investigate architecture, update triggers, and developer gotchas

### Step 2: Identified key repositories
- **ZimaOS** (https://github.com/IceWhaleTech/ZimaOS) - Main repo, 2.4k stars, Shell scripts
- **CasaOS** (https://github.com/IceWhaleTech/CasaOS) - Base system, 33.4k stars, Go
- **CasaOS-AppManagement** (https://github.com/IceWhaleTech/CasaOS-AppManagement) - App lifecycle management, Go
- **CasaOS-AppStore** (https://github.com/IceWhaleTech/CasaOS-AppStore) - App manifest files, 158+ apps
- **zimaos-rauc** (community forks at github.com/726lhc/zimaos-rauc, github.com/spuder/zimaos-rauc) - RAUC update bundles

### Step 3: App update mechanism deep dive
- Read `service/compose_app.go` - found `Update()` and `PullAndApply()` functions
- Read `service/appstore_management.go` - found `IsUpdateAvailable()` with caching
- Read `route/v2/compose_app.go` - found `UpdateComposeApp()` API handler
- Read OpenAPI spec at `api/app_management/openapi.yaml` - found all API endpoints

Key findings:
- App updates work by comparing Docker image tags/digests between installed and store versions
- `PATCH /compose/{id}` is the API endpoint to trigger an update
- `GET /apps/upgradable` lists all apps with available updates
- Updates are asynchronous - the API returns immediately and the update runs in background
- PullAndApply uses a backup-restore pattern for atomicity
- IsUpdateAvailable caches results for 1 hour using gcache
- For `:latest` tags, it compares Docker image digests (not tag strings)
- A `NoUpdateBlacklist` exists for images that should never be flagged for update

### Step 4: System OTA update mechanism
- ZimaOS uses RAUC (Robust Auto-Update Controller) for system-level updates
- Built on Buildroot, uses A/B partition scheme
- Updates delivered as signed `.raucb` bundle files
- Trigger methods: dashboard red dot, offline file placement, CLI
- Boot fallback mechanism using `BOOT_ORDER`, `BOOT_A_LEFT`, `BOOT_B_LEFT` variables

### Step 5: Developer gotchas discovered
- Issue #328: All custom containers get same project name in v1.5.0
- Issue #382: OTA from 1.5.0 to 1.5.3 fails due to LZO compression incompatibility
- Issue #196: UI mismatch when using Portainer/Dockge alongside ZimaOS
- v1.5.0 introduced paid premium tier, community backlash
- docker-compose.yml must use x-casaos extension for metadata
- Image tags must be specific versions, never :latest for app store submissions
- App name pattern restricted to ^[a-z0-9][a-z0-9_-]*$

### Step 6: App store catalog update mechanism
- `UpdateCatalog()` in `service/appstore.go`:
  1. HTTP HEAD request to check zip package size (5-second timeout)
  2. Skips if content-length unchanged (idempotent)
  3. Downloads zip to temp directory
  4. Backs up existing catalog
  5. Replaces active catalog
  6. Rebuilds cache (catalog, categories, recommendations)
  7. Restores backup on failure

### Step 7: Deep source code analysis (2026-03-12)
- Read full source of `service/compose_app.go` Update(), PullAndApply(), Pull() functions
- Read full source of `service/appstore_management.go` IsUpdateAvailable(), IsUpdateAvailableWith()
- Read full source of `service/appstore.go` UpdateCatalog(), BuildCatalog()
- Read full source of `pkg/docker/digest.go` CompareDigest(), GetDigest(), tokenAndURL()
- Read full source of `pkg/docker/image.go` PullImage()
- Read full source of `route/v2/compose_app.go` UpdateComposeApp() handler
- Read full source of `route/v2/docker.go` RecreateContainerByID() handler
- Read full source of `route/v2/image.go` PullImages() handler
- Read full source of `common/message.go` all event type definitions
- Read full source of `common/constants.go` NeedCheckDigestTags
- Read full source of `main.go` cron setup
- Read OpenAPI spec `api/app_management/openapi.yaml`
- Read CasaOS-AppStore structure: Apps/Plex/docker-compose.yml, build scripts
- Confirmed: digest comparison code is credited to containrrr/watchtower
- Confirmed: rauc.txt manifest contains version, download URLs, checksums
- Confirmed: RAUC offline path is /DATA/rauc/offline/ or /ZimaOS-HD/rauc/offline/

### Sources consulted
- GitHub repos: CasaOS-AppManagement, CasaOS-AppStore, ZimaOS, CasaOS
- ZimaOS docs: Build-Apps manual, OpenAPI docs, release notes
- Community forum: community.zimaspace.com
- CasaOS wiki: wiki.casaos.io
- Third-party blogs and GitHub issues
- rauc.txt manifest from IceWhaleTech/zimaos-rauc

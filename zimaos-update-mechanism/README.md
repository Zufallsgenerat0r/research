# ZimaOS/CasaOS App Update Mechanism: Deep Technical Analysis

## Overview

ZimaOS/CasaOS has **two separate update systems**:

1. **App Updates** (Docker container/compose apps) -- handled by `CasaOS-AppManagement`
2. **System/Firmware Updates** (OS-level OTA) -- handled by RAUC with A/B partitions

This report covers both in detail, with exact code references, API endpoints, and workflow descriptions.

---

## Part 1: App Updates (CasaOS-AppManagement)

### Repository
- **Source:** https://github.com/IceWhaleTech/CasaOS-AppManagement
- **Language:** Go
- **Version at time of analysis:** 0.4.16

### Architecture

CasaOS manages apps as Docker Compose projects. Each installed app is a `ComposeApp` backed by a `docker-compose.yml` stored locally. The app store is a catalog of compose files with metadata in `x-casaos` extensions.

### API Endpoints for Updates

All endpoints are under `/v2/app_management/` (registered at the CasaOS gateway).

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| `PATCH` | `/compose/{id}` | `updateComposeApp` | **Trigger an app update** to latest store version |
| `GET` | `/compose` | `myComposeAppList` | List installed apps (includes `UpdateAvailable` field) |
| `PATCH` | `/container/{id}` | `recreateContainerByID` | Recreate a single container (with optional `pull=true` to pull latest image) |
| `PUT` | `/images` | `pullImages` | Pull latest images for specified container IDs |
| `PUT` | `/compose/{id}` | `applyComposeAppSettings` | Apply new compose YAML settings (effectively a reconfigure) |

**OpenAPI spec location:** `api/app_management/openapi.yaml`

### The Complete Update Workflow

#### Step 1: Catalog Sync (Periodic)

**File:** `main.go` lines 82-104

The app store catalog is refreshed on a 10-minute cron schedule:

```go
// run once at startup
go func() {
    service.MyService.AppStoreManagement().UpdateCatalog()
}()

// then every 10 minutes
crontab.AddFunc("@every 10m", func() {
    service.MyService.AppStoreManagement().UpdateCatalog()
})
```

**File:** `service/appstore.go` -- `UpdateCatalog()` method (lines 71-175)

The catalog sync process:
1. HTTP HEAD request to check if the remote zip package size has changed (5-second timeout)
2. If content-length is unchanged, **skip** (no-op optimization)
3. Download the zip archive to a temp directory
4. Back up the existing catalog directory
5. Replace the active catalog with the new one
6. Rebuild in-memory structures: catalog map, category map, recommend list
7. On failure, restore from backup

The app store is a zip file containing `Apps/` directory with per-app `docker-compose.yml` files.

#### Step 2: Check If Update Is Available

**File:** `service/appstore_management.go` -- `IsUpdateAvailable()` (lines 486-505) and `isUpdateAvailable()` (lines 507-536) and `IsUpdateAvailableWith()` (lines 546-588)

Two comparison strategies:

**For tagged images (e.g., `lscr.io/linuxserver/plex:1.41.3`):**
- Compare the image tag string in the installed compose YAML against the tag in the store compose YAML
- If tags differ, update is available
- Defined at line 587: `return currentTag != storeTag, err`

**For `:latest` tagged images:**
- Tags defined in `common/constants.go` line 35: `var NeedCheckDigestTags = []string{"latest"}`
- Query the Docker registry for the remote image digest (using Docker Distribution API v2)
- Compare against the local image's `RepoDigests` from `docker image inspect`
- Uses `docker.CompareDigest()` which does HTTP HEAD to the registry manifest endpoint
- If digests differ, update is available
- A blacklist exists for problematic images: `NoUpdateBlacklist` (line 542-544)

**Caching:** Results are cached using `gcache` (`isAppUpgradable` field). Cache is purged every time `UpdateCatalog()` runs (every 10 minutes).

#### Step 3: Trigger the Update

**File:** `route/v2/compose_app.go` -- `UpdateComposeApp()` (lines 399-439)

API handler for `PATCH /compose/{id}`:

```go
func (a *AppManagement) UpdateComposeApp(ctx echo.Context, id codegen.ComposeAppID,
    params codegen.UpdateComposeAppParams) error {
    // 1. Look up the installed compose app
    composeApp, ok := composeApps[id]

    // 2. Unless force=true, check if update is actually available
    if params.Force != nil && !*params.Force {
        if !service.MyService.AppStoreManagement().IsUpdateAvailable(composeApp) {
            return "compose app is up to date"
        }
    }

    // 3. Trigger async update
    composeApp.Update(backgroundCtx)

    // 4. Return immediately
    return "compose app is being updated asynchronously"
}
```

Query parameters:
- `force` (boolean) -- skip the update-available check

#### Step 4: Execute the Update

**File:** `service/compose_app.go` -- `Update()` (lines 171-258)

The `Update()` method:

1. Load `StoreInfo` from the app's `x-casaos` extension to find the `store_app_id`
2. Fetch the latest `ComposeApp` from the store catalog using that ID
3. Validate that local and store services match (same service names required)
4. For each service in the store version:
   - If the image tag is in `NeedCheckDigestTags` (i.e., `:latest`), keep the local tag (digest comparison handles this)
   - Otherwise, update the local image reference to match the store version
5. Serialize the updated compose YAML
6. Launch async goroutine that:
   - Publishes `app:update-begin` event to message bus
   - Marks app as upgrading (`StartUpgrade`)
   - Calls `PullAndApply()` with the new YAML
   - On error, publishes `app:update-error` event
   - On completion, publishes `app:update-end` event and clears upgrade state

#### Step 5: Pull and Apply

**File:** `service/compose_app.go` -- `PullAndApply()` (lines 428-484)

1. **Backup** the current `docker-compose.yml` to `docker-compose.yml.bak`
2. **Write** the new compose YAML to the compose file
3. **Load** the new compose app from the updated file
4. **Pull** all images (`docker pull` for each service)
5. **Up** the compose app with `docker compose up` (via Docker Compose API)
6. On any failure, **restore** from the backup file and restart the old version

#### Step 6: Docker Image Pull

**File:** `pkg/docker/image.go` -- `PullImage()` (lines 29-56)

Standard Docker SDK image pull:
```go
func PullImage(ctx context.Context, imageName string,
    handleOut func(io.ReadCloser)) error {
    cli, _ := client.NewClientWithOpts(client.FromEnv,
        client.WithAPIVersionNegotiation())
    opts, _ := GetPullOptions(imageName)  // handles registry auth
    out, _ := cli.ImagePull(ctx, imageName, opts)
    handleOut(out)  // streams progress
}
```

### Container-Level Updates (Legacy v1 Apps)

For standalone containers (not compose apps), the update mechanism is different:

**File:** `route/v2/docker.go` -- `RecreateContainerByID()` (lines 32-77)

API: `PATCH /container/{id}?pull=true&force=true`

1. Inspect the existing container
2. If `pull=true`, call `PullLatestImage()` which:
   - Compares local image digest vs. remote registry digest
   - If different, pulls the new image
3. If image was updated (or `force=true`):
   - Clone the container config
   - Stop and remove the old container
   - Create and start a new container with the same config but new image

### Message Bus Events

All update operations publish events to CasaOS-MessageBus for UI notifications:

- `app:update-begin` / `app:update-end` / `app:update-error`
- `docker:image:pull-begin` / `docker:image:pull-progress` / `docker:image:pull-end` / `docker:image:pull-error`
- `docker:container:create-begin` / `docker:container:create-end`
- `docker:container:start-begin` / `docker:container:start-end`

### Known Limitations

1. **`:latest` tag problem:** If an installed app uses `:latest` and the store also specifies `:latest`, the system falls back to digest comparison. This requires network access to the Docker registry and can be slow.
2. **Blacklisted images:** Some images (e.g., `johnguan/stable-diffusion-webui:latest`) are blacklisted from digest comparison because it does not work correctly for them.
3. **No automatic updates:** There is no auto-update feature. Users must manually trigger updates through the UI or API.
4. **Service mismatch blocks updates:** If the installed compose app has different service names than the store version, the update is rejected entirely.

---

## Part 2: App Store Structure (CasaOS-AppStore)

### Repository
- **Source:** https://github.com/IceWhaleTech/CasaOS-AppStore
- **Structure:**

```
Apps/
  Plex/
    docker-compose.yml   # Compose spec + x-casaos metadata
    icon.png
    thumbnail.png
    screenshot-*.png
    appfile.json         # Legacy format
  ...
category-list.json       # App categories
recommend-list.json      # Featured/recommended apps
build/scripts/setup/     # Installation scripts
```

### Default App Store

On installation, the app store is placed at `/var/lib/casaos/appstore/default/`. The setup script (`99-setup-appstore.sh`) handles atomic replacement with backup/restore.

### Remote App Stores

Additional app stores can be registered via `POST /v2/app_management/appstore?url=<zip_url>`. Each remote store is downloaded as a zip, extracted to a content-addressed directory under `/var/lib/casaos/appstore/<host>/<md5hash>/`.

---

## Part 3: System/Firmware Updates (ZimaOS OTA via RAUC)

### Technology

ZimaOS uses **RAUC** (Robust Auto-Update Controller) for OS-level updates. The system is built with Buildroot.

### Repository
- **Source:** https://github.com/IceWhaleTech/zimaos-rauc (the actual IceWhaleTech/ZimaOS repo)
- **Releases:** https://github.com/IceWhaleTech/ZimaOS/releases (latest: v1.5.4)

### Update Architecture

**A/B Partition (Slot) Scheme:**
- System has two root filesystem partitions (Slot A and Slot B)
- Only one slot is active at a time
- Updates are written to the inactive slot
- On reboot, the system switches to the updated slot
- If the new slot fails to boot, RAUC can fall back to the previous slot

**Update Bundle Format:**
- Files are `.raucb` (RAUC bundle) format
- Example: `zimaos_zimacube-1.4.1.raucb`
- Bundles are signed and verified before installation
- Checksum verification via `checksums.txt`

### How System Updates Are Triggered

**Online (OTA):**
1. The system checks a `rauc.txt` manifest file hosted on GitHub/Aliyun OSS
2. This file contains version info, download URLs, and checksums
3. When a new version is available, the dashboard shows a red notification dot
4. User clicks the red dot to initiate the update
5. The `.raucb` bundle is downloaded and installed to the inactive slot
6. System reboots into the updated slot

**Offline:**
1. User downloads the `.raucb` file from GitHub releases
2. Uploads it to `/ZimaOS-HD/rauc/offline/` (or `/DATA/rauc/offline/` via SSH)
3. The system periodically scans this directory
4. When a bundle is found, the red update dot appears
5. User initiates the update from the dashboard

**CLI (Manual):**
- Users can also trigger updates from the command line, though the exact CLI commands are not well-documented in the public repos

### Distribution Infrastructure

- Primary: GitHub Releases at `IceWhaleTech/ZimaOS`
- CDN Mirror: Aliyun OSS (for Chinese users)
- The `rauc.txt` file acts as the update manifest, synced to Aliyun OSS via CI/CD

### Known Issues

- **OTA from v1.5.0 to v1.5.3 failed** because the 1.5.3 kernel uses LZO-compressed squashfs but the 1.5.0 kernel lacks `CONFIG_SQUASHFS_LZO` support (GitHub Issue #382)
- **Multi-drive systems** can cause RAUC to write to the wrong drive if multiple disks have ZimaOS partition labels

---

## Summary: Update Flow Diagram

### App Update Flow
```
Every 10 min: cron -> AppStoreManagement.UpdateCatalog()
                       |-> HTTP HEAD check zip size
                       |-> Download zip if changed
                       |-> Rebuild catalog cache
                       |-> Purge update-available cache

User clicks "Update":
  UI -> PATCH /v2/app_management/compose/{id}
         |-> IsUpdateAvailable() [cached, tag or digest comparison]
         |-> ComposeApp.Update() [async goroutine]
              |-> Fetch store version of compose YAML
              |-> Merge image references
              |-> PullAndApply()
                   |-> Backup current docker-compose.yml
                   |-> Write new docker-compose.yml
                   |-> docker pull (each service image)
                   |-> docker compose up
                   |-> On failure: restore backup, restart old version
              |-> Publish events to MessageBus
```

### System Update Flow
```
System checks rauc.txt manifest (GitHub/Aliyun OSS)
  OR: User places .raucb in /DATA/rauc/offline/

Dashboard shows red notification dot
  -> User clicks to update
     -> Download .raucb bundle (if OTA)
     -> Verify signature and checksum
     -> RAUC installs to inactive A/B slot
     -> System reboots into updated slot
     -> On boot failure: fallback to previous slot
```

---

## Key Source Files Reference

| File | Purpose |
|------|---------|
| `main.go` | Cron setup (10-min catalog refresh), service initialization |
| `service/appstore.go` | `UpdateCatalog()` -- downloads and rebuilds store catalog |
| `service/appstore_management.go` | `IsUpdateAvailable()`, `IsUpdateAvailableWith()` -- version comparison logic |
| `service/compose_app.go` | `Update()`, `PullAndApply()`, `Pull()` -- core update execution |
| `service/container.go` | `RecreateContainer()` -- container-level update for legacy apps |
| `service/image.go` | `PullLatestImage()` -- pulls and compares image digests |
| `pkg/docker/digest.go` | `CompareDigest()`, `GetDigest()` -- Docker registry digest comparison |
| `pkg/docker/image.go` | `PullImage()` -- Docker SDK image pull wrapper |
| `route/v2/compose_app.go` | `UpdateComposeApp()` -- HTTP handler for PATCH /compose/{id} |
| `route/v2/docker.go` | `RecreateContainerByID()` -- HTTP handler for PATCH /container/{id} |
| `route/v2/image.go` | `PullImages()` -- HTTP handler for PUT /images |
| `common/message.go` | Event type definitions for message bus |
| `common/constants.go` | `NeedCheckDigestTags`, version constants |
| `api/app_management/openapi.yaml` | Full OpenAPI 3.0.3 specification |

---

## Sources

- [CasaOS-AppManagement GitHub](https://github.com/IceWhaleTech/CasaOS-AppManagement)
- [CasaOS-AppStore GitHub](https://github.com/IceWhaleTech/CasaOS-AppStore)
- [ZimaOS / zimaos-rauc GitHub](https://github.com/IceWhaleTech/ZimaOS)
- [ZimaOS Releases](https://github.com/IceWhaleTech/ZimaOS/releases)
- [ZimaOS Offline Update Docs](https://www.zimaspace.com/docs/zimaos/Install-offline)
- [CasaOS Wiki: Manually Update Compose App](https://wiki.casaos.io/en/guides/manually-update-compose-app-with-latest-tag)
- [OTA Bug: Issue #382](https://github.com/IceWhaleTech/ZimaOS/issues/382)
- [CasaOS Discussion: Docker App Updates](https://github.com/IceWhaleTech/CasaOS/discussions/744)
- [Community Forum](https://community.zimaspace.com/t/how-to-install-update-the-latest-release-of-zimaos-on-zimacube-from-cli-1-3-02/4123)

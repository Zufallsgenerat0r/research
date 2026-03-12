# ZimaOS App Update Mechanism: How It Works

<!-- AI-GENERATED-NOTE -->
> [!NOTE]
> This is an AI-generated research report. All text and code in this report was created by an LLM (Large Language Model). For more information on how these reports are created, see the [main research repository](https://github.com/simonw/research).
<!-- /AI-GENERATED-NOTE -->

## Overview

ZimaOS is an open-source NAS operating system by [IceWhale Technology](https://github.com/IceWhaleTech), evolved from [CasaOS](https://github.com/IceWhaleTech/CasaOS). It has two distinct update mechanisms:

1. **App updates** — Docker container image updates managed by [CasaOS-AppManagement](https://github.com/IceWhaleTech/CasaOS-AppManagement) (Go service)
2. **System/firmware OTA updates** — Full system image updates via [RAUC](https://rauc.io/) (A/B partition scheme)

---

## 1. App Update Mechanism

### Architecture

Apps in ZimaOS are Docker Compose applications. The [CasaOS-AppStore](https://github.com/IceWhaleTech/CasaOS-AppStore) contains 158+ app manifests as `docker-compose.yml` files with `x-casaos` metadata extensions. The AppManagement service manages the full app lifecycle: install, update, start/stop, uninstall.

### How the App Store Catalog Updates

The app store catalog refresh (`UpdateCatalog()` in `service/appstore.go`) works as follows:

1. Makes an HTTP HEAD request to the app store URL (5-second timeout) to check the zip package size
2. **Skips download if Content-Length is unchanged** — this is how it avoids unnecessary work
3. Downloads new catalog zip to a temporary directory
4. Backs up the existing catalog directory
5. Atomically replaces the active catalog
6. Rebuilds in-memory caches (app catalog, categories, recommendations)
7. Restores backup on failure

Third-party app stores can be registered via `POST /appstore?url=<store_url>`.

### How App Update Availability Is Checked

The `IsUpdateAvailable()` function in `service/appstore_management.go`:

1. Checks an in-memory cache (results are **cached for 1 hour** via `gcache`)
2. If not cached, retrieves the store's version of the compose app by `StoreAppID`
3. For tags in `common.NeedCheckDigestTags` (like `:latest`): **compares Docker image digests** using the Docker client API
4. For other tags: does a **simple string comparison** of image tags
5. Checks against a `NoUpdateBlacklist` — some images are excluded from update detection
6. Returns false if the app is marked as "uncontrolled"

The `GET /apps/upgradable` endpoint returns the list of all installed apps that have updates available.

### How to Trigger an App Update

#### Via the Dashboard UI
Click the update indicator on an app card in the ZimaOS dashboard. This calls the API endpoint below.

#### Via API
```
PATCH /v2/compose/{id}
```

**Parameters:**
| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `id` | string | path | Compose app ID (project name) |
| `force` | boolean | query | Skip update availability check |

**Example:**
```bash
curl -X PATCH "http://<zimaos-ip>/v2/app-management/compose/plex?force=true"
```

#### What Happens Internally

The `UpdateComposeApp()` handler in `route/v2/compose_app.go`:

1. Validates the app ID exists in the local compose app list
2. Unless `force=true`, checks `IsUpdateAvailable()` — returns early if already up to date
3. Calls `composeApp.Update()` which runs **asynchronously**
4. Returns immediately with: `"compose app 'X' is being updated asynchronously"`

The `Update()` function in `service/compose_app.go`:

1. Fetches the store version of the compose app
2. **Validates service compatibility** — rejects updates if service names don't match between versions
3. Updates Docker image references from the store's compose definition
4. Spawns a goroutine that:
   - Publishes `EventTypeAppUpdateBegin`
   - Calls `PullAndApply()`
   - Publishes `EventTypeAppUpdateEnd` or `EventTypeAppUpdateError`

The `PullAndApply()` function implements **atomic updates with rollback**:

1. Backs up the current `docker-compose.yml`
2. Writes the new compose configuration
3. Pulls new Docker images (with progress events)
4. Starts containers via `UpWithCheckRequire()` (validates volumes exist, filters unavailable devices)
5. **On failure**: restores the backup compose file and restarts original containers

### Other Related API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/apps/upgradable` | List all apps with available updates |
| `GET` | `/apps/{id}/stable` | Get stable version of an app from the store |
| `GET` | `/apps/{id}/stable/{serviceName}` | Get stable version of a specific service |
| `POST` | `/compose` | Install a compose app |
| `PUT` | `/compose/{id}` | Apply new settings to an existing app |
| `PATCH` | `/container/{id}?pull=true` | Recreate a single container (optionally pulling latest image) |
| `POST` | `/image` | Pull container images asynchronously |

---

## 2. System/Firmware OTA Update Mechanism

ZimaOS uses **[RAUC](https://rauc.io/) (Robust Auto-Update Controller)** for system-level updates, built on top of Buildroot.

### A/B Partition Scheme

The system uses two redundant root partitions (Slot A and Slot B):

- The active slot runs the current system
- Updates are written to the **inactive** slot
- After successful installation, the bootloader is configured to boot the updated slot
- RAUC deactivates the target slot before writing, reactivates after success

### Update Bundles

Updates are delivered as `.raucb` files — RAUC bundles containing:
- Filesystem image(s)
- A manifest listing images to install
- Optional pre/post-install scripts
- All wrapped in a **signed SquashFS image** (signing is mandatory)

### How to Trigger a System Update

#### 1. Online (OTA) via Dashboard
Click the **red dot** in the top-left corner of the ZimaOS dashboard when an update is available.

#### 2. Offline Update
Place the `.raucb` file in `/ZimaOS-HD/rauc/offline/` (or `/DATA/rauc/offline/`). The system periodically scans this directory. Wait a few minutes for the red dot to appear.

#### 3. CLI
```bash
rauc install /path/to/zimaos_zimacube-<version>.raucb
```

### Boot Fallback / Rollback

The bootloader manages boot attempts using environment variables:
- `BOOT_ORDER` — which slot to try first (A or B)
- `BOOT_A_LEFT` / `BOOT_B_LEFT` — remaining boot attempts per slot

If a slot fails to boot (attempts reach zero), the bootloader automatically switches to the other slot. The `rauc-mark-good` service runs on successful boot to confirm the slot is healthy.

---

## 3. Developer Gotchas

### Docker Compose Format Requirements

- **App name** must match `^[a-z0-9][a-z0-9_-]*$` — lowercase only, no special characters
- **Image tags must be specific versions** (e.g., `:1.41.3`), never `:latest` for app store submissions
- The `x-casaos` extension block is required for app store metadata (title, description, icon, category, architecture support, etc.)
- System variables available: `$PUID`, `$PGID`, `$TZ`, `$AppID`

### Custom Container Project Name Bug (Issue [#328](https://github.com/IceWhaleTech/ZimaOS/issues/328))

In ZimaOS 1.5.0, **all custom containers added via the Web UI share the same project name**. This means:
- Only the last added container appears in the apps list
- Deleting one custom container deletes all of them
- The project directory is `/var/lib/casaos/apps/yourprojectname` instead of unique per-app
- Workaround: None reliable as of the issue filing. App store apps are unaffected.

### UI Mismatch with Third-Party Tools (Issue [#196](https://github.com/IceWhaleTech/ZimaOS/issues/196))

Using **Portainer or Dockge** alongside ZimaOS causes UI inconsistencies. Containers created outside ZimaOS's management layer aren't properly tracked.

### OTA Compression Incompatibility (Issue [#382](https://github.com/IceWhaleTech/ZimaOS/issues/382))

OTA upgrade from v1.5.0 to v1.5.3 fails because:
- v1.5.3 uses LZO-compressed squashfs
- v1.5.0 kernel has `CONFIG_SQUASHFS_LZO` disabled
- RAUC writes successfully to Slot B, but the bootloader can't mount it
- System falls back to Slot A — **no OTA workaround**, must fresh-install

This is a recurring pattern (also happened during 1.3.x cycle).

### Version 1.5.0 Licensing Change

ZimaOS 1.5.0 introduced a **premium/paid tier**, which caused significant community backlash. Developers should be aware of licensing implications.

### Update Detection for `:latest` Tags

CasaOS cannot easily detect updates for images tagged `:latest` because there's no version string to compare. The system falls back to **Docker digest comparison**, which is more expensive (requires pulling manifest from registry). The code comments note: "check update is hard and cost a lot of time, specially when the tag is latest."

### App Store Submission Requirements

Each app directory must contain:
- `docker-compose.yml` (required)
- `icon.png` (required)
- `screenshot-1.png` (required) — proof it runs on CasaOS
- `screenshot-2.png+` (optional)
- `thumbnail.png` (optional, 784x442px for featured apps)

### IsUpdateAvailable Caching

Update checks are cached for **1 hour**. If you push a new version of your app to the store, users won't see the update for up to an hour after the catalog refreshes. This can cause confusion during development/testing.

### Uncontrolled Apps

Apps installed with `?uncontrolled=true` are **exempt from version tracking** — they won't show up in update checks. This is useful for development but means users must manually manage updates.

### No Package Manager — Docker Only

ZimaOS is built on **Buildroot, not a traditional Linux distro**. There is no `apt`, `yum`, or any package manager. Docker containers are the **only** extension mechanism. You cannot install system-level packages. ([#117](https://github.com/IceWhaleTech/ZimaOS/issues/117))

### No `.env` File Support in Web UI

The Docker Compose import via the Web UI does **not support `.env` files**. All environment variables must be inlined in the compose file. ([#195](https://github.com/IceWhaleTech/ZimaOS/issues/195))

### Cannot Edit App Store Apps' Compose Files

Changes to compose files for apps installed from the store **get overwritten**. You must uninstall and reinstall as a custom app to modify compose configuration.

### `localhost` Doesn't Resolve to Host

From within containers, `localhost` does not resolve to the ZimaOS host. Use `host.docker.internal` with `extra_hosts` mapping instead.

### Docker Swarm Directives Break Import

Strip `deploy`, `configs`, and `secrets` directives from compose files before importing — these Swarm-only features cause the import to fail.

### `WEBUI_PORT` Is Allocated Once

The `WEBUI_PORT` magic variable is assigned once at install time and **never reassigned** if the port gets taken by another app later.

### System Updates Can Break Running Apps

Multiple ZimaOS version upgrades (v1.4.3, v1.4.4-1, v1.5.3) have broken existing containers with exit code 137 or "failed to start" errors. App settings may also reset after power cycles. ([#288](https://github.com/IceWhaleTech/ZimaOS/issues/288), [#272](https://github.com/IceWhaleTech/ZimaOS/issues/272))

### GPU Passthrough Is Fragile

GPU passthrough works inconsistently across containers, and **NVIDIA drivers can break on OS update** with no fix path due to Buildroot's immutable nature. ([#225](https://github.com/IceWhaleTech/ZimaOS/issues/225))

### Storage Management Is GUI-Coupled

- CLI-mounted drives aren't recognized by the Files app
- Only one partition per disk is supported
- Samba/CIFS share paths can get incorrectly stripped ([#294](https://github.com/IceWhaleTech/ZimaOS/issues/294))
- The `/media/ZimaOS-HD` symlink resets on every reboot ([#343](https://github.com/IceWhaleTech/ZimaOS/issues/343))

### Docker Registry Polling

ZimaOS queries `registry-1.docker.io` **every 30 seconds**, which can cause issues with Pi-hole or other DNS filtering tools.

### Volume Path Conventions

Docker apps on ZimaOS use specific path conventions:
- App data: `/DATA/AppData/$AppID/`
- App config: `/var/lib/casaos/apps/<appname>/`
- User data: Typically under `/DATA/` mount point
- RAUC offline updates: `/ZimaOS-HD/rauc/offline/` or `/DATA/rauc/offline/`

---

## Summary

| Aspect | App Updates | System Updates |
|--------|-------------|----------------|
| **Technology** | Docker Compose + CasaOS-AppManagement | RAUC A/B partitions |
| **Format** | Docker images from registries | Signed `.raucb` bundles |
| **Trigger** | Dashboard UI / `PATCH /compose/{id}` API | Dashboard red dot / offline file / `rauc install` CLI |
| **Rollback** | Backup-restore of compose file + containers | Automatic bootloader fallback to previous slot |
| **Atomicity** | PullAndApply with backup pattern | A/B slot write with boot verification |
| **Check frequency** | Cached for 1 hour | Periodic scan of offline directory |

## Key Sources

- [CasaOS-AppManagement](https://github.com/IceWhaleTech/CasaOS-AppManagement) — Core update logic in Go
- [CasaOS-AppStore](https://github.com/IceWhaleTech/CasaOS-AppStore) — App manifest repository
- [ZimaOS](https://github.com/IceWhaleTech/ZimaOS) — Main repo and issue tracker
- [ZimaOS Docker App Adaptation Manual](https://www.zimaspace.com/docs/zimaos/Build-Apps) — Official developer guide
- [ZimaOS OpenAPI Docs](https://www.zimaspace.com/docs/zimaos/OpenAPI-Live-Preview) — Live API reference
- [CasaOS Wiki - Manually Update Compose App](https://wiki.casaos.io/en/guides/manually-update-compose-app-with-latest-tag)
- [ZimaOS Offline Update Guide](https://www.zimaspace.com/docs/zimaos/Install-offline)
- [RAUC Documentation](https://rauc.readthedocs.io/en/latest/basic.html)

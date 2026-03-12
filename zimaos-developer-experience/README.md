# ZimaOS Developer Experience: Gotchas, Limitations, and Practical Guide

**Research Date:** 2026-03-12

## Overview

ZimaOS is a NAS operating system by [IceWhaleTech](https://github.com/IceWhaleTech/ZimaOS) that evolved from the open-source [CasaOS](https://casaos.io/) project. It runs on Buildroot (not a standard Linux distro), targets x86-64 UEFI hardware, and manages applications primarily through Docker containers with a simplified web UI. This report documents the real-world developer experience based on official documentation, GitHub issues, community forum posts, and external reviews.

---

## 1. How to Create Custom Apps for ZimaOS

### Method 1: Via the ZimaOS Web UI ("Custom Install")

1. Open the ZimaOS App Store in the web dashboard.
2. Click **"Custom Install"** in the upper right corner.
3. Either paste a `docker run` command or upload/paste a `docker-compose.yml` file.
4. Configure access port, volume mounts, and environment variables through the UI.
5. Click Install.

**Source:** [ZimaOS Docker Application Adaptation Manual](https://www.zimaspace.com/docs/zimaos/Build-Apps)

### Method 2: Via CLI (SSH)

1. SSH into ZimaOS.
2. Navigate to `/DATA/AppData/` and create a folder for your app.
3. Create a `docker-compose.yml` inside it.
4. Run `docker compose up -d`.

**Caveat:** Apps created via CLI will not appear correctly in the ZimaOS web UI. The Files app and dashboard only recognize containers managed through ZimaOS's own app management layer.

### Method 3: Contributing to the App Store

Submit a PR to the [CasaOS-AppStore](https://github.com/IceWhaleTech/CasaOS-AppStore) repository. Each app directory must contain:

| File | Required? | Spec |
|------|-----------|------|
| `docker-compose.yml` | Yes | Must include `x-casaos` metadata |
| `icon.png` | Yes | 192x192px, transparent background |
| `screenshot-1.png` | Yes (min 1) | 1280x720px |
| `thumbnail.png` | Featured only | 784x442px |

**Source:** [CasaOS-AppStore CONTRIBUTING.md](https://github.com/IceWhaleTech/CasaOS-AppStore/blob/main/CONTRIBUTING.md)

### Docker Compose `x-casaos` Metadata Format

ZimaOS/CasaOS uses a custom extension field `x-casaos` at two levels in `docker-compose.yml`:

**Service level** (inside each service):
```yaml
x-casaos:
  envs:
    - container: "MY_VAR"
      description:
        en_us: "Description of the variable"
  ports:
    - container: "8080"
      description:
        en_us: "Web UI"
  volumes:
    - container: "/data"
      description:
        en_us: "Application data"
```

**Compose app level** (top-level):
```yaml
x-casaos:
  architectures:
    - amd64
    - arm64
  main: my-service-name
  author: YourName
  category: Utilities
  description:
    en_us: "App description"
  title:
    en_us: "App Title"
  icon: https://example.com/icon.png
  index: /
  port_map: "8080"
```

**Key rules:**
- The `name` field must match `^[a-z0-9][a-z0-9_-]*$` (lowercase, numbers, underscores, hyphens only).
- Use specific image tags (e.g., `:0.1.2`), never `:latest`.
- Use `$$xxx` instead of `$xxx` in compose files to avoid variable interpolation.
- Available system variables: `$PUID`, `$PGID`, `$TZ`, `$AppID`.
- `WEBUI_PORT` is allocated once at install time and never reallocated.
- Multi-language fields must include at least `en_us` as fallback.
- Language codes are case-sensitive (e.g., `en_US` not `en_us` in some contexts -- the docs are inconsistent here).

---

## 2. Common Pitfalls Developers Encounter

### 2.1 All Custom Containers Share the Same Project Name

**Problem:** When adding multiple docker-compose apps via the web UI, they all get the same project name under `/var/lib/casaos/apps/`. Only the last one appears in the app list, and deleting one deletes them all.

**Impact:** Critical for anyone deploying more than one custom app.

**GitHub Issue:** [#328](https://github.com/IceWhaleTech/ZimaOS/issues/328)

### 2.2 No `.env` File Support

**Problem:** The web UI stores everything as a single `docker-compose.yml` under `~/.casaos/<dockerAppName>/`. There is no way to use a separate `.env` file, which many standard compose workflows depend on.

**Workaround:** Inline all environment variables directly in the compose file, or use Portainer/Dockge (but see gotcha 2.3).

**GitHub Issue:** [#195](https://github.com/IceWhaleTech/ZimaOS/issues/195)

### 2.3 Containers Managed Outside ZimaOS UI Display Incorrectly

**Problem:** If you use Portainer, Dockge, or CLI to manage Docker containers, ZimaOS's web UI shows them incorrectly -- they appear as "Launch & Open" even when running properly.

**GitHub Issue:** [#196](https://github.com/IceWhaleTech/ZimaOS/issues/196)

### 2.4 Cannot Edit Docker Compose After App Store Installation

**Problem:** Apps installed from the ZimaOS App Store cannot have their underlying `docker-compose.yml` edited. The system manages it, and changes get overwritten.

**Workaround:** Export the compose file, uninstall the app, and reinstall as a custom app.

**Forum Post:** [Edit docker compose after installing app](https://community.zimaspace.com/t/edit-docker-compose-after-installing-app/7897)

### 2.5 Docker Compose Import Fails with Swarm/Advanced Features

**Problem:** Importing docker-compose files that contain Docker Swarm directives, certain volume definitions, or complex YAML features will fail silently or with cryptic errors about duplicate keys and invalid YAML.

**Solution:** Strip out any Swarm-specific configuration (`deploy`, `configs`, `secrets` at Swarm level) and simplify volume definitions.

**Forum Post:** [Cannot build custom app - import from Docker Compose](https://community.zimaspace.com/t/solved-cannot-build-custom-app-import-from-docker-compose/5977)

### 2.6 `localhost` Does Not Resolve to Host from Containers

**Problem:** If your container needs to reach a service on the ZimaOS host, `localhost:xxxx` will not work.

**Solution:** Use `http://host.docker.internal:xxxx` and add to your compose file:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Source:** [ZimaOS Build Apps Manual](https://www.zimaspace.com/docs/zimaos/Build-Apps)

### 2.7 App Update Behavior Differs from CasaOS

**Problem:** In CasaOS, changing an image tag in settings triggered a pull and restart. In ZimaOS, this does not work the same way, and there are no logs to debug the update process.

**GitHub Issue:** [#271](https://github.com/IceWhaleTech/ZimaOS/issues/271)

---

## 3. Version Compatibility Issues

### 3.1 CasaOS-to-ZimaOS Migration

- **No in-place upgrade** from CasaOS to ZimaOS. Must do a fresh install + data migration.
- CasaOS must be **>= v0.4.4** for the CTOZ migration tool to work (older versions lack standardized Docker Compose configs).
- CasaOS-AppStore apps are **not 100% compatible** with ZimaOS. Icons and titles may be overwritten.

**Source:** [Migrate from CasaOS to ZimaOS](https://www.zimaspace.com/docs/zimaos/Migrate-from-CasaOS-to-ZimaOS), [GitHub Issue #422](https://github.com/IceWhaleTech/ZimaOS/issues/422)

### 3.2 ZimaOS Version Upgrade Problems

| Upgrade Path | Issue |
|--------------|-------|
| v1.3.3 -> v1.4.1 | Update stuck at 0%, version reverts after reboot ([#229](https://github.com/IceWhaleTech/ZimaOS/issues/229)) |
| v1.4.3 | Docker daemon connection errors after upgrade ([forum](https://community.zimaspace.com/t/solved-after-zimaos-upgrade-v1-4-3-i-am-getting-cannot-connect-to-docker-daemon-errors/5649)) |
| v1.4.3 | Custom app import from docker-compose completely broken ([forum](https://community.zimaspace.com/t/solved-cannot-build-custom-app-import-from-docker-compose/5977)) |
| v1.4.4-1 | Most apps fail to start: "failed to start compose app" ([#288](https://github.com/IceWhaleTech/ZimaOS/issues/288)) |
| v1.5.2 -> v1.5.3 | Stable Diffusion broke on dashboard (still accessible via direct URL) ([forum](https://community.zimaspace.com/t/update-1-5-3-and-stable-diffusion/7325)) |

### 3.3 ZimaOS v1.5.0: Paid Licensing

- Introduced a **Plus tier** ($29 lifetime, no subscription).
- Free tier caps: **10 apps, 4 disks, 3 users**.
- Existing community members could get a free Plus license until June 30, 2026.
- Caused significant community backlash.

**Source:** [NotebookCheck coverage](https://www.notebookcheck.net/ZimaOS-1-5-0-goes-paid-community-reacts-with-dissapointment.1122850.0.html)

---

## 4. Docker Compose Format Requirements and Restrictions

### What Works
- Standard Docker Compose V2 syntax.
- Multi-container stacks (since CasaOS v0.4.4+).
- `x-casaos` extension metadata for app store integration.
- `WEBUI_PORT` variable for dynamic port assignment.
- System variables: `$PUID`, `$PGID`, `$TZ`, `$AppID`.
- GPU resource reservations with NVIDIA runtime.

### What Does NOT Work or Is Not Supported
- **`.env` files** -- not supported in web UI.
- **Docker Swarm directives** (`deploy`, `configs`, `secrets` at swarm level) -- must be stripped.
- **Shared services / dependency declarations** between apps.
- **Flexible port reallocation** -- `WEBUI_PORT` is assigned once, never reassigned.
- **Flexible device allocation** -- GPU/device passthrough must be hardcoded.
- **`version` field** -- omit it (modern Docker Compose practice).
- **Advanced networking** (custom DNS, extra networks, labels) -- limited from the UI; must use CLI or Portainer.

### Compose File Storage Location
- App Store apps: `/var/lib/casaos/apps/<appname>/docker-compose.yml`
- Custom apps: `~/.casaos/<dockerAppName>/docker-compose.yml`
- Global environment variables: `/etc/casaos/env`

---

## 5. Network and Storage Gotchas

### Network
- **`localhost` doesn't resolve to host** from Docker containers. Use `host.docker.internal` with `extra_hosts`.
- **Docker registry polling**: `zimaos-app-manager` queries `registry-1.docker.io` every 30 seconds, even on a fresh install. This causes issues with Pi-hole or DNS filtering. ([forum](https://community.zimaspace.com/t/zimaos-queries-registry-1-docker-io-every-30-seconds/6271))
- **Samba/CIFS share path stripping bug**: The LAN Storage UI incorrectly strips the share name from the server address, making it impossible to mount many standard NAS shares. No CLI workaround because `mount.cifs` is unavailable on Buildroot. ([#294](https://github.com/IceWhaleTech/ZimaOS/issues/294))

### Storage
- **CLI-mounted drives not recognized** by the Files app. Only drives mounted through ZimaOS's storage management layer are visible. ([forum](https://community.zimaspace.com/t/files-app-shows-storage-not-mount-error-message-after-manually-mounting-usb-drives-by-cli/6736))
- **Single partition per disk limit**. Cannot mount multiple partitions from one disk via the UI. ([#343](https://github.com/IceWhaleTech/ZimaOS/issues/343))
- **USB drives invisible to media apps** like Plex. ([#209](https://github.com/IceWhaleTech/ZimaOS/issues/209))
- **No iSCSI volume support**. ([#95](https://github.com/IceWhaleTech/ZimaOS/issues/95))
- **ZFS mount points not integrated** into the Files App storage section.
- **`/media/ZimaOS-HD` symlink resets on every reboot** -- points to `/DATA` and cannot be permanently changed.
- **Paths with spaces** caused display abnormalities and size calculation errors (fixed in later versions).
- **macOS SMB uploads** failed with files containing illegal characters (fixed in later versions).

---

## 6. Update-Related Problems

### Settings Reset Bug
Since v1.4.0, customized settings (timezone, default search engine, disk standby) may not persist after power-off/power-on cycles. A simple reboot retains settings, but a full power cycle can lose them. ([forum](https://community.zimaspace.com/t/zimaos-settings-resets-every-now-and-then/4966))

### OS Overwrites User Changes
ZimaOS updates can overwrite user customizations. This is a fundamental difference from CasaOS-on-Debian, where the base OS doesn't touch user configs. Multiple community members have flagged this as a reason to prefer CasaOS + Debian over ZimaOS.

### Apps Not Starting After Boot
Apps may not auto-start after boot, showing exit code 137 in Portainer. Docker service startup interval was insufficient in some versions, causing race conditions. ([#272](https://github.com/IceWhaleTech/ZimaOS/issues/272))

### Backup Before Update
Always back up `/ZimaOS-HD/.casaos/db/local-storage.db` before updating -- this contains RAID configuration data and is needed to rebuild storage after a reinstall.

---

## 7. The Buildroot Constraint

ZimaOS is built on **Buildroot**, not Debian/Ubuntu. This is the root cause of many developer frustrations:

- **No package manager** (`apt`, `yum`, `dnf` -- none available). ([#117](https://github.com/IceWhaleTech/ZimaOS/issues/117), [forum](https://community.zimaspace.com/t/package-manager-not-supported/3960))
- **Cannot install additional drivers** (e.g., NVIDIA drivers cannot be reinstalled after an update breaks them). ([#225](https://github.com/IceWhaleTech/ZimaOS/issues/225))
- **No `mount.cifs`** available from CLI, making manual Samba mounting impossible.
- **All extensions must go through Docker containers** -- there is no other way to add functionality.
- **Cannot add system-level tools** like `htop`, `iotop`, `nmap`, etc.

The trade-off is lightweight footprint and reliable OTA updates, but it severely limits what power users and developers can do outside Docker.

---

## 8. GPU Passthrough Issues

- **Inconsistent GPU visibility**: GPU may work in some containers (e.g., Jellyfin) but not others (e.g., Stremio), even when `nvidia-smi` works at the host level. ([forum](https://community.zimaspace.com/t/gpu-passthrough-issue-nvidia-visible-in-zimaos-jellyfin-but-missing-in-stremio-container/8080))
- **GPU not recognized after updates**: Upgrading ZimaOS can break NVIDIA driver/VA-API functionality with no easy fix (can't reinstall drivers due to Buildroot). ([#225](https://github.com/IceWhaleTech/ZimaOS/issues/225))
- **No GPU passthrough for ZVM** (ZimaOS Virtual Machine). ([#167](https://github.com/IceWhaleTech/ZimaOS/issues/167))
- **Docker compose GPU syntax**: Use resource reservations:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```
- **Fallback consideration**: The official docs recommend apps should fall back to CPU when GPU is unavailable.

---

## 9. Third-Party App Stores

ZimaOS supports adding third-party app stores via URL in the App Store settings. Notable ones:

- **[BigBearCasaOS](https://github.com/bigbeartechworld/big-bear-casaos)** -- pre-installed on IceWhale hardware, community-maintained, wide selection.
- **Community-contributed stores** -- over 100 third-party apps available for media management, game servers, private code hosting, etc.
- **Refresh issues**: Third-party store refresh has been noted as unreliable. ([#98](https://github.com/IceWhaleTech/ZimaOS/issues/98))

---

## 10. Summary: Top 10 Things Every ZimaOS Developer Should Know

1. **There is no package manager.** Buildroot means Docker is your only extension mechanism.
2. **Custom containers share a project name.** Deploy more than one via the UI and they collide.
3. **No `.env` file support.** Inline everything or use Portainer/Dockge (with UI display trade-offs).
4. **You cannot edit App Store apps' compose files.** Uninstall and reinstall as custom if you need changes.
5. **`localhost` doesn't work from containers.** Use `host.docker.internal` with `extra_hosts`.
6. **Strip Swarm directives** from compose files before importing.
7. **`WEBUI_PORT` is one-shot.** It's allocated once and never reassigned if the port gets taken.
8. **Updates can break everything.** Back up `/ZimaOS-HD/.casaos/db/local-storage.db` and your compose files.
9. **GPU support is fragile.** Works in some containers, not others, and can break on OS update with no fix path.
10. **CasaOS apps are not 100% ZimaOS-compatible.** Test thoroughly; icons and titles may be overwritten.

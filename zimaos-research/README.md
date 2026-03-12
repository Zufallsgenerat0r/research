# ZimaOS Research Report

## 1. What is ZimaOS?

**ZimaOS** is an open-source NAS operating system developed by [IceWhale Technology](https://github.com/IceWhaleTech). It evolved from [CasaOS](https://github.com/IceWhaleTech/CasaOS) (33.4k GitHub stars), which is a lightweight personal cloud software layer that runs on top of existing Linux distributions. ZimaOS takes the CasaOS foundation and builds it into a **full standalone OS using Buildroot**, with enhanced storage management, hardware optimizations, and OTA update capabilities.

### Key Differences: ZimaOS vs CasaOS

| Feature | CasaOS | ZimaOS |
|---------|--------|--------|
| **Type** | Software overlay on Linux | Full standalone OS (Buildroot) |
| **Installation** | `wget -qO- https://get.casaos.io \| sudo bash` | USB installer image (.img) |
| **Architecture** | amd64, arm64, armv7 | x86-64 (UEFI required) |
| **Storage** | Basic disk management | RAID 0/1/5/6/JBOD, ZFS, Btrfs |
| **Updates** | APT/manual script | RAUC-based OTA with A/B partitions |
| **Additional Features** | Core Docker app management | VM manager (ZVM), GPU support, Thunderbolt, iSCSI/NFS/SMB |
| **License** | Apache 2.0 (fully open) | CE-Edition free (limited); Plus Edition $29 lifetime |
| **Target Hardware** | RPi, NUC, any Linux box | ZimaBoard, ZimaCube, ZimaBlade, generic x86-64 |

### Pricing (v1.5.0+, 2025)

ZimaOS v1.5.0 introduced a paid tier. The free **CE-Edition** is limited to 10 apps, 4 disks, and 3 users. The **Plus Edition** costs $29 (one-time, lifetime license) and removes all limits. Existing users can upgrade for free until June 30, 2026.

---

## 2. App Ecosystem Structure

### 2.1 Docker-Based App Architecture

Every app in ZimaOS/CasaOS is a Docker container (or multi-container compose stack) defined by a `docker-compose.yml` file with a custom `x-casaos` metadata extension. The system manages the full lifecycle: installation, configuration, start/stop, health checks, logs, and uninstallation.

### 2.2 App Store Structure

The official app store is maintained at [CasaOS-AppStore](https://github.com/IceWhaleTech/CasaOS-AppStore) (158+ apps in the official repo, 800+ across third-party stores).

**Directory layout:**
```
CasaOS-AppStore/
├── Apps/
│   ├── Jellyfin/
│   │   ├── docker-compose.yml
│   │   ├── icon.png
│   │   └── screenshot-1.png
│   ├── Nextcloud/
│   ├── HomeAssistant/
│   └── ... (158+ apps)
├── category-list.json
├── featured-apps.json
└── recommend-list.json
```

Each app directory contains:
- `docker-compose.yml` (required) -- with `x-casaos` extension
- `icon.png` (required) -- 192x192 PNG
- `screenshot-1.png` (required) -- proving it works on CasaOS
- `thumbnail.png` (optional) -- 784x442 PNG for featured apps

### 2.3 Docker Compose Pattern (Example: Jellyfin)

```yaml
name: jellyfin
services:
  jellyfin:
    image: linuxserver/jellyfin:10.10.7    # Pinned version, NOT :latest
    environment:
      PGID: $PGID        # Preset system variable
      PUID: $PUID        # Preset system variable
      TZ: $TZ            # Preset system variable
    network_mode: bridge
    ports:
      - target: 8096
        published: "8097"
        protocol: tcp
    restart: unless-stopped
    volumes:
      - type: bind
        source: /DATA/AppData/$AppID/config   # $AppID = app name
        target: /config
      - type: bind
        source: /DATA/Media
        target: /Media
    deploy:
      resources:
        reservations:
          memory: "256M"
    container_name: jellyfin
```

### 2.4 The `x-casaos` Extension

The `x-casaos` section provides metadata at two levels:

**Service level** (per container):
- Multilingual descriptions for environment variables, ports, and volumes
- Container-specific configuration hints

**Compose level** (per app):
- `architectures`: supported platforms (amd64, arm, arm64)
- `main`: primary service name
- `author`, `category`, `developer`
- `description`, `tagline`, `title`: multilingual (en_US, zh_CN, etc.)
- `icon`, `thumbnail`, `screenshot`: CDN URLs
- `port_map`: web UI port designation
- `tips.before_install`: markdown-formatted pre-install notes

### 2.5 Special Environment Variables

| Variable | Purpose |
|----------|---------|
| `$PUID` | User ID for container permissions |
| `$PGID` | Group ID for container permissions |
| `$TZ` | System timezone |
| `$AppID` | App name, used in volume paths |
| `${WEBUI_PORT}` | Dynamically assigned available port |

Global variables are stored in `/etc/casaos/env`. App data is persisted at `/DATA/AppData/$AppID/`.

### 2.6 Third-Party App Stores

CasaOS/ZimaOS supports adding third-party app store sources via URL. Eight community app stores exist, providing nearly 500 additional apps beyond the official 158+. Users add stores through Settings or via the API (`POST /v2/app_management/appstore`).

### 2.7 Custom App Installation

Users can install any Docker app by pasting a `docker-compose.yml` via the "Install a Custom App" feature in the UI, or programmatically via `POST /v2/app_management/compose` with YAML body.

---

## 3. Key GitHub Repositories

The [IceWhaleTech GitHub organization](https://github.com/IceWhaleTech) has 43 repositories. The system is built as **Go microservices** communicating via a message bus, with a Vue.js frontend.

### 3.1 Core Repositories

| Repository | Stars | Language | Description |
|-----------|-------|----------|-------------|
| [CasaOS](https://github.com/IceWhaleTech/CasaOS) | 33.4k | Go | Base personal cloud system |
| [ZimaOS](https://github.com/IceWhaleTech/ZimaOS) | 2.4k | Shell | Full NAS OS (Buildroot-based), releases only |
| [CasaOS-AppStore](https://github.com/IceWhaleTech/CasaOS-AppStore) | 306 | Shell | Docker compose app manifests |
| [CasaOS-UI](https://github.com/IceWhaleTech/CasaOS-UI) | 127 | Vue | Web frontend |
| [ZimaDocs](https://github.com/IceWhaleTech/ZimaDocs) | 34 | CSS | Documentation site source |

### 3.2 Microservice Components

| Repository | Stars | Purpose |
|-----------|-------|---------|
| [CasaOS-AppManagement](https://github.com/IceWhaleTech/CasaOS-AppManagement) | 24 | App lifecycle (install/run/update/remove) |
| [CasaOS-Gateway](https://github.com/IceWhaleTech/CasaOS-Gateway) | 23 | Dynamic API gateway (port 8080) |
| [CasaOS-CLI](https://github.com/IceWhaleTech/CasaOS-CLI) | 18 | Command-line interface |
| [CasaOS-UserService](https://github.com/IceWhaleTech/CasaOS-UserService) | 15 | Authentication and user management |
| [CasaOS-LocalStorage](https://github.com/IceWhaleTech/CasaOS-LocalStorage) | 14 | Disk and storage management |
| [CasaOS-MessageBus](https://github.com/IceWhaleTech/CasaOS-MessageBus) | -- | Inter-service event/message bus |
| [CasaOS-Common](https://github.com/IceWhaleTech/CasaOS-Common) | -- | Shared libraries and utilities |

### 3.3 Update Infrastructure

| Repository | Purpose |
|-----------|---------|
| [zimaos-rauc](https://github.com/IceWhaleTech/zimaos-rauc) | RAUC OTA update bundles |

### 3.4 Microservice Architecture

```
                    ┌─────────────────┐
                    │   CasaOS-UI     │  (Vue.js frontend)
                    │   Port: 80/443  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ CasaOS-Gateway  │  (Echo/Go, port 8080)
                    │ API Router/Auth │  JWT (ECDSA), CORS
                    └────────┬────────┘
                             │ Routes registered via Management API
            ┌────────────────┼────────────────┐
            │                │                │
   ┌────────▼──────┐ ┌──────▼───────┐ ┌──────▼──────────┐
   │ AppManagement │ │ UserService  │ │ LocalStorage    │
   │ /v2/app_mgmt  │ │ /v1/users    │ │ /v1/storage     │
   └───────┬───────┘ └──────────────┘ └─────────────────┘
           │
   ┌───────▼───────┐
   │ MessageBus    │  (event bus for app:install-begin, etc.)
   └───────────────┘
```

All backend services bind to **localhost only** (127.0.0.1 / ::1). The Gateway handles all external access and JWT authentication (exempting localhost requests). Services register their API routes with the Gateway's management port at startup.

Configuration files live in `/etc/casaos/`. The Gateway config search order: `./gateway.ini` -> `./conf/gateway.ini` -> `$HOME/.casaos/gateway.ini` -> `/etc/casaos/gateway.ini`.

---

## 4. Update Mechanisms

### 4.1 System Updates (ZimaOS only -- RAUC-based OTA)

ZimaOS uses [RAUC (Robust Auto-Update Controller)](https://rauc.io/) for system-level updates, built into the Buildroot image.

**Architecture:**
- **A/B partition scheme**: Two boot slots (A and B). Updates write to the inactive slot; the system reboots into the updated slot. If the update fails, the system can fall back to the previous slot.
- **Update bundles**: `.raucb` files containing kernel, system partition, and boot partition.
- **Releases**: Published at [github.com/IceWhaleTech/ZimaOS/releases](https://github.com/IceWhaleTech/ZimaOS/releases) (59 releases as of March 2026, latest v1.5.4).

**Update methods:**

| Method | How |
|--------|-----|
| **Dashboard OTA** | Red notification dot appears in top-left of dashboard; click to update |
| **Command line** | `sudo -i` then `curl -fsSL 'https://ota.zimaos.com/' \| sh` |
| **Offline** | Upload `.raucb` file to `/ZimaOS-HD/rauc/offline/`; system auto-detects |
| **Manual RAUC bundle** | Download `.raucb` from GitHub releases, apply manually |
| **Fresh install** | Download `.img` installer from GitHub releases |

**Update channels:** Automatic (stable), Beta channel, and command-line.

CasaOS (non-ZimaOS) does **not** use RAUC. It updates via its installation script or package manager, since it runs on top of an existing Linux distro.

### 4.2 App Updates

App updates are a **separate mechanism** from system updates and are handled by the [CasaOS-AppManagement](https://github.com/IceWhaleTech/CasaOS-AppManagement) service.

**Key characteristics:**
- **No automatic app updates.** CasaOS/ZimaOS deliberately pins apps to specific image versions (e.g., `linuxserver/jellyfin:10.10.7`) for stability.
- **Store-driven upgrades.** When the app store updates an app's manifest with a newer version tag, the system can detect it.

**API endpoints for app updates:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /v2/app_management/apps/upgradable` | GET | List all installed apps that have newer versions in the store |
| `PATCH /v2/app_management/compose/{id}` | PATCH | Update a specific compose app's container images to the latest store version |
| `PATCH /v2/app_management/container/{id}` | PATCH | Recreate container with option to pull latest image (`PullLatestImage` param) |

**App install lifecycle events** (via MessageBus):
- `app:install-begin` -- installation started (properties: app name, icon)
- `app:install-progress` -- progress update (properties: progress %, title, port conflict check, dry run)
- `app:install-end` -- installation complete
- `app:install-error` -- installation failed (properties: error message)

**Manual workarounds for auto-updates:**
1. Edit the docker-compose.yml to change the image tag from a pinned version to `:latest`
2. Install [Watchtower](https://github.com/containrrr/watchtower) as a container to periodically check for and apply image updates
3. Use `docker compose down --rmi all && docker compose up` from the command line

### 4.3 System vs App Updates -- Summary

| Aspect | System Update | App Update |
|--------|--------------|------------|
| **Scope** | OS kernel, system partition, boot | Individual Docker containers |
| **Mechanism** | RAUC OTA (A/B partition) | Docker image pull + compose recreate |
| **Trigger** | Dashboard notification / CLI / offline | Manual via UI or API; no auto-update |
| **Rollback** | Automatic (A/B slot fallback) | Manual (re-pull old image tag) |
| **Delivery** | `.raucb` bundles from ota.zimaos.com or GitHub | Updated docker-compose.yml manifests in app store |
| **Frequency** | Major releases (v1.2 -> v1.3 -> v1.4 -> v1.5) | Per-app, when maintainers update the store manifest |

---

## 5. API Reference (CasaOS-AppManagement v2)

The full OpenAPI 3.0.3 specification is at:
`https://raw.githubusercontent.com/IceWhaleTech/CasaOS-AppManagement/main/api/app_management/openapi.yaml`

Base path: `/v2/app_management`

### Complete Endpoint List

**Common:**
- `GET /info` -- System architecture info
- `POST /convert` -- Convert appfile to compose format
- `GET /global` -- All global settings
- `GET|PUT|DELETE /global/{key}` -- Individual settings

**App Store:**
- `GET /appstore` -- List registered stores
- `POST /appstore` -- Register new store (URL param)
- `DELETE /appstore/{id}` -- Unregister store
- `GET /categories` -- App categories with counts
- `GET /apps` -- List all store apps (filter by category, author, recommended)
- `GET /apps/upgradable` -- List upgradable installed apps
- `GET /apps/{id}` -- App store info
- `GET /apps/{id}/stable` -- Stable version tag
- `GET /apps/{id}/compose` -- Compose YAML/JSON

**Compose App Lifecycle:**
- `GET /compose` -- List installed compose apps
- `POST /compose` -- Install app (YAML body, supports dry_run)
- `GET /compose/{id}` -- Get installed app details
- `PUT /compose/{id}` -- Apply settings (YAML body)
- `PATCH /compose/{id}` -- Update to latest store version
- `DELETE /compose/{id}` -- Uninstall (option: delete_config_folder)
- `PUT /compose/{id}/status` -- Start/restart/stop
- `GET /compose/{id}/containers` -- List containers
- `GET /compose/{id}/logs` -- Get logs
- `GET /compose/{id}/healthcheck` -- Health check

**Container:**
- `PATCH /container/{id}` -- Recreate container (PullLatestImage, Force)

**Image:**
- `POST /image` -- Batch pull images by container IDs

**Internal:**
- `GET /web/appgrid` -- App grid (internal)

---

## 6. Sources

- [ZimaOS GitHub Repository](https://github.com/IceWhaleTech/ZimaOS)
- [CasaOS GitHub Repository](https://github.com/IceWhaleTech/CasaOS)
- [CasaOS-AppStore GitHub Repository](https://github.com/IceWhaleTech/CasaOS-AppStore)
- [CasaOS-AppManagement GitHub Repository](https://github.com/IceWhaleTech/CasaOS-AppManagement)
- [CasaOS-Gateway GitHub Repository](https://github.com/IceWhaleTech/CasaOS-Gateway)
- [IceWhaleTech GitHub Organization](https://github.com/IceWhaleTech)
- [ZimaOS RAUC Repository](https://github.com/IceWhaleTech/zimaos-rauc)
- [ZimaOS Documentation](https://www.zimaspace.com/docs/zimaos/)
- [ZimaOS Offline Update Guide](https://www.zimaspace.com/docs/zimaos/Install-offline)
- [ZimaOS Docker App Adaptation Manual](https://www.zimaspace.com/docs/zimaos/Build-Apps)
- [ZimaOS OpenAPI Documentation](https://www.zimaspace.com/docs/zimaos/How-to-use-OpenAPI)
- [CasaOS-AppStore Contributing Guide](https://github.com/IceWhaleTech/CasaOS-AppStore/blob/main/CONTRIBUTING.md)
- [CasaOS Wiki - Manually Update Compose App](https://wiki.casaos.io/en/guides/manually-update-compose-app-with-latest-tag)
- [CasaOS Wiki - Development](https://wiki.casaos.io/en/contribute/development)
- [ZimaOS 1.5 Launch Announcement (PR Newswire)](https://www.prnewswire.com/news-releases/icewhale-launches-zimaos-1-5-simplified-focused-and-open-nas-operating-system-for-homes-smbs-and-tech-enthusiasts-302569303.html)
- [ZimaOS 1.5 Pricing Discussion (NotebookCheck)](https://www.notebookcheck.net/ZimaOS-1-5-0-goes-paid-community-reacts-with-dissapointment.1122850.0.html)
- [CasaOS vs ZimaOS Comparison](https://shop.zimaspace.com/blogs/zima-campaign-hub/casaos-vs-zimaos-choice-guide)
- [IceWhale Founder Interview (NASCompares)](https://nascompares.com/2025/11/08/zimaos-interview-with-lauren-pan-founder-of-icewhale/)
- [RAUC Official Site](https://rauc.io/)
- [ZimaOS Update Command Blog Post](https://www.johnsypin.com/2025/09/21/zimaos-update-command/)

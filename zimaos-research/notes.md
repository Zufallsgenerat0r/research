# ZimaOS Research Notes

## Research Process

### Initial Web Searches
- Searched for "ZimaOS what is it CasaOS IceWhale Technology"
- Searched for "ZimaOS update mechanism how system updates work"
- Searched for "ZimaOS app store how it works Docker apps"
- Searched for "ZimaOS developer documentation API"
- Searched for "CasaOS app update mechanism Docker compose"

### GitHub Repositories Explored
- https://github.com/IceWhaleTech/ZimaOS - Main ZimaOS repo (Shell, 2.4k stars)
- https://github.com/IceWhaleTech/CasaOS - Base system (Go, 33.4k stars)
- https://github.com/IceWhaleTech/CasaOS-AppStore - App manifests (Shell, 306 stars)
- https://github.com/IceWhaleTech/CasaOS-AppManagement - App lifecycle (Go, 24 stars)
- https://github.com/IceWhaleTech/CasaOS-Gateway - API gateway (Go, 23 stars)
- https://github.com/IceWhaleTech/CasaOS-UI - Frontend (Vue, 127 stars)
- https://github.com/IceWhaleTech/zimaos-rauc - RAUC OTA update bundles
- https://github.com/IceWhaleTech/ZimaDocs - Documentation (CSS, 34 stars)
- https://github.com/IceWhaleTech/CasaOS-CLI - CLI tool (Go, 18 stars)
- https://github.com/IceWhaleTech/CasaOS-UserService - Auth (Go, 15 stars)
- https://github.com/IceWhaleTech/CasaOS-LocalStorage - Storage (Go, 14 stars)

### Key Findings

#### ZimaOS vs CasaOS
- CasaOS is a lightweight software overlay on existing Linux distros (Debian, Ubuntu, RPi OS)
- ZimaOS is a full standalone OS built with Buildroot, evolved from CasaOS
- ZimaOS adds: RAID support (0,1,5,6,JBOD), ZFS/Btrfs, RAUC OTA updates, VM manager (ZVM), GPU support
- As of v1.5.0 (2025), ZimaOS split into free CE-Edition (limited to 10 apps, 4 disks, 3 users) and paid Plus ($29 lifetime)

#### System Architecture
- Microservices written in Go, communicating via CasaOS-MessageBus
- CasaOS-Gateway serves as dynamic API gateway (default port 8080)
- Services register routes with the gateway via management API
- All backend services bind to localhost only - gateway handles external access
- Config files in /etc/casaos/
- JWT authentication with ECDSA keys

#### System Update Mechanism (RAUC-based)
- Built on Buildroot with RAUC (Robust Auto-Update Controller)
- Uses A/B partition scheme for safe updates
- Update bundles are .raucb files
- Methods: Dashboard OTA, CLI (`curl -fsSL 'https://ota.zimaos.com/' | sh`), offline (/ZimaOS-HD/rauc/offline/)
- Releases hosted on GitHub

#### App Update Mechanism
- No built-in automatic app updates in CasaOS/ZimaOS
- App store tracks versions with pinned image tags (not :latest)
- PATCH /v2/app_management/compose/{id} updates container images to latest store version
- GET /v2/app_management/apps/upgradable checks for upgradable apps
- Manual workaround: change image tag to "latest", use Watchtower for auto-updates
- App install emits events: app:install-begin, app:install-progress, app:install-end, app:install-error

#### App Store Structure
- Each app = directory under Apps/ with docker-compose.yml + icon.png + screenshot
- Docker compose files use x-casaos extension for metadata (multilingual descriptions, icons, categories, architecture support)
- 158+ apps in official store, 800+ including third-party stores
- Third-party stores can be added via URL
- Environment variables: $PUID, $PGID, $TZ, $AppID, ${WEBUI_PORT}
- Global env vars in /etc/casaos/env
- App data stored at /DATA/AppData/$AppID/

#### OpenAPI
- API versioned: v1 and v2 under /v2/app_management/
- Echo framework in Go
- OpenAPI 3.0.3 spec at api/app_management/openapi.yaml
- Endpoints organized: Common, AppStore, Compose, Container, Image, Internal

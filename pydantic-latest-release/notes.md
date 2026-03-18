# Research Notes: Latest Major Release of Python Pydantic

## Research Date: 2026-03-18

## Sources Consulted

- [pydantic · PyPI](https://pypi.org/project/pydantic/) — Package metadata and version history
- [Releases · pydantic/pydantic](https://github.com/pydantic/pydantic/releases) — GitHub release notes
- [Pydantic v2.12 Release Announcement](https://pydantic.dev/articles/pydantic-v2-12-release)
- [Pydantic v2.11 Release Announcement](https://pydantic.dev/articles/pydantic-v2-11-release)
- [Pydantic v2 Pre-Release Blog](https://blog.pydantic.dev/blog/2023/04/03/pydantic-v2-pre-release/)
- [Introducing Pydantic v2](https://pydantic.dev/articles/pydantic-v2)
- [pydantic-core GitHub](https://github.com/pydantic/pydantic-core) — Rust validation core
- [Migration Guide](https://docs.pydantic.dev/latest/migration/) — Official v1→v2 migration docs
- [Version Policy](https://docs.pydantic.dev/latest/version-policy/)
- [bump-pydantic](https://github.com/pydantic/bump-pydantic) — Automated migration tool
- [Pydantic V3 Discussion (Issue #10033)](https://github.com/pydantic/pydantic/issues/10033)
- [Pydantic Roadmap Article](https://pydantic.dev/articles/roadmap)
- [Changelog](https://docs.pydantic.dev/latest/changelog/)

## Key Findings

### Latest major version
- **Pydantic v2** is the current latest major release (v1 → v2 on June 30, 2023)
- Latest stable: **v2.12.5** (November 26, 2025)
- Current beta: **v2.13.0b2** (February 24, 2026)
- Pydantic v3 is planned but has no release date yet

### Core architecture change
- Validation engine completely rewritten in **Rust** via the `pydantic-core` package
- Uses a "core schema" concept — a structured Python dict that bridges pydantic (Python) and pydantic-core (Rust)
- Tree-based validator architecture (CombinedValidator pattern) in Rust

### Performance
- **5–50x faster** than v1 depending on workload
- ~17x faster for models with common field types
- v2.11 added up to 2x improvement in schema build/startup times

### Breaking changes (v1 → v2)
- `parse_raw()` / `parse_file()` → `model_validate_json()` / `model_validate()`
- `from_orm()` → `model_validate()` with `from_attributes=True`
- `Config` class → `model_config` dict
- `@validator` → `@field_validator`
- `Optional[T]` no longer implies a default of `None`
- Subclass serialization only includes fields from the annotated type
- `pydantic.generics.GenericModel` removed; use `Generic` directly

### Migration tools
- `pydantic.v1` compatibility shim ships inside v2
- `bump-pydantic` CLI tool for automated code transformation

### Recent minor releases (2025)
- **v2.11**: Build-time performance (up to 2x faster schema construction)
- **v2.12**: Python 3.14 support (PEP 649/749), experimental MISSING sentinel, PEP 728 TypedDict support

### v3 outlook
- No massive API overhaul planned
- Focus on cleanup, edge-case fixes, removal of v1 shims
- Expected to be much less disruptive than v1→v2

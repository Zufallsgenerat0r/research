# Latest Major Release of Python Pydantic

<!-- AI-GENERATED-NOTE -->
> [!NOTE]
> This is an AI-generated research report. All text and code in this report was created by an LLM (Large Language Model). For more information on how these reports are created, see the [main research repository](https://github.com/simonw/research).
<!-- /AI-GENERATED-NOTE -->

## Overview

**Pydantic v2** is the latest major release of the Pydantic data validation library for Python. Released on **June 30, 2023**, it represented a complete ground-up rewrite of the validation engine. As of March 2026, the latest stable version is **v2.12.5** (November 26, 2025), with **v2.13** in beta. Pydantic v3 is planned but has no confirmed release date.

---

## Core Architectural Change: Rust-Powered Validation

The defining change in Pydantic v2 is the migration of all validation and serialization logic from pure Python to **Rust**, housed in a separate package called [`pydantic-core`](https://github.com/pydantic/pydantic-core).

The architecture uses a **core schema** concept — a structured, serializable Python dictionary that describes validation and serialization rules. This acts as the communication bridge between the Python-side `pydantic` package (which handles model definitions and developer-facing APIs) and the Rust-side `pydantic-core` (which performs actual validation and serialization).

Internally, `pydantic-core` uses a tree-based `CombinedValidator` pattern where validators call each other in a tree structure, enabling modular composition without performance penalties.

---

## Performance Improvements

| Benchmark | Improvement |
|-----------|-------------|
| General validation | **5–50x faster** than v1 |
| Common field types | **~17x faster** |
| Schema build time (v2.11+) | **Up to 2x faster** startup |

Simply upgrading from v1 to v2 delivers an approximately 5x "free" performance boost. The Rust rewrite allows the code to be more modular and extensible without incurring the overhead that would result from equivalent abstractions in Python.

Starting with v2.11 (2025), the team also addressed build-time/startup performance, achieving up to 2x improvement in schema construction times through multiple targeted optimizations.

---

## Key New Features

### TypeAdapter
A new class that allows validation and serialization of arbitrary types without requiring a `BaseModel` class. Replaces the old `schema_of` utility from v1.

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(list[int])
result = adapter.validate_python(["1", "2", "3"])  # [1, 2, 3]
```

### Strict Mode
Pydantic v2 introduced strict mode, which disables the "magic" type coercion from v1. In strict mode, a string `"123"` will not be silently converted to an integer — a validation error is raised instead.

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)
    value: int

StrictModel(value="123")  # ValidationError in strict mode
```

### Improved JSON Schema Generation
- Targets **JSON Schema draft 2020-12** (with OpenAPI extensions)
- `GenerateJsonSchema` class enables customizable schema generation
- Better type representation (e.g., `Decimal` exposed as string)
- Optional fields properly indicate null is allowed

### Dict-Based Configuration
The `Config` inner class has been replaced with a `model_config` class attribute using `ConfigDict`:

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    name: str
```

---

## Breaking Changes (v1 → v2)

### API Renames

| v1 | v2 |
|----|-----|
| `Model.parse_raw(data)` | `Model.model_validate_json(data)` |
| `Model.parse_file(path)` | `Model.model_validate(data)` |
| `Model.from_orm(obj)` | `Model.model_validate(obj)` with `from_attributes=True` |
| `Model.dict()` | `Model.model_dump()` |
| `Model.json()` | `Model.model_dump_json()` |
| `Model.schema()` | `Model.model_json_schema()` |

All BaseModel methods now follow `model_*` or `__*pydantic*__` naming patterns.

### Validator Decorators

```python
# v1
from pydantic import validator

class MyModel(BaseModel):
    name: str

    @validator("name")
    def validate_name(cls, v):
        return v.strip()

# v2
from pydantic import field_validator

class MyModel(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return v.strip()
```

### Optional Field Behavior
In v1, `Optional[str]` implicitly set a default of `None`. In v2, `Optional[str]` means the field **accepts** `None` but is still **required** unless a default is explicitly provided:

```python
class MyModel(BaseModel):
    name: Optional[str]        # Required in v2, accepts None
    name: Optional[str] = None # Optional with default None (equivalent to v1)
```

### Other Breaking Changes
- `__eq__` only returns `True` when comparing two `BaseModel` instances
- Subclass serialization only includes fields from the annotated type (prevents data leakage)
- `pydantic.generics.GenericModel` removed — use `Generic` directly as a parent class
- Dataclasses no longer accept tuples as input; must use dicts
- `__post_init__` for dataclasses is called after validation (not before)

---

## Migration Path

### Strategy 1: Compatibility Shim (Gradual Migration)
Pydantic v2 ships with the full v1 library accessible under `pydantic.v1`:

```python
# Temporary — use v1 imports while migrating
from pydantic.v1 import BaseModel
```

This allows running v1 and v2 code side-by-side during a gradual migration.

### Strategy 2: Automated Migration with bump-pydantic
The [`bump-pydantic`](https://github.com/pydantic/bump-pydantic) CLI tool performs automated code transformations:

```bash
pip install bump-pydantic
bump-pydantic <your_project_directory>
```

It handles common renames, decorator changes, and configuration migration automatically.

---

## Recent Releases (2025–2026)

### v2.11 — Build-Time Performance
- Up to **2x faster** schema build/startup times
- Multiple small-to-medium optimizations targeting initialization overhead

### v2.12 (October 7, 2025)
- **Python 3.14 support** — handles PEP 649 (deferred evaluation of annotations) and PEP 749 (lazy type annotations)
- **Experimental MISSING sentinel** — a new way to indicate unset field values, distinct from `None`
- **PEP 728 support** — improved TypedDict type handling
- Compatibility version checks for pydantic-core

### v2.13 (Beta, February 2026)
- Currently in beta (v2.13.0b2 released February 24, 2026)

---

## Future: Pydantic v3

Based on [GitHub Issue #10033](https://github.com/pydantic/pydantic/issues/10033) and the official roadmap:

- **No massive API overhaul** — v3 will focus on cleanup, edge-case fixes, and refinement
- **Removal of v1 compatibility shims** (`pydantic.v1` module will be dropped)
- **Strategy**: New features introduced as opt-in in minor releases, then stabilized in the major release
- **Expected to be far less disruptive** than the v1→v2 transition
- No confirmed release date as of March 2026

---

## Summary

Pydantic v2 is a landmark release that fundamentally changed the library's architecture by moving validation to Rust. The result is dramatic performance improvements (5–50x), cleaner APIs, and better type system integration. While the v1→v2 migration involved significant breaking changes, the team provided robust migration tools and a compatibility layer. The library continues active development through v2.x minor releases, with v3 planned as a gentler evolution focused on cleanup rather than another architectural overhaul.

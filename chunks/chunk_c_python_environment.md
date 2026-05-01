# Chunk C — Lucifex Python Environment Setup

You are working in the Lucifex project repository. Chunks A and B established the foundation and folder scaffold. Your job in Chunk C is to turn the backend into a proper Python project: declare dependencies, configure tooling, set up the `src/` layout, and create the `__init__.py` files that make the backend folders importable.

You will not write any application code in this chunk. No FastAPI app. No SQLAlchemy models. No actual logic. The output of this chunk is configuration and packaging metadata that will let later chunks add real code on top.

You will not run any commands that install packages. You will not create or activate a virtual environment. The chunk produces the configuration files; the operator runs the install manually after review.

When you are finished, report back with confirmation of each operation and show the updated file tree.

---

## Architectural decisions for this chunk

These are confirmed and locked in before execution:

1. **`src/` layout** — The Python package lives under `backend/src/lucifex/`, not at `backend/lucifex/`. The src layout forces an editable install before imports work, which catches packaging bugs early and ensures tests run against the installed package the way users would.
2. **Package name** — `lucifex` (singular, lowercase). Imports look like `from lucifex.core.clips import ...`.
3. **Python version** — `3.12`, pinned in `.python-version` and required in `pyproject.toml`.
4. **Build backend** — `hatchling` via the standard `[build-system]` table. Modern, fast, well-supported.
5. **Tooling** — `ruff` for linting and formatting, `mypy` for type checking, `pytest` for tests. Configuration lives in `pyproject.toml`, not separate config files.

---

## Operation 1 — Create the `src/` layout under `backend/`

The existing `backend/` folder contains subfolders (`api/`, `core/`, `agent/`, etc.) created in Chunk B. These need to be moved under `backend/src/lucifex/` to follow the src layout.

**Important: this is a relocation, not a duplication.** The contents of each existing backend subfolder (its README, and only its README at this point) move from `backend/<subfolder>/` to `backend/src/lucifex/<subfolder>/`.

Specifically, perform these moves:

| Move from | Move to |
|-----------|---------|
| `backend/api/` | `backend/src/lucifex/api/` |
| `backend/core/` | `backend/src/lucifex/core/` |
| `backend/agent/` | `backend/src/lucifex/agent/` (with all nested folders) |
| `backend/db/` | `backend/src/lucifex/db/` (with all nested folders) |
| `backend/providers/` | `backend/src/lucifex/providers/` (with all nested folders) |
| `backend/platforms/` | `backend/src/lucifex/platforms/` |
| `backend/workers/` | `backend/src/lucifex/workers/` |
| `backend/jobs/` | `backend/src/lucifex/jobs/` |
| `backend/auth/` | `backend/src/lucifex/auth/` |
| `backend/observability/` | `backend/src/lucifex/observability/` |
| `backend/config/` | `backend/src/lucifex/config/` |

The `backend/tests/` folder does NOT move — tests live alongside the package, not inside it. After this operation, the structure should be:

```
backend/
├── src/
│   └── lucifex/
│       ├── api/
│       ├── core/
│       ├── agent/
│       │   ├── tools/
│       │   └── prompts/
│       ├── db/
│       │   ├── models/
│       │   ├── migrations/
│       │   └── repositories/
│       ├── providers/
│       │   ├── llm/
│       │   ├── video_generation/
│       │   ├── image_generation/
│       │   └── tts/
│       ├── platforms/
│       ├── workers/
│       ├── jobs/
│       ├── auth/
│       ├── observability/
│       └── config/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

Each moved folder retains its `README.md` from Chunk B exactly as written. No README content changes in this operation.

The `backend/README.md` at the top of `backend/` is also unchanged — but you will update it in Operation 7 below.

---

## Operation 2 — Create the `lucifex/__init__.py`

Create the file `backend/src/lucifex/__init__.py` with this exact content:

```python
"""Lucifex — Commercial Grade Apps for Personal Use.

Autonomous content production system. The operator directs strategy through
a chat interface; the system generates AI video clips, manages multi-platform
distribution, and tracks performance across multiple brand identities.

See `docs/architecture.md` for system design and `docs/decision_log.md` for
architectural decisions.
"""

__version__ = "0.0.1"
```

This is the package's top-level init. The version string is the single source of truth — `pyproject.toml` will read it dynamically rather than duplicating.

---

## Operation 3 — Create empty `__init__.py` files in every package subfolder

Python treats any folder containing an `__init__.py` as a package (importable). Folders without one are not importable. Every subfolder under `backend/src/lucifex/` needs an empty `__init__.py`.

Create empty `__init__.py` files (zero bytes, no content) at the following paths:

- `backend/src/lucifex/api/__init__.py`
- `backend/src/lucifex/core/__init__.py`
- `backend/src/lucifex/agent/__init__.py`
- `backend/src/lucifex/agent/tools/__init__.py`
- `backend/src/lucifex/db/__init__.py`
- `backend/src/lucifex/db/models/__init__.py`
- `backend/src/lucifex/db/repositories/__init__.py`
- `backend/src/lucifex/providers/__init__.py`
- `backend/src/lucifex/providers/llm/__init__.py`
- `backend/src/lucifex/providers/video_generation/__init__.py`
- `backend/src/lucifex/providers/image_generation/__init__.py`
- `backend/src/lucifex/providers/tts/__init__.py`
- `backend/src/lucifex/platforms/__init__.py`
- `backend/src/lucifex/workers/__init__.py`
- `backend/src/lucifex/jobs/__init__.py`
- `backend/src/lucifex/auth/__init__.py`
- `backend/src/lucifex/observability/__init__.py`
- `backend/src/lucifex/config/__init__.py`

**Two folders deliberately do NOT get an `__init__.py`:**

- `backend/src/lucifex/agent/prompts/` — this folder holds markdown prompt files, not Python code. It is not a Python package.
- `backend/src/lucifex/db/migrations/` — Alembic creates and manages this folder's contents. Adding an `__init__.py` now would conflict with Alembic's later setup.

These two folders keep their `README.md` from Chunk B but get no `__init__.py`.

---

## Operation 4 — Create `__init__.py` files for the test tree

The `backend/tests/` folder also needs to be a package so test discovery works correctly. Create empty `__init__.py` files at:

- `backend/tests/__init__.py`
- `backend/tests/unit/__init__.py`
- `backend/tests/integration/__init__.py`
- `backend/tests/e2e/__init__.py`

---

## Operation 5 — Create `pyproject.toml` at `backend/pyproject.toml`

Create the file `backend/pyproject.toml` with this exact content:

```toml
# ============================================================================
# Lucifex — Backend Package Configuration
# ============================================================================
# This file declares the Lucifex Python package, its dependencies, dev
# dependencies, and the configuration for ruff, mypy, and pytest.
#
# Single source of truth: this file. No setup.py, no requirements.txt,
# no separate ruff/mypy config files. Everything lives here.
# ============================================================================

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# ============================================================================
# Project metadata
# ============================================================================

[project]
name = "lucifex"
description = "Autonomous content production system. Commercial Grade Apps for Personal Use."
readme = "README.md"
requires-python = ">=3.12,<3.13"
license = { text = "Proprietary" }
authors = [
    { name = "Jake" }
]
keywords = ["ai", "video", "automation", "content"]
classifiers = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: End Users/Desktop",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
]
dynamic = ["version"]

# ----------------------------------------------------------------------------
# Runtime dependencies
# ----------------------------------------------------------------------------
# These are installed in production. Keep this list lean — every dependency
# is a security and maintenance liability. Pin to compatible ranges, not
# exact versions, so security patches flow through.
# ----------------------------------------------------------------------------

dependencies = [
    # Web framework
    "fastapi>=0.115,<0.117",
    "uvicorn[standard]>=0.32,<0.36",

    # Settings and validation
    "pydantic>=2.9,<3.0",
    "pydantic-settings>=2.6,<3.0",

    # Database
    "sqlalchemy>=2.0,<3.0",
    "alembic>=1.13,<2.0",
    "asyncpg>=0.30,<0.31",
    "psycopg[binary]>=3.2,<4.0",

    # Auth and crypto
    "bcrypt>=4.2,<5.0",
    "cryptography>=43,<46",
    "python-jose[cryptography]>=3.3,<4.0",

    # Observability
    "structlog>=24.4,<26.0",
    "sentry-sdk[fastapi]>=2.18,<3.0",

    # Job queue
    "arq>=0.26,<1.0",

    # HTTP client (for provider/platform adapters)
    "httpx>=0.28,<1.0",
]

# ----------------------------------------------------------------------------
# Optional dependency groups
# ----------------------------------------------------------------------------
# Installed only when explicitly requested. The "dev" group is what you
# install locally; the "test" group is what CI installs.
# ----------------------------------------------------------------------------

[project.optional-dependencies]
dev = [
    # Code quality
    "ruff>=0.8,<1.0",
    "mypy>=1.13,<2.0",

    # Testing
    "pytest>=8.3,<9.0",
    "pytest-asyncio>=0.24,<2.0",
    "pytest-cov>=6.0,<8.0",
    "httpx>=0.28,<1.0",  # used in test client

    # Type stubs
    "types-python-jose>=3.3,<4.0",
]

test = [
    "pytest>=8.3,<9.0",
    "pytest-asyncio>=0.24,<2.0",
    "pytest-cov>=6.0,<8.0",
    "httpx>=0.28,<1.0",
]

# ============================================================================
# Hatch (build backend) configuration
# ============================================================================

[tool.hatch.version]
path = "src/lucifex/__init__.py"

[tool.hatch.build.targets.wheel]
packages = ["src/lucifex"]

# ============================================================================
# Ruff (linter + formatter) configuration
# ============================================================================
# Ruff replaces flake8, black, isort, and pyupgrade in a single fast tool.
# ============================================================================

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]
extend-exclude = ["migrations"]

[tool.ruff.lint]
# Selected rule sets:
#   E, W   — pycodestyle (PEP 8 errors and warnings)
#   F      — pyflakes (unused imports, undefined names)
#   I      — isort (import sorting)
#   B      — flake8-bugbear (likely bugs)
#   C4     — flake8-comprehensions (better list/dict comprehensions)
#   UP     — pyupgrade (modern Python idioms)
#   N      — pep8-naming
#   SIM    — flake8-simplify
#   RUF    — ruff-specific rules
select = ["E", "W", "F", "I", "B", "C4", "UP", "N", "SIM", "RUF"]
ignore = [
    "E501",  # line too long — formatter handles this
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # assert is fine in tests
"__init__.py" = ["F401"]    # unused imports are fine in __init__

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"

# ============================================================================
# Mypy (type checker) configuration
# ============================================================================

[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
no_implicit_optional = true
check_untyped_defs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_untyped_decorators = true

# Migrations are auto-generated; we don't type-check them.
[[tool.mypy.overrides]]
module = "lucifex.db.migrations.*"
ignore_errors = true

# Third-party libraries without type stubs.
[[tool.mypy.overrides]]
module = ["arq.*"]
ignore_missing_imports = true

# ============================================================================
# Pytest configuration
# ============================================================================

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "-ra",                         # show short test summary for all but passes
    "--strict-markers",            # error on unknown @pytest.mark
    "--strict-config",             # error on unknown config
    "--cov=lucifex",               # measure coverage of the lucifex package
    "--cov-report=term-missing",   # show uncovered lines in terminal
]
asyncio_mode = "auto"
markers = [
    "unit: fast isolated tests",
    "integration: tests that use real infrastructure (DB, storage)",
    "e2e: full end-to-end flows",
    "slow: tests that take longer than 1 second",
]

# ============================================================================
# Coverage configuration
# ============================================================================

[tool.coverage.run]
source = ["src/lucifex"]
omit = [
    "*/migrations/*",
    "*/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

---

## Operation 6 — Create `.python-version` at the project root

At the project root (NOT inside `backend/`), create a file named `.python-version` with exactly this content (no trailing whitespace, single line):

```
3.12
```

This file is read by tools like `pyenv`, `uv`, and IDE Python extensions to automatically select the correct Python version for this project.

---

## Operation 7 — Update `backend/README.md`

Replace the existing `backend/README.md` (created in Chunk B) with this expanded version. The change adds a "Layout" section explaining the `src/` layout and a "Local development" section with setup instructions.

```markdown
# Backend

The Lucifex backend. Python 3.12 with FastAPI. Houses the business logic, agent loop, database, providers, platforms, and background workers.

## Internal organization

| Folder | Purpose |
|--------|---------|
| `src/lucifex/api/` | HTTP endpoints. Thin transport layer. |
| `src/lucifex/core/` | Pure domain logic. Depends on nothing else. The brain of the brain. |
| `src/lucifex/agent/` | The AI agent loop, tools, and system prompts. |
| `src/lucifex/db/` | SQLAlchemy models, Alembic migrations, repositories. |
| `src/lucifex/providers/` | Adapters for AI services (LLM, video, image, TTS). |
| `src/lucifex/platforms/` | Adapters for posting platforms (TikTok, YouTube, etc.). |
| `src/lucifex/workers/` | Background job runner processes. |
| `src/lucifex/jobs/` | Job type definitions — what each background task does. |
| `src/lucifex/auth/` | Authentication, sessions, encryption primitives. |
| `src/lucifex/observability/` | Logging, metrics, error tracking, audit log writers. |
| `src/lucifex/config/` | Settings and environment variable loading. |
| `tests/` | Unit, integration, and end-to-end tests. |

## Layout

The backend uses the `src/` layout, with the importable package at `backend/src/lucifex/`. Imports across the codebase look like:

```python
from lucifex.core.clips import approve_clip
from lucifex.providers.llm.anthropic import AnthropicProvider
```

The src layout forces an editable install before imports resolve, which catches packaging bugs early and ensures tests run against the installed package the way users would.

## The dependency rule

Dependencies point inward toward `core/`. The API layer, workers, and adapters depend on `core/`. `core/` depends on nothing else. This is hexagonal architecture (also called Ports and Adapters or Clean Architecture).

## Local development

From the `backend/` directory:

```bash
# Create and activate a virtual environment (Python 3.12)
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate         # macOS/Linux

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

Common commands once installed:

| Command | Purpose |
|---------|---------|
| `ruff check .` | Lint the codebase. |
| `ruff format .` | Auto-format the codebase. |
| `mypy src` | Type-check the package. |
| `pytest` | Run all tests. |
| `pytest tests/unit` | Run unit tests only. |

## See also

- `pyproject.toml` — package metadata, dependencies, tool configuration
- `../docs/architecture.md` — full system design
- `../docs/decision_log.md` — architectural decisions
```

---

## Operation 8 — Add a new section to `.gitignore`

Append the following section to the existing `.gitignore` at the project root. The Chunk B fix already corrected the `output/*` pattern; this operation only adds new entries.

Add these lines to the end of the existing `.gitignore`, preserving everything already there:

```
# ============================================================================
# Section 8 — Python build artifacts
# ============================================================================
*.egg-info/
.eggs/
src/*.egg-info/
backend/src/*.egg-info/

# ============================================================================
# Section 9 — Tool caches added in Chunk C
# ============================================================================
.ruff_cache/
.mypy_cache/
.pytest_cache/
.coverage
htmlcov/
```

Several of these patterns may already exist in earlier sections. That is acceptable — duplicate ignore rules are harmless. Do NOT remove or reorder existing patterns. Only append.

---

## Operation 9 — Update the project root `README.md`

Append a new "Development" section to the existing root `README.md`. Do NOT replace the existing content; preserve it and add this section to the end.

Append this content:

```markdown

## Development

This project is in early scaffold. To work on the backend locally, see [`backend/README.md`](backend/README.md).

Required:
- Python 3.12 (pinned in `.python-version`)
- A virtual environment per backend setup instructions
- Editable install (`pip install -e ".[dev]"`) from the `backend/` directory

The frontend is not yet scaffolded with tooling — that comes in a later chunk.
```

---

## Operation 10 — Save this chunk document

Save this entire chunk document into the `chunks/` folder as `chunk_c_python_environment.md`.

---

## Constraints

Do not create any of the following in this chunk:

- Application code (`.py` files containing logic)
- A `requirements.txt` (dependencies live in `pyproject.toml`)
- A `setup.py` (replaced by `pyproject.toml`)
- A `.flake8`, `.mypy.ini`, `pytest.ini`, or `setup.cfg` (configuration lives in `pyproject.toml`)
- Any virtual environment (the operator creates this manually)
- Any frontend tooling (`package.json`, `tsconfig.json`, etc.)
- Any Dockerfiles
- Any `.github/workflows/` files

Do not run any of the following:

- `pip install`
- `python -m venv`
- `pyenv install`
- Any other package or version manager
- Any git commands

The only filesystem operations needed are: create folders, create files, move folders/files (Operation 1), and append to existing files (Operations 8 and 9).

---

## When you are finished

Report back with:

1. Confirmation that all subfolders moved successfully under `backend/src/lucifex/`, with their READMEs intact.
2. Confirmation that `backend/src/lucifex/__init__.py` exists with the docstring and `__version__`.
3. Confirmation that all 18 expected `__init__.py` files exist under `backend/src/lucifex/` (excluding `agent/prompts/` and `db/migrations/`).
4. Confirmation that all 4 test `__init__.py` files exist under `backend/tests/`.
5. Confirmation that `backend/pyproject.toml` exists with the full content.
6. Confirmation that `.python-version` exists at the project root with content `3.12`.
7. Confirmation that `backend/README.md` has been updated with the new layout, development, and command sections.
8. Confirmation that `.gitignore` has the appended sections 8 and 9.
9. Confirmation that root `README.md` has the appended development section.
10. Confirmation that `chunks/chunk_c_python_environment.md` exists.
11. The complete file tree of `backend/` after all operations.

Do not stage, commit, or push anything. The operator will review and run git commands manually.

---

## After Copilot finishes — operator instructions

**1. Eye-check the high-stakes files:**
- `backend/pyproject.toml` — read it top to bottom. This is the single source of truth for the entire Python build. Pay attention to: Python version requirement, dependency versions, ruff and mypy strictness levels, pytest configuration.
- `backend/src/lucifex/__init__.py` — verify the docstring and `__version__`.
- The updated `backend/README.md` — confirm the layout section makes sense.

**2. Verify the move worked:**
- `backend/api/` (and all other moved folders) should NOT exist at the old path.
- `backend/src/lucifex/api/` (and equivalents) should exist with the correct README inside.
- `backend/tests/` should still exist at its original location (not moved).

**3. Spot-check a few `__init__.py` files** to confirm they exist as zero-byte (or near-zero-byte) files where expected.

**4. Stage and commit:**

```
git add .
git commit -m "Chunk C — Python environment: src layout, pyproject.toml, package init files"
git push
```

**5. After the commit lands, optionally test the install locally** (this is not part of the chunk; it's just sanity-checking that the configuration works):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
ruff check .
mypy src
pytest
```

Each command should run without errors. `pytest` will report "no tests collected" — that's expected; we have no tests yet. `mypy src` will succeed because there's no application code to type-check yet. `ruff check .` should pass because there's no application code.

If any command fails, that's a configuration bug to fix before moving to Chunk D. Better to catch it now than after we've added real code on top of a broken foundation.

---

## What to verify before moving to Chunk D

- [ ] All folders successfully moved to `backend/src/lucifex/`.
- [ ] All required `__init__.py` files exist; none in `agent/prompts/` or `db/migrations/`.
- [ ] `backend/pyproject.toml` is well-formed (no syntax errors).
- [ ] `.python-version` exists and contains `3.12`.
- [ ] `backend/README.md` and root `README.md` have their expanded content.
- [ ] `.gitignore` retains the Chunk B fix (`output/*` not `output/`) AND has the new Sections 8 and 9 appended.
- [ ] `chunks/chunk_c_python_environment.md` exists.
- [ ] Optional: `pip install -e ".[dev]"` from `backend/` succeeds.
- [ ] `git status` is clean after commit.
- [ ] `git log` shows three commits: A, B, B-fix, B-readme-tweak, and now C. (Five commits total counting the fix and tweak — exact count depends on whether you bundled them.)

When all boxes are checked, come back and we plan Chunk D — the database scaffold (SQLAlchemy base classes, the first migration, Alembic configuration).

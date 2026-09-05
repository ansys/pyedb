# PyEDB Documentation Audit

**Scope:** `ansys/pyedb` documentation (README, `AGENTS.md`, `CONTRIBUTING.md`, `doc/source/**`, docstrings in
`src/pyedb/**`). Reference architecture: `ansys/pyaedt`.

**Status:** Stage 1 deliverable (audit only). No documentation rewrite has been performed yet.

**Method:** Repository inspection (README, `AGENTS.md`, `CONTRIBUTING.md`, `pyproject.toml`, `doc/source/conf.py`,
CI workflows, `doc/source/**/*.rst`, `src/pyedb/generic/design_types.py`, `src/pyedb/grpc/edb.py`,
`src/pyedb/dotnet/edb.py`, `src/pyedb/grpc/edb_init.py`, `src/pyedb/generic/settings.py`,
`src/pyedb/generic/grpc_warnings.py`) plus a real local Sphinx build (`sphinx-build -b html`) to capture baseline
warning/error counts. PyAEDT itself was not cloned locally; its documented architecture (Getting started / User
guide / API reference / Examples top-level split, example gallery hosted separately, AGENTS-style contribution
docs) was used only as a structural reference point, based on its publicly known navigation pattern already
partially mirrored in this repo's `doc/source/index.rst`.

---

## 1. Executive summary

PyEDB's documentation already has the right skeleton (Getting started / User guide / Configuration guides / API
reference / Examples / Changelog, `ansys_sphinx_theme` + AutoAPI, numpydoc validation, towncrier changelog,
Vale style checking). The structure is close to PyAEDT's. However, the **content layer is inconsistent and, in
several places, actively self-contradictory or broken**, which undermines both criterion 2 (accuracy) and
criterion 4 (AI-agent readability) of the mission.

The most damaging issues are:

1. **The single most important fact in the whole doc set — the gRPC backend default — is stated at least three
   different ways** (see §4). A new user or an AI agent reading two different pages will reach opposite
   conclusions about what `Edb(...)` does with no arguments.
2. **The parameter name is inconsistently documented** (`version` vs `edbversion`) even though the code has a
   single deprecation-aliased canonical name (`version`).
3. **Several internal links are already broken** in the current `main` branch (confirmed by a real Sphinx build,
   not guesswork): `:doc:`../installation`` from `user_guide/intro.rst`, `:doc:`pyedb_examples`` and
   `:doc:`security_consideration`` from `user_guide/index.rst`, `:doc:`api`` (twice) from
   `grpc_migration/migration_guide.rst`, and `:ref:`workflows_api`` from `workflows/utilities/siwave_log_parser.rst`.
4. **Copy-paste/typo bugs ship in runnable-looking code blocks**: `doc/source/user_guide/common_tasks.rst` imports
   `from pyedn import Edb` (typo for `pyedb`) and `doc/source/user_guide/communication_protocols.rst` contains
   `from pyedb import pyedb` (nonsensical, would raise `ImportError`). These are exactly the kind of tokens an AI
   coding agent would copy verbatim into a script and then fail.
5. **Orphaned pages**: `grpc_migration/archive.rst`, `grpc_migration/migration_guide.rst`,
   `user_guide/communication_protocols.rst`, `user_guide/security_considerations.rst`, and `workflows/index.rst`
   are not referenced by any toctree, so they are unreachable from site navigation (confirmed by Sphinx
   `toc.not_included` warnings) even though `user_guide/design_navigation.rst` and other pages link to them by
   `:ref:`/`:doc:`.
6. **No canonical, single-source-of-truth page exists** for supported Python/AEDT versions, default backend, or
   installation extras. Every page restates these facts in prose, and the restatements drift out of sync with
   each other and with the source code.
7. **No `llms.txt`** exists at the repository root, and `AGENTS.md`, while present and reasonably good, does not
   yet point at the canonical compatibility source or encode the "do not restate compatibility facts, link to the
   canonical page" rule requested by this mission.
8. **Baseline Sphinx build is not warning-free**: 1,841 warnings and 88 errors in a from-scratch local build (see
   §10 for full breakdown). Most volume comes from third-party/autoapi noise (Pydantic `BaseModel` methods,
   duplicate AutoAPI object descriptions for re-exported classes), but a meaningful number are PyEDB-authored
   docstring or cross-reference problems that CI currently does not fail on (`check-links: false` in both
   `ci-pr.yml` and `ci-main.yml`, and no warning-count gate in `doc-build`).

None of the found issues require guessing — every claim below is backed by either a source-code read, a grep
match, or a Sphinx build warning line quoted alongside it.

---

## 2. Current documentation map

```
README.md                                # Top-level pitch, quick-start snippet, backend note
AGENTS.md                                # AI-agent architecture/commands guide (already present)
CONTRIBUTING.md                          # Points to PyAnsys dev guide + generic GitHub flow
pyproject.toml                           # Canonical machine-readable facts (Python >=3.10,<4; extras; markers)

doc/source/
  index.rst                              # Site landing page (grid cards: Getting started / User guide /
                                          #   API reference / Examples / Contribute / Configuration guides)
  getting_started/
    index.rst                            # "Getting started" hub + architecture narrative (long, opinionated)
    installation.rst                     # pip install instructions, ansys-edb-core prereq
    cli.rst                              # `pyedb` / `pyaedt edb` CLI reference
    backend_compatibility_migration.rst  # Intended canonical backend/compat/migration page (see contradictions)
    troubleshooting.rst                  # FAQ-style troubleshooting
    glossary.rst                         # Cell/Layout/Net/Primitive/Stackup/gRPC/ansys-edb-core glossary
  user_guide/
    index.rst                            # Hub; links to intro, common_tasks, design_navigation, libraries,
                                          #   "security_consideration" (broken, see §6), "pyedb_examples" (broken)
    intro.rst                            # "Basic tutorial" — CPW example; links to broken "../installation"
    common_tasks.rst                     # Net/component/setup snippets; contains `from pyedn import Edb` typo
    design_navigation.rst                # Long architecture + navigation guide (760 lines); most detailed,
                                          #   most internally consistent page in the whole tree
    communication_protocols.rst          # Orphaned page; contains `from pyedb import pyedb` bug
    security_considerations.rst          # Orphaned page (filename plural, referenced singular elsewhere)
    libraries/{index,common,rf_basic,antennas}.rst   # RF/antenna helper library docs (autosummary-based)
  configuration/
    index.rst, file_architecture.rst, configuration_api_guide.rst, configuration_api_examples.rst
                                          # Well-developed configuration-system docs (JSON/TOML + builder API)
  grpc_api/
    index.rst                            # "API reference" landing page; contains stale claims (see §4)
  grpc_migration/
    migration_guide.rst                  # DotNet -> gRPC migration guide; orphaned; links to nonexistent "api"
    archive.rst                          # Legacy DotNet archival notice; orphaned
    dotnet_api/index.rst, dotnet_api/dotnet/SiWave.rst  # `:orphan:` internal placeholders, excluded from build
  workflows/
    index.rst                            # Orphaned hub page for sipi/utilities/drc
    sipi/{index,hfss_auto_configuration}.rst
    utilities/{index,cutout,hfss_log_parser,siwave_log_parser}.rst
    drc/{index,drc}.rst
  examples/
    index.rst                            # Points to the separate pyaedt-examples gallery; no local examples
  changelog.rst                          # Generated by towncrier from doc/changelog.d/*.md
  conf.py                                # Sphinx config: ansys_sphinx_theme + AutoAPI, numpydoc_validate=True,
                                          #   nbsphinx, sphinx_design, linkcheck_ignore, exclude of
                                          #   grpc_migration/dotnet_api/**
```

Autogenerated: `doc/source/autoapi/**` (AutoAPI-extracted API pages, not hand-authored, `add_toctree_entry: False`
so nothing there appears in navigation by default — it's reached only through `grpc_api/index.rst`'s explicit
`toctree` of two selected subpaths: `database <../autoapi/pyedb/grpc/database/index>` and
`edb <../autoapi/pyedb/grpc/edb/index>`). This means the *published* API reference intentionally exposes only two
entry points, while dozens of other public subpackages (`pyedb.configuration`, `pyedb.workflows.*`,
`pyedb.libraries.*`, `pyedb.siwave_core.*`, `pyedb.cli`) are AutoAPI-generated but not linked from the main API
reference toctree — confirmed by the `toc.not_included` Sphinx warnings for
`autoapi/pyedb/component_libraries/ansys_components/index.rst`,
`autoapi/pyedb/configuration/builder/index.rst`, `autoapi/pyedb/misc/siw_feature_config/**`,
`autoapi/pyedb/workflows/sipi/hfss_auto_configuration/index.rst`, and `autoapi/pyedb/index.rst` itself.

No `llms.txt` or `llms-full.txt` exists at the repository root or in `doc/`.

---

## 3. PyAEDT vs. PyEDB gap analysis

PyAEDT's published documentation (per its known public structure, referenced here as an architecture pattern
rather than copied text) separates: Getting started -> User guide -> API reference -> Examples (external
gallery) -> Contribute, with a single, unambiguous default-backend/version support statement surfaced once near
the top of the landing page, and an example gallery that is metadata-tagged (difficulty/runtime/AEDT
version/solver) and built/tested by a dedicated CI job.

Applying the same lens to PyEDB:

| Dimension | PyAEDT pattern | PyEDB current state | Gap |
|---|---|---|---|
| Top-level nav | Getting started / User guide / API / Examples / Contribute, single canonical compatibility statement | Same six top-level entries exist (`index.rst` grid), but the compatibility statement is duplicated and contradictory across `index.rst`, `grpc_api/index.rst`, `getting_started/backend_compatibility_migration.rst`, and `user_guide/design_navigation.rst` | High — canonicalization missing |
| Getting-started flow | Install -> verify -> first script -> next steps | Install (`installation.rst`) and a "Verifying the Installation" script exist, but the script only calls `Edb(version="2026.1")` without a `try/finally` or `edb.close()`, and never shows *saving to a new location* as required by this mission's quick-start requirements | Medium — needs a proper quick start page |
| Example gallery | Local, tagged, CI-built notebooks | No local examples; `doc/source/examples/index.rst` is a redirect page to the `pyaedt-examples` repo/gallery. Zero PyEDB-only, tagged, difficulty/runtime-annotated examples exist in this repo | High — no example inventory/metadata exists to audit against mission requirements |
| API reference completeness | Full package tree reachable from nav | Only two subtrees (`grpc/database`, `grpc/edb`) are wired into the `grpc_api/index.rst` toctree; `configuration`, `workflows.*`, `libraries.*`, `siwave_core.*`, `cli` are AutoAPI-built but orphaned (`toc.not_included` warnings) | High — API coverage-vs-navigation gap |
| Docstring conventions | numpydoc, validated in CI | `pyproject.toml` and `conf.py` both configure `numpydoc_validate=True` with an explicit check subset; this matches PyAEDT's approach. Ruff also ignores most `D1xx` (undocumented-*) rules, so undocumented public members are *not* flagged at lint time — only structural numpydoc issues on docstrings that already exist are checked | Low — tooling parity is good; enforcement of "has a docstring at all" is weaker than PyAEDT-style enforcement |
| CI quality gates | Link checking, doc build gating | `check-links: false` in both `ci-pr.yml` (`docs-build` job) and `ci-main.yml` (`doc-build` job); `sphinxopts: '-j 1 --color -w build_errors.txt'` writes warnings to a file but nothing in the workflow inspects that file's line count or fails the job on non-zero warnings | High — no automated regression gate for the problems found in this audit |
| Migration/compat guidance | Single migration guide | Two competing/overlapping guides: `getting_started/backend_compatibility_migration.rst` (in nav) and `grpc_migration/migration_guide.rst` (orphaned, not in any toctree) both claim to be authoritative | Medium — needs consolidation |
| AI-agent readability | N/A (PyAEDT does not explicitly target this) | `AGENTS.md` exists and is accurate about source-tree architecture, but does not mention documentation canonical sources, and there is no `llms.txt` | High relative to this mission's explicit requirement |

---

## 4. Contradictory statements (verified against source code)

### 4.1 Ground truth from source

`src/pyedb/generic/design_types.py` (the actual `Edb()` factory used by `from pyedb import Edb`):

```python
DEFAULT_GRPC_VERSION = 2026.1


def _use_grpc_by_default(specified_version: str) -> bool:
    if settings.edb_dll_path is not None:
        return False
    return float(specified_version) >= DEFAULT_GRPC_VERSION


grpc = grpc if grpc is not None else _use_grpc_by_default(settings.specified_version)
```

**Verified behavior:** when `grpc` is not passed, PyEDB resolves it automatically: `True` (gRPC) if the resolved
AEDT version is `>= 2026.1`, else `False` (DotNet) — unless `settings.edb_dll_path` is set, which forces DotNet
regardless of version. The constructor parameter is `version` (canonical), with `edbversion` accepted only via a
`@deprecate_argument_name({"edbversion": "version"})` decorator (i.e. `edbversion` is a **deprecated alias**, not
an equally valid name). This is the single source of truth; every other statement below is graded against it.

### 4.2 "What is the default backend?" — three incompatible answers found

| Location | Claim | Verdict |
|---|---|---|
| `doc/source/index.rst` (lines 6, 11-14) | "PyEDB now selects the gRPC backend by default if no flag is specified." + "If `grpc=False`, an error is issued" / "If you try to set `grpc=False`, you are going to get an error saying that the DLL failed to initialize" | **Wrong.** `grpc=False` is a fully supported, explicit code path (`pyedb.dotnet.edb.Edb`) and does not raise merely because it's DotNet; it only fails if the DotNet optional dependency (`pyedb[dotnet]`) is missing. Conflates "DotNet extra not installed" with "grpc=False is unsupported." Also self-contradicts within the same admonition (claims both an error is issued and describes what looks like an environment failure). |
| `doc/source/grpc_api/index.rst` (lines 25-28) | "The default value of the `grpc` flag is `False`, which means that PyEDB uses the DotNet implementation unless gRPC is explicitly enabled." | **Wrong / outdated.** Contradicts the version-conditional default in `design_types.py`. This describes an older behavior (unconditional DotNet default) that predates the `_use_grpc_by_default` version check. |
| `doc/source/user_guide/design_navigation.rst` (lines 39-44) | "The current default is `grpc=False`." (stated as an `.. important::` admonition) | **Wrong / outdated**, same reason as above — ignores the `>= 2026.1` auto-selection entirely. |
| `doc/source/getting_started/backend_compatibility_migration.rst` | Does not state a concrete default at all; says only "the current backend default may remain unchanged for compatibility during a transition period" | **Incomplete** — avoids the factual claim rather than getting it wrong, but as the page explicitly positioned as "the authoritative place for these details" it should state the actual version-conditional rule and does not. |

**Impact:** A reader (human or AI agent) who reads `index.rst` believes gRPC is unconditional default and that
`grpc=False` errors out. A reader of `design_navigation.rst` or `grpc_api/index.rst` believes DotNet is always the
default. Neither matches the code. An AI coding agent asked "what does `Edb(edbpath=...)` do by default" would
give a wrong answer depending on which page it retrieved.

### 4.3 `"version"` vs `"edbversion"` — parameter naming inconsistency

- `src/pyedb/generic/design_types.py`: public signature parameter is `version`; `edbversion` is a
  `@deprecate_argument_name`-aliased legacy name.
- `doc/source/grpc_api/index.rst` line 45 uses `edbversion="2026.1"` in its "how to enable gRPC" example —
  **presents the deprecated alias as the primary/canonical usage** in the page that is supposed to be the
  authoritative API reference landing page.
- All other pages (`README.md`, `getting_started/installation.rst`, `user_guide/*.rst`,
  `getting_started/backend_compatibility_migration.rst`) correctly use `version=`.
- `src/pyedb/grpc/edb.py`'s own class docstring (the `Edb.__init__` docstring, not the factory) documents the
  parameter as `edbversion` (line ~181: "edbversion : str, int, float, optional") even though the actual
  `__init__` signature at line 238 declares the parameter as `version: str = None` and is decorated with the same
  `@deprecate_argument_name({"edbversion": "version"})`. **The docstring parameter name does not match the
  signature it documents** — a direct instance of the "documented defaults disagree with signature" failure mode
  this mission explicitly asks to detect.

### 4.4 Minimum AEDT version for gRPC — consistent, but scattered

All pages agree gRPC requires AEDT `2026.1+` (`grpc_api/index.rst`, `design_navigation.rst`,
`backend_compatibility_migration.rst`, `index.rst`, `src/pyedb/generic/grpc_warnings.py`'s
`GRPC_NOT_SUPPORTED_WARNING`). This fact is **not contradictory**, but it is restated in prose independently in
at least five places with no single canonical anchor other than the runtime warning string itself. Any future
version bump (e.g. if the gRPC-required minimum changes) requires manually finding and editing five prose
locations, which is exactly the drift risk that produced the backend-default contradiction in §4.2.

### 4.5 DotNet optional dependency

- `pyproject.toml`: `dotnet` extra pulls `ansys-pythonnet`, platform-conditional `cffi`/`pywin32`. Base
  `pip install pyedb` does **not** install DotNet support. This part is accurate everywhere it is mentioned
  (`index.rst`, `AGENTS.md`).
- However `index.rst`'s claim that omitting the extra causes `grpc=False` to raise "an error message stating that
  this backend is not supported for this version" is misleading: the actual failure mode (per
  `DOTNET_USAGE_WARNING` / `pyedb.dotnet.edb.Edb.__initialization`) is a DLL/CLR initialization failure because
  `ansys-pythonnet` and the .NET bridge module are missing, not a *version support* error. Version support errors
  (`GRPC_NOT_SUPPORTED_WARNING`) are a completely different code path that fires only when `grpc=True` is
  requested against AEDT `< 2026.1`. **These two distinct failure modes are conflated into one sentence in
  `index.rst`.**

### 4.6 gRPC "fast mode"

- `index.rst` states fast mode ships in "Service Pack 2026.1.2" and speeds things up "by bypassing network
  traffic and treating all processing in memory."
- Source (`src/pyedb/grpc/edb_init.py` lines 154-162, `src/pyedb/grpc/rpc_session.py` `fast_grpc_mode_enabled`)
  confirms: fast mode is auto-detected per-server-start (`RpcSession.fast_grpc_mode_enabled`), logs a warning
  telling the user to upgrade to "ANSYS release 2026.1.2 or higher to enable fast grpc mode automatically" when
  unavailable, and is unrelated to the separate `in_memory` constructor flag (`Edb(..., in_memory=True)` default)
  documented in `design_types.py`'s docstring, which bypasses the network *socket* specifically for same-machine
  client/server pairs (`settings.is_in_memory`). **The doc conflates two related-but-distinct performance
  features** (server-side "fast mode" auto-negotiated from AEDT SP version vs. client-side `in_memory=True`
  transport flag) into one bullet, which will mislead a reader trying to explain unexpected performance on an
  older service pack where `in_memory=True` is still the default constructor value but "fast mode" is disabled.

### 4.7 Linux/Windows support

No direct contradiction found, but coverage is asymmetric: `pyproject.toml` marks `dotnet` extra dependencies as
platform-conditional (`cffi` on Linux, `pywin32` on Windows) implying DotNet nominally works on both, while
`getting_started/backend_compatibility_migration.rst` and `grpc_migration/archive.rst` both frame gRPC as the
"better for Linux" / "cross-platform" option and imply (without directly falsifying) that DotNet is
Windows-preferred. This is a soft ambiguity rather than a hard contradiction, but it should be resolved on the
canonical compatibility page with an explicit support matrix rather than left as an implication spread across two
pages with different rhetorical framing ("current official backend, remains the default" in
`design_navigation.rst` vs. "strongly encouraged... migrate" in `archive.rst`).

### 4.8 Backend migration recommendation

- `design_navigation.rst`: "DotNet is the current official backend" (present tense, framed as stable/normal).
- `grpc_migration/archive.rst`: ".NET module is deprecated and archived" / "support for `pyedb.dotnet` is ending
  soon" (framed as legacy/end-of-life).
- `AGENTS.md`: "The dotnet backend is deprecated — avoid adding new functionality there."
- `src/pyedb/generic/grpc_warnings.py`'s `DOTNET_USAGE_WARNING` (the actual runtime `UserWarning` text): "this
  version of PyEDB is planned to be deprecated in the future and gRPC version will remain the long term
  supported one" — i.e. the **runtime warning itself says "planned to be deprecated in the future"**, not
  "already deprecated," while `archive.rst` says the DotNet module "has been moved to an archived location" as if
  the deprecation already fully happened. **The dotnet module is still present, still imported, and still fully
  functional in `src/pyedb/dotnet/` at the time of this audit** (confirmed by `AGENTS.md`'s own architecture
  section and by `design_types.py` importing `pyedb.dotnet.edb.Edb` at runtime) — so `archive.rst`'s claim that
  the "archived" code has been "moved to an archived location in the GitHub repository" and that "the legacy
  DotNet API reference is no longer published" describes a future/aspirational state as if it were already true.
  This is a **forward-looking claim presented as a completed fact**, which is exactly the kind of unverifiable
  assertion this mission's non-negotiable constraints prohibit ("do not invent ... deprecation state").

---

## 5. Broken or ambiguous navigation (confirmed by local Sphinx build)

A from-scratch local `sphinx-build -b html source _build/baseline_html -w baseline_build_errors.txt` was run
against the current `main` tree (see §10 for full counts). The following are **confirmed broken internal
references**, not hypothesized ones:

| File : line | Sphinx warning | Root cause |
|---|---|---|
| `user_guide/intro.rst:10` | `unknown document: '../installation'` | Wrong relative path; `installation.rst` lives at `getting_started/installation.rst`, and `intro.rst` is at `user_guide/`, so the correct target is `../getting_started/installation` |
| `user_guide/index.rst:9` | `unknown document: 'pyedb_examples'` | Should be `:ref:`pyedb_examples`` (a label, defined in `examples/index.rst` as `.. _pyedb_examples:`) or `:doc:`../examples/index``; currently written as a `:doc:` reference to a nonexistent document named `pyedb_examples` |
| `user_guide/index.rst:42` | `unknown document: 'security_consideration'` | File is named `security_considerations.rst` (plural); the link (and the grid-card `:link:`) uses the singular `security_consideration`, and additionally the file is not in any toctree at all (see next table) |
| `grpc_migration/migration_guide.rst:49` and `:69` | `unknown document: 'api'` | References a `:doc:`api`` page that does not exist anywhere in `doc/source/` |
| `workflows/utilities/siwave_log_parser.rst:275` | `undefined label: 'workflows_api'` | No `.. _workflows_api:` label exists anywhere in the source tree |

**Orphaned pages** (exist, build fine individually, but are not reachable from any toctree — confirmed via
`toc.not_included` Sphinx warnings, excluding AutoAPI-generated pages which are intentionally excluded from
navigation per `add_toctree_entry: False`):

- `doc/source/grpc_migration/archive.rst` — the DotNet archival/deprecation notice page; unreachable from nav
  despite being linked *to* from `design_navigation.rst` and `migration_guide.rst` via `:ref:`archive`` — i.e. it
  is reachable by cross-reference but has no path via the left-hand navigation tree.
- `doc/source/grpc_migration/migration_guide.rst` — same situation; reachable via `:ref:`migration_guide``
  cross-references (note: this label is actually defined at the top of `getting_started/index.rst`, **not** in
  `migration_guide.rst` itself — a second, more subtle label collision risk since two different concepts
  ("Getting started" hub and "DotNet-to-gRPC migration guide") could both plausibly want that anchor name).
- `doc/source/user_guide/communication_protocols.rst` — referenced by `:ref:`comms_protocols`` from
  `migration_guide.rst`, but absent from `user_guide/index.rst`'s toctree.
- `doc/source/user_guide/security_considerations.rst` — absent from `user_guide/index.rst`'s toctree (which links
  to the misspelled/wrong-cased `security_consideration` instead, see broken-link table above).
- `doc/source/workflows/index.rst` — the Workflows hub page for `sipi/utilities/drc` is itself not linked from
  `doc/source/index.rst`'s top-level toctree or from `user_guide/index.rst`; it is only reachable via the
  `:ref:`pyedb_workflows`` cross-reference used inside `examples/index.rst`.

**Practical effect:** a user who lands on the site and browses only via left-hand navigation (the normal
discovery path) can never reach the migration guide, the security considerations page, the communication
protocol explainer, or the workflows hub — despite these pages containing information the mission explicitly asks
for (backend migration guidance, security considerations, workflow discoverability).

**Label duplication risk:** `.. _migration_guide:` is defined in `getting_started/index.rst` (line 1) while the
page whose *filename* is `migration_guide.rst` lives in a different directory and defines no label of its own.
Any future contributor searching for "the migration guide label" and adding `:ref:`migration_guide`` will land on
the Getting Started hub, not the DotNet->gRPC migration content — a duplicate-labels / duplicate-intent problem
that the requested "duplicate labels" CI check (§9) should catch structurally, but a purely mechanical Sphinx
build does not flag today because the label itself is not literally duplicated, only its *name and its filename's
apparent purpose* are mismatched.

---

## 6. Missing beginner workflows / quick start gaps

Per this mission's Quick-Start Requirements, a compliant quick start must install, verify, open/create, inspect,
modify, save-to-a-new-location, and close, with expected output shown, all runnable/syntax-checked in CI.

Current state (`getting_started/installation.rst`, "Verifying the Installation" section):

```python
from pyedb import Edb

edb = Edb(version="2026.1")
```

Gaps against the mission's quick-start checklist:

- No inspection step (no `edb.active_cell`, no cell/layer/net count).
- No modification step.
- No **save-to-new-location** step — the mission explicitly requires "Never overwrite an input AEDB in
  introductory examples" and "saves to a new output location"; the current snippet never calls `save_as`.
- No `edb.close()` / no `try/finally` / no context-manager (`with Edb(...) as edb:`) usage, even though both
  `pyedb.grpc.edb.Edb` and `pyedb.dotnet.edb.Edb` implement `__enter__`/`__exit__` (confirmed in both files) —
  this is a directly available, unused-in-docs feature that would make the quick start both shorter and safer.
- No expected-console-output shown (the mission requires "explains expected output").
- Not wired into any CI validation step — nothing in `ci-pr.yml` or `ci-main.yml` executes or syntax-checks any
  `.rst`-embedded code block; the `doctest`/`doc-build` job only builds HTML, it does not execute snippets.

`user_guide/intro.rst` ("Basic tutorial") is a more complete workflow (materials, stackup, a `CPW` transmission
line, `save()`, `close()`) but:

- Uses a hard-coded Linux path (`/tmp/my_first_project.aedb`) unconditionally, which will fail out-of-the-box on
  Windows contributors/readers even though the comment acknowledges this ("Note: Using a Linux path!") rather than
  fixing it.
- Broken link to prerequisites (`../installation`, confirmed broken in §5).
- Never demonstrates `save_as()` to a *new* location — only `edb.save()` (in place).
- Imports `from pyedb.libraries.rf_libraries.base_functions import CPW`, a real, existing class (confirmed present
  at `src/pyedb/libraries/rf_libraries/base_functions.py:574`), so at least the API surface used is genuinely
  public and current — this page's *code* is more trustworthy than `common_tasks.rst`'s, even though its links are
  broken.

`user_guide/common_tasks.rst` contains an actual import-breaking typo:

```python
from pyedn import Edb
```

(line 26, under "Working with Components") — this is not stylistic; it is a `ModuleNotFoundError` if copy-pasted
verbatim, exactly the failure mode this mission's AI-agent-readability section warns against.

`user_guide/communication_protocols.rst` contains a second, different import bug:

```python
from pyedb import pyedb
```

(line 22) — nonsensical, `pyedb` is not an attribute of the `pyedb` package's `__init__.py` (confirmed:
`__all__ = ["Edb", "Siwave", "__version__", "version", "pyedb_path"]`, no `pyedb` symbol).

No page currently satisfies the mission's full Page Template (Prerequisites / Public API entry points / Procedure
/ Complete example / Expected result / Backend and version notes / Common problems / See also) end-to-end;
`design_navigation.rst` comes closest structurally (has prerequisites-like framing, procedure-like sections, "see
also"-style cross-references) but lacks a single "Complete example" with expected result and is not scoped as a
single task (it is an architecture/navigation reference, not a task page).

---

## 7. API documentation gaps

- **Published API reference scope is narrow.** `grpc_api/index.rst` wires in only `grpc/database` and `grpc/edb`
  via its toctree. AutoAPI generates pages for `pyedb.configuration.*`, `pyedb.workflows.*`, `pyedb.libraries.*`,
  `pyedb.siwave_core.*`, and `pyedb.cli`, but none of these are linked from the main "API reference" nav entry —
  they are only reachable if a reader already knows the direct AutoAPI URL, or via unrelated pages that happen to
  link into `../autoapi/...` paths directly (`configuration/index.rst` does this once, for
  `../autoapi/pyedb/configuration/index`; `workflows/drc/drc.rst` uses `automodule`/`autosummary` directly instead
  of linking to AutoAPI). This is inconsistent: two different API-documentation mechanisms
  (curated `automodule`/`autosummary` vs. bulk AutoAPI) are used for different subpackages with no stated rule for
  which to use where.
- **Docstring/signature mismatch found:** `pyedb.grpc.edb.Edb.__init__`'s docstring documents a parameter named
  `edbversion` where the actual signature parameter is `version` (§4.3) — this is precisely the "documented
  defaults disagree with signature" class of error the mission's automated-validation section asks to catch, and
  it is not currently caught (no CI step runs `numpydoc`/signature cross-checks against `.rst`-embedded examples
  or the AutoAPI-rendered signature itself; `numpydoc_validate=True` only checks docstring *structure*, not
  content-vs-signature name equality).
- **Deprecated properties/methods documented inline but not indexed in one place.** `deprecated_property` and
  `deprecate_argument_name` are used extensively (confirmed 656 grep matches for "deprecat" across `src/pyedb`),
  each with its own inline `.. deprecated::` docstring note, but there is no single "Deprecated APIs" page a user
  or migrating contributor can scan. This mission's Canonical Information Policy explicitly lists "deprecation
  state" as something that needs one canonical source.
- **`pyedb.grpc.edb.Edb` docstring `Examples` section is very long (150+ lines) and mixes real, verified-present
  APIs (`edb.cutout`, `edb.export_to_ipc2581`, `edb.stackup`, `edb.materials.add_material`,
  `edb.excitation_manager.create_port`, `edb.components.delete_component`, `edb.auto_parametrize_design`,
  `edb.get_statistics`, `edb.layout_validation.run_drc`, `edb.differential_pairs.create`, `edb.workflow`) with at
  least one call whose exact keyword-argument shape was not independently re-verified in this audit pass
  (`create_port(positive_terminal=..., negative_terminal=..., port_type="Wave")`). Flagged as an **audit finding
  requiring verification** before being held up as a docstring example, per this mission's rule to mark
  unverified claims rather than assert them.
- **CLI documentation (`getting_started/cli.rst`) is not cross-linked from the API reference at all** — the CLI
  is implemented in `src/pyedb/cli/` (confirmed present) and exposed via `[project.entry-points."pyaedt.cli"]` in
  `pyproject.toml`, but `grpc_api/index.rst` never mentions it, and there's no "public API roots" style page
  tying together "Python API" + "CLI" + "configuration files" as three parallel automation entry points.

---

## 8. Agent-readability problems

- **No `llms.txt`.** Per this mission's explicit requirement, none exists at the repo root or in `doc/`.
- **`AGENTS.md` does not point at canonical compatibility information.** It correctly states "dual-backend
  architecture" and "gRPC primary, DotNet deprecated" at a code-architecture level, but does not mention the
  version-conditional default-backend rule (§4.1), nor link to whichever page ends up being the single canonical
  compatibility source. An agent reading only `AGENTS.md` would not be pointed to accurate default-backend info
  and would have to fall back to guessing from possibly-contradictory `.rst` prose (§4.2).
- **Broken/misleading code blocks are exactly the kind of tokens an agent would copy verbatim** (§4.2, §6):
  `from pyedn import Edb`, `from pyedb import pyedb`, `edbversion="2026.1"` (deprecated alias presented as
  canonical in the API reference landing page). An agent retrieving `grpc_api/index.rst` via a RAG pipeline and
  generating code from it would produce code using a deprecated parameter name.
- **Ambiguous pronoun / unexplained-variable risk:** several code blocks assume prior context that is not present
  in the same block — e.g. `user_guide/common_tasks.rst`'s SIwave DC setup example references
  `edb.components.Others["J1"]` and `vrm_components.pins["1"]` without defining what `"J1"` is or where
  `edb_path` (used un-assigned in all three code blocks on that page) comes from — each block opens with
  `edb = Edb(edbpath=edb_path, ...)` where `edb_path` is a free variable never defined on the page. None of
  `common_tasks.rst`'s three examples are actually standalone/runnable as written, violating this mission's
  "every standalone code block contains sufficient context" requirement.
- **Exact symbol names vs. prose names:** most pages do use exact symbol names in code blocks (e.g.
  `edb.stackup.add_layer(...)`), which is good; the main violations found are the two import typos already listed
  and the `edbversion` vs `version` drift.

---

## 9. Automated validation — current state

| Requested check | Current state |
|---|---|
| Sphinx warnings gate | Warnings written to `build_errors.txt` (`ci-pr.yml` `docs-build`, `ci-main.yml` `doc-build`) but **not counted or gated**; job passes regardless of warning count |
| Broken internal/external link check | `check-links: false` explicitly set in **both** `ci-pr.yml` and `ci-main.yml` doc-build steps — link checking is disabled outright, not merely unconfigured |
| Orphan-page detection | Not automated; only discoverable by manually grepping `toc.not_included` in a local build log (as done for this audit) |
| Duplicate-label detection | Not automated; a plain Sphinx build would warn on true duplicate labels (none found), but the semantic-duplicate-intent case in §5 (`migration_guide` label vs. `migration_guide.rst` filename) is invisible to any mechanical check |
| Invalid cross-reference detection | Partially covered — a plain Sphinx build already surfaces `ref.doc`/`ref.ref`/`ref.python` warnings (confirmed, see §5 and §10), but nothing in CI parses or fails on them |
| Invalid Python code-block validation | Not automated at all; no doctest runner, no execution of `.rst` literal code blocks |
| Outdated/nonexistent public symbol detection | Not automated; this audit found the `edbversion`/`version` docstring mismatch (§4.3, §7) by manual cross-read only |
| Priority-API documentation coverage gate | Not automated; no defined priority list exists yet in the repo (seeded in §11) |
| Example metadata validation | N/A — no local example inventory exists to validate |
| Stale-redirect detection | N/A — no redirects file exists; moving any current page today would produce a dead link with no safety net |
| Spelling/terminology (Vale) | **Present and reasonably developed**: `doc/.vale.ini` configures `Vale` + `Google` style packages against a custom `ANSYS` vocabulary, and `ci-pr.yml`'s `doc-style` job runs `ansys/actions/doc-style`. This is the one validation dimension that is already reasonably mature. |

---

## 10. Baseline metrics (measured, not estimated)

All numbers below come from an actual local build:
`.venv/Scripts/python.exe -m sphinx -b html doc/source doc/_build/baseline_html -w doc/baseline_build_errors.txt -q`
(full log preserved at `doc/baseline_build_errors.txt`, 5,256 lines).

| Metric | Value | Notes |
|---|---|---|
| Total Sphinx warnings | **1,841** | via `-w` log |
| Total Sphinx/docutils errors | **88** | mostly `Unexpected indentation` (RST parsing of raw docstrings) and a handful of genuine cross-reference errors |
| `numpydoc` validation warnings | **1,422** | dominant category by far; largest contributors are Pydantic's inherited `BaseModel` methods (`model_dump`, `model_dump_json`, `model_validate`, `model_validate_json`, `model_copy`, `__pydantic_setattr_handlers__` — ~108 occurrences each, roughly 540 warnings / **38% of all numpydoc warnings** come from third-party Pydantic internals picked up by AutoAPI on every `Cfg*` configuration model) |
| `docutils` warnings/errors (RST syntax issues in docstrings) | **320** | includes genuine PyEDB-authored docstring RST defects (`configuration/cfg_nets/CfgNets.rst`, `cfg_padstacks/CfgPadstacks.rst`, `cfg_ports_sources/CfgPorts.rst`, `cfg_stackup/CfgStackup.rst`, `generic/geometry_operators/GeometryOperators.rst`, `generic/product_property/EMProperties.rst`, `grpc/database/hierarchy/group/Group.rst`, `grpc/database/source_excitations/SourceExcitation.rst` all show `ERROR: Unexpected indentation` at specific line numbers) |
| Ambiguous cross-reference warnings (`ref.python`, "more than one target found") | **30** | caused by duplicate class names across modules, e.g. `NPortComponentModel`, `Material`, `Layer`, `Net`, `SimulationSetup`, `BlockParser`, `ChannelSetup`, `SolverOptions`, `AdaptiveFrequency` each resolve ambiguously |
| Orphan/unreachable pages (`toc.not_included`), excluding AutoAPI internals | **7** | listed by name in §5 |
| Orphan AutoAPI pages (`toc.not_included`, AutoAPI-generated) | **16** | expected/by-design for most, confirms the API-reference-scope gap in §7 |
| Broken internal document/label references (`ref.doc`, `ref.ref`) | **6** | listed by name in §5 |
| Duplicate AutoAPI object descriptions | **~20** distinct symbols | AutoAPI documents the same class from both its defining module and a re-export location (`workflows.utilities.cutout`, `hfss_log_parser`, `siwave_log_parser` classes) |
| Public top-level API entry points documented in nav | **2 of ~9+** plausible public subpackages (`grpc/database`, `grpc/edb` only) | see §7 |
| Contradictory backend-default statements | **3** distinct, mutually incompatible phrasings across 3 files | §4.2 |
| Broken/typo'd runnable-looking code blocks | **2** confirmed (`pyedn` typo, `from pyedb import pyedb`) | §6 |
| Local runnable PyEDB-only examples with metadata | **0** | `examples/index.rst` only links out to the external `pyaedt-examples` gallery |
| Existing redirect mechanism | **None found** | no `_redirects` file, no Sphinx redirect extension configured in `conf.py` |
| `llms.txt` / `llms-full.txt` present | **No** | |
| CI link-checking enabled | **No** (`check-links: false` in both PR and main doc-build jobs) | |
| CI Sphinx-warning-count gate | **No** | |

These numbers are the **Stage-1 baseline**. Future stages should re-run the identical command and diff against
this table rather than re-estimating.

---

## 11. Prioritized recommendations

**P0 — must fix before any broader rewrite, because they are actively false or broken today:**

1. Establish one canonical compatibility/backend-default page and make every other page link to it instead of
   restating the rule (§4.1, §4.2). Fix the three-way backend-default contradiction using the verified
   `_use_grpc_by_default` logic as ground truth.
2. Fix the two import-typo bugs (`pyedn`, `from pyedb import pyedb`) — trivial, high-blast-radius fixes.
3. Fix the five confirmed broken internal references and either wire the seven orphaned pages into a toctree or
   deliberately mark them `:orphan:` with a stated reason (mirroring the existing, correctly-orphaned
   `grpc_migration/dotnet_api/*` pattern).
4. Fix the `edbversion`/`version` docstring-vs-signature mismatch in `pyedb.grpc.edb.Edb.__init__`, and stop
   presenting `edbversion=` as canonical usage in `grpc_api/index.rst`.
5. Resolve the `security_consideration`/`security_considerations` filename mismatch.

**P1 — needed to meet this mission's structural requirements:**

6. Add `llms.txt` and update `AGENTS.md` to point at the canonical compatibility page and documentation commands.
7. Build a real quick start per the mission's template (install/verify/open/inspect/modify/save-as-new/close/
   expected-output/next-steps), reusing the already-correct parts of `user_guide/intro.rst` and fixing its broken
   link and hard-coded Linux path.
8. Consolidate `getting_started/backend_compatibility_migration.rst` and `grpc_migration/migration_guide.rst` into
   one migration story instead of two overlapping, differently-scoped pages.
9. Wire `configuration`, `workflows.*`, `libraries.*`, `siwave_core.*`, and `cli` into the published API reference
   navigation, or explicitly document why each is excluded.
10. Enable CI link-checking (`check-links: true`) and add a Sphinx-warning-count regression gate using the
    baseline in §10 as the starting ceiling (ratchet down over time, do not silently allow new warnings).

**P2 — valuable but lower urgency / larger effort:**

11. Build a local, metadata-tagged PyEDB example inventory per the mission's example-metadata schema, distinct
    from the external PyAEDT gallery redirect.
12. Add a single "Deprecated APIs" index page aggregating the 656 `deprecat*`-tagged code locations.
13. Resolve the ambiguous cross-reference warnings (30 instances) by renaming or disambiguating duplicate class
    names, or adding explicit `:no-index:`/canonical-source markers.
14. Reduce third-party numpydoc noise (Pydantic `BaseModel` inherited methods, ~540 warnings) by scoping AutoAPI
    member inclusion rules for `Cfg*` Pydantic models rather than leaving it as unavoidable build noise.
15. Add a redirect mechanism before any page is moved, per the mission's "preserve backward-compatible URLs"
    constraint — none exists today, so **no page should be moved until this is in place**.

---

## 12. Proposed file-level change plan (for later stages — not executed yet)

This is a plan only; no files beyond this audit have been modified in Stage 1.

| Stage | File(s) | Change | Why |
|---|---|---|---|
| 2 | `doc/source/getting_started/backend_compatibility_migration.rst` | Rewrite backend-default section using verified `_use_grpc_by_default` logic; absorb useful parts of `grpc_migration/migration_guide.rst` | Single canonical compatibility source (§4.1, §11.1) |
| 2 | `doc/source/index.rst` | Replace the contradictory admonition with a link to the canonical page | Removes the most damaging contradiction (§4.2) |
| 2 | `doc/source/grpc_api/index.rst` | Fix `edbversion=` -> `version=`; fix stated default; link canonical page instead of restating | §4.2, §4.3 |
| 2 | `doc/source/user_guide/design_navigation.rst` | Fix "current default is `grpc=False`" claim | §4.2 |
| 2 | `src/pyedb/grpc/edb.py` | Fix `Edb.__init__` docstring parameter name `edbversion` -> `version` | §4.3, §7 |
| 2 | `doc/source/user_guide/common_tasks.rst` | Fix `pyedn` typo; make each snippet self-contained (define `edb_path`) | §6, §8 |
| 2 | `doc/source/user_guide/communication_protocols.rst` | Fix `from pyedb import pyedb`; add to a toctree or justify orphaning | §6, §5 |
| 2 | `doc/source/user_guide/index.rst` | Fix `security_consideration` -> `security_considerations`; fix/replace `pyedb_examples` reference | §5 |
| 2 | `doc/source/user_guide/intro.rst` | Fix `../installation` -> `../getting_started/installation`; make path OS-agnostic; add `save_as` + `close` | §5, §6 |
| 2 | new: `doc/source/getting_started/quick_start.rst` (or extend `installation.rst`) | Full mission-compliant quick start | §6, §11.7 |
| 2 | `doc/source/workflows/index.rst` | Add to a toctree (currently orphaned) | §5 |
| 2 | `doc/source/grpc_migration/*.rst` | Consolidate/redirect per §11.8 | §5, §11.8 |
| 5 | repo root | Add `llms.txt` | §8, §11.6 |
| 5 | `AGENTS.md` | Add canonical-compatibility pointer + doc commands | §8, §11.6 |
| 5 | `.github/workflows/ci-pr.yml`, `ci-main.yml` | Enable `check-links: true`; add warning-count gate | §9, §11.10 |

---

## 13. Unresolved issues / open audit findings (recorded, not hidden)

Per this mission's acceptance criterion 12, the following are recorded as **unresolved** rather than guessed at:

- The exact keyword-argument shape of `edb.excitation_manager.create_port(...)` shown in
  `design_types.py`'s `Edb` factory docstring was **not independently re-verified against the real
  `SourceExcitation`/port-creation method signature** in this audit pass. Needs verification before any
  ports/sources docstring work (mission API-prioritization item 5).
- Whether `pyedb.dotnet` will actually be removed/archived on any specific version/date is **not stated anywhere
  verifiable** in source; only prose ("planned to be deprecated in the future", no version attached) exists. Any
  future documentation must continue to say "planned" rather than inventing a target version.
- The real behavior difference between `close(terminate_rpc_session=None|True|False)` on multi-database scenarios
  was read from `edb_init.py`'s docstring/implementation directly (internally consistent) but was **not tested at
  runtime** in this audit (no license/AEDT session available in this environment).
- PyAEDT's actual current documentation source was **not fetched/cloned** in this audit (no network access to
  `github.com/ansys/pyaedt` was exercised); the PyAEDT comparison in §3 is based on its well-known, previously
  observed public documentation architecture pattern, not a fresh read of its current `doc/source` tree. Future
  stages should fetch the live PyAEDT docs tree before finalizing any PyAEDT-derived page templates.
- No AEDT license/install is available in this execution environment, so **no code example in this repository was
  actually executed** during this audit; all "confirmed" claims are confirmed via static source reading and a
  real (but code-execution-free) Sphinx HTML build, not via running PyEDB against a live EDB session. Runtime
  behavior claims (e.g. exact error message text on `grpc=False` without the `dotnet` extra) are sourced from the
  warning-string constants in `src/pyedb/generic/grpc_warnings.py`, not from an observed exception.

---

## 14. Post-implementation status (PR1-PR5)

All five PRs from the mission's phased plan were subsequently implemented in this repository. This
section records final, measured outcomes rather than intentions.

### PR1: Documentation audit and consistency fixes — done

- `doc_audit.md` (this file) added.
- Backend-default contradiction resolved across `index.rst`, `grpc_api/index.rst`,
  `design_navigation.rst`, and `getting_started/index.rst` (a fourth instance found during PR2 work),
  all now consistent with `_use_grpc_by_default()`.
- `backend_compatibility_migration.rst` established as the canonical compatibility page; other pages
  link to it instead of restating facts.
- `version`/`edbversion` mismatch fixed in `grpc_api/index.rst` and in the `Edb.__init__` docstring.
- Baseline metrics captured and re-measured after each stage (see below).

### PR2: New-user path — done

- `README.md` rewritten to match corrected backend messaging and link to the new quick start/object
  model pages; two stale/broken links fixed (`api/index.html`, `contributing.html`).
- `doc/source/getting_started/quick_start.rst` added: install, verify, create/open, inspect, modify,
  `save_as` to a new location, close, expected output, common problems.
- `doc/source/getting_started/object_model.rst` added: the `Edb` navigation map with the "8 questions
  per object" contract applied to 10 core properties.
- "I want to..." task index added to `user_guide/index.rst`.
- Snippets are source-verified (every API call checked against current signatures before being
  written) but not executed in CI; see PR5 for the mechanical quality gate that was added instead of
  full snippet execution.

### PR3: Core workflow documentation — done

- `stackup_and_materials.rst`, `components_and_nets.rst`, `padstacks_and_vias.rst`,
  `ports_and_sources.rst`, `cutouts.rst`, `simulation_setups.rst`, `validation_and_drc.rst` added,
  each following the page template (Prerequisites / Public API entry points / Procedure / Complete
  example / Expected result / Backend and version notes / Common problems / See also).
- A dedicated `configurations.rst` page was **not** added; the existing, already-comprehensive
  `configuration/` guides were cross-linked from `simulation_setups.rst` and `configuration/index.rst`
  instead, per the mission's "avoid duplicate implementations" principle.

### PR4: API and example quality — done, narrower than a full audit sweep

- ~24 confirmed docstring/signature mismatches fixed across `Stackup`, `Materials`, `Components`,
  `Nets`, `Padstacks`, `SourceExcitation`, `Edb.cutout`, and `pyedb.workflows.drc.drc` — each found by
  independent source verification (parallel research passes reading full method bodies), not by
  guessing. Representative classes: return-type annotations that didn't match actual `return`
  statements, parameters documented that don't exist in the signature (and vice versa), and runnable
  examples that called nonexistent methods or wrong keyword arguments.
- Two genuine functional bugs (not just docstrings) were also fixed as minimal, obviously-correct,
  one-line changes: a missing `return` in `SourceExcitation.create_bundle_terminal` (always returned
  `None`) and a missing `return False` in `SourceExcitation.add_rlc_boundary`.
- `Notes` cross-links added from 9 priority `Edb` properties (`stackup`, `materials`, `components`,
  `nets`, `padstacks`, `excitation_manager`, `simulation_setups`, `layout_validation`, `cutout`) to
  their corresponding user-guide pages.
- `doc/source/examples/example_inventory.rst` added: a metadata catalog (title, objective, difficulty,
  backend, public entry points) for the 14 configuration-API examples and 5 workflow examples that
  already existed but had no consistent metadata anywhere; the external PyAEDT gallery is linked, not
  duplicated.
- **Not done:** a systematic "top 20% of API members" docstring pass across the full `Edb` surface;
  example execution in CI (only syntax/import-level verification was performed, by the author, not by
  an automated harness).

### PR5: Agent-readiness and CI — done

- `AGENTS.md` upgraded with the `llms.txt` pointer and a `doc/check_doc_quality.py` reference.
- `llms.txt` added at the repository root: project summary, canonical compatibility link, object-model
  guide, task guides, public API roots, example catalog link, migration guidance, and explicit rules
  for AI coding agents (do not restate the backend default from memory, use `version=` not
  `edbversion=`, never overwrite an input `.aedb`, always close sessions, do not invent signatures).
- `llms-full.txt` was **not** added (deferred; the mission marks it optional and the existing `.rst`
  corpus is large enough that a full-content bundle was not attempted in this pass).
- `check-links: true` enabled in both `ci-pr.yml` and `ci-main.yml` (previously `false` in both). A
  real local `linkcheck` build was run first to confirm the only failures were sandbox-specific
  (missing local CA bundle / one rate-limited external host); the rate-limited host was added to
  `linkcheck_ignore` and `linkcheck_retries`/`linkcheck_timeout` were configured in `conf.py`.
- `doc/check_doc_quality.py` added: a self-contained script (independent of the `ansys/actions/doc-build`
  reusable action's internals) that runs a clean, forced-full-reread Sphinx build and fails if Sphinx
  warnings exceed 1830, errors exceed 90, any hand-authored page is unreachable from a toctree, or any
  internal document/label reference is broken. Wired into `ci-pr.yml` as a new `doc-quality-gate` job
  that the `package` job now also depends on. Writes a Markdown table to `$GITHUB_STEP_SUMMARY` so
  warning/error counts, orphan-page count, and broken-ref count are visible directly on the PR's
  workflow run page, not just buried in a log.
- A CI-visible duplicate-page-title check and a signature/default-vs-docstring static checker (as
  distinct, separate tools) were **not** built; the closest coverage is the orphan-page and
  broken-reference checks already in `doc/check_doc_quality.py`, plus the manual signature-vs-docstring
  fixes already applied in PR4.

### An important process failure, caught and corrected

During PR4, an editing tool call used a non-unique `oldString` (generic docstring boilerplate shared
by several `SourceExcitation.create_*` methods) that matched the wrong location and silently deleted
the `class SourceExcitation(SourceExcitationInternal):` declaration along with ~350 surrounding lines,
breaking `from pyedb import Edb` entirely. This was caught by chance during unrelated cross-reference
verification, not by any automated check that existed at the time. The file was restored from `git`
and all intended fixes were re-applied one at a time, re-verifying the import after every single edit
(this safer procedure caught a second, identical failure mode on the first re-attempt). `AGENTS.md`
now documents this failure mode and the safer editing procedure under "Editing docstrings safely".
This is recorded here, not hidden, per this mission's own instruction to record unresolved issues and
process failures rather than omit them.

### Final measured metrics (clean, forced-full-reread build via `doc/check_doc_quality.py`)

| Metric | Original baseline (§10) | Final | Delta |
|---|---|---|---|
| Sphinx warnings | 1,841 | 1,814 | -27 |
| Sphinx/docutils errors | 88 | 84 | -4 |
| Hand-authored orphan pages | 7 | 0 | -7 |
| Broken internal doc/label references | 6 | 0 | -6 |
| Contradictory backend-default statements | 3 (later found: 4) | 0 | -4 |
| Broken/typo'd runnable-looking code blocks | 2 confirmed | 0 confirmed remaining | -2 |
| Local runnable PyEDB-only examples with metadata | 0 | 19 (14 configuration + 5 workflow) | +19 |
| `llms.txt` present | No | Yes | — |
| CI link-checking enabled | No | Yes (both workflows) | — |
| CI Sphinx-warning-count gate | No | Yes (`doc-quality-gate` job, ceiling 1830/90) | — |
| Unit tests passing | (not part of original baseline) | 1609/1609 | — |

These numbers were re-measured with the same command class used for the original baseline
(`sphinx -b html ... -E`, i.e. a forced full re-read, not a cached-doctree build), so they are
directly comparable. Remaining ambiguous cross-reference warnings (`ref.python`, ~30 in the original
audit), Pydantic `BaseModel` numpydoc noise (~540 warnings), and duplicate AutoAPI object descriptions
(~20 symbols) are unchanged and remain open per §11's P2 backlog — none of these were in scope for the
work performed in PR1-PR5.



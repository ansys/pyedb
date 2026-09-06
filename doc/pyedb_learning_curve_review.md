# PyEDB Learning-Curve, Discoverability, and Documentation Engineering Review

**Repository:** `ansys/pyedb` · **Branch reviewed:** `documentation-refactoring` @ `93ee0289` (2026-09-05)
**Reviewer scope:** GitHub repository (local clone, current working tree), published documentation
source (`doc/source/**`), PyAEDT/PyAnsys conventions (referenced structurally, not re-fetched live).
**Status:** Engineering review. Sections marked **[VERIFIED]** are backed by a direct source-code read,
grep match, or file inspection performed in this session. Sections marked **[INTERPRETATION]** are
reasoned conclusions drawn from verified evidence. Sections marked **[RECOMMENDATION]** are proposed
work, not existing fact. Sections marked **[ASSUMPTION — NEEDS VALIDATION]** are explicitly flagged as
unverified and require a follow-up check (e.g., a live AEDT session, or a fresh clone of `ansys/pyaedt`)
before being treated as fact.

> **Important scoping note, verified in this session:** This repository already contains a prior audit
> deliverable, `doc_audit.md` (712 lines, repo root), covering much of the same ground this review was
> commissioned to cover (contradiction analysis, broken-link inventory, baseline Sphinx metrics, a
> prioritized P0/P1/P2 backlog), together with a "Post-implementation status (PR1-PR5)" section
> recording that most of that backlog was already implemented on this branch (a canonical
> backend-compatibility page, `llms.txt`, a `quick_start.rst`, an `object_model.rst`, seven new
> per-domain `user_guide/*.rst` pages, an `example_inventory.rst`, and a CI documentation-quality gate).
> This review independently re-verifies the load-bearing claims in `doc_audit.md` against current
> source and doc files (see §3 and the citations throughout) and then produces the full 25-part
> deliverable requested, including personas, information architecture, progressive example tracks,
> training-dataset specifications, troubleshooting-by-symptom, and a phased roadmap — content that
> `doc_audit.md` did not attempt. Where this review's findings match `doc_audit.md`, that is stated
> explicitly rather than re-discovered from scratch; where this review goes further or disagrees, that
> is also stated explicitly.

---

## Table of contents

1. Executive summary
2. Review methodology and scope
3. Verified current-state findings
4. Existing strengths
5. Learning-curve barriers
6. Example and documentation inventory
7. Gap analysis
8. User personas and top tasks
9. Proposed information architecture
10. First 30 Minutes learning path
11. Standard example specification
12. Progressive example tracks (A–H)
13. API abstraction and mental-model recommendations
14. API-reference improvements
15. Training dataset specification
16. Troubleshooting architecture
17. Documentation testing and CI strategy
18. Contribution and governance model
19. Phased implementation roadmap
20. Prioritized backlog
21. Risks and mitigations
22. Success metrics
23. Quick wins for the first 30 days
24. Recommended next actions
25. Sources and evidence

---

## 1. Executive summary

PyEDB is a mature, actively developed Python API (dual-backend: gRPC `ansys-edb-core` and a deprecated
DotNet/pythonnet backend) for creating, inspecting, and modifying Ansys Electronics Database (EDB/AEDB)
layout designs prior to solving in AEDT. **[VERIFIED]** (`README.md`, `pyproject.toml`,
`src/pyedb/generic/design_types.py`).

The documentation set has the right *skeleton* — Getting started / User guide / Configuration guides /
API reference / Examples / Workflows / Changelog, built with `ansys_sphinx_theme` + AutoAPI, numpydoc
validation, a Vale style gate, and (as of this branch) a `doc-quality-gate` CI job — and a prior session
on this same branch has already closed the most damaging *factual* defects that existed at an earlier
baseline: a three-way contradiction about the default gRPC/DotNet backend selection rule, a
`version`/`edbversion` parameter-naming mismatch between the docstring and the actual signature, two
import-typo bugs in runnable-looking code blocks, and several broken/orphaned documentation pages.
**[VERIFIED]** (`doc_audit.md` §4, §11, §14; independently re-confirmed in this session against
`src/pyedb/generic/design_types.py`, `doc/source/index.rst`, `doc/source/getting_started/
backend_compatibility_migration.rst`, and `doc/source/getting_started/object_model.rst` — see §3).

What remains is **not** "the documentation is broken" but **"the learning experience is not yet a
guided curriculum."** Concretely, verified in this session:

- There are **zero PyEDB-only example files with runnable, tested code** in this repository. The
  `doc/source/examples/example_inventory.rst` page is a *catalog of pointers* to (a) prose inside
  `doc/source/configuration/configuration_api_examples.rst` and (b) prose inside `doc/source/workflows/
  **/*.rst` — not standalone, individually executable, CI-verified scripts or notebooks. **[VERIFIED]**
- **No code block anywhere in `doc/source/**` is executed by CI.** The `docs-build` job only builds
  HTML; the new `doc-quality-gate` job (`doc/check_doc_quality.py`) checks Sphinx warning/error counts,
  orphan pages, and broken references — it does not run a single Python statement from a `.rst` file.
  **[VERIFIED]** (`.github/workflows/ci-pr.yml` lines 465–517; `doc_audit.md` §14 PR5 notes the same
  gap).
- **There is no small, purpose-built, redistributable training dataset.** All `tests/example_models/`
  fixtures (`si_verse/ANSYS-HSD_V1.aedb`, `TEDB/*.aedb`, etc.) are internal test fixtures, not
  documented, licensed, or sized for a beginner tutorial; none is referenced from any `doc/source/**`
  page. **[VERIFIED]** (`tests/example_models/**` listing; no cross-reference found in `doc/source/**`
  greps performed in this session).
- **The beginner path (`quick_start.rst`) is non-destructive and uses `save_as`, matching the mission's
  core design principle**, but it operates on a **freshly created, empty** database (no existing layers,
  nets, or components), so a first-time user never sees what "inspecting a real board" looks like within
  the guided path. **[VERIFIED]** (`doc/source/getting_started/quick_start.rst`).
- **Persona-, task-, and dataset-driven curricula (Parts 2, 6, 9 of this mission) do not exist in any
  form** — there is a task index (`user_guide/index.rst` "I want to..." table) but no persona
  definitions, no progressive tracks, no troubleshooting-by-symptom architecture, and no dataset
  specification. **[VERIFIED]** (full `doc/source/**` inventory, §6).

The net effect: a new user today can reach a **correct, accurate, non-destructive quick start** in
about 10 minutes (a genuine improvement over the older, contradictory baseline recorded in
`doc_audit.md` §6), but has **no guided path beyond that** into stackup editing, connectivity queries,
ports/sources, cutouts, or configuration-driven automation that is demonstrably tested, dataset-backed,
and verification-first in the way this mission specifies. This review's backlog (§20) is built to close
exactly that remaining gap, on top of — not instead of — the work already recorded in `doc_audit.md`.

---

## 2. Review methodology and scope

**What was inspected in this session (evidence basis for every §3–§7, §11–§18 claim):**

- Git metadata: `git remote -v`, `git log`, `git diff --stat main...HEAD` (confirms branch identity,
  current commit, and the scope of uncommitted/staged documentation changes).
- `doc_audit.md` (712 lines) — read in full, treated as a prior audit deliverable to cross-check, not
  as ground truth to copy without verification.
- `llms.txt` (94 lines) — read in full.
- `README.md` (193 lines) — read in full.
- `pyproject.toml` (353 lines) — read in full (Python version support, optional-dependency extras,
  ruff/numpydoc/towncrier/pytest configuration).
- `src/pyedb/generic/design_types.py` (424 lines) — read in full; this is the actual `Edb()` factory
  and the ground truth for backend-selection behavior.
- `.github/workflows/ci-pr.yml` (538 lines) — read in full; this is the ground truth for what CI
  actually gates today.
- Every file under `doc/source/**/*.rst` was enumerated (48 files) and the following were read in full:
  `index.rst`, `getting_started/{index,quick_start,object_model,backend_compatibility_migration,
  glossary,troubleshooting,cli}.rst`, `user_guide/{index,stackup_and_materials,components_and_nets,
  ports_and_sources,validation_and_drc}.rst`, `configuration/index.rst`, `workflows/utilities/
  cutout.rst`, `examples/example_inventory.rst`.
- `src/pyedb/grpc/edb.py`, `src/pyedb/grpc/edb_init.py`, `src/pyedb/grpc/database/{nets,padstacks}.py`
  were grepped/read to independently confirm specific API claims made in `object_model.rst` and
  `doc_audit.md` (backend lifecycle methods `save`/`save_as`/`close`, `Nets.netlist`,
  `Padstacks.pins`).
- `tests/example_models/**` was enumerated (100+ files/dirs) to assess what fixture data exists and
  whether it is documentation-facing.
- `tests/unit/**/*.py` was enumerated (file names only, not full content) to establish current unit-test
  domain coverage as a proxy for which API surfaces are exercised at all.

**What was explicitly *not* done in this session, and is flagged as a limitation:**

- **No live AEDT/EDB session was available.** No code example — old or new — was actually executed.
  All "expected output" claims in this review, and all claims already present in `doc/source/
  getting_started/quick_start.rst`, are **source-verified** (the methods called exist, with matching
  signatures) but **not runtime-verified** in this session. This mirrors the same limitation
  `doc_audit.md` §13 records for its own findings.
- **`ansys/pyaedt`'s live documentation tree was not fetched or cloned in this session.** Per this
  review's instructions to use current published sources, this is a gap; PyAEDT-derived structural
  comparisons in this report (§9, §13) are based on the well-known, previously observed PyAEDT
  documentation architecture (Getting started / User guide / API reference / external example gallery)
  already used as a reference point by `doc_audit.md` §3, not on a fresh read performed in this session.
  This is flagged as **[ASSUMPTION — NEEDS VALIDATION]** wherever it materially affects a
  recommendation.
- **GitHub Issues/Discussions were not queried** (no network access to the GitHub API was exercised in
  this session). Any claim in this report about "likely user confusion" that is not directly tied to a
  reproducible doc/code defect is labeled **[INTERPRETATION]**, not evidence from an actual issue
  thread.
- **The full `src/pyedb/**` tree (hundreds of files) was not read line-by-line.** API-surface claims in
  this report are anchored to the same files `doc_audit.md` already verified (`design_types.py`,
  `edb.py`, `edb_init.py`, `nets.py`, `padstacks.py`, `stackup.py`, `materials.py`,
  `source_excitations.py`, `workflows/drc/drc.py`) plus the doc pages that cite additional modules
  (`cutout.py`, `hfss_auto_configuration.py`). Any API family not covered by one of these files is
  described only at the level of detail visible from its documentation page, and is flagged accordingly.

**Grading rule applied throughout:** a claim is marked **[VERIFIED]** only if this session (or the
already-reviewed `doc_audit.md`, itself grounded in a real Sphinx build and source reads) produced a
direct citation. Everything else is marked **[INTERPRETATION]**, **[RECOMMENDATION]**, or
**[ASSUMPTION — NEEDS VALIDATION]**.

---

## 3. Verified current-state findings

### 3.1 Backend selection — the P0 contradiction is fixed **[VERIFIED]**

Ground truth, `src/pyedb/generic/design_types.py` lines 117–121, 363–364:

```python
def _use_grpc_by_default(specified_version: str) -> bool:
    if settings.edb_dll_path is not None:
        return False
    return (
        float(specified_version) >= DEFAULT_GRPC_VERSION
    )  # DEFAULT_GRPC_VERSION = 2026.1


grpc = grpc if grpc is not None else _use_grpc_by_default(settings.specified_version)
```

Cross-checked against the three pages `doc_audit.md` §4.2 previously found contradictory:

- `doc/source/index.rst` (lines 6–20): now states the version-conditional rule correctly, plus
  correctly separates the "gRPC unsupported below 2026.1 → `RuntimeError`" failure mode from the
  "DotNet extra not installed → initialization failure" failure mode as two distinct bullets. Matches
  source (`design_types.py` lines 385–386: `raise RuntimeError(GRPC_NOT_SUPPORTED_WARNING)`).
- `doc/source/getting_started/backend_compatibility_migration.rst` (lines 55–74): states the same rule
  in a table and is now the canonical page other pages link to instead of restating.
- `doc/source/getting_started/object_model.rst` (line 25): defers to
  `backend_compatibility_migration` rather than restating a default.

**Conclusion:** the single most damaging defect recorded in `doc_audit.md` (§4.2, three incompatible
default-backend statements) is verifiably no longer present in the three files that previously
disagreed. This review did not find a fourth/new location restating an incorrect default.

### 3.2 `version` vs. `edbversion` — fixed at the two previously-cited locations **[VERIFIED]**

- `design_types.py` line 125: `@deprecate_argument_name({"edbversion": "version"})` — `edbversion` is a
  deprecated alias, `version` is canonical. Confirmed unchanged from `doc_audit.md`'s reading.
- `backend_compatibility_migration.rst` line 83 and `quick_start.rst` lines 59, 70, 111 all use
  `version=`, never `edbversion=`. No occurrence of `edbversion=` was found in any `doc/source/**` file
  read in this session.

### 3.3 Quick start exists, is non-destructive, and uses public APIs only **[VERIFIED]**

`doc/source/getting_started/quick_start.rst` (145 lines):

- Creates a new EDB in a temp directory, inspects (`active_cell`, `cell_names`, `stackup.layers`,
  `nets.netlist`), performs one modification (`stackup.add_layer(...)`), calls `save_as()` to a
  **different** path (never overwrites the input), and calls `close()`. This satisfies this mission's
  non-destructive/verification-first core design principle for at least this one page.
- Shows the context-manager form (`with Edb(...) as edb:`), confirmed against
  `src/pyedb/grpc/edb.py` lines 369/373 (`__enter__`/`__exit__` exist) — not asserted without a source
  check.
- Includes a "Common problems" table (3 rows) and "Next steps" links.
- **Gap (not present in `doc_audit.md`'s own findings, newly identified in this review):** the
  "Expected output" block (lines 85–99) shows `Existing layers: []` and `Existing nets: []` because the
  script opens a **freshly created, empty** database. A first-time user following this page literally
  never sees a populated stackup, a real net name, or a real component — the single most common shape
  of "inspect an existing board" task (Part 2/6's top task list, item 3) is not demonstrated anywhere in
  the guided beginner path. This is a **learning-curve gap**, not a factual defect.

### 3.4 Object model page — accurate against source, but incomplete against the full `Edb` surface **[VERIFIED, with a scoped caveat]**

`doc/source/getting_started/object_model.rst` (231 lines) documents 10 properties
(`stackup`, `materials`, `components`, `nets`, `padstacks`, `excitation_manager`, `modeler`/`layout`,
`simulation_setups`, `configuration`, `layout_validation`) using an "8 questions per object" template
(how to obtain it / what it owns / what it returns / does it mutate / does it require saving / both
backends? / preferred API / smallest example).

Spot-checked against source in this session:

- `Padstacks.pins` — **[VERIFIED]** `src/pyedb/grpc/database/padstacks.py` line 297:
  `def pins(self) -> Dict[str, PadstackInstance]`. Matches the page's claim
  (`dict[int, PadstackInstance]` in the page text is imprecise — the real return type is
  `Dict[str, PadstackInstance]`, keyed by **instance name**, not `int`. **[DISCREPANCY FOUND]**: the
  object-model page states `edb.padstacks.pins` returns `dict[int, PadstackInstance]`; the actual
  docstring/signature says `Dict[str, PadstackInstance]` keyed by name. This is a small but real
  documentation/signature mismatch of exactly the kind `doc_audit.md` flagged elsewhere (§4.3) and
  should be fixed (see backlog item DOC-041 in §20).
- `Nets.netlist` — **[VERIFIED]** `src/pyedb/grpc/database/nets.py` line 244: `def netlist(self) ->
  List[str]`. Matches the page's claim exactly.
- `save()` / `save_as(path, version="")` / `close(terminate_rpc_session=None)` — **[VERIFIED]**
  `src/pyedb/grpc/edb_init.py` lines 258, 285, 407. Matches the page's claims exactly, including the
  optional `version` downgrade parameter on `save_as` and the `terminate_rpc_session` parameter on
  `close`.
- **Not independently re-verified in this session:** the exact return type and keyword arguments of
  `edb.excitation_manager.create_port(...)` shown on `ports_and_sources.rst` and in the `Edb` factory's
  own docstring Examples section. `doc_audit.md` §13 already flagged this exact call as unverified in
  its own audit pass; this review did not close that gap either (no time was budgeted to read the full
  `SourceExcitation` class body). **[ASSUMPTION — NEEDS VALIDATION]**, carried forward as backlog item
  DOC-042.

### 3.5 No runnable, CI-tested PyEDB-only examples exist **[VERIFIED]**

`doc/source/examples/example_inventory.rst` (174 lines) is a **metadata catalog with cross-links**, not
a set of example files:

- The "Configuration API examples" table (14 rows) points to prose blocks inside
  `configuration/configuration_api_examples.rst` — that page was not fully read in this session, but
  the inventory page's own text (lines 34–44) confirms these are documentation sections, not standalone
  scripts or notebooks with independent files.
- The "PyEDB workflow examples" table (5 rows) points to prose inside `workflows/**/*.rst` pages
  (`cutout.rst`, `hfss_auto_configuration.rst`, `drc.rst`, two log-parser pages) — same structure.
- The "PyAEDT + PyEDB combined examples" section explicitly defers to the external
  `pyaedt-examples` gallery and states its own metadata is "not duplicated here to avoid drift" (lines
  160–165).

**Conclusion:** there is currently no `doc/source/examples/*.py`, no Jupyter notebook, and no
`sphinx-gallery`-style example script in this repository, despite `sphinx-gallery` being a declared doc
dependency in `pyproject.toml` (line 109: `sphinx-gallery>=0.14.0,<0.22`). The dependency is installed
but unused for local examples — a **[VERIFIED]** capability/usage gap.

### 3.6 CI executes zero documentation code **[VERIFIED]**

`.github/workflows/ci-pr.yml`:

- `docs-build` job (lines 465–479): runs `ansys/actions/doc-build` with `check-links: true` (confirms
  `doc_audit.md`'s claim that link-checking was enabled during PR1-PR5 — previously `false`). This job
  builds HTML and checks links; it does not execute any embedded Python code block.
- `doc-quality-gate` job (lines 481–517): runs `python doc/check_doc_quality.py`, which (per
  `doc_audit.md` §14 PR5) performs a clean Sphinx build and fails on excessive warnings/errors, orphan
  pages, or broken internal references. It does not execute code blocks either.
- `unit-tests-grpc` / `unit-tests-dotnet` (lines 156–209, 101–155) run `pytest tests/unit`, and
  `system-tests-*` (lines 215–463, self-hosted runners) run `pytest tests/system` — both against the
  `tests/` tree, not against `doc/source/**`.

**Conclusion:** there is no mechanism today that would catch a regression like "this doc code block
calls a method that no longer exists" except the manual, one-off source-verification passes recorded in
`doc_audit.md` PR4 ("~24 confirmed docstring/signature mismatches fixed ... by independent source
verification", explicitly **not** by an automated harness). This is the single largest remaining
structural risk identified in this review (see §17).

### 3.7 No small, purpose-built training dataset exists **[VERIFIED]**

`tests/example_models/**` contains dozens of `.aedb` fixture folders (`si_verse/ANSYS-HSD_V1.aedb`,
`TEDB/*.aedb`, `wirebond_projects/*.aedb`, etc.) used by `tests/unit` and `tests/system`, plus
`.gds`/`.dxf`/`.brd`-adjacent fixtures and JSON configuration fixtures under `TEDB/edb_config_json/`.
None of these:

- are referenced by name from any `doc/source/**` page (checked via the full read of the pages listed
  in §2; no `tests/example_models` path string appears in any of them),
- have documented provenance, license terms, expected object counts, or a stated maintenance owner,
  or
- are packaged/described as downloadable teaching material distinct from internal CI fixtures.

This directly explains why the quick start (§3.3) had to fall back to "create an empty database" rather
than "open a small, realistic board" — **there is currently no dataset in this repository that is safe,
documented, and appropriately sized to hand a first-time user.** This is the evidentiary basis for
Part 9's dataset specification (§15) and is one of this review's highest-leverage recommendations
(§23, quick win QW-3).

### 3.8 Existing task index is real but shallow **[VERIFIED]**

`doc/source/user_guide/index.rst` "I want to..." table (lines 15–50) maps 12 goals to destination
pages. This is a genuine, working first pass at this mission's Part 3 "Path A" navigation requirement.
It is not yet organized by persona, does not distinguish beginner/intermediate/advanced entries, and
does not yet include several of this mission's required Path-A entries verbatim (compare database
revisions, batch-process multiple designs, run PyEDB in CI — none of these three are present). See §9
for the full gap-mapped proposal.

---

## 4. Existing strengths

Recorded explicitly, per this mission's instruction not to omit what already works:

1. **Accurate, canonical backend-compatibility page.** `backend_compatibility_migration.rst` is now a
   genuine single source of truth for the gRPC/DotNet default rule, with other pages linking to it
   instead of restating it. **[VERIFIED]**, §3.1.
2. **A real, non-destructive, source-verified quick start with a context-manager example.**
   `quick_start.rst` follows this mission's "input → copy/create → open → inspect → modify → validate →
   save-as-new → close" phase separation almost exactly (§3.3). **[VERIFIED]**
3. **A navigation-first object-model page using a consistent, repeatable template** ("8 questions per
   object") applied to 10 properties, each with a smallest-example code block. This is close in spirit
   to this mission's Part 7 (API abstraction / mental model) requirement and Part 5 (standard example
   template) requirement, just not yet extended to the full API surface. **[VERIFIED]**, §3.4.
4. **Per-domain user-guide pages already follow a disciplined template.** `stackup_and_materials.rst`,
   `components_and_nets.rst`, `ports_and_sources.rst`, `validation_and_drc.rst` (all read in full this
   session) consistently include: Prerequisites → Public API entry points → Procedure → Complete example
   → Expected result → Backend and version notes → Common problems → See also. This is materially the
   same structure this mission's Part 5 "Standard Example Template" asks for, missing only explicit
   "software/license requirements," "cleanup," and "next recommended example" as separately labeled
   subsections (they are partially present inside "Backend and version notes" / "See also"). **[VERIFIED]**
5. **Configuration-driven automation is already treated as a first-class, well-motivated workflow.**
   `configuration/index.rst` (140 lines) explicitly frames *when* to use the declarative
   JSON/TOML system versus direct API calls, states the two are complementary within one session, and
   links to a 14-example catalog. This substantially satisfies this mission's Part 6 Track G
   requirement at the conceptual level; it needs runnable/tested examples and CI coverage to be
   complete (§12, Track G). **[VERIFIED]**
6. **A working CLI with a documented command surface and `--json` machine-readable output**, useful for
   CI/DevOps personas (`getting_started/cli.rst`, `pyedb version|create|save|exec|attach|export|config`).
   **[VERIFIED]**
7. **CI already gates documentation quality mechanically** (`doc-quality-gate` job, warning/error
   ceiling, orphan-page detection, broken-reference detection) — a meaningfully more mature starting
   point than "no gate at all." **[VERIFIED]**, §3.6.
8. **`llms.txt` exists and is disciplined about not restating unstable facts** — it explicitly tells an
   AI agent to resolve the backend default from source rather than memorizing it, and states the
   `version`/`edbversion` rule once. This is good practice per this mission's own AI-agent-readability
   spirit, even though this mission's remit is human-facing documentation primarily. **[VERIFIED]**

---

## 5. Learning-curve barriers

Ranked by estimated user impact (not yet effort-weighted; see §7 for the full ranked gap analysis).

### 5.1 No dataset-backed "inspect a real board" experience anywhere in the guided path — **High impact**

Every "Complete example" in `quick_start.rst`, `stackup_and_materials.rst`, `components_and_nets.rst`,
and `ports_and_sources.rst` opens a **freshly created, empty** `Edb` instance (`Edb(edbpath=input_path,
version="2026.1")` with `input_path` pointing at a nonexistent folder — EDB creates an empty design).
Every one of these pages, verified in this session, contains an explicit code comment acknowledging the
resulting output is empty:

- `stackup_and_materials.rst`: adds a layer to an empty stack — informative, but never shows reading an
  *existing* multi-layer stackup.
- `components_and_nets.rst` line 66-67: *"edb.components.instances and edb.nets.netlist are empty on a
  freshly created, unpopulated database; this example shows the calls used once a design is loaded."*
- `ports_and_sources.rst` line 66-67: *"A freshly created, empty database has no padstack instances yet;
  this example shows the call pattern for a design that already has vias or pins placed."*

**Consequence:** a new user can run every beginner example successfully and still never see what a
non-trivial `edb.nets.netlist`, `edb.components.instances`, or `edb.padstacks.pins` result looks like,
never practices distinguishing "empty because nothing is there" from "empty because I queried the wrong
name" (this mission's Tutorial 3 requirement), and has no template for opening a delivered board file.
This is the single highest-impact fix available (§23, QW-3) and is only unresolved because no dataset
exists yet (§3.7).

### 5.2 Zero automated verification that any documented example still runs — **High impact, structural**

Confirmed in §3.6: no CI job executes a single `.rst`-embedded code block. `doc_audit.md` PR4 itself
records a near-miss: a manual edit accidentally deleted a class declaration and broke `from pyedb import
Edb` entirely, caught "by chance during unrelated cross-reference verification, not by any automated
check that existed at the time" (`doc_audit.md` §14, "An important process failure, caught and
corrected"). This is direct, first-party evidence that the current safety net is a human reading
carefully, not a machine — exactly the situation this mission's Part 11 (Executable Documentation and
CI) exists to prevent. **[VERIFIED]**, with the failure-mode evidence coming from `doc_audit.md` itself.

### 5.3 No persona-differentiated entry points — **Medium-high impact**

The "I want to..." table (`user_guide/index.rst`) is task-oriented but not level-oriented: a PCB
engineer with limited Python and an advanced automation engineer land on the same table with no signal
about which entries are beginner-safe versus which require deeper object-model familiarity. This
mission's Part 2 (personas) and Part 3 (two-path IA) call for exactly this distinction, and it is
currently absent. **[VERIFIED absence]** / **[RECOMMENDATION forthcoming]**, §8–§9.

### 5.4 No troubleshooting-by-symptom architecture — **Medium impact**

`getting_started/troubleshooting.rst` (90 lines) is a flat FAQ (5 issues: gRPC connection failure,
TRANSIENT_FAILURE, permission errors, slow geometry creation, a Windows/uv OpenSSL DLL conflict) plus a
generic "Getting Help" section. It is accurate and specific where it exists, but it does not cover most
of this mission's required symptom list (net lookup returns nothing, modification doesn't persist,
reopened database fails, cutout omits geometry, config applies partially, CI-only failures, etc. — see
§16 for the full required list cross-checked against what exists today). **[VERIFIED]**

### 5.5 API reference navigation intentionally narrow — **Medium impact**

`doc_audit.md` §7 (already verified by that prior audit and not re-litigated line-by-line here) found
that the published API reference toctree (`grpc_api/index.rst`) wires in only two AutoAPI subtrees
(`grpc/database`, `grpc/edb`), while `pyedb.configuration`, `pyedb.workflows.*`, `pyedb.libraries.*`,
`pyedb.siwave_core.*`, and `pyedb.cli` are AutoAPI-generated but not linked from the main API-reference
navigation entry. This review's own read of `configuration/index.rst` line 139 confirms at least
`configuration` is linked from a *different* page's toctree
(`../autoapi/pyedb/configuration/index`), partially mitigating but not closing this gap — a reader who
starts from "API reference" in top-level navigation will still not discover `workflows.*` or `cli`.
**[VERIFIED, carried forward from `doc_audit.md`, spot-checked]**

### 5.6 Object-model page has at least one confirmed signature/documentation mismatch — **Low-medium impact, high signal risk**

See §3.4: `edb.padstacks.pins` is documented on `object_model.rst` as `dict[int, PadstackInstance]` but
the verified source signature is `Dict[str, PadstackInstance]` keyed by instance **name**. This is a
small, concrete instance of exactly the defect class `doc_audit.md` spent significant effort eliminating
elsewhere (§4.3, §7) — evidence that the underlying risk (docs drifting from signatures) is not fully
eliminated by the PR1-PR5 work, only reduced. **[VERIFIED, newly found in this session]**

### 5.7 No configuration-schema-level validation guidance for "why did my config only partially apply" — **Medium impact for the CI/DevOps and CAD-automation personas**

`configuration/index.rst` explains *when* to use configuration files well, but this session's read did
not find (and did not have budget to fully verify across `configuration_api_guide.rst`, not fully read)
an explicit page addressing partial-application diagnosis, idempotency guarantees, or precedence rules
when mixing configuration-driven and direct-API calls in the same session — all explicitly required by
this mission's Track G and Part 10 troubleshooting list. **[GAP — NEEDS FURTHER VERIFICATION against
`configuration_api_guide.rst`, which was not fully read in this session; flagged rather than asserted]**.

---

## 6. Example and documentation inventory

This inventory covers every distinct learning resource identified in `doc/source/**` during this
session's full-text reads (§2). Per this mission's dimensions; columns are abbreviated where a full
sentence would be redundant. "N/A" means the dimension does not apply to that resource type (e.g., a
catalog page has no "APIs demonstrated" of its own).

| # | Title | Path | Category | Level | Public API only? | Input data supplied? | Destructive? | Assertions/validation shown? | Version last validated |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Quick start | `getting_started/quick_start.rst` | Fundamentals | Beginner | Yes | No (creates empty DB) | No (`save_as`) | Prose "Expected output" block only, no `assert` | Source-verified this session |
| 2 | Object model | `getting_started/object_model.rst` | Conceptual + API map | Beginner–Intermediate | Yes | N/A (snippets only) | No | Prose only | Source-verified this session, 1 discrepancy found (§3.4) |
| 3 | Backend, compatibility, and migration | `getting_started/backend_compatibility_migration.rst` | Conceptual | All | Yes | N/A | N/A | N/A | Source-verified this session |
| 4 | Stackup and materials | `user_guide/stackup_and_materials.rst` | Workflow (Track C) | Beginner–Intermediate | Yes | No (creates empty DB) | No (`save_as`) | Prose "Expected result" | Source-verified this session |
| 5 | Components and nets | `user_guide/components_and_nets.rst` | Workflow (Track B/D) | Beginner–Intermediate | Yes | No (empty DB; comment admits it) | No (`save_as`) | Prose "Expected result" | Source-verified this session |
| 6 | Ports and sources | `user_guide/ports_and_sources.rst` | Workflow (Track F) | Intermediate | Yes | No (empty DB; comment admits it) | No (`save_as`) | Prose "Expected result" | `create_port` signature **not** independently re-verified (§3.4) |
| 7 | Validation and DRC | `user_guide/validation_and_drc.rst` | Workflow (Track D/H) | Intermediate | Yes | No (empty DB) | No (`close()` only, no save shown) | Prose "Expected result", return-shape described | Source-verified this session |
| 8 | Padstacks and vias | `user_guide/padstacks_and_vias.rst` | Workflow (Track D) | Intermediate | Not fully re-read this session | Unknown | Unknown | Unknown | Not verified this session — **flagged for follow-up** |
| 9 | Cutouts | `user_guide/cutouts.rst` | Workflow (Track F) | Intermediate | Not fully re-read this session | Unknown | Unknown | Unknown | Not verified this session — **flagged for follow-up** |
| 10 | Simulation setups | `user_guide/simulation_setups.rst` | Workflow (Track F) | Intermediate | Not fully re-read this session | Unknown | Unknown | Unknown | Not verified this session — **flagged for follow-up** |
| 11 | Configuration guides index | `configuration/index.rst` | Conceptual (Track G) | All | Yes | N/A | N/A | N/A | Source-verified this session |
| 12 | Configuration API examples (14 items) | `configuration/configuration_api_examples.rst` | Workflow (Track G) | Beginner–Advanced (per-row) | Not fully re-read this session | Unknown | Unknown | Unknown | Metadata only verified via `example_inventory.rst`; page itself not fully read |
| 13 | EDB cutout workflow | `workflows/utilities/cutout.rst` | Workflow class reference (Track F/H) | Intermediate–Advanced | Yes | No dataset; snippet assumes `edb` pre-populated | Not shown (no `save_as` in the "Quickstart" snippet) | No | Source-verified this session (full parameter table read) |
| 14 | HFSS auto configuration | `workflows/sipi/hfss_auto_configuration.rst` | Workflow class reference | Advanced | Not fully re-read this session | Unknown | Unknown | Unknown | Not verified this session — **flagged for follow-up** |
| 15 | DRC engine | `workflows/drc/drc.rst` | Workflow class reference (Track H) | Advanced | Yes (via `validation_and_drc.rst` cross-check) | No dataset | No | Return-shape described | Cross-verified via `validation_and_drc.rst` |
| 16 | Example inventory (catalog page) | `examples/example_inventory.rst` | Meta / catalog | N/A | N/A | N/A | N/A | N/A | Source-verified this session; confirmed **no runnable files exist**, only cross-links |
| 17 | CLI reference | `getting_started/cli.rst` | Reference (Track H) | Intermediate–Advanced | Yes | N/A (CLI, not a script) | Depends on subcommand | `--json` output shown as example, no assertion demonstrated | Source-verified this session |
| 18 | Troubleshooting (flat FAQ) | `getting_started/troubleshooting.rst` | Troubleshooting | All | Yes | N/A | N/A | N/A | Source-verified this session; **not organized by symptom taxonomy this mission requires** |
| 19 | Glossary | `getting_started/glossary.rst` | Conceptual | Beginner | N/A | N/A | N/A | N/A | Source-verified this session; only 6 terms (Cell, ansys-edb-core, gRPC, Layout, Net, Primitive, Stackup) — thin relative to this mission's Part 3 Path-B concept list |

**Duplicated examples:** none found — each workflow page owns a distinct domain; `example_inventory.rst`
correctly avoids duplicating content and instead cross-links (§3.5). **[VERIFIED]**

**Examples using deprecated/private APIs:** none found in the pages read this session. `ports_and_sources.rst`
and `object_model.rst` both explicitly flag `Edb.create_port`/`Edb.create_siwave_syz_setup`-style
direct-on-`Edb` wrappers as deprecated and steer the reader to the non-deprecated
`excitation_manager`/`simulation_setups` forms instead — this is good practice, not a defect.
**[VERIFIED]**

**Examples requiring unavailable input files:** all beginner/intermediate pages read this session
avoid this by creating an empty DB in a temp directory — technically "always available" but at the cost
of §5.1's realism gap. `cutout.rst`'s "Quickstart" snippet assumes a pre-populated `edb` variable with no
stated source — **borderline**, flagged for follow-up (row 13).

**Examples with implicit environment dependencies:** all examples require a licensed local AEDT
installation (stated in `quick_start.rst` prerequisites) — this is a real, unavoidable dependency of the
product, not a documentation defect, but it is not always restated on every subsequent page (e.g.,
`stackup_and_materials.rst`'s own "Prerequisites" section says only "An open `Edb` instance", deferring
the AEDT/license requirement to `quick_start.rst` — acceptable via cross-reference, but means a reader
who lands directly on a workflow page via search will not see the license requirement restated). **[INTERPRETATION]**

**API-reference pages without practical examples / tutorial pages without conceptual context:** the
2-subtree-only API-reference toctree gap (§5.5) means most `pyedb.grpc.database.*` classes are only
reachable via AutoAPI auto-generated stub pages with no example, since the narrative user-guide pages
link *to* specific classes but the reverse direction (AutoAPI page → narrative tutorial) does not exist
as a systematic cross-link pattern. **[INTERPRETATION, consistent with `doc_audit.md` §7]**

**Unclear boundaries between PyEDB, PyAEDT, EDB, AEDT, HFSS 3D Layout, SIwave:** `README.md` (§ "What is
EDB?", lines 123–141) explains this reasonably well in prose form, and `example_inventory.rst` draws a
clear line for *examples* ("PyEDB-only" vs. "PyAEDT + PyEDB combined", §3.5), but there is no single,
short, canonical **concept page** dedicated to this boundary that a task page can link to (this
mission's Part 3 Path-B item "PyEDB versus PyAEDT responsibilities" and "EDB versus AEDT project data"
are not currently separate pages — they are folded into the README and glossary only). **[VERIFIED
absence]** — see backlog DOC-010.

---

## 7. Gap analysis

Ranked by **user impact** (H/M/L) × **implementation effort** (S/M/L) × **technical risk** (H/M/L),
with **frequency of likely user need** noted qualitatively. This table is the direct evidentiary bridge
into §20's backlog IDs.

| Gap | User impact | Effort | Technical risk | Frequency | Evidence |
|---|---|---|---|---|---|
| No small, documented, license-clear training dataset | High | Medium | Low | Every beginner touches this | §3.7, §5.1 |
| Zero CI execution of documentation code examples | High | Medium–Large | Medium (flaky license/AEDT dependency in CI) | Affects every future doc change | §3.6, §5.2 |
| No persona-differentiated / leveled navigation | Medium-High | Small–Medium | Low | Every new user | §5.3, §3.8 |
| Troubleshooting is a flat FAQ, not symptom-organized | Medium | Medium | Low | Common, especially for CI/PI personas | §5.4 |
| API reference navigation excludes `workflows.*`, `libraries.*`, `siwave_core.*`, `cli` | Medium | Small | Low | Advanced/CAD-automation personas | §5.5 (from `doc_audit.md` §7) |
| `object_model.rst` `padstacks.pins` type mismatch | Low-Medium | Small | Low (but recurring risk class) | Anyone reading vias/pins docs | §3.4, §5.6 |
| `create_port` signature not independently re-verified | Medium (ports/sources is a top-20 task) | Small (verification only) | Medium (could mislead SI/PI persona) | Common for SI/PI persona | §3.4 carried from `doc_audit.md` §13 |
| No configuration partial-application/idempotency guidance | Medium | Medium | Low | CI/DevOps and CAD-automation personas | §5.7 |
| No dedicated PyEDB/PyAEDT/EDB/AEDT/HFSS-3D-Layout/SIwave boundary page | Medium | Small | Low | Every new user, especially PCB/PI engineers | §6 (unclear boundaries finding) |
| Glossary thin (6 terms) vs. this mission's ~15-term Path-B concept list | Medium | Small | Low | Every new user | §6, row 19 |
| No progressive example tracks (A–H) as a stated curriculum | Medium | Large | Low | Intermediate users plateau without one | §8–§12 (net-new, no existing page attempts this) |
| No worked "reopen and verify persistence" pattern reused across pages | Medium | Small | Low | Every workflow page implicitly needs this | §11 (net-new template gap) |
| Several user-guide pages not re-verified this session (`padstacks_and_vias`, `cutouts`, `simulation_setups`, `hfss_auto_configuration`, 14 config examples) | Unknown until verified | Small (verification pass) | Medium (unverified = risk) | High (these are top-20 tasks) | §6 rows 8–10, 12, 14 |

---

## 8. User personas and top tasks

**[RECOMMENDATION — net new content; no persona definitions exist in the repository today, verified by
the full `doc/source/**` inventory in §2/§6.]**

### 8.1 Personas

**P1 — PCB/package engineer, limited Python.**
Background: strong AEDT/HFSS 3D Layout GUI experience, writes short scripts by copying examples.
Goals: automate a repetitive layout task (renaming nets, checking a stackup) without becoming a
software engineer. Misconceptions: assumes PyEDB "is" AEDT and that any AEDT GUI action has a 1:1
PyEDB call; assumes `grpc`/`version` arguments are optional trivia rather than load-bearing. Setup
constraints: often on a locked-down corporate Windows machine, may not have pip/network access without
IT approval. Preferred format: copy-pasteable, heavily commented scripts with visible printed output.
Top tasks: open an EDB, list layers/nets/components, make one change, save as new file. Common failure
mode: overwrites the only copy of a shared board file because no page told them to use `save_as`.
Abstraction level: Level 1 (workflow APIs) almost exclusively; configuration files may suit this persona
even better than direct API calls.

**P2 — Python developer, limited EDB knowledge.**
Background: comfortable with packages, virtual environments, pytest, git. Goals: integrate PyEDB into a
larger Python automation pipeline. Misconceptions: expects "empty result" to always mean "error"; expects
a fully Pythonic, exception-first error model everywhere (this mission's Part 8 "Error Behavior" analysis
matters most for this persona). Setup constraints: usually fine with pip/CI, but may run in a container
without AEDT installed and be confused when nothing works. Preferred format: API reference with type
hints, runnable examples with assertions. Top tasks: install, verify version constraints, query design
objects reliably, distinguish missing-object from empty-result. Common failure mode: assumes a
`None`/empty-list return is a bug rather than a documented "not found" convention. Abstraction level:
Level 2 (domain object APIs), reads Level 3 docs when debugging.

**P3 — Experienced AEDT user moving into automation.**
Background: deep EDB/AEDT domain knowledge (stackup, nets, ports) from years of GUI use; new to Python
and to PyEDB's specific object model. Goals: replace manual, repetitive GUI steps with scripts. Setup
constraints: has AEDT licensed and installed already — the easiest persona to onboard technically.
Preferred format: task-oriented "I want to..." recipes mapped directly to GUI-familiar concepts
(stackup, ports, cutout). Top tasks: stackup editing, ports/sources, cutouts, simulation setup creation.
Common failure mode: expects PyEDB property mutation to auto-save (this mission's Part 7 "mutation vs.
persistence" distinction is critical for this persona — confirmed as a real, verified behavior in
`object_model.rst`: "Does it require saving? Yes" appears on every property). Abstraction level: Level 1
→ Level 2 as confidence grows.

**P4 — Signal-integrity / power-integrity engineer preparing simulations.**
Background: strong EM/PI domain knowledge, may know EDB scripting from an older PyAEDT/legacy-EDB
workflow. Goals: prepare ports, sources, cutouts, and simulation setups reliably and repeatably across
many board revisions. Setup constraints: needs license-aware guidance (which steps need a solver license
versus which are license-free preparation — this mission's Part 11 requirement). Preferred format:
domain-authentic examples (differential pairs, wave ports, DCIR setups) with expected numeric/electrical
results, not just "no exception raised." Top tasks: create ports/sources, generate cutouts, add
HFSS/SIwave setups, validate setup completeness before handing off to solve. Common failure mode:
constructs a port on the wrong reference net and discovers it only at solve time, because no
license-free "port completeness" validation step was shown (§16 troubleshooting: "reference conductor
cannot be identified"). Abstraction level: Level 1/2, occasionally Level 3 for exotic port geometries.

**P5 — CAD automation engineer building repeatable production workflows.**
Background: strong scripting background across multiple EDA tools, values idempotency and
reproducibility over exploratory API discovery. Goals: build a maintainable pipeline (e.g., nightly
cutout + DRC across a design library). Setup constraints: needs batch-processing, structured-logging,
and resource-cleanup guidance. Preferred format: production-grade complete scripts, not fragments; a
stated "idempotent" contract. Top tasks: batch processing, configuration-driven workflows, DRC/validation
at scale, structured reporting. Common failure mode: leaks RPC sessions/file locks across many
sequential `Edb(...)` calls in a loop because `close()`/context-manager discipline was not modeled at
scale (only shown for a single instance in `quick_start.rst`). Abstraction level: Level 1 (configuration)
+ Level 2 (direct API) mixed deliberately.

**P6 — CI/DevOps engineer validating layout transformations.**
Background: general software CI/CD expertise, little to no EDA domain knowledge. Goals: wire PyEDB
scripts into a pipeline that fails loudly and clearly on regressions. Setup constraints: headless
execution, no GUI, needs explicit guidance on which operations require an AEDT/SIwave/HFSS license versus
which are license-free (this mission's explicit requirement). Preferred format: CLI-first (`pyedb --json
...`) and machine-readable diagnostics. Top tasks: run PyEDB in CI, validate a database, detect
regressions between revisions, exit with a meaningful status code. Common failure mode: "works
interactively, fails in CI" (this mission's explicit troubleshooting entry, §16) because of an
environment/license/headless-mode difference not documented anywhere central. Abstraction level: Level 1
via CLI, rarely touches Level 2/3 directly.

**P7 — Advanced EDB user needing low-level API access.**
Background: deep familiarity with the underlying `ansys-edb-core` gRPC object model, possibly a former
DotNet-backend power user. Goals: implement a capability not exposed by any high-level PyEDB wrapper
(custom via structures, exotic net-class scripting). Setup constraints: comfortable reading AutoAPI-
generated reference pages directly. Preferred format: full API reference with ownership/lifetime
semantics, escape-hatch guidance from Level 1/2 into Level 3. Top tasks: everything in Part 6's Track D,
plus arbitrary low-level `ansys-edb-core` access when the high-level wrapper is insufficient. Common
failure mode: mutates an object obtained from a stale reference after a cutout/rebuild invalidated it
(this mission's Part 8 "object identity after layout modifications" — not yet documented anywhere
verified in this session). Abstraction level: Level 3 by definition, needs the clearest "escape hatch"
documentation of any persona.

### 8.2 Top 20 user tasks (ranked)

Ranking blends frequency-of-need (informed by the 7 personas above) and the mission's own seed list.
"Current coverage" cites the verified page if one exists.

| Rank | Task | Current coverage | Gap |
|---|---|---|---|
| 1 | Install PyEDB and verify the active version/backend | `getting_started/installation.rst`, `quick_start.rst` §2 | None — well covered |
| 2 | Open an existing EDB safely (not just create an empty one) | Partially — all examples create empty DBs (§5.1) | **High** — no page opens a real board |
| 3 | Create a non-destructive working copy before editing | `save_as` shown, but no explicit "copy first, open the copy" pattern shown before any mutation | **Medium** |
| 4 | List layers / inspect stackup | `stackup_and_materials.rst` | Low — needs a populated-dataset variant |
| 5 | List nets, classify power/ground | `components_and_nets.rst` (list only; no power/ground classification shown) | **Medium** |
| 6 | Locate components by reference designator | `components_and_nets.rst` | Low |
| 7 | Inspect pins and connectivity | Not verified this session (`padstacks_and_vias.rst` unread) | **Needs verification** |
| 8 | Find primitives by layer/net/type | Not found in any page read this session | **High — no coverage found** |
| 9 | Inspect and place padstack instances | Not verified this session | **Needs verification** |
| 10 | Edit stackup/material properties | `stackup_and_materials.rst` | Low |
| 11 | Create or modify geometry (traces, polygons) | `object_model.rst` mentions `edb.modeler.create_rectangle/create_trace` only as a one-line pointer | **Medium — no worked example** |
| 12 | Define ports or sources | `ports_and_sources.rst`, but on an empty DB and with one unverified signature | **Medium** (§3.4, §5.1) |
| 13 | Generate a cutout | `workflows/utilities/cutout.rst` (excellent parameter reference, no dataset-backed worked example with before/after counts) | **Medium** |
| 14 | Add an analysis setup (HFSS/SIwave) | `simulation_setups.rst` not verified this session | **Needs verification** |
| 15 | Apply a configuration file | `configuration/index.rst` (conceptual only in this session's read; 14 examples not individually re-verified) | **Needs verification of examples** |
| 16 | Validate a database (DRC, DC shorts) | `validation_and_drc.rst` — well covered | Low |
| 17 | Save and reopen a database, verify persistence | `save`/`save_as`/`close` documented; **no page shows the reopen-and-assert step** | **High** — directly required by this mission's core design principle |
| 18 | Export or hand off data downstream | `cli.rst` export commands documented; no Python-API equivalent walkthrough found | **Medium** |
| 19 | Compare database revisions | Not found anywhere | **High — no coverage found** |
| 20 | Batch-process multiple designs / run in CI | CLI exists; no batch-processing or CI-recipe page found | **High — no coverage found** |

---

## 9. Proposed information architecture

**[RECOMMENDATION]** Extend, do not replace, the existing `user_guide/index.rst` "I want to..." table
(§3.8) into two explicit, cross-linked paths, reusing every page verified to already exist in §6.

### Path A — "I want to..." (extend the existing table)

Add these currently-missing rows (mapped to top tasks 2, 7–9, 11, 17, 19, 20 from §8.2), each linking to
a **new** page proposed in §12/§19:

| Goal | Proposed destination |
|---|---|
| Open an existing EDB (not create a new one) and inspect a populated design | New: `getting_started/tutorial_open_inspect.rst` (§10, Tutorial 1) |
| Find primitives by layer, net, or type | New: `user_guide/geometry_and_connectivity.rst` (Track D) |
| Inspect pins and padstack instances on a net | Extend `user_guide/padstacks_and_vias.rst` once re-verified |
| Create or modify a trace/polygon | Extend `user_guide/geometry_and_connectivity.rst` |
| Save, close, reopen, and verify a modification persisted | New: `getting_started/tutorial_modify_and_verify.rst` (§10, Tutorial 4) |
| Compare two database revisions | New: `user_guide/design_comparison.rst` (Track H) |
| Batch-process multiple designs / run PyEDB in CI | New: `user_guide/production_automation.rst` (Track H) |
| Choose between the Python API, the configuration system, and the CLI | New: `getting_started/choosing_an_automation_style.rst` (cross-links Level 1/2/3 guidance, §13) |

### Path B — "I need to understand..." (net new; currently only the 6-term glossary exists, §6 row 19)

Extend `getting_started/glossary.rst` into a proper conceptual index, or add a parallel
`getting_started/concepts/index.rst` linking short (300–600 word) pages for each of this mission's
required Path-B topics. Proposed minimum set, each citing its authoritative source page:

1. What an EDB database contains → expand `glossary.rst` + link from `README.md` "What is EDB?"
2. Database/cell/layout/layer/net/primitive/component/pin/terminal/padstack relationships → **new**
   diagram page, `getting_started/object_model.rst` extended with a relationship diagram (§13.3)
3. Object ownership and lifetime → **new** subsection inside `object_model.rst` (currently answers
   "does it mutate/require saving" per-property but not general lifetime rules, §5.6/§14)
4. Live handles vs. copied data → **new**, tied directly to the `padstacks.pins` type-mismatch finding
   (§3.4) as a worked cautionary example
5. Units and unit conversion → **new**, directly motivated by `cutout.rst`'s own explicit unit table
   (already a good in-repo example of unit discipline to generalize, §14.1)
6. Transactions, saving, committing, rollback, closing → largely covered by `object_model.rst`
   "Database lifecycle" section already; promote it to a standalone linkable page
7. Object identity after layout modification → **new**, directly motivated by the P7 persona failure
   mode (§8.1) and this mission's Part 8 requirement — **currently zero coverage found**
8. Geometry tolerances → **new**, motivated by `cutout.rst`'s `extent_defeature`/`simple_pad_check`
   parameters (evidence such behavior exists and needs explaining)
9. Connectivity semantics → **new**, feeds Track D and the DRC/validation pages
10. EDB vs. AEDT project data / PyEDB vs. PyAEDT responsibilities → **new**, directly closes the gap
    found in §6 ("Unclear boundaries...")
11. Headless execution → partially covered in `getting_started/index.rst` ("gRPC ... can run ... without
    a GUI") — promote to an explicit statement in the new automation-style page
12. Software/EDB version compatibility → already well covered by
    `backend_compatibility_migration.rst` — link, do not duplicate
13. Public/advanced/low-level API levels → **new**, see §13
14. Logging and diagnostics → **new**, motivated by P6 persona and §16 troubleshooting

### Cross-linking rule (formalized from what the existing pages already do well, §4 item 4)

Every task page **must** link: (a) the conceptual page(s) it depends on, (b) the API-reference class(es)
it uses, (c) the "next recommended example," and (d) the relevant troubleshooting entries (§16). Every
conceptual page **must** link at least one task page that puts the concept into practice. Every
API-reference page (once the toctree gap in §5.5 is closed) **must** link back to at least one task page
per the governance rule in §18.

---

## 10. First 30 Minutes learning path

**[RECOMMENDATION]** This path assumes **Dataset 1: INTRO_BOARD** (§15) exists and ships with the
package or a documentation-referenced download. Until that dataset exists, this path cannot be fully
non-destructive-and-realistic at the same time — this is the direct reason dataset creation is this
review's top-ranked quick win (§23, QW-3). The five tutorials below extend, not replace,
`quick_start.rst` (kept as the "operate on an empty DB" reference) and reuse verified API calls only.

### Tutorial 1 — Open, inspect, and close

**Objective:** open an existing (not newly created) EDB, verify it opened, identify the active cell,
close it correctly.

```python
# Tutorial 1: Open, inspect, and close (uses INTRO_BOARD, see dataset spec in the review §15)
import shutil
import tempfile
from pathlib import Path

import pyedb
from pyedb import Edb

print(
    "PyEDB version:", pyedb.__version__
)  # [VERIFIED] pyedb.__init__ exports __version__

# 1. Locate the supplied training database (never edit the original).
source_path = Path("datasets/intro_board.aedb")  # shipped/downloaded read-only copy
assert source_path.exists(), f"Training dataset not found at {source_path}"

# 2. Create a non-destructive working copy in a temporary directory.
work_dir = Path(tempfile.mkdtemp(prefix="pyedb_tutorial1_"))
working_copy = work_dir / "intro_board.aedb"
shutil.copytree(source_path, working_copy)

# 3. Open the working copy (never the original).
edb = Edb(edbpath=str(working_copy), version="2026.1")

# 4. Verify it opened successfully and identify the active cell.
assert (
    edb.active_cell is not None
), "Expected an active cell after opening an existing design"
print("Active cell:", edb.active_cell)
print("Cell names:", edb.cell_names)

# 5. Close correctly.
edb.close()
print("Closed. Working copy left at:", working_copy)
```

**Expected output (values depend on the actual INTRO_BOARD dataset once built, §15):** a non-`None`
`active_cell`, a `cell_names` list with at least one entry, no traceback.
**Verification:** the `assert` statements are the deterministic check this mission's core design
principle requires — the tutorial fails loudly, not silently, if the dataset is missing or the open
failed. **Cleanup:** `work_dir` is a `tempfile.mkdtemp` directory; instruct the reader to
`shutil.rmtree(work_dir)` when done, or rely on OS temp-directory cleanup. **Common errors:**
`AssertionError` on the dataset path → dataset not downloaded/installed; `RuntimeWarning: AEDT is not
properly installed` → see `quick_start.rst`'s existing "Common problems" table (reuse, don't duplicate).
**Next:** Tutorial 2.

### Tutorial 2 — Understand the design hierarchy

**Objective:** inspect stackup layers, nets, components, pins, primitives, padstack definitions, and
padstack instances on the now-open INTRO_BOARD working copy (continuing from Tutorial 1, same session).

```python
# Tutorial 2: Understand the design hierarchy (continues Tutorial 1's `edb` session)

# Stackup: signal vs. dielectric layers
layers = (
    edb.stackup.layers
)  # [VERIFIED] dict[str, StackupLayer], object_model.rst + this session's grep
signal_layers = [name for name, layer in layers.items() if layer.type == "signal"]
dielectric_layers = [
    name for name, layer in layers.items() if layer.type == "dielectric"
]
print(
    f"{len(layers)} layers total: {len(signal_layers)} signal, {len(dielectric_layers)} dielectric"
)
assert len(layers) > 0, "INTRO_BOARD must define at least one layer"

# Nets
net_names = (
    edb.nets.netlist
)  # [VERIFIED] List[str], src/pyedb/grpc/database/nets.py:244
print(f"{len(net_names)} nets, first 5: {net_names[:5]}")
assert len(net_names) > 0, "INTRO_BOARD must define at least one net"

# Components
components = edb.components.instances  # dict[str, Component], per object_model.rst
print(f"{len(components)} components: {list(components.keys())[:5]}")

# Pins on the first component (if any)
if components:
    first_ref_des = next(iter(components))
    comp = edb.components[first_ref_des]
    print(f"Component {first_ref_des} at {comp.location}")

# Padstack instances (vias/pins) — [VERIFIED] Dict[str, PadstackInstance], keyed by NAME
# NOTE: object_model.rst currently (incorrectly) states dict[int, ...]; use .keys() defensively.
pin_names = list(edb.padstacks.pins.keys())
print(f"{len(pin_names)} padstack instances, first 5: {pin_names[:5]}")
```

**Object relationship diagram (text form, pending a rendered SVG/PNG asset — see backlog DOC-030):**

```
Database
 └── Cell (a.k.a. "design"; edb.active_cell / edb.cell_names)
      └── Layout
           ├── Stackup ── Layer* (signal | dielectric | non-stackup) ── Material
           ├── Net* ── Primitive* (Path/Trace, Polygon, Rectangle, Circle, Bondwire)
           ├── Component* ── Pin* (→ PadstackInstance)
           ├── PadstackDefinition* ── PadstackInstance* (placed vias/pins, on a Net, on a Layer range)
           └── Terminal* (→ Port | Source) ── created on a PadstackInstance, Pin, or Primitive edge
```

**Verification:** every `assert` above is a deterministic, non-exception-based check tied to the known
INTRO_BOARD object counts (§15 dataset spec fixes these counts once the dataset is built — this tutorial
should assert exact counts, not just `> 0`, once the dataset is finalized). **Common errors:**
`AttributeError` on `layer.type` if the dataset's layer objects use a different property name — this is
exactly the kind of assumption this review recommends verifying against source before publishing (see
§14, governance rule "verify against source before generating example code"). **Next:** Tutorial 3.

### Tutorial 3 — Query the design

**Objective:** demonstrate recommended selection patterns, and explicitly teach the missing-vs-empty
distinction this mission's core design principle requires.

```python
# Tutorial 3: Query the design (continues the same `edb` session)


# Retrieve a net by name — distinguish "found" from "not found".
def get_net_safely(edb, net_name):
    """Look up a net by name, returning None (not raising) if it does not exist."""
    if net_name in edb.nets.netlist:
        return edb.nets[net_name]
    return None


net = get_net_safely(edb, "GND")
if net is None:
    print(
        "Net 'GND' does not exist in this design. Available nets:",
        edb.nets.netlist[:10],
    )
else:
    print("Found net:", net.name)

# Find components by reference designator, with an explicit existence check.
ref_des = "U1"
if ref_des in edb.components.instances:
    comp = edb.components[ref_des]
    print(f"{ref_des} is at {comp.location}, part {comp.part_name}")
else:
    print(
        f"No component named {ref_des!r}. Known components: {list(edb.components.instances.keys())[:10]}"
    )

# Selecting objects on a layer (pattern shown; exact primitive-query API to be confirmed against
# source before publishing — flagged as [ASSUMPTION -- NEEDS VALIDATION] in this review, see backlog
# item DOC-050 "Track D primitive-by-layer query API verification").
```

**Diagnostics-on-failure pattern (recommended house style, net new):**

```python
def require_net(edb, net_name):
    """Return the net or raise a clear, actionable error listing available nets."""
    if net_name not in edb.nets.netlist:
        raise KeyError(
            f"Net {net_name!r} not found. {len(edb.nets.netlist)} nets available, e.g. {edb.nets.netlist[:5]}"
        )
    return edb.nets[net_name]
```

**Verification:** the tutorial explicitly contrasts a `None`/message result (query pattern) against a
raised, diagnostic-rich `KeyError` (fail-fast pattern) and asks the reader to choose deliberately —
directly satisfying this mission's "distinguishing a missing object from an empty result" and "reporting
useful diagnostics when a query fails" requirements. **Next:** Tutorial 4.

### Tutorial 4 — Make one safe modification

**Objective:** modify, validate in-memory, save to a new location, close, reopen, and assert the change
persisted — the exact sequence this mission's core design principle demands and that §8.2 top task 17
identifies as currently missing from every existing page.

```python
# Tutorial 4: Make one safe modification, then verify it survives a save/reopen cycle.
from pyedb import Edb

# Continuing from Tutorial 1's working_copy path (a fresh copy is used here for a clean run).
edb = Edb(edbpath=str(working_copy), version="2026.1")

layers_before = set(edb.stackup.layers.keys())
edb.stackup.add_layer(
    layer_name="TEST_LAYER", layer_type="signal", material="copper", thickness="20um"
)
layers_after = set(edb.stackup.layers.keys())

# Validate the in-memory result before saving anything.
assert "TEST_LAYER" in layers_after, "Layer was not added in memory"
assert layers_after - layers_before == {"TEST_LAYER"}, "Unexpected extra/missing layers"

# Save to a NEW location — the working copy from Tutorial 1 is left untouched on disk until this line.
output_path = work_dir / "intro_board_modified.aedb"
edb.save_as(str(output_path))
edb.close()

# Reopen the saved output and assert the modification persisted.
edb_reopened = Edb(edbpath=str(output_path), version="2026.1")
assert (
    "TEST_LAYER" in edb_reopened.stackup.layers
), "Modification did not persist after save/reopen"
print("Verified: TEST_LAYER persisted after save_as + reopen.")
edb_reopened.close()
```

**Verification:** two `assert` blocks — one in-memory (before save), one post-reopen (after save) —
directly implementing this mission's "assert that the modification persisted" requirement. **Cleanup:**
close both `Edb` sessions explicitly (shown); remove `work_dir` when finished with the whole tutorial
series. **Common errors:** if the second `assert` fails but the first passed, the defect is in
`save_as`/persistence, not in the mutation — this diagnostic separation is the pedagogical point of the
tutorial. **Next:** Tutorial 5.

### Tutorial 5 — Validate and report

**Objective:** produce a machine-readable report with the exact fields this mission specifies.

```python
# Tutorial 5: Validate and report
import json
import pyedb
from pyedb import Edb

edb = Edb(edbpath=str(output_path), version="2026.1")

report = {
    "database_path": str(output_path),
    "cell_name": str(edb.active_cell),
    "pyedb_version": pyedb.__version__,
    "layer_count": len(edb.stackup.layers),
    "net_count": len(edb.nets.netlist),
    "component_count": len(edb.components.instances),
    "padstack_instance_count": len(edb.padstacks.pins),
    "dc_shorts_found": len(edb.layout_validation.dc_shorts()),
}
report["validation_result"] = "PASS" if report["dc_shorts_found"] == 0 else "FAIL"

print(json.dumps(report, indent=2))
edb.close()
```

**Verification:** the report itself is the deterministic artifact; a CI job can `assert
report["validation_result"] == "PASS"` or diff `report` against an expected baseline (this is the seed
of the CI strategy in §17). **Next steps:** link to Track B (Design exploration) and Track H (Production
automation) for the intermediate/advanced continuation of this path.

**Total estimated time:** ~25–30 minutes for a reader who already completed `quick_start.rst`'s
installation/verification steps, consistent with this mission's "approximately 30 minutes" requirement,
assuming Dataset 1 (§15) is available and pre-downloaded.

---

## 11. Standard example specification

**[RECOMMENDATION]** Formalize the template already implicitly used by `stackup_and_materials.rst`,
`components_and_nets.rst`, `ports_and_sources.rst`, and `validation_and_drc.rst` (§4 item 4), extended
with the sections those pages are missing.

### 11.1 Required sections (every new/rewritten example page)

1. **What you will learn** (1–2 sentences) — currently implicit in the page title/intro; make explicit.
2. **When to use this workflow** — currently missing on all 4 verified pages; add.
3. **Prerequisites** — already present on all 4 verified pages.
4. **Software and license requirements** — currently deferred to `quick_start.rst` only; **add an
   explicit one-line restatement with a link** ("Requires a licensed local AEDT 2026.1+ installation;
   see Quick start prerequisites") to every workflow page so a reader arriving via search sees it.
5. **Input design and provenance** — currently absent everywhere except "creates an empty DB"; once
   §15's datasets exist, every page states which dataset it uses and links to its provenance record.
6. **API concepts introduced** — currently folded into "Public API entry points"; keep, but explicitly
   separate "concept" (e.g., "a port needs a reference terminal") from "entry point" (the class name).
7. **Complete executable example** — already present on all 4 verified pages; **add the reopen-and-
   verify step** (currently only Tutorial 4 in §10 does this).
8. **Expected output** — currently prose ("Expected result") on all 4 verified pages; **upgrade to a
   literal `assert`-bearing code block** wherever the return shape is deterministic (net names, layer
   counts), keeping prose only for genuinely environment-dependent values (paths, hashes).
9. **Deterministic verification** — net new as a *labeled* section; currently blended into "Expected
   result" prose. Separating it makes it scannable and CI-extractable (§17).
10. **Common failures and diagnostics** — already present as "Common problems" on all 4 verified pages;
    keep the name or rename for consistency — recommend keeping "Common problems" since it is already
    established across 4+ pages and changing it has zero benefit and real churn cost.
11. **Cleanup** — currently implicit (`edb.close()` is shown, but not called out as its own step);
    **add an explicit "Cleanup" subsection** even when it is one line, so automated example-linting (§17)
    can grep for it.
12. **Next recommended example** — currently folded into "See also"; keep "See also" but ensure the
    *first* bullet is always the single best next page (an ordering convention, not a new section).
13. **Related conceptual pages** — currently folded into "See also"; same recommendation as #12.
14. **Related API-reference pages** — currently present via `:attr:`/`:class:` Sphinx cross-references
    in "Public API entry points"; keep.
15. **Version compatibility notes** — currently "Backend and version notes" on all 4 verified pages;
    keep the existing name.

**Net change recommended:** add sections 2, 4 (as an explicit restatement), 5 (once datasets exist), and
9 (split out of "Expected result") to the existing template; do not rename sections 10/12/13/15, since
they already exist consistently across 4+ pages and renaming has negative ROI (churn without reader
benefit) per this mission's own maintainability principle.

### 11.2 Required phase separation (already followed; formalize as a lint rule)

Every example's "Complete executable example" code block must contain, in this order, each as a visibly
separate block or comment-delimited section:

1. Define inputs (paths, dataset references, parameters with units)
2. Create a temporary or working copy
3. Open the database
4. Inspect or modify the layout
5. Validate the result (in-memory assertion)
6. Save the database (`save_as` to a new path in beginner/intermediate examples)
7. Close resources
8. Reopen and verify, when persistence is relevant to the lesson

Verified today: steps 1, 3, 4, 6, 7 are present on all 4 checked pages; step 2 (working copy) is
implicit only via "creates a new empty DB in a temp dir" rather than "copies a supplied dataset"; step 5
(in-memory assertion) is present as prose, not as a Python `assert`; step 8 (reopen-and-verify) is
**absent from every existing page** and is the single most important structural addition this review
recommends (directly implements this mission's core design principle).

### 11.3 Beginner-example negative constraints (audit checklist, apply to every new page)

| Constraint | Status on the 4 verified pages today |
|---|---|
| Must not overwrite the supplied source database | ✅ (`save_as` used everywhere) |
| Must not use private attributes/undocumented methods | ✅ verified (no `_`-prefixed access found) |
| Must not depend on unexplained environment state | ⚠️ partial — AEDT/license requirement not restated per-page (§11.1 item 4) |
| Must not conceal operations in large helper functions | ✅ (all examples are flat, linear scripts) |
| Must not combine unrelated workflows | ✅ (each page is single-domain) |
| Must not require inferring success from absence of exceptions | ❌ **not yet met** — no `assert`-based verification exists on any of the 4 pages; only prose "Expected result" |
| Must not contain unexplained/unitless geometry values | ✅ (all dimensions use explicit unit strings, e.g. `"35um"`, `"5mil"`) |
| Must not omit resource cleanup | ✅ (`edb.close()` shown) |
| Must not use constructors/methods not validated against current API | ⚠️ mostly ✅, with one confirmed exception (`create_port` signature, §3.4) and one confirmed type-mismatch (`padstacks.pins`, §3.4) |

---

## 12. Progressive example tracks

**[RECOMMENDATION]** Each track maps to an existing page (extend it) or a proposed new page (build it),
using the standard template from §11. Effort/CI columns feed §19's roadmap and §20's backlog.

### Track A — Database fundamentals

| Level | Example | Status |
|---|---|---|
| Beginner | Open an existing database (Tutorial 1, §10) | **New** — no existing page opens a pre-supplied dataset |
| Beginner | Create a working copy before editing | **New**, folded into Tutorial 1 |
| Beginner | Inspect project metadata (cell names, active cell) | Partially covered by `quick_start.rst` |
| Beginner | Save and close (including context manager) | Covered — `quick_start.rst` "Using a context manager" |
| Intermediate | Handle an invalid path (`FileNotFoundError`/similar) | **New** — no negative-path example found anywhere |
| Intermediate | Handle an unsupported EDB/AEDT version | Partially — `quick_start.rst` "Common problems" table documents the error text but shows no try/except pattern |
| Intermediate | Recover from a failed open (retry/diagnostic pattern) | **New** |
| Required dataset | INTRO_BOARD (§15) | To be built |
| CI strategy | Run against a real small AEDB fixture in the self-hosted system-test runners (`tests/system`), assert exit code and object counts; license-dependent, so gate as `system` not `unit` (mirrors existing `pytest.mark.system`) | Net new CI wiring, see §17 |

### Track B — Design exploration

| Level | Example | Status |
|---|---|---|
| Beginner | List and classify layers | Tutorial 2 (§10); extend `stackup_and_materials.rst` |
| Beginner | List nets | `components_and_nets.rst` — covered |
| Beginner | Identify power/ground nets | **New** — no net-classification-by-role example found (the configuration-API inventory row "Net classification and live querying" suggests this exists in the *configuration* track already — cross-link rather than duplicate, see `example_inventory.rst` row 4) |
| Intermediate | Find components, inspect pins | Partially — component lookup covered; pin inspection not verified this session (`padstacks_and_vias.rst`) |
| Intermediate | Inspect connectivity | **New** |
| Intermediate | Inspect geometry/bounding boxes | **New** |
| Advanced | Produce a full design inventory report | Tutorial 5 (§10) is the beginner seed; extend to a richer report (per-layer area, per-net pin count) for the advanced tier |
| Required dataset | INTRO_BOARD, PRODUCTION_BOARD (§15) | To be built |
| CI strategy | Assert exact object counts against the dataset's documented "expected validation results" (§15) | Net new |

### Track C — Stackup and materials

| Level | Example | Status |
|---|---|---|
| Beginner | Read the stackup | `stackup_and_materials.rst` step 1 — covered |
| Beginner | Understand stackup ordering | **New** — not addressed in the verified page |
| Intermediate | Add a layer | `stackup_and_materials.rst` step 3 — covered |
| Intermediate | Remove a layer safely | **New** — no removal example found |
| Intermediate | Change layer thickness | Partially — `object_model.rst` shows `edb.stackup["TopLayer"].thickness = "0.035mm"` in the `Edb` factory docstring, not in the user-guide page itself; **promote into `stackup_and_materials.rst`** |
| Intermediate | Assign conductor/dielectric materials | `stackup_and_materials.rst` step 2 — covered |
| Advanced | Create/modify material definitions | Partially covered (`add_conductor_material`/`add_dielectric_material` shown; editing an existing material's properties not shown) |
| Advanced | Validate units | **New** — directly needed given the Part-8 unit-handling requirement |
| Advanced | Validate layer ordering | **New** |
| Advanced | Apply stackup changes via configuration | Covered conceptually by "Stackup materials and layers" config example (`example_inventory.rst` row 12) — cross-link, do not duplicate |
| Required dataset | STACKUP_TRAINING (§15) | To be built |
| CI strategy | Assert layer count/order/material before and after each mutation; assert `ValueError` is raised for a duplicate material name (already documented behavior, `stackup_and_materials.rst` "Common problems" row 1) | Net new |

### Track D — Geometry and connectivity

| Level | Example | Status |
|---|---|---|
| Beginner | Find primitives on a net | **New — no coverage found anywhere in this session's reads** (§8.2 rank 8) |
| Intermediate | Query primitives by layer and type | **New** |
| Intermediate | Create a trace | Mentioned only as a one-line pointer in `object_model.rst` (`edb.modeler.create_trace(...)`); **no worked example exists** |
| Intermediate | Create a polygon | Same as above |
| Intermediate | Modify geometry | **New** |
| Intermediate | Place a via using an existing padstack | Not verified this session (`padstacks_and_vias.rst`) |
| Advanced | Create a padstack definition | Not verified this session |
| Advanced | Validate connectivity | **New** |
| Advanced | Find disconnected/isolated objects | **New** — directly needed for the CONNECTIVITY_TRAINING dataset (§15) |
| Advanced | Explain geometric tolerance behavior | **New**, ties to Path-B concept #8 (§9) |
| Required dataset | INTRO_BOARD, CONNECTIVITY_TRAINING (§15) | To be built |
| CI strategy | Assert known disconnection/isolation counts against CONNECTIVITY_TRAINING's documented expected results | Net new |

### Track E — Components and models

| Level | Example | Status |
|---|---|---|
| Beginner | Find and classify components | `components_and_nets.rst` — covered (lookup); classification (RLC vs. IC vs. discrete) not shown |
| Beginner | Inspect pins | Not verified this session |
| Intermediate | Assign component types | **New** |
| Intermediate | Assign RLC properties | **New** — mentioned only via `comp.set_property("Value", "10nH")` in the `Edb` factory docstring Examples, not in a user-guide page |
| Advanced | Associate package/component models | Partially — "Assign models from the Ansys vendor component library" config example exists (`example_inventory.rst` row 14); no direct-API equivalent verified |
| Advanced | Identify missing component data | **New** |
| Advanced | Validate model assignments | **New** |
| Advanced | Export a component audit report | **New** — natural extension of Tutorial 5 (§10) |
| Required dataset | INTRO_BOARD, PRODUCTION_BOARD (§15) | To be built |
| CI strategy | Assert exact component/pin counts; assert a known-missing-model component is flagged | Net new |

### Track F — Ports, sources, and simulation preparation

| Level | Example | Status |
|---|---|---|
| Beginner | Explain terminal/port/source/reference concepts | **New**, ties to Path-B concept list (§9) |
| Intermediate | Single-ended port | `ports_and_sources.rst` step 1 — covered, but on an empty DB (§5.1) and with an unverified signature (§3.4) |
| Advanced | Differential port | Config-API example exists ("Differential wave port", `example_inventory.rst` row 6); no direct-API user-guide equivalent verified |
| Intermediate | Select reference conductors | **New** — directly needed for the §16 troubleshooting entry "reference conductor cannot be identified" |
| Intermediate | Voltage/current sources | `ports_and_sources.rst` step 3 — covered |
| Intermediate | Analysis setups | Not verified this session (`simulation_setups.rst`) |
| Advanced | Generate a cutout | `workflows/utilities/cutout.rst` — excellent parameter reference, no dataset-backed before/after worked example |
| Advanced | Validate setup completeness | **New** — directly needed before license-dependent solve (this mission's Part 11 requirement) |
| Advanced | Export/hand off the prepared model | Partially — CLI `export` commands documented (`cli.rst`); no Python-API walkthrough |
| Advanced | Clarify when PyAEDT is required | Partially — `example_inventory.rst`'s "PyAEDT + PyEDB combined examples" section draws the line at "requires a full AEDT solve"; promote this single sentence into the Path-B boundary page (§9) |
| Required dataset | PORTS_TRAINING (§15) | To be built |
| CI strategy | Assert port/terminal creation succeeded and reference net resolved, **without** invoking a solver (license-free preparation-only test, per this mission's Part 11) | Net new — this is the single most important CI-strategy addition for the SI/PI persona (P4) |

### Track G — Configuration-driven workflows

| Level | Example | Status |
|---|---|---|
| Beginner | Configuration concepts | `configuration/index.rst` — covered well |
| Beginner | Export configuration from an existing design | Not independently re-verified this session (`configuration_api_guide.rst` unread) |
| Beginner | Make one configuration change, apply it | 14 examples cataloged in `example_inventory.rst`; individual pages not re-verified this session |
| Intermediate | Validate the result | **Needs verification** whether any example shows post-apply assertion |
| Intermediate | Configuration schemas and validation | `configuration/file_architecture.rst` not read this session — **needs verification** |
| Intermediate | Precedence rules (config vs. direct API) | **New** — flagged as a gap in §5.7 |
| Intermediate | Idempotency | **New** — flagged as a gap in §5.7 |
| Advanced | Mixing configuration and direct API calls | Conceptually stated as "complementary" in `configuration/index.rst`; no worked example combining both in one script verified |
| Advanced | Configuration use in CI | **New** |
| Advanced | Versioning configuration files | **New** — natural fit since config files are already plain JSON/TOML (`configuration/index.rst` explicitly calls out `git diff` friendliness) |
| Advanced | Diagnosing partial/failed application | **New** — flagged as a gap in §5.7, directly required by §16 |
| Required dataset | INTRO_BOARD (export), STACKUP_TRAINING (apply) | To be built |
| CI strategy | This track is the **most CI-friendly** of all eight tracks because configuration files are plain data — assert round-trip equality (export → apply to a copy → export again → diff) as a strong regression test | Net new, high leverage |

### Track H — Production automation

| Level | Example | Status |
|---|---|---|
| Beginner | Structured logging | **New** |
| Beginner | Deterministic outputs | Tutorial 5 (§10) is the seed |
| Intermediate | Exception handling | **New** |
| Intermediate | Temporary working directories | Modeled already in `quick_start.rst`/Tutorial 1 (§10) via `tempfile` |
| Intermediate | Batch processing | **New — no coverage found** (§8.2 rank 20) |
| Intermediate | Idempotent scripts | **New** |
| Advanced | Restart/recovery strategies | **New** |
| Advanced | Regression checks / design comparison | **New — no coverage found** (§8.2 rank 19) |
| Advanced | Performance considerations | Partially — `troubleshooting.rst` already documents "Script runs slowly when creating many geometries" with a concrete recommendation (batch operations) — good existing content to cross-link |
| Advanced | Memory/object lifetime | **New**, ties to Path-B concept #7 (§9) |
| Advanced | Parallelism limitations | **New** — especially relevant given the gRPC single-service-per-machine model; **[ASSUMPTION — NEEDS VALIDATION]** whether multiple concurrent `Edb` sessions against one `ansys-edb-core` service are supported — not verified in this session |
| Advanced | CI execution | CLI (`cli.rst`) is a good foundation; no end-to-end CI recipe page found |
| Advanced | Artifact and log retention | **New** |
| Required dataset | PRODUCTION_BOARD (§15) | To be built |
| CI strategy | This track *is* the CI strategy (§17) — its own examples should be the literal scripts CI reuses to test the rest of the documentation | Net new, foundational |

---

## 13. API abstraction and mental model

### 13.1 Do the three levels already exist, and are they distinguished today?

**[VERIFIED, partially]** The three levels this mission asks about **do exist in the code** but are
**not explicitly named or contrasted anywhere in the documentation** as a deliberate three-tier system:

- **Level 1 (Workflow APIs):** the CLI (`cli.rst`) and the configuration system
  (`configuration/index.rst`) both function as Level 1 today — `configuration/index.rst` explicitly
  states its goal is that "Users can be productive in minutes without needing to understand the
  underlying EDB object model or the PyEDB API surface" (line 69–70, verified this session). This is
  good evidence Level 1 already exists in spirit; it is just not labeled "Level 1" or cross-referenced
  as such from the object-model page.
- **Level 2 (Domain object APIs):** this is exactly what `object_model.rst`'s 10 documented properties
  (`stackup`, `materials`, `components`, `nets`, `padstacks`, `excitation_manager`, `modeler`/`layout`,
  `simulation_setups`, `configuration`, `layout_validation`) represent. **[VERIFIED]**
- **Level 3 (Low-level EDB access):** referenced obliquely — `configuration/index.rst` line 82–85 names
  four scenarios that "demand a level of granularity that goes beyond what a declarative system can
  reasonably express" (fine-grained geometry, net-class scripting, dynamic layout modification, deep
  object-level inspection) and recommends "the PyEDB Python APIs directly" — but this still describes
  Level 2, not a documented Level 3 escape hatch into raw `ansys-edb-core` objects. **No page in this
  session's reads explicitly shows how to drop from Level 2 into a lower-level `ansys-edb-core` call
  when a high-level wrapper is missing a capability.** This is the concrete gap behind persona P7's
  documented need (§8.1) and this mission's explicit "low-level escape route" requirement.

### 13.2 Proposed level-selection guide **[RECOMMENDATION]**

Add a short decision guide (new page, `getting_started/choosing_an_automation_style.rst`, already
proposed in §9's Path-A table) with this explicit structure:

| Question | Answer → level |
|---|---|
| Can I express my entire task as "what the design should look like" (a static description)? | Yes → **Level 1: configuration file** |
| Do I need to react to values already in the design (existing nets, existing components) while building the description? | Yes → **Level 1: configuration builder API** (`create_config_builder`, session-aware `get()` helpers per `configuration/configuration_api_guide.rst`) |
| Do I need to create/query/modify individual layers, nets, components, padstacks, ports, or setups imperatively? | Yes → **Level 2: `edb.<domain>` properties** (`object_model.rst`) |
| Does my task require a capability not exposed by any `edb.<domain>` method, or direct access to the underlying `ansys-edb-core` object? | Yes → **Level 3: low-level EDB access** — document the actual escape hatch (e.g., a `.` attribute exposing the raw `ansys.edb.core` object) once verified against source; **flagged as [ASSUMPTION — NEEDS VALIDATION]: the exact name of this escape-hatch attribute on `pyedb.grpc.edb.Edb` was not confirmed in this session and must be verified against source before publishing** |

### 13.3 Mental model diagram (text form; render as SVG/PNG for the actual page — backlog DOC-030)

```
                          ┌─────────────────────────────┐
                          │   Level 1: Workflow APIs     │
                          │  CLI (pyedb ...) │ Config    │
                          │  files/builder (edb.config-  │
                          │  uration.*)                  │
                          └───────────────┬───────────────┘
                                          │ delegates to
                          ┌───────────────▼───────────────┐
                          │  Level 2: Domain object APIs   │
                          │  edb.stackup / .materials /    │
                          │  .components / .nets /         │
                          │  .padstacks / .excitation_     │
                          │  manager / .modeler /          │
                          │  .simulation_setups /          │
                          │  .layout_validation             │
                          └───────────────┬───────────────┘
                                          │ wraps
                          ┌───────────────▼───────────────┐
                          │ Level 3: Low-level EDB access   │
                          │ ansys-edb-core gRPC objects      │
                          │ (escape hatch — verify exact     │
                          │ attribute name before publishing)│
                          └─────────────────────────────────┘
```

### 13.4 Per-object documentation contract (extend the existing "8 questions" template)

`object_model.rst` already answers 8 questions per Level-2 object (§3.4). **[RECOMMENDATION]** extend to
the full set this mission's Part 7 requires, adding 3 more questions per object where not already
covered: **intended audience** (which persona, §8.1, is this object for), **error behavior** (exception /
`None` / `False` / empty collection — see §14.3), and **recommended Level-1 alternative, if one exists**
(e.g., `edb.stackup.add_layer` → "or use the `stackup` configuration section"). This directly closes the
"choose the correct API level" requirement without inventing a new template — it is an incremental
extension of a template that is already proven to work across 10 properties.

---

## 14. API-reference improvements

### 14.1 Units — existing good practice to generalize

**[VERIFIED]** `workflows/utilities/cutout.rst`'s "Complete parameter reference" table (lines 54–140) is
the **best existing example in the repository** of explicit unit discipline: every parameter's type,
default, and unit (or unit-override parameter, e.g. `custom_extent_units`) is stated in one table, with
an explicit top-line rule: *"Defaults are shown in bold; physical values are in metres unless a `*_units`
parameter is supplied."* **[RECOMMENDATION]** generalize this exact table format to every other
parameter-heavy method across the codebase (`stackup.add_layer`, `excitation_manager.create_port`,
`simulation_setups.create_siwave_setup`, etc.) as the standard "Parameters" table format in docstrings
and user-guide pages alike. This is a template-reuse recommendation, not a new invention — the pattern
already exists and works.

Verified unit-acceptance pattern from `quick_start.rst`/`stackup_and_materials.rst`: dimensions are
passed as **strings containing units** (`thickness="35um"`, `"5mil"`), not bare floats — this is good,
consistent practice across every example checked this session. **[VERIFIED]** No example in this
session's reads passed a bare, unitless numeric geometry value, satisfying this mission's explicit
"avoid unexplained bare numeric geometry values" requirement already, for the pages checked.

### 14.2 Object lifetime — partially documented, needs consolidation

**[VERIFIED, partial]** `object_model.rst`'s "Database lifecycle" section (lines 212–224) already
answers 4 of this mission's 7 required lifetime questions (what happens on close, on `save`/`save_as`,
using the context manager, and — implicitly — that unsaved changes are lost on `close()` for the gRPC
backend). **Not found anywhere in this session's reads:**
- What happens when the selected cell changes (multi-cell databases)
- What happens when an object is deleted (does a held reference become invalid?)
- What happens when the layout is "rebuilt" (e.g., after a cutout)
- What happens after a transaction is committed (if PyEDB exposes an explicit transaction concept —
  **[ASSUMPTION — NEEDS VALIDATION]**, not confirmed to exist in the API surface reviewed this session)
- What a cutout returns, precisely, when it produces a new design/database (`workflows/utilities/
  cutout.rst`'s `open_cutout_at_end` parameter — **"Load the resulting .AEDB into the active `edb`
  object. Default True"** — is the closest existing answer, and it is a good one, but it does not state
  what happens to object references held from *before* the cutout ran)

**[RECOMMENDATION]** add these 5 missing answers as a new "Object lifetime and identity" subsection of
`object_model.rst`, directly citing the `cutout.rst` `open_cutout_at_end` behavior as the one concrete,
verified example to build the explanation around.

### 14.3 Error behavior — inconsistent across verified pages, needs a stated policy

Cross-referencing the 4 pages checked in full this session:

| API family | Verified failure mode | Source |
|---|---|---|
| `edb.nets["X"]` / `edb.components["X"]` | `KeyError` | `components_and_nets.rst` "Common problems" row 1 |
| `edb.materials.add_material(...)` with a duplicate name | `ValueError` | `stackup_and_materials.rst` "Common problems" row 1 |
| `edb.stackup.add_layer(...)` with a non-signal/dielectric `layer_type` | Silent — object created in `non_stackup_layers`, not an error | `stackup_and_materials.rst` "Common problems" row 2 |
| `edb.excitation_manager` accessed with no open database | Returns `None` (not an exception) | `ports_and_sources.rst` "Common problems" row 1, `object_model.rst` |
| `edb.layout_validation.illegal_net_names(fix=True)` not saved | Silent — mutates in-memory only, no warning at call time | `validation_and_drc.rst` "Common problems" row 1 |
| `Rules.parse_file(...)` | Does not exist (`AttributeError`), despite looking plausible from naming convention | `validation_and_drc.rst` "Common problems" row 2 |
| Version not installed | `RuntimeWarning` (not an exception subclass typically caught the same way as `RuntimeError`) | `design_types.py` lines 341, 346, 354, 359 — **[VERIFIED]** directly from source: `raise RuntimeWarning(...)` |
| gRPC requested below 2026.1 | `RuntimeError` | `design_types.py` line 386 — **[VERIFIED]** |

**Finding:** PyEDB's verified error behavior already spans **`KeyError`, `ValueError`, `RuntimeError`,
`RuntimeWarning`, silent `None` returns, and silent in-memory-only mutation with no warning** — six
distinct failure modes across roughly a dozen checked call sites, with no stated house rule for which
family should apply where. **[VERIFIED finding]**. Notably, `design_types.py` line 341/346 raises
`RuntimeWarning` via `raise` (not `warnings.warn`), which means it behaves as an exception at the call
site despite the misleading "Warning" class name — a subtlety worth flagging explicitly in the API
reference since a reader might reasonably assume `RuntimeWarning` is only ever emitted via `warnings.warn`
and can be ignored.

**[RECOMMENDATION]** Publish an explicit "Error behavior policy" page (or a section of
`object_model.rst`) stating, as a governance rule going forward (§18): lookups by name raise `KeyError`;
validation of new input raises `ValueError`; environment/version problems raise `RuntimeError` or
`RuntimeWarning` (document that PyEDB's `RuntimeWarning` usage here is exception-like, not
`warnings.warn`-based); accessors that depend on session state return `None` when that state is absent
rather than raising; fix-capable validation methods (`illegal_net_names(fix=True)`) mutate silently and
require an explicit `save()`/`save_as()` afterward (already true, already documented per-page — just not
stated as a cross-cutting rule).

### 14.4 API-reference navigation completeness

Restated from §5.5/§7 (not re-derived): wire `pyedb.workflows.*`, `pyedb.libraries.*`,
`pyedb.siwave_core.*`, and `pyedb.cli` into the main `grpc_api/index.rst` toctree, or explicitly document
why each is intentionally excluded (per `doc_audit.md`'s own P1 recommendation #9, not yet closed per
this session's re-check of `grpc_api/index.rst`'s toctree scope — **[NEEDS RE-VERIFICATION]**, `grpc_api/
index.rst` itself was not re-read in full in this session, only cited from `doc_audit.md`).

---

## 15. Training dataset specification

**[RECOMMENDATION — net new.]** No dataset meeting any of these specifications currently exists in
`doc/source/**` or is referenced from it (§3.7). `tests/example_models/**` contains **unrelated internal
test fixtures** (large, undocumented, no stated license/provenance for teaching purposes) that must not
be conflated with these purpose-built datasets — reusing an internal test fixture as a public teaching
asset without an explicit provenance/license review would be a governance risk, not a shortcut.

| Field | Dataset 1: INTRO_BOARD | Dataset 2: STACKUP_TRAINING | Dataset 3: CONNECTIVITY_TRAINING | Dataset 4: PORTS_TRAINING | Dataset 5: PRODUCTION_BOARD |
|---|---|---|---|---|---|
| Purpose | First 30 Minutes path (§10), Tracks A/B/D beginner tier | Track C (stackup/materials) | Track D connectivity/validation lessons | Track F (ports/sources) | Tracks B/E/H intermediate–advanced tier |
| Contents | 2 signal + 2 reference layers, ~5 nets, 2–3 components, several vias, one differential pair | 4+ conductor/dielectric materials, 6+ layers, at least one layer with intentionally incomplete material data | 1 disconnected trace, 1 isolated via, 1 ambiguous net condition (e.g., a net with zero primitives) | Structures for 1 single-ended port, 1 differential pair, explicit reference-conductor geometry | Moderate realistic complexity: dozens of nets/components, multiple padstack definitions |
| Provenance | **To be authored** — synthetic, Ansys-owned, purpose-built (not derived from a customer board) | Synthetic | Synthetic | Synthetic | Synthetic or a sanitized/simplified derivative of an existing internal reference design, subject to legal/IP review before publication |
| License | MIT (matches repository license, `LICENSE`) — **must be explicitly confirmed by the maintainers before publishing**, since `tests/example_models/**` fixtures may carry different terms | Same | Same | Same | Same, with extra IP-review step given "moderately realistic" scope |
| Units | Millimeters (layout), micrometers (layer thickness) — stated explicitly on the dataset's own documentation page | Micrometers (thickness) | Millimeters | Millimeters | Millimeters |
| Coordinate system | Standard EDB right-handed XY, origin at board corner — **[ASSUMPTION — NEEDS VALIDATION]**, exact EDB coordinate convention not independently re-verified against source in this session | Same | Same | Same | Same |
| Expected object counts | Fixed, exact numbers stated once built (e.g., "5 layers, 6 nets, 3 components, 9 padstack instances") — tutorials in §10 must assert these exact numbers, not just `> 0` | Fixed | Fixed (e.g., "exactly 1 disconnected trace, 1 isolated via") | Fixed | Fixed |
| Expected validation results | Zero DC shorts, zero DRC violations (a "clean" board for teaching happy-path queries) | At least one material intentionally incomplete → `layout_validation` or a dedicated stackup-validation check should report exactly that one finding | Exactly the disconnection/isolation findings the dataset was built to contain — nothing more, nothing less | Port/terminal creation succeeds on the intended structures; reference-conductor resolution succeeds | A small number of intentionally seeded issues (missing model, orphaned pin) for the "identify missing component data" lesson (Track E) |
| File size | Target < 5 MB (small enough to ship in the repository or as a lightweight CI/download artifact) | Target < 5 MB | Target < 2 MB | Target < 5 MB | Target < 50 MB (still small relative to `tests/example_models/si_verse/ANSYS-HSD_V1.aedb`) |
| Version compatibility | Built/validated against AEDT 2026.1 (gRPC default) at minimum; **[ASSUMPTION — NEEDS VALIDATION]** whether it also needs a DotNet-backend-compatible variant given the backend's deprecated-but-supported status | Same | Same | Same | Same |
| Examples that consume it | Tutorials 1–5 (§10), Track A/B beginner examples | Track C examples | Track D connectivity examples, Track H "regression checks" | Track F examples | Track B/E/H intermediate–advanced examples |
| Maintenance owner | **To be assigned** — recommend the same owner as the "Database fundamentals" workflow domain (§18) | Stackup/materials workflow owner | Geometry/connectivity workflow owner | Ports/sources workflow owner | Production-automation workflow owner |

**Build sequencing recommendation:** build INTRO_BOARD first (unblocks §10's entire First-30-Minutes
path, the single highest-leverage quick win, §23 QW-3), then PORTS_TRAINING (unblocks Track F, the
SI/PI persona's top task), then STACKUP_TRAINING and CONNECTIVITY_TRAINING (unblock Tracks C/D), then
PRODUCTION_BOARD last (highest effort, needed only for intermediate/advanced tiers).

---

## 16. Troubleshooting architecture

**[RECOMMENDATION, restructuring `getting_started/troubleshooting.rst`]** The existing page (§5.4) is
accurate but flat (5 entries). Below, every symptom this mission requires is cross-checked against
what currently exists; new entries are marked accordingly. Each existing entry is kept verbatim (do not
re-litigate content that is already correct) and re-homed under the new symptom taxonomy.

| # | Symptom | Currently covered? | Diagnostic evidence |
|---|---|---|---|
| 1 | The database does not open | Partially — "Cannot connect to ansys-edb-core service", "TRANSIENT_FAILURE", "permission errors" cover *connection*-level failures; a bad `edbpath`/nonexistent-file case is **not covered** | `troubleshooting.rst` rows 1–3 |
| 2 | The active layout is missing | **Not covered** | — |
| 3 | A net lookup returns no result | **Not covered as troubleshooting**, though `components_and_nets.rst` "Common problems" documents the `KeyError` behavior — cross-link rather than duplicate | `components_and_nets.rst` row 1 |
| 4 | A component or primitive lookup is empty | Same as #3 | `components_and_nets.rst` row 1 |
| 5 | A modification does not persist | Partially — `validation_and_drc.rst` "Common problems" row 1 covers this for `fix=True` calls specifically; not generalized | `validation_and_drc.rst` row 1 |
| 6 | A saved database cannot be reopened | **Not covered** | — |
| 7 | Layer order becomes invalid | **Not covered** | — |
| 8 | Material assignment fails | Partially — `stackup_and_materials.rst` "Common problems" rows 1 and 3 | `stackup_and_materials.rst` |
| 9 | A port or terminal cannot be created | Partially — `ports_and_sources.rst` "Common problems" row 1 (`excitation_manager` is `None`) | `ports_and_sources.rst` |
| 10 | A reference conductor cannot be identified | **Not covered** | — |
| 11 | A cutout omits expected geometry | **Not covered** — `cutout.rst`'s extensive parameter table documents *inputs* (e.g. `include_voids_in_extents`, `include_partial_instances`) that affect this, but no troubleshooting entry connects "my cutout is missing X" to "check these parameters" | `cutout.rst` parameter table (indirect) |
| 12 | Connectivity changes unexpectedly | **Not covered** | — |
| 13 | An object becomes invalid after an operation | **Not covered** — directly related to the §14.2 object-lifetime gap | — |
| 14 | The script works interactively but fails in CI | **Not covered** | — |
| 15 | PyEDB uses an unexpected EDB version | Well covered | `quick_start.rst` "Common problems", `backend_compatibility_migration.rst` |
| 16 | PyEDB and PyAEDT use incompatible versions | **Not covered** | — |
| 17 | Logging does not provide enough information | **Not covered** | — |
| 18 | A configuration file applies only partially | **Not covered** (§5.7) | — |
| 19 | A batch process leaks resources or retains locks | **Not covered** | — |

**Verified existing content not in this mission's required list, keep as-is:** the Windows/`uv`
OpenSSL DLL-naming-conflict entry (`troubleshooting.rst` lines 41–82) is detailed, root-caused, and
solution-oriented — a strong existing example of the diagnostic depth this mission wants replicated
across the 13 currently-uncovered symptoms above.

### 16.1 Worked example: closing symptom #3/#4 with a diagnostic snippet (template for the other 12 new entries)

```python
# Diagnostic: "A net lookup returns no result" / "component lookup is empty"
def diagnose_missing_net(edb, net_name):
    """Print a diagnostic report distinguishing 'wrong name' from 'design truly has no nets'."""
    all_nets = edb.nets.netlist  # [VERIFIED] List[str]
    print(f"Total nets in design: {len(all_nets)}")
    if net_name in all_nets:
        print(
            f"'{net_name}' exists. If a lookup elsewhere still failed, check for a typo or"
            " case-sensitivity difference in that other call site."
        )
    else:
        close_matches = [n for n in all_nets if net_name.lower() in n.lower()]
        print(f"'{net_name}' not found. Closest matches: {close_matches[:5] or 'none'}")
        print(f"First 10 net names in the design: {all_nets[:10]}")


diagnose_missing_net(edb, "GND")
```

**Expected diagnostic output:** either confirmation the net exists (pointing the reader to a different
root cause) or a ranked list of near-matches plus a design-wide sample — turning "empty result, no idea
why" into an actionable next step, directly satisfying this mission's "reporting useful diagnostics when
a query fails" requirement (already partially modeled in Tutorial 3, §10). **[RECOMMENDATION]** author
the remaining 12 new-entry diagnostics using this same pattern: (1) print the relevant collection's total
size, (2) state explicitly whether the target was found, (3) if not found, print near-matches and a
sample of valid values.

---

## 17. Documentation testing and CI strategy

### 17.1 Current CI baseline (restated from §3.6, not re-derived)

`.github/workflows/ci-pr.yml` verified jobs relevant to documentation quality: `doc-style` (Vale),
`docs-build` (HTML build + `check-links: true`), `doc-quality-gate` (`doc/check_doc_quality.py`, warning/
error/orphan/broken-reference ceiling). None execute example code. Separately, `unit-tests-grpc`/
`unit-tests-dotnet` and the four self-hosted `system-tests-*` jobs run `pytest tests/unit` and `pytest
tests/system` respectively, gated by `USE_GRPC` env var and requiring `ANSYSLMD_LICENSE_FILE` (line 7) —
confirming license-dependent test infrastructure **already exists and is wired to self-hosted runners**,
which is the correct home for any new example-execution tests proposed below (they need the same
AEDT license and are not appropriate for `ubuntu-latest`/`windows-latest` hosted runners).

### 17.2 Proposed architecture — extend `tests/system`, do not invent a parallel harness

**[RECOMMENDATION]** Rather than building a bespoke "run `.rst` code blocks" harness from scratch (higher
risk, per this mission's own effort/risk weighting), promote every new tutorial/example script (§10–§12)
to a literal, `pytest`-collected file under a new `tests/system/test_documentation_examples/` directory,
each function docstring-linked back to the `.rst` page it embodies. This reuses:

- the existing `system` pytest marker (`pyproject.toml` line 273: `"system: mark test as a system
  test."`) — **[VERIFIED]** the marker already exists and is the natural home for license-dependent
  tests;
- the existing self-hosted Windows/Linux runners already licensed for AEDT (`ci-pr.yml` lines 215–463);
- the existing `--cov=pyedb` coverage plumbing (bonus: doc-example coverage becomes visible in the same
  Codecov reports already uploaded, lines 264–269 etc.).

Each documentation-example test must:

1. Copy the relevant §15 dataset into a `tmp_path` fixture (never touch the source dataset — this is the
   same non-destructive discipline already required of the `.rst` prose, now enforced mechanically).
2. Run the exact code shown on the `.rst` page (ideally via a shared, literal Python module imported by
   both the test and a `literalinclude`/`jupyter-execute`-style Sphinx directive in the `.rst` page, so
   the two can never drift — this is the single most durable fix for the exact "silent breakage" failure
   mode `doc_audit.md` recorded during PR4, §5.2).
3. Assert the documented object counts/behavior (already specified per-dataset in §15).
4. Assert persistence by reopening the saved output (Tutorial 4 pattern, §10) wherever the page claims a
   change persists.
5. Close all `Edb` sessions in a `finally` block (or via `with Edb(...) as edb:`), even on assertion
   failure, so a failing test does not leak an RPC session or file lock — directly testing this mission's
   "closes databases and releases file locks" CI requirement.

### 17.3 Distinguishing license-free preparation from license-dependent solving

**[RECOMMENDATION]** Tag every documentation-example test with either `@pytest.mark.no_licence` (marker
already exists, `pyproject.toml` line 275: `"no_licence: mark test that do not need a licence."` —
**[VERIFIED]**) or leave it under the default `system`/license-dependent path. Concretely:

- Track A/B/C/D/G tests that only open, inspect, and modify an EDB **without invoking a solver** should
  be evaluated for `no_licence` eligibility — **[ASSUMPTION — NEEDS VALIDATION]**: whether opening an EDB
  at all requires an AEDT license, or only *solving* does, was not independently confirmed against
  source or a license server in this session; `quick_start.rst`'s own prerequisites state "PyEDB does not
  work without an AEDT installation" (line 13) but installation and license-checkout are not necessarily
  the same gate. This must be verified with the PyEDB maintainers before tagging any test `no_licence`.
- Track F "validate setup completeness" tests (port/terminal/reference creation, no solve) are the
  clearest candidate for a license-free/no-solve tag per this mission's explicit Part 11 instruction —
  isolate model-preparation tests from solver-execution tests.
- Any test that calls `edb.solve_siwave()` or an equivalent solve trigger (seen only in the `Edb` factory
  docstring's Examples section, `design_types.py` line 257, not independently exercised) must be
  clearly separated into its own opt-in, longer-timeout CI job, mirroring how `system-tests-windows-grpc`
  already uses a 180-minute timeout (`ci-pr.yml` line 307) versus the 60-minute DotNet Windows job (line
  247) — i.e., solve-triggering tests are already known, in this codebase's own CI config, to need a much
  larger time budget, and should not share a job with fast preparation-only tests.

### 17.4 Additional quality gates to add to `doc/check_doc_quality.py`

Building on the already-implemented ceiling checks (warnings/errors/orphans/broken-refs, `doc_audit.md`
§14 PR5), add, in priority order:

1. **Public-API-only lint for beginner pages** — grep every code block under `getting_started/**` and
   the "Beginner"-tagged rows of §12's tracks for `_`-prefixed attribute access; fail if found. Directly
   implements this mission's "verifies that beginner examples use public APIs only" requirement.
2. **Deprecated-API-use detector** — grep for the known deprecated call sites already identified in this
   review and in `doc_audit.md` (`Edb.create_port`, `Edb.create_siwave_syz_setup`,
   `Edb.create_siwave_dc_setup`, `Edb.create_voltage_source`, `Edb.create_current_source` — all
   confirmed as deprecated thin wrappers by `object_model.rst`/`ports_and_sources.rst`, §3.4) in any
   *newly added* code block; fail the PR if a new example introduces one of these without an explicit
   `.. deprecated::` callout.
3. **Dataset-availability check** — for every documentation example that references a §15 dataset by
   name, assert the dataset manifest/checksum file exists in the expected location before the build
   proceeds.
4. **Stale-path detector** — grep all `.rst` files for `tests/example_models` or any other filesystem
   path string that is not resolved through a documented download/fixture mechanism, catching the exact
   "hard-coded Linux path" defect class `doc_audit.md` §6 already found once (`/tmp/my_first_project.aedb`
   in the pre-fix `intro.rst`) and fixed there, but which nothing currently prevents from recurring in a
   *new* page.

---

## 18. Contribution and governance model

### 18.1 Governance rule for new/changed public APIs

**[RECOMMENDATION]** Formalize as a PR template checklist / `CONTRIBUTING.md` addendum (not re-reading
`CONTRIBUTING.md` in full this session — flagged for a follow-up cross-check against whatever process
already exists there):

When a public API is introduced or substantially changed, the PR must include:
1. An API-reference (docstring) update whose parameter names match the actual signature — enforced
   mechanically via the "documented defaults disagree with signature" class of check this review
   recommends adding to `doc/check_doc_quality.py` (§17.4), motivated directly by the two confirmed
   instances of this exact defect class found across this review and `doc_audit.md` combined
   (`edbversion`/`version`, §3.2; `padstacks.pins` type, §3.4/§5.6).
2. One minimal usage example (Level 2 style, per §13).
3. One realistic workflow example, when the API is part of a top-20 task (§8.2) — e.g., any new port/
   source/cutout capability should get a Track F example, not just a docstring snippet.
4. One failure/boundary case, explicitly stating which of the six observed error-behavior families
   (§14.3) it belongs to.
5. Unit semantics stated explicitly (string-with-units vs. bare float vs. unit-aware object), following
   the `cutout.rst` parameter-table format (§14.1) as the house style.
6. Ownership/lifetime semantics (does this object survive a cutout, a cell change, a close?) per §14.2.
7. Mutation/persistence semantics (does this require `save()`?) — already a near-universal pattern in
   existing pages (every checked page says "Yes" here); keep enforcing it.
8. Test coverage — a corresponding `tests/unit` (and, if license-dependent, `tests/system`) test,
   consistent with the existing test-file inventory already covering nearly every domain (§2: `test_
   stackup.py`, `test_ports.py`, `test_components.py`, `test_nets.py`, `test_padstack.py`, etc. all
   already exist as of this session's `tests/unit/**` enumeration — **[VERIFIED]** the test infrastructure
   for most domains already exists; the gap is *documentation* coverage, not test coverage).
9. Backward-compatibility notes and migration guidance when replacing an older API — the existing
   `.. deprecated::` docstring pattern (656 grep matches per `doc_audit.md` §7) is the right mechanism;
   this review's only addition is recommending a single aggregated "Deprecated APIs" index page
   (`doc_audit.md` §11 P2 item 12, not yet built as of this session's `doc/source/**` inventory — still
   an open recommendation, carried forward to backlog DOC-060).

### 18.2 Example-review rubric

**[RECOMMENDATION]** Score every new/changed example PR against:

| Criterion | Pass bar |
|---|---|
| Correctness | Every API call verified against current source signature (not memory/training data) |
| Reproducibility | Runs unattended against a documented §15 dataset with no manual setup beyond the stated prerequisites |
| Conceptual clarity | Links at least one Path-B concept page (§9) |
| Safety | Never overwrites the source dataset; always closes resources (§11.3 checklist) |
| Public API usage | No `_`-prefixed access, no undocumented method, on beginner-tagged pages |
| Deterministic verification | Contains at least one `assert` or equivalent machine-checkable outcome (§11.1 item 9) |
| Discoverability | Linked from the "I want to..." table (§9) and from the relevant Track (§12) |
| Maintainability | Uses the standard template (§11), not a one-off structure |
| Version compatibility | States backend/version applicability explicitly, per the existing "Backend and version notes" pattern |
| Cleanup/resource management | `close()` or context manager shown, even in short snippets |

### 18.3 Suggested workflow owners

**[RECOMMENDATION — names not assigned, roles proposed; actual owner assignment is a maintainer
decision outside this review's evidence base]**

| Domain | Proposed owning page(s) | Rationale |
|---|---|---|
| Stackup and materials | `stackup_and_materials.rst`, `configuration/*` stackup sections | Single coherent domain, already has a dedicated page |
| Geometry and components | `components_and_nets.rst`, new Track D page | Natural pairing — components sit on geometry |
| Padstacks/vias | `padstacks_and_vias.rst` | Needs re-verification pass first (§6 row 8) before ownership assignment is meaningful |
| Ports and sources | `ports_and_sources.rst` | Highest-priority verification target (§3.4 unresolved `create_port` signature) |
| Configuration | `configuration/index.rst` + 3 sub-pages | Already the most mature domain; owner should also own Track G |
| Simulation setup | `simulation_setups.rst` | Needs re-verification pass first (§6 row 10) |
| CI/automation | `cli.rst`, new Track H pages | Natural pairing with the `doc-quality-gate` CI job maintainer |

---

## 19. Phased implementation roadmap

**Note:** Phase 0 (equivalent to this mission's "Phase 1: Foundations") is **already substantially
complete** on this branch per `doc_audit.md`'s own PR1-PR5 record (§14 of that file) and this review's
independent re-verification (§3). The phases below therefore start from the *next* increment of work,
renumbered to avoid implying the foundational audit still needs to happen.

### Phase 1 — Verification and dataset foundation (2–3 weeks)

**Tasks:** (a) close the 5 "needs verification" gaps from §6 (`padstacks_and_vias.rst`, `cutouts.rst`,
`simulation_setups.rst`, `hfss_auto_configuration.rst`, the 14 configuration examples) with the same
source-verification rigor already applied elsewhere; (b) fix the two confirmed defects from §3.4/§3.6
(`padstacks.pins` type, `create_port` signature); (c) build Dataset 1 (INTRO_BOARD) and Dataset 4
(PORTS_TRAINING) per §15; (d) define personas and top-20 tasks formally in the docs (§8, currently only
in this review).
**Dependencies:** none — can start immediately.
**Deliverable:** a verified, complete inventory (closing every "unknown"/"not verified" row in §6) plus
two shipped datasets.
**Owner:** documentation maintainer + one workflow-domain owner per §18.3.
**Effort:** ~2–3 weeks for one dedicated contributor.
**Risk:** Medium — dataset authoring requires domain expertise to make the "intentional defects" (e.g.,
CONNECTIVITY_TRAINING's disconnected trace) genuinely representative rather than contrived.
**Acceptance criteria:** every row in §6's inventory table has a definitive verified/fixed status; both
datasets pass a manual open/inspect/close smoke test.

### Phase 2 — First 30 Minutes path (3–4 weeks)

**Tasks:** author Tutorials 1–5 (§10) as real `.rst` pages plus their `tests/system` mirrors (§17.2);
extend `object_model.rst` with the "Object lifetime and identity" subsection (§14.2) and the extended
per-object question template (§13.4).
**Dependencies:** Phase 1 (needs INTRO_BOARD).
**Deliverable:** a complete, dataset-backed, assertion-verified beginner path satisfying this mission's
core design principle end-to-end.
**Owner:** Database-fundamentals workflow owner (§18.3).
**Effort:** ~3–4 weeks.
**Risk:** Low — builds directly on the already-proven `quick_start.rst` template.
**Acceptance criteria:** a new user can complete Tutorials 1–5 in ≤30 minutes using only the published
pages, with every step's success verifiable via a printed assertion or report field (not "no
traceback").

### Phase 3 — Workflow tracks A–H (6–10 weeks)

**Tasks:** build out every "New" cell in §12's eight track tables, prioritized by §8.2's ranked top-20
tasks (primitives-by-layer/net/type, reopen-and-verify pattern reuse, batch processing, design
comparison, and the Track F "validate setup completeness before solve" example first, since these map to
the highest-impact, zero-coverage gaps found in §6/§7).
**Dependencies:** Phase 1 (remaining 3 datasets), Phase 2 (reuses the reopen-and-verify pattern).
**Deliverable:** every track has at least one beginner and one intermediate/advanced example, dataset-
backed, per §12.
**Owner:** one owner per domain per §18.3, coordinated by the documentation maintainer.
**Effort:** ~6–10 weeks, parallelizable across owners since tracks are largely independent.
**Risk:** Medium — Track F (ports/sources) carries the unresolved `create_port` signature risk (§3.4)
and should not proceed until Phase 1 closes it.
**Acceptance criteria:** every "New — no coverage found" row in §12 has a published, dataset-backed
example with deterministic verification.

### Phase 4 — Production quality and CI (4–8 weeks)

**Tasks:** implement §17's `tests/system/test_documentation_examples/` harness; add the 4 quality gates
in §17.4 to `doc/check_doc_quality.py`; resolve the `no_licence`-eligibility question (§17.3) with the
maintainers; build the "Deprecated APIs" index page (§18.1 item 9); wire the remaining AutoAPI subtrees
into `grpc_api/index.rst`'s toctree per §14.4 (re-verify this is still open first).
**Dependencies:** Phases 1–3 (needs the example scripts to test).
**Deliverable:** every published example is a literal, CI-executed test; examples cannot silently go
stale.
**Owner:** CI/automation workflow owner (§18.3) + documentation maintainer.
**Effort:** ~4–8 weeks.
**Risk:** Medium-High — self-hosted runner capacity and AEDT license availability may bottleneck test
execution frequency; needs coordination with whoever manages the existing `system-tests-*` self-hosted
runners.
**Acceptance criteria:** ≥90% of documentation examples execute in CI (per §22's target); a broken
example fails a PR, not a future user's afternoon.

### Phase 5 — Continuous improvement (ongoing)

**Tasks:** quarterly review of GitHub Issues/Discussions for documentation-attributable questions
(process not verified to exist today — **[GAP]**, no evidence found this session of a recurring
documentation-issue review cadence); convert recurring questions into new troubleshooting entries (§16)
or examples; periodic beginner usability testing (e.g., timing a new hire completing §10's path);
dataset maintenance as the API surface evolves; version-migration guides as new AEDT releases ship.
**Dependencies:** Phases 1–4 substantially complete.
**Owner:** documentation maintainer, standing responsibility.
**Effort:** ongoing, ~0.1–0.2 FTE steady-state.
**Acceptance criteria:** time-to-first-successful-inspection and time-to-first-persisted-modification
(§22) trend down release over release, not just hold steady.

---

## 20. Prioritized backlog

IDs use the prefix `DOC-` for documentation-only work and `CI-` for CI/tooling work, continuing rather
than colliding with `doc_audit.md`'s own (unlabeled) P0/P1/P2 items — those are treated as already
in-flight/complete per §14 of that file and are not re-listed here except where this review found a
residual gap.

| ID | Recommendation | User problem | Persona | Area | Deliverable | Priority | Impact | Effort | Dependencies | Risk | Acceptance criteria | Owner | Phase |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DOC-001 | Build INTRO_BOARD dataset | No realistic "inspect an existing board" example exists (§5.1) | P1, P2, P3 | Datasets | `datasets/intro_board.aedb` + provenance page | P0 | High | M | None | Low | Dataset opens, matches documented exact object counts | Docs maintainer | 1 |
| DOC-002 | Build PORTS_TRAINING dataset | Ports/sources examples run on empty DBs (§5.1) | P4 | Datasets | `datasets/ports_training.aedb` | P0 | High | M | None | Low | Single-ended + differential structures verified present | Docs maintainer | 1 |
| DOC-003 | Verify `edb.excitation_manager.create_port(...)` signature against source | Unverified API call in a top-20-task page (§3.4) | P4 | Ports/sources | Corrected `ports_and_sources.rst` + docstring | P0 | High | S | None | Low | Signature matches `SourceExcitation` source exactly | Ports/sources owner | 1 |
| DOC-004 | Fix `edb.padstacks.pins` type documentation (`dict[int,...]` → `Dict[str,...]`) | Confirmed doc/signature mismatch (§3.4/§5.6) | P2, P7 | Object model | Corrected `object_model.rst` | P0 | Medium | S | None | Low | Matches `src/pyedb/grpc/database/padstacks.py:297` exactly | Docs maintainer | 1 |
| DOC-005 | Re-verify `padstacks_and_vias.rst`, `cutouts.rst`, `simulation_setups.rst`, `hfss_auto_configuration.rst` against source | 4 top-20-task pages unverified this session (§6) | All | Multiple | Verification report + fixes | P0 | High | M | None | Medium | Every code call cross-checked against current signatures | Respective domain owners | 1 |
| DOC-006 | Re-verify the 14 configuration API examples against source | Unverified top-20-task content (§8.2 rank 15) | P1, P5, P6 | Configuration | Verification report + fixes | P0 | High | M | None | Medium | Every example's calls cross-checked | Configuration owner | 1 |
| DOC-010 | Author PyEDB/PyAEDT/EDB/AEDT/HFSS-3D-Layout/SIwave boundary page | Unclear product boundaries (§6) | P1, P3, P4 | Conceptual (Path B) | New page | P1 | Medium | S | None | Low | Page exists, linked from README and user_guide index | Docs maintainer | 2 |
| DOC-011 | Author Tutorials 1–5 (First 30 Minutes path) | No guided path past quick start (§10) | P1, P2 | Beginner path | 5 new `.rst` pages | P0 | High | M | DOC-001 | Low | Completable in ≤30 min, every step asserts success | Database-fundamentals owner | 2 |
| DOC-012 | Add "Object lifetime and identity" subsection to `object_model.rst` | Missing lifetime semantics (§14.2) | P3, P5, P7 | Conceptual | Extended page | P1 | Medium | S | None | Low | Answers all 7 lifetime questions from mission Part 8 | Docs maintainer | 2 |
| DOC-013 | Extend the "8 questions" template to 11 (audience, error behavior, Level-1 alternative) | Incomplete per-object contract (§13.4) | All | Object model | Extended page | P1 | Medium | S | None | Low | All 10 properties re-documented with 11 answers each | Docs maintainer | 2 |
| DOC-020 | Add Track D "find primitives by layer/net/type" example | Zero coverage, top-20 rank 8 (§8.2, §12) | P2, P4, P7 | Geometry | New page section | P0 | High | M | DOC-001 | Low | Example runs against INTRO_BOARD, asserts primitive count | Geometry owner | 3 |
| DOC-021 | Add reopen-and-verify step to every existing workflow page | Persistence never verified today (§11.2) | All | All workflow pages | Edits to 4+ existing pages | P0 | High | S | None | Low | Every "Complete example" ends with a reopen+assert block | Docs maintainer | 3 |
| DOC-022 | Add "compare database revisions" example (Track H) | Zero coverage, top-20 rank 19 (§8.2) | P5, P6 | Production automation | New page | P1 | Medium | M | DOC-001, PRODUCTION_BOARD | Medium | Detects a known, seeded diff between two dataset revisions | Automation owner | 3 |
| DOC-023 | Add "batch-process multiple designs / run in CI" example (Track H) | Zero coverage, top-20 rank 20 (§8.2) | P5, P6 | Production automation | New page | P0 | High | M | DOC-001 | Medium | Processes ≥3 copies of INTRO_BOARD in a loop, closes each session cleanly | Automation owner | 3 |
| DOC-024 | Add Track F "validate setup completeness before solve" example | No license-free pre-solve validation shown (§12 Track F) | P4 | Ports/sources | New page section | P0 | High | M | DOC-002, DOC-003 | Medium | Verifies port/reference completeness with zero solver calls | Ports/sources owner | 3 |
| DOC-030 | Render the object-relationship diagram as SVG/PNG | Text-only diagram is a stopgap (§10, §13.3) | All | Conceptual | Rendered asset in `object_model.rst` | P2 | Medium | S | None | Low | Diagram renders correctly in built HTML | Docs maintainer | 3 |
| DOC-040 | Restructure `troubleshooting.rst` by symptom taxonomy | Flat FAQ, 13 of 19 required symptoms uncovered (§16) | All | Troubleshooting | Rewritten page | P1 | High | M | None | Low | All 19 symptoms from §16 have an entry with diagnostic code | Docs maintainer | 2–3 |
| DOC-041 | Add explicit unit-table format to all parameter-heavy method docstrings | Inconsistent unit documentation outside `cutout.rst` (§14.1) | P1, P2, P4 | API reference | Docstring edits across modules | P1 | Medium | M | None | Low | Every geometry/dimension parameter states its unit explicitly | Respective domain owners | 3–4 |
| DOC-042 | Publish an "Error behavior policy" page/section | 6 undocumented, inconsistent failure-mode families (§14.3) | P2, P5, P6 | API reference | New page/section | P1 | Medium | S | None | Low | States the rule for KeyError/ValueError/RuntimeError/RuntimeWarning/None/silent-mutation | Docs maintainer | 3 |
| DOC-050 | Verify and document primitive-by-layer query API | Unverified assumption in Tutorial 3 (§10) | P2, P7 | Geometry | Corrected tutorial + docstring | P0 | Medium | S | None | Low | Exact method name/signature confirmed against source | Geometry owner | 1 |
| DOC-060 | Build an aggregated "Deprecated APIs" index page | 656 scattered `.. deprecated::` notes, no single index (§18.1 item 9, carried from `doc_audit.md` §11 P2-12) | P3, P5, P7 | API reference | New page | P2 | Medium | M | None | Low | Every `deprecate_argument_name`/`deprecated_property` use is listed once | Docs maintainer | 4 |
| DOC-061 | Wire `workflows.*`, `libraries.*`, `siwave_core.*`, `cli` into `grpc_api/index.rst` toctree | API reference navigation excludes major public subpackages (§5.5, §14.4) | P5, P7 | API reference | Toctree edit | P1 | Medium | S | None | Low | All 5 subpackages reachable from top-level "API reference" nav | Docs maintainer | 4 (re-verify first) |
| DOC-062 | Author "Choosing an automation style" Level 1/2/3 guide | No explicit level-selection guidance exists (§13.1–13.2) | All | Conceptual | New page | P1 | Medium | S | None | Low | Decision table matches §13.2; escape-hatch attribute name verified against source | Docs maintainer | 2 |
| DOC-070 | Build STACKUP_TRAINING, CONNECTIVITY_TRAINING, PRODUCTION_BOARD datasets | Remaining 3 of 5 required datasets missing (§15) | All | Datasets | 3 datasets + provenance pages | P1 | High | L | DOC-001 pattern reuse | Medium (PRODUCTION_BOARD needs IP review) | Each matches its §15 spec exactly | Docs maintainer + legal review for PRODUCTION_BOARD | 1 (partial), 3 (complete) |
| CI-001 | Build `tests/system/test_documentation_examples/` harness | Zero CI execution of doc examples (§3.6, §5.2, §17.2) | All | CI | New test directory + CI wiring | P0 | High | L | DOC-001, DOC-011 | Medium | Every Tutorial 1–5 script runs and passes in CI | CI/automation owner | 4 |
| CI-002 | Add public-API-only lint for beginner pages | No mechanical enforcement of "no private APIs" (§17.4 item 1) | All | CI | `doc/check_doc_quality.py` extension | P1 | Medium | S | None | Low | Fails PR if `_`-prefixed access appears in a beginner-tagged block | CI/automation owner | 4 |
| CI-003 | Add deprecated-API-use detector for new code blocks | No mechanical enforcement of "no new deprecated calls" (§17.4 item 2) | All | CI | `doc/check_doc_quality.py` extension | P1 | Medium | S | None | Low | Fails PR if a new block calls a known-deprecated wrapper without a `.. deprecated::` callout | CI/automation owner | 4 |
| CI-004 | Add dataset-availability and stale-path checks | Prevents recurrence of the hard-coded-path defect class (§17.4 items 3–4) | All | CI | `doc/check_doc_quality.py` extension | P2 | Medium | S | None | Low | Fails PR if a referenced dataset/path is missing or unresolved | CI/automation owner | 4 |
| CI-005 | Resolve `no_licence`-eligibility for open/inspect-only tests with maintainers | Unclear which tests can skip full AEDT license gating (§17.3) | P6 | CI | Documented policy | P1 | Medium | S | None | Medium | Written policy checked into `CONTRIBUTING.md` or `AGENTS.md` | Maintainers + CI owner | 4 |

---

## 21. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Dataset authoring (§15) requires domain expertise (SI/PI knowledge) that documentation contributors may not have | Medium | High (blocks nearly every downstream phase) | Pair a documentation contributor with a domain subject-matter expert (P4-equivalent) for dataset design; do not let a non-domain-expert invent "realistic" electrical structures |
| PRODUCTION_BOARD dataset provenance/IP review stalls Phase 3 | Medium | Medium | Start PRODUCTION_BOARD's legal/IP review in parallel with Phase 1, not sequentially after |
| Self-hosted runner capacity cannot absorb new `tests/system/test_documentation_examples/` load (§17.2, CI-001) | Medium | Medium | Start with a small, fast subset (Tutorials 1–5 only) before promoting the full Track A–H example set to CI |
| `create_port` signature (DOC-003) turns out to require a breaking doc change if the real signature differs meaningfully from what `object_model.rst`/`ports_and_sources.rst` currently show | Low-Medium | Medium | Prioritize DOC-003 first in Phase 1 specifically because it blocks Track F (the SI/PI persona's top task) |
| New symptom-based troubleshooting entries (DOC-040) are written speculatively rather than from real user reports, reducing their practical accuracy | Medium | Medium | Where possible, validate each new entry against an actual reproduction (open a bad path, trigger the real exception) rather than guessing the error text |
| CI example-execution harness (CI-001) becomes a maintenance burden if not kept in lock-step with the `.rst` prose it mirrors | Medium | High | Use a shared, literal Python module included by both the test and the `.rst` page (via `literalinclude`) so the two cannot silently diverge — stated explicitly in §17.2 |
| Governance rubric (§18.2) is adopted on paper but not enforced in review practice | Medium | Medium | Wire the mechanical parts (public-API-only lint, deprecated-API detector) into CI (CI-002/CI-003) rather than relying on manual review discipline alone |
| This review's own unverified claims (`padstacks_and_vias.rst`, `simulation_setups.rst`, etc. — §6) turn out to hide additional defects beyond what was estimated | Medium | Medium | Phase 1 explicitly budgets a dedicated verification pass (DOC-005/DOC-006) before any new content is built on top of unverified pages |

---

## 22. Success metrics

| Metric | Current baseline (this session) | 6-month target |
|---|---|---|
| Time to install and validate PyEDB | Not measured (no live AEDT session available this session); `quick_start.rst` §2 is a ~1-minute check once installed | < 10 minutes end-to-end from a clean environment |
| Time to first successful database inspection | Not measured; blocked today by §5.1 (no populated dataset in the guided path) | < 10 minutes, using Tutorial 1 (§10) against INTRO_BOARD |
| Time to first persisted modification | Not measured; `quick_start.rst` demonstrates the mechanics but not a reopen-verify | < 30 minutes, using Tutorial 4 (§10) |
| % of documentation examples executed in CI | **0%** (§3.6, verified) | ≥ 90% |
| % of beginner examples using public APIs only | 100% on the 4 pages checked this session (§11.3), **not mechanically enforced** | 100%, mechanically enforced (CI-002) |
| % of tutorials with deterministic (`assert`-based) verification | **0%** on the 4 pages checked this session — all use prose "Expected result" (§11.1 item 9) | 100% |
| API domains with task-based entry pages | Partial — 12 of an estimated 20 top tasks have a page (§8.2); several unverified | All 20 top tasks (§8.2) have a linked entry point |
| API-reference pages with practical examples | Not fully assessed (only `grpc/edb`, `grpc/database` subtrees are in nav, §5.5); most AutoAPI stub pages have no example | Every Level-2 domain object (10 properties in `object_model.rst`) cross-linked from ≥1 practical example |
| Broken documentation links | **0** per `doc_audit.md`'s final measured metrics (§14 of that file) — not independently re-run in this session | Maintain 0, gated by existing `check-links: true` |
| Examples with missing input data | **N/A today** — every example creates an empty DB rather than requiring external input (§3.3); this will become a real metric once §15 datasets exist | 0 (every dataset-dependent example ships with or auto-fetches its dataset) |
| Documentation-related support issues | Not measured (GitHub Issues not queried this session, §2) | Track quarterly; establish a baseline in Phase 5 |
| Use of private APIs in public examples | **0** confirmed in the 4 pages checked this session | Maintain 0, mechanically enforced (CI-002) |
| User completion rate for the beginner path | Not measurable until Tutorials 1–5 (§10) exist | Establish a baseline in Phase 2, then track improvement |

---

## 23. Quick wins for the first 30 days

Ranked by the mission's own prioritization guidance (§ "If resources are limited") and cross-referenced
to this review's backlog IDs (§20):

1. **QW-1 — Fix the confirmed `padstacks.pins` type mismatch (DOC-004).** Trivial, one-line fix,
   directly reduces the risk class `doc_audit.md` already spent significant effort eliminating.
2. **QW-2 — Verify the `create_port` signature (DOC-003).** Small effort, closes a known risk on a
   top-20 task page before any new Track F content is built on top of it.
3. **QW-3 — Build the INTRO_BOARD dataset (DOC-001).** This is the single highest-leverage item in the
   entire backlog: it unblocks Tutorial 1–5 (§10), Track A/B/D beginner examples (§12), and the
   `tests/system` CI harness (§17.2) all at once.
4. **QW-4 — Author the "Choosing an automation style" Level 1/2/3 guide (DOC-062).** Small effort
   (mostly synthesis of already-verified facts from `configuration/index.rst` and `object_model.rst`),
   high clarity payoff for every persona in §8.1.
5. **QW-5 — Author the PyEDB/PyAEDT/EDB/AEDT boundary page (DOC-010).** Small effort, closes a
   verified, recurring source of confusion (§6) using content that already exists in scattered form
   (`README.md`, `example_inventory.rst`).
6. **QW-6 — Add the reopen-and-verify step to the 4 already-verified workflow pages (DOC-021).** Small,
   mechanical edit to existing, already-correct pages; immediately upgrades every one of them to meet
   this mission's core design principle.
7. **QW-7 — Restructure `troubleshooting.rst`'s existing 5 entries under the new symptom taxonomy
   (first half of DOC-040).** No new content required for this first pass — pure reorganization of
   already-verified, already-accurate material into the structure this mission requires; new symptom
   entries can follow incrementally.
8. **QW-8 — Publish the "Error behavior policy" section (DOC-042).** Small effort; the six failure-mode
   families are already fully identified in this review (§14.3) and just need to be written up once.

---

## 24. Recommended next actions

1. Share this report with the PyEDB documentation maintainer and the domain owners proposed in §18.3;
   confirm or reassign ownership.
2. Immediately execute Quick Wins QW-1 and QW-2 (§23) — both are small, source-verification-only fixes
   that reduce active risk on published pages.
3. Schedule dataset authoring (DOC-001, DOC-002) as the first substantive work item; identify the subject-matter expert
   pairing needed per the top risk in §21.
4. Commission the outstanding verification passes (DOC-005, DOC-006) for `padstacks_and_vias.rst`,
   `cutouts.rst`, `simulation_setups.rst`, `hfss_auto_configuration.rst`, and the 14 configuration
   examples before building any new content that depends on them.
5. Decide, with the maintainers, the `no_licence` eligibility question (CI-005) early — it affects the
   design of every subsequent CI-execution test (CI-001).
6. Re-run `doc/check_doc_quality.py` (already in the repository) as a baseline check before starting
   Phase 1, to confirm this review's understanding of current metrics is still accurate at whatever
   point work actually begins (documentation and code both continue to change).
7. Track progress against the backlog IDs in §20 as GitHub issues, one issue per ID, preserving the
   `DOC-`/`CI-` prefixing so this report remains a durable index.

---

## 25. Sources and evidence

**Repository files read in full or substantially in this session** (primary evidence for every
**[VERIFIED]** claim above unless otherwise attributed to `doc_audit.md`):

- `README.md`, `pyproject.toml`, `llms.txt`, `doc_audit.md` (712 lines)
- `src/pyedb/generic/design_types.py` (424 lines, full)
- `src/pyedb/grpc/edb.py` (targeted greps: `__enter__`/`__exit__`, `cell_names`, `active_cell`)
- `src/pyedb/grpc/edb_init.py` (targeted greps: `save`, `close`, `save_as`, confirmed line numbers 258,
  285, 407)
- `src/pyedb/grpc/database/nets.py` (targeted read, `netlist` property, line 244)
- `src/pyedb/grpc/database/padstacks.py` (targeted read, `pins` property, line 297)
- `.github/workflows/ci-pr.yml` (538 lines, full)
- `doc/source/index.rst`, `doc/source/getting_started/index.rst`,
  `doc/source/getting_started/quick_start.rst` (145 lines, full),
  `doc/source/getting_started/object_model.rst` (231 lines, full),
  `doc/source/getting_started/backend_compatibility_migration.rst` (197 lines, full),
  `doc/source/getting_started/glossary.rst` (28 lines, full),
  `doc/source/getting_started/troubleshooting.rst` (90 lines, full),
  `doc/source/getting_started/cli.rst` (114 lines, full)
- `doc/source/user_guide/index.rst` (162 lines, full),
  `doc/source/user_guide/stackup_and_materials.rst` (135 lines, full),
  `doc/source/user_guide/components_and_nets.rst` (118 lines, full),
  `doc/source/user_guide/ports_and_sources.rst` (119 lines, full),
  `doc/source/user_guide/validation_and_drc.rst` (131 lines, full)
- `doc/source/configuration/index.rst` (140 lines, full)
- `doc/source/workflows/utilities/cutout.rst` (179 lines, full)
- `doc/source/examples/example_inventory.rst` (174 lines, full)
- Directory enumerations: `doc/source/**/*.rst` (48 files), `tests/example_models/**` (100+ entries,
  truncated listing), `tests/unit/**/*.py` (50 files, names only), `.github/workflows/*.yml` (4 files)
- Git metadata: `git remote -v`, `git log -1`, `git diff --stat main...HEAD`

**Pages referenced from other pages but not independently re-read in this session** (cited only via
`doc_audit.md` or via cross-reference from a page that *was* read; flagged throughout as
"not verified this session" or "[NEEDS RE-VERIFICATION]"): `doc/source/user_guide/padstacks_and_vias.rst`,
`doc/source/user_guide/cutouts.rst`, `doc/source/user_guide/simulation_setups.rst`,
`doc/source/workflows/sipi/hfss_auto_configuration.rst`, `doc/source/workflows/drc/drc.rst` (read
indirectly via `validation_and_drc.rst`'s cross-checked claims only), `doc/source/configuration/
configuration_api_guide.rst`, `doc/source/configuration/configuration_api_examples.rst`,
`doc/source/configuration/file_architecture.rst`, `doc/source/grpc_api/index.rst` (cited only via
`doc_audit.md`), `CONTRIBUTING.md`.

**External sources referenced but not fetched live in this session** (per this mission's request to use
current published sources — flagged as a limitation, not silently assumed): the live PyAEDT documentation
tree at `https://aedt.docs.pyansys.com/`, the live PyEDB documentation site at
`https://edb.docs.pyansys.com/`, the PyAnsys developer guide at `https://dev.docs.pyansys.com/`, and the
`ansys/pyedb` GitHub Issues/Discussions pages. All PyAEDT-structural comparisons in this report (§9, §13)
rely on `doc_audit.md`'s own prior characterization of PyAEDT's publicly known documentation architecture,
which that document itself flags as "referenced here as an architecture pattern rather than copied text"
(`doc_audit.md`, header section) — this review did not independently re-verify that characterization
against a fresh clone or live fetch of `ansys/pyaedt`.

**Explicit unresolved items carried forward (not resolved by this review, listed for transparency):**

1. The exact keyword-argument shape of `edb.excitation_manager.create_port(...)` — flagged by
   `doc_audit.md` §13 as unverified, and still unverified after this session (§3.4, DOC-003).
2. Whether `pyedb.dotnet` has any concrete removal version/date — `doc_audit.md` §13 confirms only
   "planned to be deprecated in the future," no version attached; this review found no new information
   changing that status.
3. Whether opening (not solving) an EDB requires an AEDT license checkout — needed to resolve the
   `no_licence` CI-tagging question (§17.3, CI-005); not verified in this session (no live AEDT/license
   server access).
4. Whether multiple concurrent `Edb` sessions against one `ansys-edb-core` service are supported
   (relevant to Track H "parallelism limitations," §12) — not verified in this session.
5. The exact EDB coordinate-system convention (origin, handedness) for dataset documentation purposes
   (§15) — not independently re-verified against source in this session.
6. Whether `grpc_api/index.rst`'s AutoAPI toctree scope (§5.5/§14.4/DOC-061) is still as narrow as
   `doc_audit.md` originally found — this review did not re-read that file in full this session and
   relies on `doc_audit.md`'s prior finding, which may already be partially superseded by
   `configuration/index.rst`'s own separate link into `../autoapi/pyedb/configuration/index` (§3.4/§5.5).

</content>

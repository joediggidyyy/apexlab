# ApexLab Toolkit — Authoritative Schematic

Owner: `joediggidyyy`  
Prepared by: `ORACL-Prime`  
Status: active scaffold  
Authority class: authoritative defining surface

## Purpose

This document is the authoritative schematic for the ApexLab toolkit.

This document is restricted to:

- explicit definitions,
- explicit constraints,
- explicit repository/package surface declarations,
- explicit status markers for undefined areas.

This document is not a planning notebook.

## Interpretation rule

The following rules are in force:

1. If a topic is **defined** here, this document is authoritative for that topic.
2. If a topic is marked **UNSPECIFIED** here, no definition is currently in force for that topic.
3. If a topic is absent here or marked **UNSPECIFIED**, refer to:
   - `projects/data-science-script-library/report_tmp/plans/20260322/LEAN_PROMOTION_AND_CONSOLIDATION_PROPOSAL_20260322.md`
   for planning context only.
4. Ambiguous or speculative language must not be added to this document.

## Current defining statements

### Identity

- Toolkit name: `ApexLab`
- Toolkit class: `standalone Python package`
- Toolkit scope: `comprehensive machine learning toolkit`
- Primary package-track repository lane: `projects/apexlab/`
- Canonical public repository name: `apexlab`
- Canonical public repository URL: `https://github.com/joediggidyyy/apexlab`
- Canonical PyPI distribution name: `apexlab`
- Canonical import package name: `apexlab`
- Default branch: `main`
- Intended package index: `PyPI`

### Maturity posture

- A minimal initial release is permitted.
- A minimal initial release is acceptable only if paired with an aggressive timeline for capability expansion.
- The target maturity state is a broad, method-diverse machine learning toolkit rather than a permanently narrow single-method package.

### Initial release scope

- The first ApexLab publication leg is `Leg 1 — initial publication push`.
- The Leg 1 package scope is a compact machine-learning toolkit centered on constrained optimization, evaluation, reporting, and reproducible demos.
- The Leg 1 shipped functionality set is:
   - one constrained core model family,
   - diagnostics around that family,
   - evaluation/report/threshold helpers,
   - deterministic split utilities,
   - synthetic demos/examples,
   - clean packaging and tests.
- The Leg 1 repository/package buildout must include:
   - package skeleton,
   - package model module,
   - diagnostics module,
   - evaluation module family,
   - dataset utility module,
   - example/demo surface,
   - minimal release documentation.
- The Leg 1 required exit state is:
   - package installs cleanly,
   - package imports cleanly,
   - examples run,
   - tests pass,
   - PyPI publication is complete,
   - repository shape matches the agreed initial package schema.
- The Leg 1 explicit non-goals are:
   - extra model families,
   - full CLI surface,
   - deep interoperability surfaces,
   - large refactors for elegance beyond what publication requires.

### Sequencing rule

- ApexLab development must follow this ordered sequence:
   1. publish fast,
   2. stabilize the package base,
   3. expand method breadth,
   4. consolidate ergonomics,
   5. add interoperability deliberately,
   6. push toward full toolkit maturity.
- Later-leg work must not block Leg 1 publication unless the work is required to satisfy a Leg 1 exit condition.

### Repository role

- `projects/apexlab/` is the package-track home for ApexLab.
- `projects/data-science-script-library/` is not the package-track home for ApexLab.
- Library-hosted ApexLab-adjacent items may continue to exist in `projects/data-science-script-library/`.
- Library-hosted ApexLab-adjacent items do not define the standalone ApexLab package surface.

### Interoperability posture

- CodeSentinel interoperability is in scope for ApexLab.
- Observer-specific naming is not part of the ApexLab package identity.
- Functionality ported into ApexLab must be expressed as native ApexLab functionality.

## Authoritative surface register

| Surface | Status | Definition |
| --- | --- | --- |
| Public repository | DEFINED | `https://github.com/joediggidyyy/apexlab` |
| Local package-track root | DEFINED | `projects/apexlab/` |
| Package publication target | DEFINED | `PyPI` |
| Canonical package name on PyPI | DEFINED | `apexlab` |
| Canonical import package name | DEFINED | `apexlab` |
| Toolkit scope | DEFINED | `comprehensive machine learning toolkit` |
| Initial release posture | DEFINED | `minimal initial release permitted` |
| Expansion requirement | DEFINED | `aggressive capability-expansion timeline required` |
| Initial release leg | DEFINED | `Leg 1 — initial publication push` |
| Initial release scope | DEFINED | `compact ML toolkit centered on constrained optimization, evaluation, reporting, and reproducible demos` |
| Sequencing rule | DEFINED | `publish -> stabilize -> broaden -> consolidate -> integrate -> mature` |
| Minimum supported Python version | UNSPECIFIED | no definition in force |
| Dependency policy | UNSPECIFIED | no definition in force |
| Versioning policy | UNSPECIFIED | no definition in force |
| CLI surface | DEFINED | `apexlab` console entry point with lite `compare` and `report` commands under `src/apexlab/cli/` |
| Public API boundary | UNSPECIFIED | no definition in force |
| Model family inventory | UNSPECIFIED | no definition in force |
| Interoperability contract with CodeSentinel | UNSPECIFIED | no definition in force |

## Repository schematic

The following statements are currently in force:

- Canonical local workspace lane: `projects/apexlab/`
- Canonical authoritative schematic path: `projects/apexlab/docs/APEXLAB_TOOLKIT_AUTHORITATIVE_SCHEMATIC.md`
- Canonical repository/package/import naming stack: `apexlab`
- The Leg 1 repository root must include:
   - `LICENSE`
   - `README.md`
   - `pyproject.toml`
   - `MANIFEST.in`
   - `.gitignore`
- The Leg 1 repository must include these top-level directories:
   - `docs/`
   - `src/`
   - `tests/`
   - `examples/`
- The authoritative documentation file for the package-track lane is:
   - `docs/APEXLAB_TOOLKIT_AUTHORITATIVE_SCHEMATIC.md`

The following Leg 1 repository schematic is in force:

```text
projects/apexlab/
├─ LICENSE
├─ README.md
├─ pyproject.toml
├─ MANIFEST.in
├─ .gitignore
├─ docs/
│  ├─ APEXLAB_TOOLKIT_AUTHORITATIVE_SCHEMATIC.md
│  ├─ INITIAL_RELEASE_SCOPE.md
│  ├─ API_OVERVIEW.md
│  └─ RELEASE_NOTES_DRAFT.md
├─ src/
│  └─ apexlab/
│     ├─ __init__.py
│     ├─ cli/
│     │  ├─ __init__.py
│     │  ├─ main.py
│     │  ├─ compare.py
│     │  └─ report.py
│     ├─ py.typed
│     ├─ datasets/
│     │  ├─ __init__.py
│     │  └─ split.py
│     ├─ diagnostics/
│     │  ├─ __init__.py
│     │  └─ convergence.py
│     ├─ evaluation/
│     │  ├─ __init__.py
│     │  ├─ metrics.py
│     │  ├─ reports.py
│     │  └─ thresholds.py
│     ├─ models/
│     │  ├─ __init__.py
│     │  └─ simplex.py
│     ├─ utils/
│     │  ├─ __init__.py
│     │  ├─ io.py
│     │  └─ manifests.py
│     └─ demos/
│        ├─ __init__.py
│        └─ synthetic.py
├─ tests/
│  ├─ test_simplex.py
│  ├─ test_convergence.py
│  ├─ test_thresholds.py
│  ├─ test_metrics.py
│  ├─ test_split.py
│  └─ test_manifests.py
└─ examples/
    ├─ simplex_regression_demo.py
    └─ evaluation_demo.py
```

## Reserved definition blocks

The following blocks are reserved for future explicit definitions.

### Package identity

Status: `PARTIALLY DEFINED`

Reserved fields:

- repository description line
- package summary line
- project classifiers
- package keywords

### CLI surface

Status: `PARTIALLY DEFINED`

Defining statements currently in force:

- ApexLab exposes a console entry point named `apexlab`.
- The currently defined lite CLI surface is limited to:
   - `apexlab compare`
   - `apexlab report`
- The lite CLI surface exists to wrap already-implemented analysis/report functionality.
- Full train/evaluate workflow coverage is not yet defined by this schematic.

### Source layout

Status: `PARTIALLY DEFINED`

Reserved fields:

- `pyproject.toml` status
- `src/` layout
- package module path
- test layout
- docs layout

Defined minimum Leg 1 layout requirements:

- repository root includes packaging metadata and release-facing docs,
- package code lives under `src/apexlab/`,
- tests live under `tests/`,
- examples live under `examples/`,
- authoritative documentation lives under `docs/`.
- the package root module is `src/apexlab/__init__.py`,
- type information marker file is `src/apexlab/py.typed`.

### API and CLI surface

Status: `PARTIALLY DEFINED`

Reserved fields:

- public API modules
- command-line entrypoints
- manifest/report schema surfaces
- diagnostics/report helpers

Defined Leg 1 module-family boundaries:

- public package namespace root: `apexlab`
- model family module lane: `apexlab.models`
- diagnostics module lane: `apexlab.diagnostics`
- evaluation module lane: `apexlab.evaluation`
- dataset utility lane: `apexlab.datasets`
- internal/support utility lane: `apexlab.utils`
- demo-support lane: `apexlab.demos`
- no full CLI surface is defined for Leg 1.

### Numerical / ML scope

Status: `PARTIALLY DEFINED`

Reserved fields:

- core solver inventory
- evaluation helpers
- dataset adapters
- benchmark/demo surfaces
- supervised methods
- unsupervised methods
- optimization methods

Defined Leg 1 numerical/module boundaries:

- core constrained model module: `apexlab.models.simplex`
- convergence diagnostics module: `apexlab.diagnostics.convergence`
- evaluation metrics module: `apexlab.evaluation.metrics`
- evaluation reports module: `apexlab.evaluation.reports`
- threshold-selection module: `apexlab.evaluation.thresholds`
- deterministic split utility module: `apexlab.datasets.split`
- demo-support module: `apexlab.demos.synthetic`
- manifest/io support modules: `apexlab.utils.manifests`, `apexlab.utils.io`

### Maturity timeline

Status: `PARTIALLY DEFINED`

Reserved fields:

- first release milestone
- later expansion milestones

Defined timeline constraints:

- the first defined milestone is `Leg 1 — initial publication push`,
- the next defined boundary after Leg 1 is `Leg 2 — stabilization and package hardening`,
- later legs exist in planning but are not yet individually authoritative in this document.

### Interoperability surface

Status: `UNSPECIFIED`

Reserved fields:

- CodeSentinel integration boundary
- artifact exchange surfaces
- manifest compatibility rules
- naming/branding conversion rules

## Change rule

New content may be added to this document only when the content can be stated as a direct definition, direct constraint, or direct status declaration.

Planning rationale, option comparison, and unresolved discussion belong in the planning surface, not here.

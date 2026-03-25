# ApexLab Release Procedure

This note captures the final operator-executed flow for publishing the `1.2.0` ApexLab release.

## Current local verification state

Already completed in this workspace:

- package version locked to `1.2.0`
- focused ApexLab test suite passing
- full ApexLab suite passing (`63 passed`)
- CLI regression tests for the patch lane passing
- field test executed successfully
- analytical reference-validation documented
- supervised tree/forest model tests passing
- fresh `1.2.0` wheel and source distribution built successfully
- wheel and source distribution smoke installs both reported `apexlab 1.2.0`
- rerun-safe publish workflow configured with skip-existing behavior

## Current local repo note

As of 2026-03-25, the intended public repository exists at:

- `https://github.com/joediggidyyy/apexlab`

Within this workspace, `projects/apexlab/` is a real git checkout with:

- `origin https://github.com/joediggidyyy/apexlab.git`

That means build, tag, push, and publish can proceed directly from this checkout once the release gates are satisfied.

## Operator release flow

1. Verify the repository remote points to `https://github.com/joediggidyyy/apexlab`.
2. Confirm the intended `ApexLab 1.2.0` package contents are present on `main` or ready to be committed there.
3. Run the package validation in the current repo context:
   - `python -m pytest tests`
   - `python -m build`
4. Confirm the final `dist/` contains only:
   - `apexlab-1.2.0-py3-none-any.whl`
   - `apexlab-1.2.0.tar.gz`
5. Perform install smoke checks from the built artifacts.
6. Commit and push the release-ready `1.2.0` tree to `main`.
7. Create the release tag `v1.2.0`.
8. Push the tag to the intended public remote.
9. Publish the artifacts via the selected release channel.
10. If the release workflow is rerun after a successful upload, rely on the publish step's skip-existing behavior rather than treating the rerun as a failure.

## Suggested release payload surfaces

- `README.md`
- `LICENSE`
- `pyproject.toml`
- `MANIFEST.in`
- `src/apexlab/`
- `examples/`
- `tests/`
- `docs/API_OVERVIEW.md`
- `docs/INITIAL_RELEASE_SCOPE.md`
- `docs/RELEASE_NOTES_DRAFT.md`
- `docs/PUBLISH_CHECKLIST.md`
- `docs/validation/REFERENCE_VALIDATION_20260324.md`

## Release decision summary

`1.2.0` is the clean reset point after the patch-lane mismatch. The correct goal is a coherent release that preserves the already-validated analytical/reporting lane while officially publishing the package-owned isolation, tree, and forest model surfaces under one version.

# ApexLab Release Procedure

This note captures the final operator-executed flow for publishing the `1.1.1` ApexLab patch release.

## Current local verification state

Already completed in this workspace:

- package version locked to `1.1.1`
- focused ApexLab test suite passing
- CLI regression tests for the patch lane passing
- field test executed successfully
- analytical reference-validation documented
- rerun-safe publish workflow configured with skip-existing behavior

## Current local repo note

As of 2026-03-25, the intended public repository exists at:

- `https://github.com/joediggidyyy/apexlab`

Within this workspace, `projects/apexlab/` is a real git checkout with:

- `origin https://github.com/joediggidyyy/apexlab.git`

That means build, tag, push, and publish can proceed directly from this checkout once the release gates are satisfied.

## Operator release flow

1. Verify the repository remote points to `https://github.com/joediggidyyy/apexlab`.
2. Confirm the intended `ApexLab 1.1.1` package contents are present on `main` or ready to be committed there.
3. Run the package validation in the current repo context:
   - `python -m pytest tests`
   - `python -m build`
4. Confirm the final `dist/` contains only:
   - `apexlab-1.1.1-py3-none-any.whl`
   - `apexlab-1.1.1.tar.gz`
5. Perform install smoke checks from the built artifacts.
6. Commit and push the release-ready `1.1.1` tree to `main`.
7. Create the release tag `v1.1.1`.
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

`1.1.1` should remain intentionally narrow. The correct goal is a clean, coherent patch release that repairs the published CLI version surface without destabilizing the broader analytical/reporting package lane.

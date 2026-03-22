# ApexLab Release Procedure

This note captures the final operator-executed flow for publishing the initial `1.0.0` ApexLab release.

## Current local verification state

Already completed in this workspace:

- package version locked to `1.0.0`
- focused ApexLab test suite passing
- wheel and source distribution builds verified
- wheel install smoke-tested
- source distribution install smoke-tested
- active `dist/` cleaned to only `1.0.0` artifacts

## Important local repo note

As of 2026-03-22, the intended public repository exists at:

- `https://github.com/joediggidyyy/apexlab`

Within this workspace, `projects/apexlab/` is still present as a project lane inside `CodeSentinel-1` rather than as a standalone local clone of that public repository.

That means the following must be performed in the actual public `apexlab` repository context before release publication:

- create the release tag there
- publish the package artifacts through the chosen release flow

## Operator release flow

1. Move into the standalone local clone of the intended public `apexlab` repository.
2. Verify the repository remote points to `https://github.com/joediggidyyy/apexlab`.
3. Confirm the synced `ApexLab 1.0.0` package contents are present on `main`.
4. Run the package validation one more time in that standalone repo context if desired:
   - `python -m pytest tests`
   - `python -m build`
5. Confirm the final `dist/` contains only:
   - `apexlab-1.0.0-py3-none-any.whl`
   - `apexlab-1.0.0.tar.gz`
6. Create the release tag `v1.0.0`.
7. Push the tag to the intended public remote.
8. Publish the artifacts via the selected release channel.

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

## Release decision summary

`1.0.0` is intentionally lean. The correct goal for first publication is a clean, coherent, well-validated minimal package surface — not a maximal feature dump.

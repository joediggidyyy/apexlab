# ApexLab Publish Checklist

This checklist is the compact pre-publish lane for the `1.2.0` release.

## Package identity

- [x] package name is `apexlab`
- [x] package version is `1.2.0`
- [x] root package exports `ApexRegressor`

## Distribution artifacts

- [x] wheel builds successfully
- [x] source distribution builds successfully
- [x] active `dist/` contains only `1.2.0` artifacts
- [x] stale `1.0.0` artifacts removed from the active release surface

## Install verification

- [x] wheel install smoke-tested
- [x] source distribution install smoke-tested
- [x] installed package reports version `1.2.0`

## Quality gates

- [x] focused ApexLab test suite passing
- [x] full ApexLab test suite passing
- [x] report helpers directly tested
- [x] version consistency directly tested
- [x] no current editor errors reported for `projects/apexlab`
- [x] field test executed successfully
- [x] analytical reference-validation run passed
- [x] CLI version-flag regression coverage added

## Publish-facing docs

- [x] `README.md` describes the current install and usage story
- [x] `RELEASE_NOTES_DRAFT.md` reflects the `1.2.0` release surface
- [x] `API_OVERVIEW.md` reflects implemented public APIs
- [x] `RELEASE_PROCEDURE.md` documents the final operator publish flow

## Final operator check before publish

- [x] confirm release notes wording is final for the intended `1.2.0` release
- [x] confirm repository remote/publish target is the intended public `apexlab` repository: `https://github.com/joediggidyyy/apexlab`
- [ ] sync the validated `1.2.0` package tree to the public `apexlab` repository
- [ ] publish the tagged `1.2.0` release artifacts through the chosen release flow
- [x] rerun-safe publish workflow skips already-uploaded artifacts when PyPI reports them as existing

## Current execution-context note

Verified from this workspace on 2026-03-25:

- the intended public repository exists at `https://github.com/joediggidyyy/apexlab`
- `projects/apexlab/` is a real git checkout with `origin` pointed at `https://github.com/joediggidyyy/apexlab.git`
- the current working tree contains the validated analytical, reporting, and model-family expansion needed for `1.2.0`
- `python -m pytest tests` passed with `63 passed`
- fresh `1.2.0` wheel and source distribution artifacts were built successfully
- both the wheel and source distribution smoke-installed cleanly and reported `apexlab 1.2.0`
- therefore the remaining tasks are committing the `1.2.0` prep, pushing the validated tree, tagging `v1.2.0`, and publishing the artifacts

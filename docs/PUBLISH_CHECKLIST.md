# ApexLab Publish Checklist

This checklist is the compact pre-publish lane for the `1.1.0` release.

## Package identity

- [x] package name is `apexlab`
- [x] package version is `1.1.0`
- [x] root package exports `ApexRegressor`

## Distribution artifacts

- [x] wheel builds successfully
- [x] source distribution builds successfully
- [x] active `dist/` contains only `1.1.0` artifacts
- [x] stale `1.0.0` artifacts removed from the active release surface

## Install verification

- [x] wheel install smoke-tested
- [x] source distribution install smoke-tested
- [x] installed package reports version `1.1.0`

## Quality gates

- [x] focused ApexLab test suite passing
- [x] full ApexLab test suite passing
- [x] report helpers directly tested
- [x] version consistency directly tested
- [x] no current editor errors reported for `projects/apexlab`
- [x] field test executed successfully
- [x] analytical reference-validation run passed

## Publish-facing docs

- [x] `README.md` describes the current install and usage story
- [x] `RELEASE_NOTES_DRAFT.md` reflects the `1.1.0` release surface
- [x] `API_OVERVIEW.md` reflects implemented public APIs
- [x] `RELEASE_PROCEDURE.md` documents the final operator publish flow

## Final operator check before publish

- [x] confirm release notes wording is final for the intended lean `1.1.0` release
- [x] confirm repository remote/publish target is the intended public `apexlab` repository: `https://github.com/joediggidyyy/apexlab`
- [ ] sync the validated `1.1.0` package tree to the public `apexlab` repository
- [ ] publish the tagged `1.1.0` release artifacts through the chosen release flow

## Current execution-context note

Verified from this workspace on 2026-03-25:

- the intended public repository exists at `https://github.com/joediggidyyy/apexlab`
- `projects/apexlab/` is a real git checkout with `origin` pointed at `https://github.com/joediggidyyy/apexlab.git`
- the current working tree contains the `1.1.0` analytical/reporting expansion and has now passed build + smoke verification locally
- therefore the remaining tasks are push/sync, tag creation, and artifact publication

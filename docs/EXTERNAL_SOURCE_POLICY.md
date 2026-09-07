# External Source Trust Policy

This policy governs any autonomous use of external repositories, libraries, frameworks, plugins, assets, generators, websites, documentation or services for Jumpy.

## Default posture
External material is research input first, dependency second. Never execute, vendor, install, copy or import third-party code/assets merely because they are public.

## Candidate quality gates
Prefer sources that satisfy most of the following:
- active maintenance or a meaningful release/update within roughly the last 18 months;
- established adoption for its category (stars/downloads/users/community references) or official/recognized stewardship;
- clear documentation and issue/release history;
- explicit license compatible with Jumpy's intended commercial distribution;
- no unresolved security red flags, suspicious install hooks or opaque binaries;
- clear benefit over implementing a smaller local solution.

A niche or new project may pass with lower popularity only when it is official, technically exceptional, or uniquely relevant and its source/licensing can be reviewed.

## License policy
Preferred licenses: MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, Zlib, CC0 for assets, and other clearly permissive terms after review.

Do not autonomously vendor GPL/AGPL code, proprietary code, source-available code with field-of-use restrictions, or content without an explicit usable license. LGPL/MPL or attribution/share-alike material requires explicit compatibility review before integration.

Every incorporated third-party asset/code component must retain required notices and be recorded in `THIRD_PARTY_NOTICES.md` or the project's equivalent.

## Security policy
- Never run arbitrary curl|sh / wget|sh installers.
- Never execute code fetched from an unreviewed source with repository secrets available.
- Research/download/evaluation happens in an isolated disposable directory or sandbox first.
- Never expose GitHub PATs, API keys, signing material or user data to third-party code.
- Pin external GitHub Actions to full commit SHAs.
- Prefer exact package versions/checksums or immutable release artifacts over moving branches/tags.
- Reject dependencies that introduce unnecessary network access, telemetry, post-install scripts, native binaries, broad filesystem access or privilege requirements.
- No external dependency may modify `.github/`, signing configuration, secrets, release credentials or publishing settings autonomously.

## Integration workflow
1. Search broadly: official docs, GitHub, Godot Asset Library, package registries and reputable technical sources.
2. Compare at least two viable candidates when the decision is material.
3. Verify recency, adoption, license, repository ownership, releases and security posture.
4. Inspect source/install behavior before execution.
5. Prototype in isolation without secrets.
6. Integrate the smallest necessary surface.
7. Run Godot/static/security validation.
8. Record provenance/license/version and why it was selected.
9. Revert automatically if validation regresses.

## Asset and sprite generation
Generated or imported visual/audio assets must have provenance that permits commercial use. Prefer procedural generation, locally generated originals, permissively licensed tools/models/assets, or user-owned inputs. Do not copy recognizable copyrighted game assets or stylesheets directly from third-party projects.

External projects may be studied for algorithms, pipelines, UX patterns and architecture when legally permitted; copying implementation must follow the source license and attribution requirements.

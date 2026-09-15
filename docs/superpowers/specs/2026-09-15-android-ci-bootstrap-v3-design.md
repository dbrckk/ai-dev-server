# Android CI Bootstrap V3 Design

## Scope

Remove transient Android SDK archive corruption as a source of false-negative release gates without weakening any mobile validation.

## Evidence

Two independent required mobile runs failed before project validation completed:

- Android Emulator package download produced an invalid ZIP during `sdkmanager` bootstrap.
- NDK 28.2.13676358 installation produced `Archive is not a ZIP archive` during Flutter/Gradle configuration.

Both failures originated in Android package downloads, not repository code.

## Design

Add `scripts/bootstrap-android-ci.sh` as the single bounded Android CI bootstrap entry point. It:

1. validates `ANDROID_HOME` and `sdkmanager`;
2. exposes platform-tools, cmdline-tools and emulator paths through `GITHUB_PATH` when available;
3. accepts Android licenses;
4. installs `platform-tools` and `emulator` with at most three attempts;
5. on a failed attempt, removes only known partial SDK download/cache directories before retrying;
6. returns non-zero after the final failed attempt.

Both `Mobile Studio Real Build` and the Flutter job in `Multi-Engine E2E Benchmark` call this script. No build/test step is skipped or converted to soft-fail.

## Safety

- Retries are bounded to three attempts.
- Cleanup is restricted to Android SDK temporary/cache package download locations; installed SDK components are not broadly deleted.
- Final failure remains a hard gate failure.
- The script never downloads from a new source and never changes credentials or permissions.

## Verification

Tests use a fake `sdkmanager` to prove first-attempt failure followed by success is retried, persistent failure remains non-zero, and both workflows use the shared bootstrap script.

#!/usr/bin/env bash
set -euo pipefail

: "${ANDROID_HOME:?ANDROID_HOME must be set}"
SDKMANAGER="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"

if [[ ! -x "$SDKMANAGER" ]]; then
  echo "sdkmanager not executable at $SDKMANAGER" >&2
  exit 2
fi

if [[ -n "${GITHUB_PATH:-}" ]]; then
  printf '%s\n' \
    "$ANDROID_HOME/platform-tools" \
    "$ANDROID_HOME/cmdline-tools/latest/bin" \
    "$ANDROID_HOME/emulator" >> "$GITHUB_PATH"
fi

# `yes` normally exits with SIGPIPE once sdkmanager has consumed every answer.
# Judge the sdkmanager process itself rather than the producer side of the pipe.
set +e
yes | "$SDKMANAGER" --licenses >/dev/null
license_status=${PIPESTATUS[1]}
set -e
if [[ "$license_status" -ne 0 ]]; then
  echo "Android SDK license acceptance failed with status $license_status" >&2
  exit "$license_status"
fi

cleanup_partial_downloads() {
  rm -rf \
    "$ANDROID_HOME/.temp" \
    "$ANDROID_HOME/.cache" \
    "${ANDROID_USER_HOME:-${HOME:-/tmp}/.android}/cache" \
    2>/dev/null || true
}

# Flutter's current Android template uses this NDK. Pre-installing it here keeps
# the same package acquisition behind the bounded retry boundary instead of
# leaving Gradle to perform an unbounded one-shot download during a fixture.
packages=(
  "platform-tools"
  "emulator"
  "ndk;28.2.13676358"
)

last_status=1
for attempt in 1 2 3; do
  set +e
  "$SDKMANAGER" "${packages[@]}"
  last_status=$?
  set -e

  if [[ "$last_status" -eq 0 ]]; then
    exit 0
  fi

  echo "Android SDK package install attempt $attempt/3 failed with status $last_status" >&2
  if [[ "$attempt" -lt 3 ]]; then
    cleanup_partial_downloads
  fi
done

exit "$last_status"

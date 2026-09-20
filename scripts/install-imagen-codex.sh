#!/usr/bin/env bash
set -euo pipefail

version="v0.1.2"
base_url="https://github.com/Leechael/imagen/releases/download/${version}"
bin_dir="$HOME/.local/bin"
mkdir -p "$bin_dir"

case "$(uname -m)" in
  x86_64|amd64)
    archive="imagen-linux-amd64.tar.gz"
    expected_sha256="2ae06f466ba49898ff0c8a2afdd77b74481002d3036c247316138c727ceb7cb0"
    ;;
  aarch64|arm64)
    archive="imagen-linux-arm64.tar.gz"
    expected_sha256="caf5f2987db8e4e5e255a7c464ea3355dba778f45e952254726c22a9c82ff4e3"
    ;;
  *)
    echo "Unsupported imagen architecture: $(uname -m)" >&2
    exit 2
    ;;
esac

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl --fail --location --silent --show-error \
  "${base_url}/${archive}" \
  --output "$tmp/$archive"

printf '%s  %s\n' "$expected_sha256" "$tmp/$archive" | sha256sum --check --status

tar -xzf "$tmp/$archive" -C "$tmp"
test -f "$tmp/imagen"
install -m 0755 "$tmp/imagen" "$bin_dir/imagen"

"$bin_dir/imagen" --version >/dev/null
printf 'imagen %s installed with verified sha256\n' "$version"

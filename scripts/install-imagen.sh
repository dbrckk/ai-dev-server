#!/usr/bin/env bash
set -euo pipefail

version="${IMAGEN_VERSION:-v0.1.2}"
bin_dir="${IMAGEN_BIN_DIR:-$HOME/.local/bin}"
base_url="https://github.com/Leechael/imagen/releases/download/${version}"

case "$(uname -s)" in
  Linux) os="linux" ;;
  *)
    echo "Unsupported OS for managed imagen install: $(uname -s)" >&2
    exit 2
    ;;
esac

case "$(uname -m)" in
  x86_64|amd64) arch="amd64" ;;
  aarch64|arm64) arch="arm64" ;;
  *)
    echo "Unsupported architecture for managed imagen install: $(uname -m)" >&2
    exit 2
    ;;
esac

archive="imagen-${os}-${arch}.tar.gz"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$bin_dir"

curl --fail --silent --show-error --location --retry 3 --max-time 120   "${base_url}/checksums.txt" -o "$tmp/checksums.txt"
curl --fail --silent --show-error --location --retry 3 --max-time 180   "${base_url}/${archive}" -o "$tmp/${archive}"

checksum_line="$(grep -E "^[0-9a-fA-F]{64}[[:space:]]+[*]?${archive}$" "$tmp/checksums.txt" || true)"
if [[ -z "$checksum_line" ]]; then
  echo "Pinned imagen release checksum is missing for ${archive}" >&2
  exit 2
fi
(
  cd "$tmp"
  printf '%s\n' "$checksum_line" | sha256sum --check --strict -
)

mkdir -p "$tmp/unpack"
tar -xzf "$tmp/${archive}" -C "$tmp/unpack"
candidate="$(find "$tmp/unpack" -type f -name imagen -perm -u+x -print -quit)"
if [[ -z "$candidate" ]]; then
  candidate="$(find "$tmp/unpack" -type f -name imagen -print -quit)"
fi
if [[ -z "$candidate" ]]; then
  echo "imagen binary not found in pinned release archive" >&2
  exit 2
fi

install -m 0755 "$candidate" "$bin_dir/imagen"
"$bin_dir/imagen" --help >/dev/null

printf 'imagen %s installed at %s\n' "$version" "$bin_dir/imagen"

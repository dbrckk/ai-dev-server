#!/usr/bin/env bash
set -euo pipefail

install_root="${ASSET_FORGE_HOME:-$HOME/.local/share/asset-forge}"
bin_dir="$HOME/.local/bin"
repo_url="${ASSET_FORGE_REPOSITORY:-https://github.com/dbrckk/asset-forge.git}"
ref="${ASSET_FORGE_REF:-main}"

mkdir -p "$(dirname "$install_root")" "$bin_dir"

if [[ -L "$install_root" ]]; then
  echo "Refusing symlinked ASSET_FORGE_HOME: $install_root" >&2
  exit 2
fi

if [[ -e "$install_root" && ! -d "$install_root/.git" ]]; then
  echo "ASSET_FORGE_HOME exists but is not a git checkout: $install_root" >&2
  exit 2
fi

if [[ ! -d "$install_root/.git" ]]; then
  git clone --filter=blob:none --no-checkout "$repo_url" "$install_root"
fi

git -C "$install_root" remote set-url origin "$repo_url"
git -C "$install_root" fetch --depth 1 origin "$ref"
git -C "$install_root" checkout --detach --force FETCH_HEAD
git -C "$install_root" clean -fdx

python -m pip install --user --no-deps --editable "$install_root"

if [[ ! -x "$bin_dir/asset-forge" ]]; then
  echo "Asset Forge console script was not installed in $bin_dir" >&2
  exit 2
fi

"$bin_dir/asset-forge" --help >/dev/null
printf 'Asset Forge installed at %s (%s)\n' "$install_root" "$(git -C "$install_root" rev-parse --short HEAD)"

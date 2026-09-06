#!/usr/bin/env bash
set -euo pipefail
npm install -g opencode-pollinations-plugin
npx --yes opencode-pollinations-plugin
cat <<'EOF'
Plugin Pollinations ajouté à OpenCode.
Dans OpenCode, utilise ensuite /poll login pour connecter ton compte Pollinations.
Les secrets restent hors du dépôt.
EOF

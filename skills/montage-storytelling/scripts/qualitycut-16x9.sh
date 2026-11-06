#!/bin/bash
# Lance la préparation QualityCut (pack AI Studio) sur une source 16:9 déjà prête.
# preparer.sh ne renormalise pas une source qui existe déjà : on garde donc le 16:9.
# Si le modèle Whisper large ne se télécharge pas (blocage observé), TURBO=1 utilise une copie
# des scripts avec whisper-large-v3-turbo, sans toucher au skill installé.
# usage : [TURBO=1] qualitycut-16x9.sh <job> <nom>      (la source doit être <job>/sources/<nom>.mov)
set -euo pipefail
J=$(cd "$1" && pwd); N=$2
export PATH="$HOME/.local/bin:$PATH"
Q=~/.claude/skills/qualitycut/scripts
if [ "${TURBO:-0}" = 1 ]; then
  T="$J/qualitycut-turbo"; rm -rf "$T"; cp -R ~/.claude/skills/qualitycut/scripts "$T"
  sed -i '' "s#mlx-community/whisper-large-v3-mlx#mlx-community/whisper-large-v3-turbo#g" "$T"/*.py; Q=$T
fi
PYTHON=${PYTHON:-$HOME/.venv-velvet/bin/python} bash "$Q/preparer.sh" "$J" "$J/sources/$N.mov"
echo "Scripts QualityCut utilisés : $Q   (à réutiliser pour couper.py, verifier.py, exporter_cuts.py)"

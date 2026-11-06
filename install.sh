#!/bin/bash
# Copie les skills de ce dépôt dans ~/.claude/skills (les anciennes versions vont dans ~/.claude/skills-sauvegarde/).
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); C=~/.claude/skills; B=~/.claude/skills-sauvegarde/$(date +%Y%m%d-%H%M%S)
mkdir -p "$C"
for s in montage-storytelling real-sfx; do
  if [ -d "$C/$s" ]; then mkdir -p "$B"; mv "$C/$s" "$B/$s"; echo "ancienne version de $s mise de côté dans $B"; fi
  cp -R "$D/skills/$s" "$C/$s"; echo "installé : $s"
done
mkdir -p "$C/montage-storytelling/colorimetrie"; cp "$D/colorimetrie/"* "$C/montage-storytelling/colorimetrie/"
[ -f "$C/real-sfx/config.json" ] || cp "$C/real-sfx/config.example.json" "$C/real-sfx/config.json"
ko=0
export PATH="$HOME/.local/bin:$PATH"
for t in ffmpeg node python3; do command -v $t >/dev/null || { echo "MANQUE : $t (installe d'abord le pack AI Studio, voir INSTALL.md)"; ko=1; }; done
[ -x ~/.venv-velvet/bin/python ] || { echo "MANQUE : ~/.venv-velvet (installe d'abord le pack AI Studio, voir INSTALL.md)"; ko=1; }
[ -d "$C/qualitycut" ] || { echo "MANQUE : le skill qualitycut (pack AI Studio, voir INSTALL.md)"; ko=1; }
if [ $ko = 1 ]; then echo "INSTALLATION INCOMPLÈTE : installe le pack AI Studio puis relance ce script."; exit 2; fi
echo "INSTALLATION OK : ferme puis rouvre Claude Code."

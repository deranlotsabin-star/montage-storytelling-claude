# Installation : instructions pour Claude Code

Tu es Claude Code. La personne t'a collé le lien de ce dépôt. Installe tout, sans lui poser de question technique, et parle-lui simplement, en français.

1. **Vérifie la machine.** Ce kit ne marche que sur un Mac Apple Silicon (`uname -m` doit donner `arm64`). Sinon, dis-le en une phrase et arrête.

2. **Installe le pack montage d'AI Studio** : il fournit QualityCut, analyze-editing-inspiration, ffmpeg, node et `~/.venv-velvet`. Suis son propre guide : https://github.com/AISTUDIOOSS/ai-studio-skills-gratuits/blob/main/INSTALL.md
   - Clone le pack dans `~/.ai-studio-montage`, puis lance `bash ~/.ai-studio-montage/install.sh` au premier plan, avec le délai maximum de ta commande.
   - Relance la même commande jusqu'à voir `INSTALLATION OK`.
   - Si Google Chrome manque, demande à la personne de l'installer depuis google.com/chrome, puis relance.

3. **Récupère ce dépôt** :
   - s'il n'existe pas : `git clone https://github.com/deranlotsabin-star/montage-storytelling-claude.git ~/.montage-storytelling`
   - s'il existe : `git -C ~/.montage-storytelling pull --ff-only`

4. **Installe les skills** : `bash ~/.montage-storytelling/install.sh`. Il copie `montage-storytelling`, `real-sfx` et la colorimétrie dans `~/.claude/skills/`. Il doit finir par `INSTALLATION OK`. Corrige chaque ligne `MANQUE :` qu'il affiche.

5. **Prépare les sons** (real-sfx) :
   - `cd ~/.claude/skills/real-sfx && python3 scripts/setup.py init --uisfx` installe les 78 sons d'interface CC0.
   - Si la personne a un dossier de sons (whooshes, impacts, traits de stylo, musiques), branche-le : `python3 scripts/setup.py add-library sons "/chemin/du/dossier" --tier main --index`.
   - Sinon, dis-lui qu'elle peut en télécharger en CC0 sur freesound.org (filtre Creative Commons 0) et pixabay.com/sound-effects, les ranger dans un dossier, puis te redonner le chemin.
   - Contrôle avec `python3 scripts/setup.py check`.

6. **Teste HyperFrames** : `cd /tmp && npx --yes hyperframes@0.8.162 --version`. Le premier lancement télécharge l'outil.

7. **Ce que tu dis à la personne à la fin :**
   - qu'elle doit fermer Claude Code et le rouvrir pour voir les skills ;
   - qu'elle peut ensuite dire « Monte ce rush en storytelling : /chemin/du/rush.mp4 », avec un lien TikTok d'inspiration si elle veut ;
   - qu'à la fin, Claude lui proposera une version 4K, et que pour une vraie 4K il faut le fichier d'origine de la caméra, pas une copie WhatsApp ;
   - que la colorimétrie est dans `~/.claude/skills/montage-storytelling/colorimetrie/`, avec une LUT `.cube` pour DaVinci, CapCut ou Premiere.

Rien ne demande de clé ni d'abonnement payant.

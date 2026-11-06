---
name: montage-storytelling
description: Monte un rush face cam parlé (avis, témoignage, storytelling) au style d'une référence TikTok de type @morgan_rize, en 16:9 1920x1080 ou 4K. Coupes QualityCut, écrans texte plein cadre beige et orange avec un mot clé en serif italique ou en gras, mots qui entrent flous au moment où ils sont dits, cartes à cocher avec le visage en vignette, texte barré, sous-titres discrets, zooms secs, étalonnage chaud, sons réels (real-sfx) et nappe musicale. À utiliser pour « monte ce rush en storytelling », « style Morgan », « monte cet avis comme la référence », ou quand on donne un rush avec une vidéo d'inspiration de ce genre.
---

# Montage storytelling (style « Morgan »)

Tu reçois un rush face cam parlé en français, et parfois une vidéo de référence. Tu fais tout dans l'ordre et tu livres un MP4. Parle simplement à la personne : elle n'est pas forcément technique.

Chemins :
- `KIT` : ce skill (`~/.claude/skills/montage-storytelling`).
- `QC` : `~/.claude/skills/qualitycut` (pack AI Studio).
- `SFX` : `~/.claude/skills/real-sfx`.
- `PY` : `~/.venv-velvet/bin/python` (créé par le pack AI Studio).
- `PROJET` : un dossier neuf à côté du rush, par exemple `<dossier du rush>/<nom>-montage/`.

Commence chaque commande par `export PATH="$HOME/.local/bin:$PATH";`. Si `PY`, `QC`, ffmpeg, node ou Google Chrome manquent, l'installation n'est pas faite : lis `INSTALL.md` à la racine du dépôt.

Lis d'abord [references/fiche-style-reference.md](references/fiche-style-reference.md) : ce sont les règles du style. [exemples/plan-exemple.json](exemples/plan-exemple.json) est un vrai plan complet, à prendre comme modèle de forme, jamais de contenu.

## 0. La référence (si la personne en donne une)

Lance le skill `analyze-editing-inspiration` sur le lien. S'il en sort une autre fiche que celle fournie ici, garde ses couleurs et ses polices pour l'étape 4 (champ `etalonnage` et CSS de `outil/monter.py`).

## 1. Source en 16:9

QualityCut met tout en vertical par défaut. Pour garder le 16:9, prépare la source toi-même avant :

```bash
bash KIT/scripts/preparer-16x9.sh /chemin/rush.mp4 PROJET/job/sources/NOM.mov [x:y:l:h]
```

Le 3e argument efface un logo incrusté. Repère sa position sur une image du rush. Un Osmo Pocket 3 reçu par WhatsApp en 832x464 donne `20:88:178:28`. Contrôle sur une image que le logo a disparu.

## 2. Coupes (QualityCut, obligatoire)

Lis `QC/SKILL.md` et `QC/references/pipeline-local.md`, et suis-les.

```bash
bash KIT/scripts/qualitycut-16x9.sh PROJET/job NOM
```

Si le téléchargement du modèle Whisper large bloque (taille qui ne bouge plus pendant 1 minute), arrête et relance avec `TURBO=1`. Puis :
- Lis `PROJET/job/transcription/LISTE-MOTS.txt` en entier.
- Écris `PROJET/job/montage/NOM.txt`, une ligne par passage gardé : `premier-dernier # motif`.
- Garde la dernière prise complète de chaque phrase. Retire les reprises, les rires, les échanges avec la personne derrière la caméra et les commentaires de fin.
- Une prise mêlée à un rire, ou que deux transcriptions lisent différemment, se remplace par une prise claire. Vérifie avec `zone.py`.
- Lance `couper.py`, `appliquer_revue.py`, `verifier.py` et `exporter_cuts.py`, avec les scripts qu'indique la fin de `qualitycut-16x9.sh`.
- Les écarts de `verifier.py` doivent se limiter à l'écriture (« 30000 » contre « 30 000 »). Un mot manquant veut dire une mauvaise prise : corrige.

## 3. Lire les mots du montage

```bash
cd PROJET && PY KIT/outil/monter.py --job job --rush NOM --liste
```

Repère :
- le hook, en 1 ou 2 phrases ;
- les chiffres et les mots chocs ;
- les énumérations de 3 éléments ou plus, qui deviennent des cartes ;
- les constructions « pas X, mais Y », qui deviennent du texte barré ;
- la phrase de fin.

## 4. Écrire `PROJET/v1/plan.json`

- `textes` : `{indice: "texte affiché"}` pour corriger l'écrit (`"30 000"`, `"€"`, `"100 %"`, `"cold call"`). Mets `""` pour masquer un mot.
- `ecrans` : une liste de `{fond: "beige"|"orange", lignes: [["i-j", style], ...]}`. Les styles possibles :
  - `petit` : la phrase autour du mot clé ;
  - `serif` : le mot qui touche, en Instrument Serif italique ;
  - `gras` : le mot qui frappe, en extra-gras ;
  - `geant` : un chiffre choc, comme « 0 € » ;
  - `barre` : barré d'un trait. Un 3e élément facultatif donne le mot qui déclenche le trait.
- `cartes` : une liste de `{titre, de, a, items: [[indice_du_mot_declencheur, "texte"], ...]}`. L'élément se coche quand le mot est dit, et le visage passe en vignette à droite.
- `muet` : `["i-j"]`, les mots sans sous-titre (« bah », « euh »).
- `tenue_fin` : les secondes de tenue du dernier écran après la dernière syllabe (1,6 conseillé).
- `etalonnage` : un filtre ffmpeg facultatif. Par défaut, c'est l'étalonnage chaud de `colorimetrie/`.

Règles du style :
- Un écran toutes les 2 à 5 s de face cam, sur la phrase forte. Il en faut environ 1 pour 5 s de vidéo.
- Le beige pour les constats et les négations, l'orange pour l'émotion, les promesses et la fin.
- Un seul mot clé par écran, et le reste en petit.
- Évite deux écrans collés, sauf pour une gradation ou la fin.
- Un texte barré a besoin d'environ 0,5 s visible après le trait. Si la phrase suivante enchaîne trop vite, fusionne-les en un seul écran.
- La dernière phrase va sur un écran orange avec `tenue_fin`.

## 5. Générer et rendre

```bash
cd PROJET && PY KIT/outil/monter.py --job job --rush NOM --plan v1/plan.json --out v1
cd PROJET/v1/composition && mkdir -p ../export && nohup sh -c 'npx --yes hyperframes@0.8.162 render . -o ../export/NOM-rendu.mp4 > ../render.log 2>&1; echo "FIN $?" >> ../render.log' >/dev/null 2>&1 &
until grep -q '^FIN' PROJET/v1/render.log 2>/dev/null; do sleep 20; done; tail -3 PROJET/v1/render.log
```

- Compte environ 1 min 30 de rendu par minute de vidéo.
- **4K** : ajoute `--resolution 4k --quality delivery` au rendu. Les textes, les écrans et les cartes sortent nets en 3840x2160. L'image filmée ne gagne en détail que si le rush d'origine est lui-même en 4K : demande le fichier original de la caméra, pas une copie WhatsApp.
- N'agrandis pas un visage avec un modèle IA (RealESRGAN et autres) : la peau devient lisse et « plastique », ce qui casse la confiance dans un avis.

## 6. Contrôler l'image

Sors une planche d'images du rendu : le hook, chaque écran, chaque carte, une ligne de sous-titres et la fin. Regarde-la vraiment.

```bash
for t in 1 3 6 10 20 30 45 58; do ffmpeg -v error -y -ss $t -i export/NOM-rendu.mp4 -frames:v 1 -vf scale=480:-1 c_$t.png; done
```

- Rien ne déborde, et chaque écran se lit en entier avant de disparaître.
- Les sous-titres se coupent en fin de phrase, jamais sur un petit mot comme « de » ou « les ».
- Pour corriger, crée `v2/` avec une copie modifiée de `plan.json`, sans changer les coupes.

## 7. Sons réels (real-sfx)

`monter.py` écrit `v1/cues.json` (whoosh à chaque écran, impact sur les mots `gras` et `geant`, clic à chaque coche, trait de feutre sur les barrés).

```bash
cd SFX && python3 scripts/setup.py check
python3 scripts/from_cues.py PROJET/v1/cues.json --video PROJET/v1/export/NOM-rendu.mp4 --out PROJET/v1/sfx/cues.json --kind barre=slices:<id d'un trait de feutre>
python3 scripts/mix.py PROJET/v1/sfx/cues.json --out PROJET/v1/sfx/NOM-sfx.mp4 --voice-safe
python3 scripts/critique.py PROJET/v1/sfx/NOM-sfx_resolved_cues.json PROJET/v1/sfx/NOM-sfx_sfx_track.wav
```

- Trouve l'id du trait de feutre avec `search.py --query "marker|underlining|scribble"`.
- Corrige seulement les 3 problèmes que donne `critique.py`, avec `sheet.py apply`. Par exemple, `{"highpass":140,"gain_db":-8}` sur un impact qui charge les basses sous la voix.
- Fige ensuite la feuille avec `sheet.py freeze`.
- Sans banque de sons : `setup.py init --uisfx`, puis ajoute des sons CC0 (voir le README).

## 8. Musique et niveau final

```bash
bash KIT/outil/musique.sh PROJET/v1/sfx/NOM-sfx.mp4 /chemin/musique.mp3 PROJET/v1/export/NOM.mp4 -19
```

La musique passe à −19 dB, baissée sous la voix, avec un fondu d'entrée et de sortie. Le niveau final est à −14 LUFS. Choisis du piano ou une nappe calme et régulière, sans batterie, pour un récit.

## 9. Vérifier et livrer

- **Le texte** : retranscris l'export final avec Whisper. Tout le discours doit revenir, dans l'ordre.
- **Le niveau** : il doit être à −14 LUFS, avec une crête sous −1 dBFS.
- **Le journal** : écris `PROJET/v1/journal.md` avec les prises choisies et pourquoi, les écrans, ce qui est vérifié et ce qui ne l'est pas.
- **Ce que tu dis à la personne** : tu ne peux pas écouter. Dis « mesuré », jamais « écouté », et donne-lui les moments précis à écouter.
- **Les libellés interprétés** : signale ceux qu'elle doit confirmer, comme « cold call » écrit à la place de ce qu'a compris la transcription.

## 10. Proposer la version 4K (toujours, une fois la vidéo livrée)

Une fois la vidéo livrée en 1080p, propose toujours la 4K à la personne, en une question : « Ta vidéo est prête. Tu veux que je t'en fasse une version 4K ? ». Si elle a l'outil de question de Claude, donne deux boutons : « Oui, en 4K » et « Non, ça me va ». Ajoute en une phrase que si elle a le fichier d'origine de la caméra, et pas une copie WhatsApp, l'image sera vraiment plus détaillée. Sinon, seuls les textes et les écrans gagnent en netteté.

Si elle dit oui :

```bash
PY KIT/scripts/version_4k.py --projet PROJET --version v1 --rush NOM [--original /chemin/fichier-camera.mp4] [--logo x:y:l:h]
```

- Le montage, les sons et la musique ne bougent pas. Le script rend la même composition en 3840x2160 et remet le son de la version livrée.
- Avec `--original`, il refait la vidéo coupée à partir du fichier 4K, avec les mêmes coupes et le même étalonnage. Il compare d'abord le son des deux fichiers et rattrape un décalage. Pour `--logo`, la position est en pixels de ce fichier 4K.
- Le rendu est environ 4 fois plus long qu'en 1080p.
- **Contrôle** : `ffprobe` doit donner 3840x2160 et la même durée que la version livrée. Sors une planche : la bouche doit tomber sur les mots, et les textes doivent être nets.
- Livre `PROJET/v1-4k/export/NOM-4k.mp4`.
- N'agrandis jamais le visage avec un modèle IA : voir l'étape 5.

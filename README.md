# Montage storytelling avec Claude Code

Monte un avis ou un témoignage filmé face caméra au style des vidéos storytelling TikTok, avec Claude Code. Tu donnes un rush, Claude choisit les prises et coupe au mot près. Il ajoute :
- des écrans texte plein cadre ;
- des cartes à cocher ;
- du texte barré ;
- des sous-titres ;
- des sons réels et une musique.

Puis il te livre le MP4, et te propose une version 4K.

Référence du style : [@morgan_rize sur TikTok](https://www.tiktok.com/@morgan_rize/video/7704290788561128736).

## Installation en un copier-coller

Il te faut un **Mac Apple Silicon** (M1 à M4), [Claude Code](https://claude.com/claude-code), [Google Chrome](https://www.google.com/chrome/) et quelques Go libres. Ouvre Claude Code et colle ce message :

```
Installe le kit montage storytelling : https://github.com/deranlotsabin-star/montage-storytelling-claude — lis INSTALL.md et fais tout.
```

Ferme puis rouvre Claude Code. Ensuite, dis-lui simplement :

```
Monte ce rush en storytelling : /chemin/de/ton-rush.mp4
```

## Les plugins utilisés (liens)

| Outil | Rôle dans le montage | Lien |
|---|---|---|
| **Pack montage AI Studio** | Il installe QualityCut (choix des prises, coupes au mot près), analyze-editing-inspiration (analyse d'une vidéo de référence), ffmpeg, node et l'environnement Python. | [github.com/AISTUDIOOSS/ai-studio-skills-gratuits](https://github.com/AISTUDIOOSS/ai-studio-skills-gratuits) |
| **montage-storytelling** (ce dépôt) | Le skill qui enchaîne tout, et le générateur des écrans, cartes et sous-titres. | [skills/montage-storytelling](skills/montage-storytelling/SKILL.md) |
| **HyperFrames** (HeyGen) | Il transforme la composition HTML animée en MP4, en 1080p ou en 4K. | [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) |
| **real-sfx** (inclus, MIT) | Il pose de vrais sons enregistrés (whooshes, impacts, clics) à l'image près et vérifie le mixage. | [skills/real-sfx](skills/real-sfx/README.md) |
| **uisfx** (inclus dans real-sfx) | Les sons d'interface CC0, pour les coches des cartes. | [github.com/romainsimon/uisfx](https://github.com/romainsimon/uisfx) |
| **MLX Whisper** | La transcription locale et gratuite, utilisée par QualityCut et pour le contrôle final. | [pypi.org/project/mlx-whisper](https://pypi.org/project/mlx-whisper/) |
| **GSAP** | Les animations des textes et des cartes. | [gsap.com](https://gsap.com) |
| **Polices** | Inter pour les textes, Instrument Serif Italic pour les mots clés (licence OFL). | [Inter](https://github.com/rsms/inter) · [Instrument Serif](https://github.com/Instrument/instrument-serif) |
| **Colorimétrie** | Notre étalonnage chaud, avec sa LUT `.cube` pour DaVinci, CapCut ou Premiere. | [colorimetrie/](colorimetrie/README.md) |
| **color-grade** (en option) | Il copie l'étalonnage d'une référence ou d'un look de film. Il n'est pas inclus (voir plus bas). | Auteur : @ai.volve.news |

Les sons et la musique CC0 viennent de [Freesound](https://freesound.org) (filtre « Creative Commons 0 ») et de [Pixabay](https://pixabay.com/sound-effects/). La musique du montage d'exemple est une nappe piano calme de Pixabay.

## Comment la vidéo est construite

```
rush.mp4 ─▶ 1. source 16:9 (+ logo caméra effacé)
          ─▶ 2. QualityCut : transcription, choix des prises, coupes au mot près, contrôle
          ─▶ 3. plan.json : quels mots vont sur quels écrans, cartes, barrés
          ─▶ 4. monter.py : composition HyperFrames (écrans, cartes, sous-titres, zooms, étalonnage)
          ─▶ 5. rendu HyperFrames ─▶ planche de contrôle
          ─▶ 6. real-sfx : sons réels sur chaque événement + autocritique
          ─▶ 7. musique.sh : nappe sous la voix, niveau −14 LUFS
          ─▶ 8. contrôle final (retranscription, niveau) ─▶ MP4 1080p
          ─▶ 9. proposition de la version 4K (version_4k.py)
```

**Les règles du style** (détail dans [la fiche de style](skills/montage-storytelling/references/fiche-style-reference.md)) :

- **Rythme** : un écran texte plein cadre toutes les 2 à 5 s de face cam, posé sur la phrase forte.
- **Deux fonds** : beige `#F2EBE6` pour les constats, dégradé orange `#F57221` → `#D03F01` pour l'émotion et la fin.
- **Un seul mot clé par écran** : en serif italique s'il doit toucher, en extra-gras s'il doit frapper, en géant pour un chiffre choc. Le reste de la phrase reste petit.
- **Le texte suit la voix** : chaque mot entre flou au moment exact où il est dit.
- **Énumération** : une carte à cocher, avec le visage en vignette à droite.
- **« Pas X, mais Y »** : X est barré d'un trait.
- **Sous-titres** : petits et discrets, coupés en fin de phrase.
- **Zooms secs** sur les coupes, pour masquer les sauts d'image.
- **Image** : étalonnage chaud et vignettage.
- **Récit en 5 temps** : le hook, la montée, la chute, la leçon, puis la phrase finale tenue à l'écran.

## Contenu du dépôt

```
INSTALL.md                         instructions d'installation pour Claude Code
install.sh                         copie les skills dans ~/.claude/skills
skills/montage-storytelling/
  SKILL.md                         la méthode complète, étape par étape
  outil/monter.py                  générateur de la composition (écrans, cartes, sous-titres, zooms)
  outil/musique.sh                 nappe musicale baissée sous la voix + niveau final
  outil/assets/                    polices (OFL) et GSAP
  scripts/preparer-16x9.sh         source 16:9 + effacement du logo de la caméra
  scripts/qualitycut-16x9.sh       QualityCut en 16:9 (et secours Whisper turbo)
  scripts/version_4k.py            version 4K du montage livré
  references/                      fiche de style de la référence + profil JSON
  exemples/plan-exemple.json       un vrai plan complet (60 s, 12 écrans, 2 cartes)
skills/real-sfx/                   sound design avec des sons réels (MIT)
colorimetrie/                      réglages d'étalonnage + LUT morgan-chaud.cube
```

## Limites

- **Ordinateur** : Mac Apple Silicon uniquement, comme le pack AI Studio.
- **Écoute** : Claude ne peut pas écouter. Il mesure le son et te dit précisément quels moments écouter.
- **4K** : elle n'apporte du détail à l'image filmée que si tu donnes le fichier d'origine de la caméra. Une vidéo passée par WhatsApp reste floue, seuls les textes deviennent plus nets.
- **QualityCut** : son outil d'alignement (MMS_FA) a une licence non commerciale. Voir les précisions dans le pack AI Studio avant un usage commercial.
- **color-grade** n'est pas inclus : il n'a ni dépôt public ni licence de redistribution. Les réglages et la LUT de [colorimetrie/](colorimetrie/README.md) suffisent pour ce style.

Composants tiers et licences : [THIRD-PARTY.md](THIRD-PARTY.md).

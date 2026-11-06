# Colorimétrie

## Ce qui est appliqué dans le montage

Un étalonnage chaud et léger, proche de la référence : on lève un peu les ombres, on réchauffe, et on ajoute un vignettage. C'est ce qui donne le côté « soirée tamisée » au visage.

**1. Le filtre** (ffmpeg, appliqué par `monter.py` sur la vidéo coupée, réglable avec le champ `etalonnage` du plan) :

```
eq=brightness=0.035:contrast=1.06:saturation=1.08:gamma=1.08,colorbalance=rs=.03:gs=.0:bs=-.04:rm=.03:bm=-.03
```

| Réglage | Effet |
|---|---|
| `brightness 0.035`, `gamma 1.08` | Débouche les ombres d'un rush de nuit. |
| `contrast 1.06`, `saturation 1.08` | Un peu plus de relief et de couleur. |
| `colorbalance rs/rm +0.03`, `bs −0.04`, `bm −0.03` | Plus de rouge et moins de bleu dans les ombres et les tons moyens : l'image se réchauffe. |

**2. Le vignettage** (CSS dans la composition, il ne fait pas partie de la LUT) : les bords s'assombrissent jusqu'à 42 % autour d'une ellipse centrée sur le visage.

```
radial-gradient(ellipse 75% 70% at 46% 42%, transparent 55%, rgba(0,0,0,.42) 100%)
```

## La LUT : `morgan-chaud.cube`

C'est le même filtre en LUT 3D (36 points), pour l'utiliser ailleurs :

- **DaVinci Resolve** : copie le fichier dans le dossier des LUT (Réglages du projet > Gestion des couleurs > Ouvrir le dossier LUT), puis clic droit sur le plan > LUT.
- **CapCut** : Ajuster > LUT > Importer.
- **Premiere** : Lumetri > Création > Look.
- **ffmpeg** : `-vf lut3d=morgan-chaud.cube`

Elle a été vérifiée contre le filtre d'origine : 45,8 dB de PSNR, soit aucune différence visible.

## Aller plus loin : le skill color-grade

Pour copier l'étalonnage d'une autre vidéo, d'après 1 à 5 images de référence ou un des 20 looks de films intégrés, et en sortir une LUT `.cube`, il y a le skill **color-grade** de @ai.volve.news. Il n'a pas de dépôt public ni de licence de redistribution, donc il n'est pas inclus ici : demande-le à son auteur, ou à la personne qui t'a envoyé ce dépôt. Une fois installé dans `~/.claude/skills/color-grade`, demande à Claude : « étalonne ce rush comme ces images et sors-moi une LUT ».

#!/bin/bash
# Met un rush au format attendu par QualityCut, mais en 16:9 (1920x1080, 30 i/s, son 48 kHz),
# et efface au besoin un logo incrusté (ex. « DJI OSMO POCKET 3 »).
# usage : preparer-16x9.sh <rush> <job>/sources/<nom>.mov [delogo=x:y:l:h, en pixels du rush d'origine]
# Ex. Osmo Pocket 3 reçu par WhatsApp (832x464) : 20:88:178:28
set -euo pipefail
in=$1; out=$2; logo=${3:-}
mkdir -p "$(dirname "$out")"
vf=""
if [ -n "$logo" ]; then IFS=: read -r x y w h <<< "$logo"; vf="delogo=x=$x:y=$y:w=$w:h=$h,"; fi
vf="${vf}scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,unsharp=5:5:0.6,setsar=1,fps=30,format=yuv420p"
ffmpeg -nostdin -v error -y -i "$in" -map 0:v:0 -map 0:a:0 -vf "$vf" -af "aresample=48000:async=1:first_pts=0" \
  -c:v libx264 -preset fast -crf 16 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a pcm_s16le -ar 48000 -ac 2 -fps_mode cfr -r 30 -map_metadata -1 "$out"
echo "ok $out"

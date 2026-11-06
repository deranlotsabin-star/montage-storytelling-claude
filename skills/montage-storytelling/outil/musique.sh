#!/bin/bash
# Pose une nappe musicale sous le film (voix + SFX déjà mixés), baissée sous la voix, fondus d'entrée et de sortie,
# puis niveau final -14 LUFS pour les réseaux. Image intacte.
# usage : musique.sh <film_sfx.mp4> <musique> <sortie.mp4> [gain_musique_dB=-19]
set -euo pipefail
in=$1; mus=$2; out=$3; g=${4:--19}
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
fo=$(python3 -c "print(max(0, $d - 2.2))")
ffmpeg -nostdin -v error -y -i "$in" -i "$mus" -filter_complex "
[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][key];
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:$d,asetpts=PTS-STARTPTS,volume=${g}dB,afade=t=in:d=0.6,afade=t=out:st=$fo:d=2.2[m];
[m][key]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=450:makeup=1[md];
[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$out"
echo "ok $out"

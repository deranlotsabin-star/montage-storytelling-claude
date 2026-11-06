#!/usr/bin/env python3
"""Fait la version 4K (3840x2160) d'un montage déjà livré, sans rien changer au montage.
  python version_4k.py --projet PROJET --version v1 --rush NOM [--original /chemin/rush-4k.mp4] [--logo x:y:l:h]

- Copie PROJET/<version>/composition dans PROJET/<version>-4k/composition.
- Avec --original (le fichier de la caméra, en 4K) : refait la vidéo coupée en 3840x2160 avec les mêmes coupes et le même
  étalonnage, après avoir vérifié que ce fichier est calé sur le rush utilisé pour le montage (son comparé).
  Sans --original : garde la vidéo 1080p ; seuls les textes, écrans et cartes gagnent en netteté.
- Rend en --resolution 4k --quality delivery, puis remet le son final de la version livrée (sons et musique compris).
- --logo : position du logo dans le fichier original (en pixels de CE fichier), à effacer.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys
ap = argparse.ArgumentParser()
for o in ('--projet', '--version', '--rush'): ap.add_argument(o, required=True)
ap.add_argument('--original'); ap.add_argument('--logo')
A = ap.parse_args()
P, V, N = os.path.abspath(A.projet), A.version, A.rush
FPS = 30
src_comp = os.path.join(P, V, 'composition'); out_dir = os.path.join(P, V + '-4k'); comp = os.path.join(out_dir, 'composition')
finals = [f for f in glob.glob(os.path.join(P, V, 'export', '*.mp4')) if not f.endswith('-rendu.mp4')]
if not finals: sys.exit(f'Pas de MP4 final dans {V}/export : livre d’abord la version 1080p (sons et musique compris).')
final = max(finals, key=os.path.getmtime)
if os.path.exists(comp): sys.exit(f'{comp} existe déjà.')
shutil.copytree(src_comp, comp)
run = lambda *c: subprocess.run(list(c), check=True)

if A.original:
    # 1. calage : le son de l'original doit tomber au même endroit que celui de la source du montage
    def son(f, d=60):
        r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-t', str(d), '-i', f, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True, check=True)
        return r.stdout
    try:
        import numpy as np
        a = np.frombuffer(son(os.path.join(P, 'job', 'sources', N + '.mov')), np.int16).astype(float)
        b = np.frombuffer(son(A.original), np.int16).astype(float)
        n = min(len(a), len(b)); a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
        c = np.fft.irfft(np.fft.rfft(a, 2 * n) * np.conj(np.fft.rfft(b, 2 * n)))
        k = int(np.argmax(c)); k = k - 2 * n if k > n else k
        decalage = -k / 8000
    except ImportError:
        decalage = 0.0; print('numpy absent : calage non vérifié, contrôle la synchro sur le rendu.')
    print(f'décalage de l’original : {decalage:+.3f} s')
    if abs(decalage) > 0.02: print('  -> compensé à la découpe.')
    # 2. source 4K, coupes et étalonnage identiques
    vf = ''
    if A.logo:
        x, y, w, h = A.logo.split(':'); vf = f'delogo=x={x}:y={y}:w={w}:h={h},'
    vf += 'scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,crop=3840:2160,setsar=1,fps=30,format=yuv420p'
    s4k = os.path.join(out_dir, N + '-4k.mov')
    run('ffmpeg', '-nostdin', '-v', 'error', '-y', *(['-ss', f'{decalage:.3f}'] if decalage > 0 else []), '-i', A.original, '-map', '0:v:0',
        '-vf', vf, '-c:v', 'libx264', '-preset', 'fast', '-crf', '14', '-r', '30', '-fps_mode', 'cfr', s4k)
    cuts = json.load(open(os.path.join(P, 'job', 'montage', N + '-cuts.json')))['segments']
    page = open(os.path.join(comp, 'index.html')).read()
    plan = json.load(open(os.path.join(P, V, 'plan.json'))) if os.path.exists(os.path.join(P, V, 'plan.json')) else {}
    grade = plan.get('etalonnage', 'eq=brightness=0.035:contrast=1.06:saturation=1.08:gamma=1.08,colorbalance=rs=.03:gs=.0:bs=-.04:rm=.03:bm=-.03')
    off = min(0.0, decalage)   # original en retard : les coupes tombent plus tôt dans son fichier
    filt = ''.join(f"[0:v]trim=start={max(0, s['startFrame'] / FPS + off):.6f}:end={s['endFrame'] / FPS + off:.6f},setpts=PTS-STARTPTS[v{i}];" for i, s in enumerate(cuts))
    filt += ''.join(f'[v{i}]' for i in range(len(cuts))) + f'concat=n={len(cuts)}:v=1:a=0[vc];[vc]{grade}[v]'
    cible = os.path.join(comp, 'assets', N + '-cuts.mp4')
    ancien = cible + '.1080p.mp4'; os.rename(cible, ancien)
    run('ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', s4k, '-i', ancien, '-filter_complex', filt, '-map', '[v]', '-map', '1:a',
        '-r', '30', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', cible)
    os.remove(ancien)

# 3. rendu 4K
log = os.path.join(out_dir, 'render.log'); rendu = os.path.join(out_dir, 'export', N + '-4k-rendu.mp4')
os.makedirs(os.path.dirname(rendu), exist_ok=True)
env = dict(os.environ, PATH=os.path.expanduser('~/.local/bin') + ':' + os.environ.get('PATH', ''))
with open(log, 'w') as L:
    r = subprocess.run(['npx', '--yes', 'hyperframes@0.8.162', 'render', '.', '-o', rendu, '--resolution', '4k', '--quality', 'delivery'], cwd=comp, stdout=L, stderr=L, env=env)
if r.returncode: sys.exit(f'rendu en échec, voir {log}')
# 4. son de la version livrée (identique à l'image près)
sortie = os.path.join(out_dir, 'export', N + '-4k.mp4')
run('ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', rendu, '-i', final, '-map', '0:v', '-map', '1:a', '-c', 'copy', '-shortest', '-movflags', '+faststart', sortie)
info = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height:format=duration', '-of', 'compact', sortie], capture_output=True, text=True).stdout
print('ok', sortie); print(info.strip())

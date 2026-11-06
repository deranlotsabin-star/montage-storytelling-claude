#!/usr/bin/env python3
"""Style « Morgan » (réf. @morgan_rize, fiche references/fiche-style-reference.md).
16:9 1920x1080, 30 i/s. Face cam + écrans texte plein cadre (beige / orange), un mot clé en serif italique ou sans extra-gras,
mots qui entrent flous au moment où ils sont dits, cartes à cocher (visage en vignette), texte barré, sous-titres discrets.
  python monter.py --job job --rush avis --liste
  python monter.py --job job --rush avis --plan v1/plan.json --out v1
Plan (JSON) :
  textes   {indice: texte affiché, "" pour masquer}
  ecrans   [{fond: beige|orange, lignes: [[ "12-14", "petit|gras|serif|barre" ], ...]}]   les lignes dans l'ordre de la voix
  cartes   [{titre: "...", de: i, a: j, items: [[mot_declencheur, "texte"], ...]}]
  muet     ["i-j", ...] mots sans sous-titre
"""
import argparse, html, json, os, shutil, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument('--job', required=True); ap.add_argument('--rush', required=True)
ap.add_argument('--plan'); ap.add_argument('--out'); ap.add_argument('--liste', action='store_true')
A = ap.parse_args()
FPS, W, H = 30, 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))
job = os.path.join(A.job, 'montage')
cuts = json.load(open(os.path.join(job, f'{A.rush}-cuts.json')))['segments']
ana = json.load(open(os.path.join(job, f'{A.rush}-analysis-minimale.json')))
P = json.load(open(A.plan)) if A.plan else {}
TX = {int(k): v for k, v in P.get('textes', {}).items()}

N, offs, mots = 0, [], {}
for s in cuts:
    offs.append(N)
    for w in ana['words']:
        if s['startFrame'] <= w['startFrame'] < s['endFrame']:
            i = int(w['id'][1:])
            fin = min(w.get('endFrame', w['startFrame'] + 6), s['endFrame'])
            mots[i] = dict(i=i, f=N + w['startFrame'] - s['startFrame'], e=N + fin - s['startFrame'], t=TX.get(i, w['text']))
    N += s['endFrame'] - s['startFrame']
NV = N                                   # images de vidéo
N += int(P.get('tenue_fin', 0) * FPS)    # le dernier écran tient après la dernière syllabe
D = N / FPS
ordre = sorted(mots)
if A.liste:
    deb = {o: n for n, o in enumerate(offs)}
    for i in ordre:
        w = mots[i]
        for o in [o for o in deb if o <= w['f'] and o > (mots[ordre[ordre.index(i) - 1]]['f'] if ordre.index(i) else -1)]:
            print(f'--- coupe {deb[o] + 1}/{len(cuts)} image {o}')
        print(f"{i:4d} {w['f'] / FPS:7.2f}s  {w['t']}")
    print(f'{len(mots)} mots, {D:.2f} s'); sys.exit()

def plage(p):
    a, _, b = str(p).partition('-')
    return [mots[i] for i in range(int(a), int(b or a) + 1) if i in mots]
def suivant(i):
    "Image du premier mot après i (fin du bloc)."
    k = [j for j in ordre if j > i]
    return mots[k[0]]['f'] if k else N
cf = sorted(set(offs[1:]))
def cale(f):
    "Début de bloc calé sur une coupe proche (6 images), comme la référence : l'écran tombe sur le raccord."
    c = [x for x in cf if f - 6 <= x <= f]
    return c[-1] if c else f
T = lambda f: f'{f / FPS:.4f}'
esc = html.escape

couverts, calques, sons, fenetres = set(), [], [], []

# --- écrans texte plein cadre
BRUT = []
for e in P.get('ecrans', []):
    tous = [w for r, *_ in e['lignes'] for w in plage(r)]
    BRUT.append(['ecran', cale(min(w['f'] for w in tous)), suivant(max(w['i'] for w in tous)), e])
for c in P.get('cartes', []):
    BRUT.append(['carte', cale(mots[c['de']]['f']), suivant(c['a']), c])
BRUT.sort(key=lambda x: x[1])
for a, b in zip(BRUT, BRUT[1:]):
    a[2] = min(a[2], b[1])   # un écran s'arrête quand le suivant commence
FEN = {id(x[3]): (x[1], x[2]) for x in BRUT}
for n, e in enumerate(P.get('ecrans', [])):
    lignes = [(plage(l[0]), l[1], l[2] if len(l) > 2 else None) for l in e['lignes']]
    tous = [w for ws, *_ in lignes for w in ws]
    f0, f1 = FEN[id(e)]
    fenetres.append((f0, f1, 'ecran'))
    couverts |= {w['i'] for w in tous}
    html_l = []
    for k, (ws, st, mot_barre) in enumerate(lignes):
        spans = ''.join(f'<span class="wd" data-f="{max(w["f"], f0)}">{esc(w["t"])}</span> ' for w in ws if w['t'])
        barre = ''
        if st == 'barre':
            fb = mots[mot_barre]['f'] + 4 if mot_barre is not None else lignes[k + 1][0][0]['f'] if k + 1 < len(lignes) else ws[-1]['e']
            barre = f'<i class="trait" data-f="{max(fb - 4, f0)}"></i>'
            sons.append(dict(f=max(fb - 4, f0), type='barre', quoi='barre ' + ' '.join(w['t'] for w in ws)))
        html_l.append(f'<div class="l {st}"><span class="lt">{spans.strip()}{barre}</span></div>')
        if st in ('gras', 'geant'): sons.append(dict(f=max(ws[0]['f'], f0), type='hit', g=.55, quoi=' '.join(w['t'] for w in ws)))
    sons.append(dict(f=f0, type='wipe', quoi=f'écran {e["fond"]}'))
    calques.append(f'<div class="ecran {e["fond"]}" data-f0="{f0}" data-f1="{f1}"><div class="bloc">{"".join(html_l)}</div></div>')

# --- cartes à cocher (visage en vignette à droite)
CARTES = []
for c in P.get('cartes', []):
    f0, f1 = FEN[id(c)]
    fenetres.append((f0, f1, 'carte'))
    items = ''.join(f'<div class="it" data-f="{max(mots[m]["f"], f0)}"><span>{esc(t)}</span><b class="ck"><svg viewBox="0 0 24 24"><path d="M6.5 12.5l3.6 3.6 7.4-8"/></svg></b></div>' for m, t in c['items'])
    for m, t in c['items']: sons.append(dict(f=max(mots[m]['f'], f0) + 5, type='click', quoi='coche ' + t))
    sons.append(dict(f=f0, type='whoosh', len=.5, quoi='carte entre')); sons.append(dict(f=f1 - 15, type='whoosh', len=.5, g=.7, quoi='carte sort'))
    calques.append(f'<div class="carte" data-f0="{f0}" data-f1="{f1}"><div class="cc"><div class="ti">{esc(c["titre"])}</div>{items}</div></div>')
    CARTES.append((f0, f1))

# --- sous-titres sur le reste (1 à 4 mots, coupure aux pauses)
muet = {w['i'] for r in P.get('muet', []) for w in plage(r)}
def dans_ecran(f): return any(a <= f < b for a, b, k in fenetres if k == 'ecran')
# ponctuation reprise de l'alignement (l'analyse exportée n'en a plus) : on coupe aux fins de phrase et aux virgules
al = os.path.join(A.job, 'transcription', f'{A.rush}-aligne.json')
src = {int(w['id'][1:]): w for w in ana['words']}
if os.path.exists(al):
    pieces = sorted(((round(x['debut'] * FPS), x['texte']) for x in json.load(open(al))), key=lambda x: x[0])
    ids = sorted(src)
    for k, i in enumerate(ids):
        sf = src[i]['startFrame']; nf = src[ids[k + 1]]['startFrame'] if k + 1 < len(ids) else 10 ** 9
        dans = [t for f, t in pieces if sf - 1 <= f < nf - 1]
        nu = lambda x: ''.join(c for c in x.lower().replace('’', "'") if c.isalnum())
        if i in mots and dans and dans[-1].rstrip()[-1:] in '.,?!…' and nu(dans[-1]) and nu(src[i]['text']).endswith(nu(dans[-1])):
            mots[i]['p'] = dans[-1].rstrip()[-1:]
FAIBLES = {'de', 'des', 'à', 'le', 'la', 'les', 'et', 'en', 'un', 'une', 'tes', 'ton', 'mon', 'mes', 'se', 'que', 'pour', 'sur', 'au', 'dans', 'du', 'je', 'tu', 'il', 'si', 'mais', 'ne', 'me', 'plus', 'ce', 'qui', 'ça', 'y', 'a', 'j’ai', 't’es', 'ai', 'j’en', 'pas'}
libres = [mots[i] for i in ordre if i not in couverts and i not in muet and mots[i]['t'] and not dans_ecran(mots[i]['f'])]
ordv = [i for i in ordre if mots[i]['t']]
phrases, g = [], []
for k, w in enumerate(libres):
    if g and (w['f'] - g[-1]['e'] > 9 or ordv.index(w['i']) != ordv.index(g[-1]['i']) + 1): phrases.append(g); g = []
    g.append(w)
    if w.get('p'): phrases.append(g); g = []
if g: phrases.append(g)
def lg(l): return len(' '.join(x['t'] for x in l))
def decoupe(ph):
    "Partition optimale d'une phrase en lignes de 5 mots / 30 signes au plus."
    n = len(ph); best = [0] + [1e9] * n; dep = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - 6), j):
            l = ph[i:j]
            if lg(l) > 30 and len(l) > 1: continue
            c = 1 + (4 if j < n and l[-1]['t'].lower() in FAIBLES else 0) + (3 if len(l) == 1 and n > 1 else 0) + (.5 if lg(l) > 27 else 0) + .1 * (len(l) - 4) ** 2 - (.6 if j < n and any(ph[j - 1]['f'] < o <= ph[j]['f'] for o in offs) else 0)
            if best[i] + c < best[j]: best[j], dep[j] = best[i] + c, i
    out, j = [], n
    while j: out.insert(0, ph[dep[j]:j]); j = dep[j]
    return out
groupes = [l for ph in phrases for l in decoupe(ph)]
for k, g in enumerate(groupes):
    f0 = g[0]['f']; fin_nat = g[-1]['e'] + 8
    f1 = min([groupes[k + 1][0]['f'] if k + 1 < len(groupes) else N, fin_nat + 30] + [a for a, b, kk in fenetres if kk == 'ecran' and a > f0])
    f1 = max(f1, f0 + 6)
    spans = ''.join(f'<span class="wd" data-f="{w["f"]}">{esc(w["t"])}</span> ' for w in g)
    calques.append(f'<div class="sub" data-f0="{f0}" data-f1="{f1}"><span class="lt">{spans.strip()}</span></div>')

# --- zooms secs sur les coupes, hors écrans et cartes (cadre alterné, cache les jump cuts)
def occupe(f): return any(a <= f < b for a, b, _ in fenetres)
pts, z = [], [1.0, 1.14]
for k, f in enumerate([0] + [c for c in cf if not occupe(c)] + [b for a, b, _ in fenetres if b < N]):
    pts.append(f)
fins = {b for a, b, _ in fenetres}
garde = []
for f in sorted(set(pts)):   # au moins 1,2 s entre deux changements de cadre, sauf au retour d'un écran (toujours)
    if not garde or f in fins or f - garde[-1] >= 36: garde.append(f)
ZO = [[f, z[k % 2]] for k, f in enumerate(garde)]

CSS = '''@font-face{font-family:Inter;src:url(assets/Inter.ttf) format("truetype");font-weight:100 900}
@font-face{font-family:"Instrument Serif";font-style:italic;src:url(assets/InstrumentSerif-Italic-latin.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215}
@font-face{font-family:"Instrument Serif";font-style:italic;src:url(assets/InstrumentSerif-Italic-latinext.woff2) format("woff2");unicode-range:U+0100-024F,U+1E00-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}
html,body{margin:0;background:#000}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#F2EBE6;font-family:Inter,sans-serif}
#fondcarte{position:absolute;inset:0;background-color:#F2EBE6;background-image:radial-gradient(rgba(60,40,30,.10) 1.6px,transparent 1.8px);background-size:30px 30px}
#wrap{position:absolute;inset:0;overflow:hidden;transform-origin:50% 50%;z-index:2}
#cam{position:absolute;inset:0;transform-origin:44% 36%}
#cam video{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse 75% 70% at 46% 42%,transparent 55%,rgba(0,0,0,.42) 100%)}
.sub{position:absolute;left:0;right:0;top:905px;text-align:center;visibility:hidden;z-index:3}
.sub .lt{font-weight:600;font-size:44px;letter-spacing:-.02em;color:#fff;text-shadow:0 2px 14px rgba(0,0,0,.55)}
.wd{display:inline-block;opacity:0;white-space:pre}
.ecran{position:absolute;inset:0;z-index:6;visibility:hidden;display:flex;align-items:center;justify-content:center}
.ecran.beige{background:#F2EBE6;color:#1E1A17}
.ecran.orange{background:linear-gradient(135deg,#F57221 0%,#E55A0E 45%,#D03F01 100%);color:#fff}
.ecran.orange:after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 60% 50% at 20% 15%,rgba(255,255,255,.10),transparent 70%)}
.bloc{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;margin-top:-30px}
.l{line-height:1;text-align:center;white-space:nowrap}
.l .lt{position:relative;display:inline-block}
.l.petit .lt,.l.barre .lt{font-weight:600;font-size:50px;letter-spacing:-.025em;padding:6px 0}
.l.gras .lt{font-weight:800;font-size:118px;letter-spacing:-.045em;padding:4px 0 10px}
.l.geant .lt{font-weight:800;font-size:250px;letter-spacing:-.05em;padding:0 0 10px;line-height:.95}
.l.serif .lt{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;font-size:168px;letter-spacing:-.01em;padding:0 0 14px}
.beige .l.gras .lt,.beige .l.serif .lt,.beige .l.geant .lt{color:#C9480F}
.orange .l.gras .lt,.orange .l.serif .lt,.orange .l.geant .lt{text-shadow:0 0 28px rgba(255,255,255,.45)}
.orange .l.petit .lt{text-shadow:0 0 18px rgba(255,255,255,.25)}
.trait{position:absolute;left:-10px;right:-10px;top:52%;height:7px;border-radius:4px;background:#E2600F;transform:scaleX(0);transform-origin:0 50%}
.orange .trait{background:#fff}
.carte{position:absolute;left:70px;top:0;bottom:0;width:770px;display:flex;align-items:center;z-index:5;visibility:hidden}
.cc{width:100%;padding:34px 34px 20px;box-sizing:border-box;background:#fff;border-radius:38px;box-shadow:0 30px 70px rgba(70,45,25,.16),0 4px 14px rgba(70,45,25,.08)}
.carte .ti{font-weight:500;font-size:33px;color:#8a837d;margin:0 0 22px 8px;letter-spacing:-.015em}
.it{display:flex;align-items:center;justify-content:space-between;background:#F4F1EE;border-radius:18px;padding:0 24px 0 28px;height:98px;margin-bottom:16px;opacity:0;
  font-weight:600;font-size:46px;letter-spacing:-.03em;color:#1E1A17}
.ck{width:50px;height:50px;border-radius:50%;border:3.5px solid #E86A1A;box-sizing:border-box;display:flex;align-items:center;justify-content:center;background:transparent}
.ck svg{width:30px;height:30px;opacity:0}.ck path{fill:none;stroke:#fff;stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}
'''
JS = '''
const FPS=30,D=%s,ZO=%s,CARTES=%s,N=Math.round(D*FPS);const t=f=>(f-.5)/FPS;
document.fonts.ready.then(()=>{
 const tl=gsap.timeline({paused:true});
 for(const c of document.querySelectorAll('.ecran,.sub,.carte')){const a=+c.dataset.f0,b=+c.dataset.f1;
   if(a>0)tl.set(c,{visibility:'visible'},t(a));else c.style.visibility='visible';if(b<N)tl.set(c,{visibility:'hidden'},t(b));}
 for(const w of document.querySelectorAll('.wd')){const f=+w.dataset.f,big=!!w.closest('.gras,.serif,.geant');
   tl.fromTo(w,{opacity:0,filter:`blur(${big?18:9}px)`,y:big?14:4},{opacity:1,filter:'blur(0px)',y:0,duration:big?.32:.2,ease:'power2.out'},t(f));}
 for(const s of document.querySelectorAll('.trait')){const f=+s.dataset.f;tl.to(s,{scaleX:1,duration:.24,ease:'power2.inOut'},t(f));
   tl.to(s.closest('.lt'),{opacity:.6,duration:.2},t(f)+.24);}
 for(const it of document.querySelectorAll('.it')){const f=+it.dataset.f,ck=it.querySelector('.ck'),sv=ck.querySelector('svg');
   tl.fromTo(it,{opacity:0,filter:'blur(8px)',y:10},{opacity:1,filter:'blur(0px)',y:0,duration:.25,ease:'power2.out'},t(f));
   tl.to(ck,{backgroundColor:'#E86A1A',duration:.12},t(f+5));tl.fromTo(sv,{opacity:0,scale:.4},{opacity:1,scale:1,duration:.18,ease:'back.out(2.5)'},t(f+5));}
 for(const [f,z] of ZO)if(f)tl.set('#cam',{scale:z},t(f));else gsap.set('#cam',{scale:z});
 for(const [a,b] of CARTES){const c=document.querySelector(`.carte[data-f0="${a}"] .cc`);
   tl.fromTo('#wrap',{x:0,scale:1,borderRadius:0},{x:420,scale:.51,borderRadius:58,duration:.5,ease:'power3.inOut'},t(a));
   tl.set('#cam',{scale:1},t(a));
   tl.fromTo(c,{opacity:0,filter:'blur(14px)',x:-30},{opacity:1,filter:'blur(0px)',x:0,duration:.45,ease:'power3.out'},t(a)+.28);
   tl.to(c,{opacity:0,filter:'blur(14px)',scale:.97,duration:.3,ease:'power2.in'},t(b-15));
   tl.to('#wrap',{x:0,scale:1,borderRadius:0,duration:.5,ease:'power3.inOut'},t(b-15)+.12);}
 tl.set({}, {}, D);
 window.__timelines=window.__timelines||{};window.__timelines['main']=tl;
});
''' % (round(D, 4), json.dumps(ZO), json.dumps(CARTES))

comp = os.path.join(A.out, 'composition')
if os.path.exists(os.path.join(comp, 'index.html')): sys.exit(f'{comp} existe déjà : nouvelle version vN+1.')
os.makedirs(os.path.join(comp, 'assets'), exist_ok=True)
base = f'{A.rush}-cuts.mp4'
GRADE = P.get('etalonnage', 'eq=brightness=0.035:contrast=1.06:saturation=1.08:gamma=1.08,colorbalance=rs=.03:gs=.0:bs=-.04:rm=.03:bm=-.03')
filt = ''.join(f"[0:v]trim=start_frame={s['startFrame']}:end_frame={s['endFrame']},setpts=PTS-STARTPTS[v{n}];"
               f"[0:a]atrim=start={s['startFrame'] / FPS:.6f}:end={s['endFrame'] / FPS:.6f},asetpts=PTS-STARTPTS[a{n}];" for n, s in enumerate(cuts))
filt += ''.join(f'[v{n}][a{n}]' for n in range(len(cuts))) + f'concat=n={len(cuts)}:v=1:a=1[vc][a];[vc]{GRADE}[v]'
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', os.path.join(A.job, 'sources', A.rush + '.mov'), '-filter_complex', filt,
                '-map', '[v]', '-map', '[a]', '-r', str(FPS), '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
                os.path.join(comp, 'assets', base)], check=True)
for f in os.listdir(os.path.join(HERE, 'assets')): shutil.copy2(os.path.join(HERE, 'assets', f), os.path.join(comp, 'assets', f))
page = f'''<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>{esc(A.rush)} · style Morgan</title>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-width="{W}" data-height="{H}" data-fps="{FPS}" data-duration="{D:.4f}">
<div id="fondcarte"></div>
<div id="wrap"><div id="cam"><video id="facecam" class="clip" src="assets/{base}" data-start="0" data-duration="{NV / FPS:.4f}" data-track-index="0" data-has-audio="true" playsinline></video></div><div id="vig"></div>
{chr(10).join(c for c in calques if c.startswith('<div class="sub"'))}
</div>
{chr(10).join(c for c in calques if not c.startswith('<div class="sub"'))}
</div><script>{JS}</script></body></html>'''
open(os.path.join(comp, 'index.html'), 'w').write(page)
json.dump({'authoringSkill': 'general-video', 'media': {'autoProxy': True}}, open(os.path.join(comp, 'hyperframes.json'), 'w'), indent=2)
json.dump({'private': True}, open(os.path.join(comp, 'package.json'), 'w'))
cues = sorted([dict(t=round(s['f'] / FPS, 3), type=s['type'], note=s['quoi'], **{k: s[k] for k in ('g', 'len') if k in s}) for s in sons], key=lambda x: x['t'])
json.dump(cues, open(os.path.join(A.out, 'cues.json'), 'w'), ensure_ascii=False, indent=1)
print(f'durée {D:.2f} s, {len(cuts)} coupes, {len(P.get("ecrans", []))} écrans, {len(CARTES)} cartes, {len(groupes)} sous-titres, {len(ZO)} zooms, {len(cues)} sons')
for a, b, k in sorted(fenetres): print(f'  {k:6} {a / FPS:6.2f}-{b / FPS:6.2f}s')

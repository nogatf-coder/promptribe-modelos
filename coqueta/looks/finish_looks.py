# Looks finales: fuera los extremos (quema, grano exagerado, dominantes chillonas), grano limitado, y cada uno con su
# descripción en inglés (para el modelo de significado) y un nombre corto en español. looks.json
import json, numpy as np

L = json.load(open('H:/coqueta-studio/looks/looks_raw.json'))
P = json.load(open('H:/coqueta-studio/looks/presets.json'))
F = json.load(open('H:/coqueta-studio/looks/features.json'))
X = np.array(F['f']); ix = {n: i for i, n in enumerate(F['names'])}
title2i = {}
for i, p in enumerate(P): title2i.setdefault(p['title'], i)

EN = {'blackwhite': 'black and white', 'bright': 'bright airy', 'dark': 'dark moody', 'contrast': 'high contrast punchy', 'soft': 'soft low contrast',
      'faded': 'faded matte film', 'deepblacks': 'deep rich blacks', 'warm': 'warm golden tones', 'cool': 'cool blue tones', 'green': 'green olive tint',
      'magenta': 'pink magenta tint', 'vivid': 'vivid saturated colors', 'muted': 'muted desaturated colors', 'vignette': 'dark vignette',
      'grain': 'film grain', 'crisp': 'crisp sharp detail clarity', 'dreamy': 'dreamy soft glow'}
ES = {'blackwhite': 'B/N', 'bright': 'luminoso', 'dark': 'oscuro', 'contrast': 'contraste', 'soft': 'suave', 'faded': 'mate', 'deepblacks': 'negros profundos',
      'warm': 'cálido', 'cool': 'frío', 'green': 'oliva', 'magenta': 'rosado', 'vivid': 'vivo', 'muted': 'apagado', 'vignette': 'viñeta', 'grain': 'grano',
      'crisp': 'nítido', 'dreamy': 'de ensueño'}
COL_ES = {'red': 'rojo', 'orange': 'naranja', 'yellow': 'amarillo', 'green': 'verde', 'teal': 'verde azulado', 'blue': 'azul', 'purple': 'violeta', 'magenta': 'magenta'}
CTX = {'wedding': 'wedding', 'portrait': 'portrait', 'landscape': 'landscape', 'hdr': 'HDR landscape', 'vintage': 'vintage retro', 'retro': 'vintage retro',
       'film': 'analog film', 'matte': 'matte', 'cinematic': 'cinematic movie', 'cross': 'cross processed', 'lomo': 'lomo toy camera', 'bleach': 'bleach bypass',
       'winter': 'winter cold', 'summer': 'summer', 'sunset': 'sunset', 'night': 'night', 'urban': 'urban street', 'fashion': 'fashion editorial',
       'pastel': 'pastel', 'sepia': 'sepia', 'moody': 'moody', 'dramatic': 'dramatic', 'clean': 'clean', 'pop': 'pop color', 'instagram': 'instagram',
       'olive': 'olive', 'teal': 'teal', 'orange': 'orange', 'golden': 'golden hour', 'portra': 'portra film', 'kodak': 'kodak film', 'fuji': 'fuji film'}

out = []
for l in L:
    i = title2i.get(l['from'])
    f = X[i] if i is not None else None
    if f is not None:
        if abs(f[ix['mean']]) > 0.16 or f[ix['p98']] < -0.12 or f[ix['p02']] > 0.2: continue
        if max(abs(f[ix['shR']]), abs(f[ix['shG']]), abs(f[ix['shB']]), abs(f[ix['hiR']]), abs(f[ix['hiG']]), abs(f[ix['hiB']])) > 0.09: continue
    p = dict(l['p']); p['grain'] = min(p['grain'], 28)
    tags = l['tags'][:5]
    en, es = [], []
    for t in tags:
        if t.startswith('sh_'): en.append(f"{t[3:]} shadows"); es.append(f"sombras {COL_ES[t[3:]]}")
        elif t.startswith('hi_'): en.append(f"{t[3:]} highlights"); es.append(f"luces {COL_ES[t[3:]]}")
        else: en.append(EN[t]); es.append(ES[t])
    ctx = []
    for w in l['words']:
        if w in CTX and CTX[w] not in ctx: ctx.append(CTX[w])
    desc = ', '.join(en) + (' look' if en else 'natural look') + (' for ' + ', '.join(ctx[:3]) if ctx else '')
    name = ' · '.join(es[:3]).capitalize() if es else 'Natural'
    out.append({'id': l['id'], 'name': name, 'desc': desc, 'tags': tags, 'gray': p['gray'], 'p': p})
json.dump(out, open('H:/coqueta-studio/looks/looks.json', 'w'), separators=(',', ':'))
print(len(out), 'looks')
for o in out[:12]: print(o['id'], '|', o['name'], '|', o['desc'])

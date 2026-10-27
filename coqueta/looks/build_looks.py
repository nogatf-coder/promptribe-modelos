# Recetas → «looks»: se agrupan por cómo se ven (k-medias sobre lo medido), se elige la receta más representativa de
# cada grupo y se describe con palabras (en qué consiste: luz, contraste, color, virado, grano…). looks.json
import json, re, collections, numpy as np

P = json.load(open('H:/coqueta-studio/looks/presets.json'))
F = json.load(open('H:/coqueta-studio/looks/features.json'))
X = np.array(F['f'], np.float64)
names = F['names']
ix = {n: i for i, n in enumerate(names)}
gray = np.array([1.0 if p['p']['gray'] else 0.0 for p in P])
grain = np.array([p['p']['grain'] for p in P]); clar = np.array([p['p']['clarity'] for p in P])
# rasgos para agrupar (escalados para que pesen parecido)
Z = np.column_stack([X / (X.std(0) + 1e-6), gray * 3, grain / 40, clar / 50])
rng = np.random.default_rng(3)
K = 170
C = Z[rng.choice(len(Z), K, replace=False)]
for it in range(60):
    d = ((Z[:, None, :] - C[None]) ** 2).sum(-1); lab = d.argmin(1)
    for k in range(K):
        m = lab == k
        if m.any(): C[k] = Z[m].mean(0)
        else: C[k] = Z[rng.integers(len(Z))]
d = ((Z[:, None, :] - C[None]) ** 2).sum(-1); lab = d.argmin(1)

HUE_NAMES = [(0, 'red'), (25, 'orange'), (55, 'yellow'), (100, 'green'), (165, 'teal'), (215, 'blue'), (270, 'purple'), (320, 'magenta'), (360, 'red')]
def hue_name(r, g, b):
    import colorsys
    h, l, s = colorsys.rgb_to_hls(max(0, r + 0.5), max(0, g + 0.5), max(0, b + 0.5))
    h *= 360
    return min(HUE_NAMES, key=lambda x: abs(x[0] - h))[1]
STOP = set('preset presets copy the and for with lr vsco pfl lightroom free new mobile desktop dng xmp lrtemplate'.split())
def words(title):
    return [w for w in re.findall(r'[a-z]{3,}', title.lower()) if w not in STOP]

looks = []
for k in range(K):
    m = np.where(lab == k)[0]
    if len(m) < 3: continue
    med = m[((Z[m] - Z[m].mean(0)) ** 2).sum(1).argmin()]
    f = X[m].mean(0); p = P[med]['p']
    tags = []  # (palabra, fuerza)
    g = lambda n: f[ix[n]]
    if gray[m].mean() > 0.5: tags.append(('blackwhite', 3))
    if g('mean') > 0.04: tags.append(('bright', g('mean') / 0.04))
    if g('mean') < -0.04: tags.append(('dark', -g('mean') / 0.04))
    if g('std') > 0.02: tags.append(('contrast', g('std') / 0.02))
    if g('std') < -0.02: tags.append(('soft', -g('std') / 0.02))
    if g('p02') > 0.04: tags.append(('faded', g('p02') / 0.04))
    if g('p02') < -0.03: tags.append(('deepblacks', -g('p02') / 0.03))
    if gray[m].mean() <= 0.5:
        if g('warm') > 0.02: tags.append(('warm', g('warm') / 0.02))
        if g('warm') < -0.02: tags.append(('cool', -g('warm') / 0.02))
        if g('tint') > 0.012: tags.append(('green', g('tint') / 0.012))
        if g('tint') < -0.012: tags.append(('magenta', -g('tint') / 0.012))
        if g('sat') > 0.025: tags.append(('vivid', g('sat') / 0.025))
        if g('sat') < -0.025: tags.append(('muted', -g('sat') / 0.025))
        sh = np.array([g('shR'), g('shG'), g('shB')]); hi = np.array([g('hiR'), g('hiG'), g('hiB')])
        if np.abs(sh).max() > 0.012: tags.append(('sh_' + hue_name(*sh), np.abs(sh).max() / 0.012))
        if np.abs(hi).max() > 0.012: tags.append(('hi_' + hue_name(*hi), np.abs(hi).max() / 0.012))
    if g('vig') < -0.05: tags.append(('vignette', -g('vig') / 0.05))
    if grain[m].mean() > 15: tags.append(('grain', grain[m].mean() / 20))
    if clar[m].mean() > 30: tags.append(('crisp', clar[m].mean() / 30))
    if clar[m].mean() < -15: tags.append(('dreamy', -clar[m].mean() / 15))
    colls = collections.Counter(P[i]['collection'] for i in m)
    tw = collections.Counter(w for i in m for w in words(P[i]['title']))
    tags.sort(key=lambda t: -t[1])
    looks.append({'id': f'look{len(looks):03d}', 'n': int(len(m)), 'tags': [t for t, _ in tags], 'strength': [round(float(s), 2) for _, s in tags],
                  'collections': [c for c, _ in colls.most_common(3)], 'words': [w for w, c in tw.most_common(12) if c >= 2][:8], 'p': p, 'from': P[med]['title']})
json.dump(looks, open('H:/coqueta-studio/looks/looks_raw.json', 'w'), indent=0)
print(len(looks), 'looks')
for L in looks[:25]: print(L['id'], L['n'], L['tags'][:5], L['collections'][:2], L['words'][:5])
print(collections.Counter(t for L in looks for t in L['tags']).most_common(40))

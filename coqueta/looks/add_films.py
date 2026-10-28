# Añade al catálogo de películas (luts.bin / luts.json) las de bake_films.mjs, con sus rasgos medidos igual que las
# demás (build_luts.py): lo que cambian, de media, en las fotos de referencia. Se puede repetir: sustituye las que ya
# estén por nombre.
import json, struct, numpy as np
from PIL import Image

D = 'H:/coqueta-studio/looks/'
S = 17
luts = json.load(open(D + 'luts.json', encoding='utf-8'))
raw = open(D + 'luts.bin', 'rb').read()
count, size = struct.unpack('<II', raw[:8]); per = size ** 3 * 3
assert size == S and len(raw) == 8 + count * per, (count, size, len(raw))
blobs = [raw[8 + i * per: 8 + (i + 1) * per] for i in range(count)]
extra = json.load(open(D + 'films-extra.json', encoding='utf-8'))
ebin = open(D + 'films-extra.bin', 'rb').read()

refs = []
for f in ['H:/reel_rec/fotos_u/u%02d.jpg' % i for i in (1, 4, 9, 12, 13, 22, 23)] + ['H:/lora/fotos/%04d.jpg' % i for i in (0, 6, 27, 36)]:
    im = Image.open(f).convert('RGB'); im.thumbnail((120, 120)); refs.append(np.asarray(im, np.float32) / 255)
def apply(grid, img):
    s1 = S - 1
    x = img * s1; i0 = np.minimum(np.floor(x).astype(int), s1 - 1); f = x - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]; fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    at = lambda db, dg, dr: grid[b0 + db, g0 + dg, r0 + dr]
    c00 = at(0, 0, 0) * (1 - fr) + at(0, 0, 1) * fr; c10 = at(0, 1, 0) * (1 - fr) + at(0, 1, 1) * fr
    c01 = at(1, 0, 0) * (1 - fr) + at(1, 0, 1) * fr; c11 = at(1, 1, 0) * (1 - fr) + at(1, 1, 1) * fr
    return (c00 * (1 - fg) + c10 * fg) * (1 - fb) + (c01 * (1 - fg) + c11 * fg) * fb
def feats(img):
    L = img @ [0.299, 0.587, 0.114]; mx, mn = img.max(-1), img.min(-1)
    sh = L < 0.3; hi = L > 0.7
    shc = (img[sh] - L[sh][:, None]).mean(0) if sh.any() else np.zeros(3)
    hic = (img[hi] - L[hi][:, None]).mean(0) if hi.any() else np.zeros(3)
    return np.array([L.mean(), L.std(), np.quantile(L, 0.02), np.quantile(L, 0.98), (img[..., 0] - img[..., 2]).mean(), (img[..., 1] - (img[..., 0] + img[..., 2]) / 2).mean(), (mx - mn).mean(), *shc, *hic])
base = [feats(r) for r in refs]

names = {e['title'] for e in extra}
keep = [(l, b) for l, b in zip(luts, blobs) if l['title'] not in names]
for k, e in enumerate(extra):
    data = ebin[k * per:(k + 1) * per]
    grid = np.frombuffer(data, np.uint8).reshape(S, S, S, 3).astype(np.float32) / 255
    f = np.mean([feats(np.clip(apply(grid, r), 0, 1)) - b for r, b in zip(refs, base)], 0)
    keep.append(({'title': e['title'], 'brand': e['brand'], 'bw': False, 'f': [round(float(x), 4) for x in f], 'made': 'Coqueta'}, data))
# los id siguen siendo su posición (las de antes no cambian)
out, blob = [], bytearray()
for i, (l, b) in enumerate(keep):
    l = dict(l); l['id'] = l.get('id') if l.get('made') != 'Coqueta' else f'lut{i:03d}'
    out.append(l); blob += b
open(D + 'luts.bin', 'wb').write(struct.pack('<II', len(out), S) + bytes(blob))
json.dump(out, open(D + 'luts.json', 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print(len(out), 'películas;', ', '.join(f"{l['id']} {l['title']}" for l in out if l.get('made') == 'Coqueta'))

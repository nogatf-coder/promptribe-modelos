# t3mujinpack (João Almeida, MIT; github.com/t3mujin/t3mujinpack) → películas del catálogo: sus HaldCLUT a tablas 3D de
# 17³ (como build_luts.py), con los rasgos medidos en las fotos de referencia, al final de luts.bin / luts.json. El
# nombre lleva «· t3mujin» (su crédito, y así no se confunde con la versión de RawTherapee de la misma película). Se
# puede repetir: sustituye las que ya estén.
import glob, json, os, re, struct, numpy as np
from PIL import Image

D = 'H:/coqueta-studio/looks/'
SRC = D + 'src/t3mujinpack/haldcluts/'
S = 17
luts = json.load(open(D + 'luts.json', encoding='utf-8'))
raw = open(D + 'luts.bin', 'rb').read()
count, size = struct.unpack('<II', raw[:8]); per = size ** 3 * 3
assert size == S and len(raw) == 8 + count * per
blobs = [raw[8 + i * per: 8 + (i + 1) * per] for i in range(count)]

def hald_to_grid(img):
    a = np.asarray(img.convert('RGB'), np.float32) / 255
    n = int(round((a.shape[0] * a.shape[1]) ** (1 / 3)))
    cube = a.reshape(-1, 3).reshape(n, n, n, 3)  # [b][g][r]
    idx = np.linspace(0, n - 1, S)
    def interp(c, ax):
        i0 = np.floor(idx).astype(int); i1 = np.minimum(i0 + 1, n - 1); t = (idx - i0)[(None,) * ax + (slice(None),) + (None,) * (3 - ax)]
        return np.take(c, i0, axis=ax) * (1 - t) + np.take(c, i1, axis=ax) * t
    return interp(interp(interp(cube, 0), 1), 2)
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
refs = []
for f in ['H:/reel_rec/fotos_u/u%02d.jpg' % i for i in (1, 4, 9, 12, 13, 22, 23)] + ['H:/lora/fotos/%04d.jpg' % i for i in (0, 6, 27, 36)]:
    im = Image.open(f).convert('RGB'); im.thumbnail((120, 120)); refs.append(np.asarray(im, np.float32) / 255)
base = [feats(r) for r in refs]

# las que ya estaban (si se repite), fuera; el resto mantiene su id
keep = [(l, b) for l, b in zip(luts, blobs) if l.get('made') != 't3mujinpack']
new = []
for path in sorted(glob.glob(SRC + '*.png')):
    m = re.match(r't3mujinpack - (.+?) - (.+)\.png$', os.path.basename(path))
    if not m: continue
    cat, film = m.groups()
    film = film.replace('Kodakchrome', 'Kodachrome').replace('AGFA', 'Agfa')
    grid = hald_to_grid(Image.open(path))
    f = np.mean([feats(np.clip(apply(grid, r), 0, 1)) - b for r, b in zip(refs, base)], 0)
    blob = np.clip(np.round(grid * 255), 0, 255).astype(np.uint8).tobytes()
    new.append(({'title': f'{film} · t3mujin', 'brand': film.split()[0], 'bw': cat == 'Black and White', 'slide': cat == 'Color Slide', 'f': [round(float(x), 4) for x in f], 'made': 't3mujinpack'}, blob))
out, data = [], bytearray()
for i, (l, b) in enumerate(keep + new):
    l = dict(l); l['id'] = f'lut{i:03d}'; out.append(l); data += b
# los de antes conservan su id (están delante y en el mismo orden)
assert all(o['id'] == l['id'] for o, (l, _) in zip(out, keep))
open(D + 'luts.bin', 'wb').write(struct.pack('<II', len(out), S) + bytes(data))
json.dump(out, open(D + 'luts.json', 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print(len(new), 'de t3mujinpack;', len(out), 'películas en total;', out[len(keep)]['id'], '…', out[-1]['id'])

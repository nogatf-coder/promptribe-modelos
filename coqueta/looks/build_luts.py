# RawTherapee Film Simulation Collection (CC BY-SA 4.0; Pat David, Pavlov Dmitry, Michael Ezra) → tablas 3D de 17³
# (luts.bin: cabecera + size³×3 bytes por película) y luts.json con nombre, marca, B/N y lo que cambia (para describirlas)
import zipfile, io, json, re, struct, numpy as np
from PIL import Image

z = zipfile.ZipFile('H:/coqueta-studio/looks/src/HaldCLUT.zip')
names = sorted(n for n in z.namelist() if n.endswith('.png') and '/Color/' in n or (n.endswith('.png') and '/Black-and-White/' in n))
S = 17
refs = []
for f in ['H:/reel_rec/fotos_u/u%02d.jpg' % i for i in (1, 4, 9, 12, 13, 22, 23)] + ['H:/lora/fotos/%04d.jpg' % i for i in (0, 6, 27, 36)]:
    im = Image.open(f).convert('RGB'); im.thumbnail((120, 120)); refs.append(np.asarray(im, np.float32) / 255)

def hald_to_grid(img):
    a = np.asarray(img.convert('RGB'), np.float32) / 255
    level = round(a.shape[0] ** (1 / 3)) ** 2 if False else int(round((a.shape[0] * a.shape[1]) ** (1 / 3)))
    n = level  # entradas por canal
    flat = a.reshape(-1, 3)
    cube = flat.reshape(n, n, n, 3)  # [b][g][r]
    idx = np.linspace(0, n - 1, S)
    # remuestreo trilineal a 17 por canal
    def interp(c, ax):
        i0 = np.floor(idx).astype(int); i1 = np.minimum(i0 + 1, n - 1); t = (idx - i0)[(None,) * ax + (slice(None),) + (None,) * (3 - ax)]
        return np.take(c, i0, axis=ax) * (1 - t) + np.take(c, i1, axis=ax) * t
    c = interp(interp(interp(cube, 0), 1), 2)
    return c  # [b][g][r][3]

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
out, blob = [], bytearray()
for n in names:
    parts = n.split('/')
    if 'Negative' in n: continue
    grid = hald_to_grid(Image.open(io.BytesIO(z.read(n))))
    f = np.mean([feats(np.clip(apply(grid, r), 0, 1)) - b for r, b in zip(refs, base)], 0)
    title = re.sub(r'\.png$', '', parts[-1]).replace('_', ' ')
    out.append({'id': f'lut{len(out):03d}', 'title': title, 'brand': parts[-2], 'bw': parts[1] == 'Black-and-White', 'f': [round(float(x), 4) for x in f]})
    blob += np.clip(np.round(grid * 255), 0, 255).astype(np.uint8).tobytes()
open('H:/coqueta-studio/looks/luts.bin', 'wb').write(struct.pack('<II', len(out), S) + bytes(blob))
json.dump(out, open('H:/coqueta-studio/looks/luts.json', 'w'), indent=0)
print(len(out), 'películas', len(blob) / 1e6, 'MB')

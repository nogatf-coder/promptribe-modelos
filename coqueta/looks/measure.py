# Medidas comunes del catálogo de películas (las mismas de build_luts.py): aplicar una tabla 17³ a una imagen y los
# rasgos de una foto (luz media, contraste, negros y blancos, calidez, tinte, saturación y color de sombras y luces),
# con las fotos de referencia para medir lo que cambia cada película.
import numpy as np
from PIL import Image

S = 17


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


def measure(grid):
    """Lo que cambia la tabla, de media, en las fotos de referencia."""
    return np.mean([feats(np.clip(apply(grid, r), 0, 1)) - b for r, b in zip(refs, base)], 0)

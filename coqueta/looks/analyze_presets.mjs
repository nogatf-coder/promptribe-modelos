// Cada receta sobre las fotos de referencia → qué cambia (rasgos medidos), de media → features.json
import fs from 'node:fs';
import { applyRecipe } from 'file:///H:/promptribe/assets/js/coqueta-foto-looks.js';
const buf = fs.readFileSync('H:/coqueta-studio/looks/refs/refs.bin');
let o = 4; const N = buf.readUInt32LE(0), refs = [];
for (let i = 0; i < N; i++) { const w = buf.readUInt32LE(o), h = buf.readUInt32LE(o + 4); o += 8; refs.push({ w, h, d: new Uint8ClampedArray(buf.subarray(o, o + w * h * 4)) }); o += w * h * 4; }
const P = JSON.parse(fs.readFileSync('H:/coqueta-studio/looks/presets.json', 'utf8'));
function feats(d, w, h) {
  const n = w * h, Ls = new Float32Array(n);
  let sR = 0, sG = 0, sB = 0, sat = 0, gray = 0, shR = 0, shG = 0, shB = 0, shN = 0, hiR = 0, hiG = 0, hiB = 0, hiN = 0, cen = 0, cn = 0, cor = 0, crn = 0;
  for (let i = 0, j = 0; i < n; i++, j += 4) {
    const r = d[j] / 255, g = d[j + 1] / 255, b = d[j + 2] / 255, L = 0.299 * r + 0.587 * g + 0.114 * b; Ls[i] = L;
    sR += r; sG += g; sB += b; const mx = Math.max(r, g, b), mn = Math.min(r, g, b), s = mx - mn; sat += s; if (s < 0.04) gray++;
    if (L < 0.3) { shR += r - L; shG += g - L; shB += b - L; shN++; } if (L > 0.7) { hiR += r - L; hiG += g - L; hiB += b - L; hiN++; }
    const x = i % w, y = (i / w) | 0, dx = x / w - 0.5, dy = y / h - 0.5, rr = Math.hypot(dx, dy);
    if (rr < 0.2) { cen += L; cn++; } else if (rr > 0.55) { cor += L; crn++; }
  }
  const so = Float32Array.from(Ls).sort(), q = (t) => so[Math.round(t * (n - 1))];
  let m = 0, v = 0; for (const L of Ls) m += L; m /= n; for (const L of Ls) v += (L - m) ** 2;
  return [m, Math.sqrt(v / n), q(0.02), q(0.5), q(0.98), (sR - sB) / n, (sG - (sR + sB) / 2) / n, sat / n, gray / n,
    shN ? shR / shN : 0, shN ? shG / shN : 0, shN ? shB / shN : 0, hiN ? hiR / hiN : 0, hiN ? hiG / hiN : 0, hiN ? hiB / hiN : 0, crn && cn ? (cor / crn) / Math.max(0.05, cen / cn) : 1];
}
const base = refs.map((r) => feats(r.d, r.w, r.h));
const out = [];
const t0 = Date.now();
P.forEach((rec, k) => {
  const acc = new Array(16).fill(0);
  refs.forEach((r, i) => { const d = applyRecipe(new Uint8ClampedArray(r.d), r.w, r.h, rec.p); const f = feats(d, r.w, r.h); for (let q = 0; q < 16; q++) acc[q] += f[q] - base[i][q]; });
  out.push(acc.map((x) => +(x / refs.length).toFixed(4)));
  if (k % 500 === 0) console.log(k, Math.round((Date.now() - t0) / 1000) + ' s');
});
fs.writeFileSync('H:/coqueta-studio/looks/features.json', JSON.stringify({ names: ['mean', 'std', 'p02', 'p50', 'p98', 'warm', 'tint', 'sat', 'gray', 'shR', 'shG', 'shB', 'hiR', 'hiG', 'hiB', 'vig'], f: out }));
console.log('fin', out.length);

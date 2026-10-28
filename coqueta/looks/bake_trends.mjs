// Estilos de redes y de apps de filtros (investigación del 28-10-2026: VSCO, Instagram, Huji/Dazz, Lightroom móvil,
// estéticas de TikTok e Instagram, estilos coreano/japonés/港风 y los del iPhone), hechos aquí como recetas de revelado
// y horneados en tablas 3D de 17³ con el motor de la web. Son interpretaciones propias de cada estilo (no copias de los
// filtros de ninguna app). `extra`: palabras para el buscador (inglés, español, portugués).
// Salida: trends-extra.bin y trends-extra.json.
import { writeFileSync } from "node:fs";
import { applyRecipe } from "file:///H:/promptribe-feed/assets/js/coqueta-foto-looks.js";

const T = [
  // ahora: limpio, natural, de película suave
  ["Clean girl", { temp: 12, tint: 3, contrast: -8, saturation: -10, vibrance: 4, hsl: { Orange: [0, -5, 6], Yellow: [0, -12, 0] }, curve: [[0, 8], [128, 133], [255, 250]] },
    ["clean girl aesthetic, warm beige cream neutral, natural glowing skin, minimal", "estética clean girl, beige crema cálido y neutro, piel natural luminosa, minimalista", "estética clean girl, bege creme quente e neutro, pele natural luminosa, minimalista"]],
  ["Old money", { temp: 8, contrast: 6, saturation: -18, hsl: { Green: [-5, -25, -5], Blue: [0, -20, -5] }, splitSH: 30, splitSS: 12, curve: [[0, 10], [64, 60], [192, 196], [255, 245]] },
    ["old money quiet luxury, deep muted warm tones, elegant", "old money, lujo silencioso, tonos cálidos profundos y apagados, elegante", "old money, luxo silencioso, tons quentes profundos e suaves, elegante"]],
  ["Bright & airy", { exposure: 0.35, contrast: -15, highlights: -20, shadows: 40, whites: 10, vibrance: 10, saturation: -5, temp: 3, curve: [[0, 12], [128, 140], [255, 255]] },
    ["bright and airy, light clean instagram preset, wedding lifestyle", "luminoso y aireado, claro y limpio para instagram, bodas y lifestyle", "claro e arejado, limpo para instagram, casamento e lifestyle"]],
  ["Moody oscuro", { exposure: -0.2, contrast: 10, highlights: -40, shadows: -10, saturation: -20, hsl: { Green: [-10, -40, -10], Blue: [0, -30, -10] }, splitSH: 190, splitSS: 15, curve: [[0, 15], [64, 50], [192, 190], [255, 240]] },
    ["dark and moody, dramatic muted instagram preset", "oscuro y moody, dramático y apagado, preset de instagram", "escuro e moody, dramático e suave, preset de instagram"]],
  ["Melocotón", { temp: 10, tint: 8, contrast: -8, highlights: -15, shadows: 20, hsl: { Orange: [-5, 5, 8], Red: [5, -10, 5] }, splitHH: 25, splitHS: 15, curve: [[0, 10], [128, 135], [255, 250]] },
    ["peachy soft warm pink orange skin, summer", "melocotón, durazno suave, rosado cálido, verano", "pêssego suave, rosado quente, verão"]],
  ["Coquette", { tint: 12, temp: 4, exposure: 0.15, contrast: -12, saturation: -5, hsl: { Red: [5, -5, 5], Magenta: [0, 10, 0] }, splitHH: 340, splitHS: 15, curve: [[0, 14], [128, 136], [255, 252]] },
    ["coquette aesthetic, soft pink, romantic, bows pearls", "estética coquette, rosa suave, romántica, lazos y perlas", "estética coquette, rosa suave, romântica, laços e pérolas"]],
  ["Dark academia", { temp: 15, exposure: -0.2, highlights: -30, shadows: 20, saturation: -25, hsl: { Green: [-10, -40, -5], Orange: [0, -5, 0] }, splitSH: 35, splitSS: 15, curve: [[0, 18], [64, 58], [192, 190], [255, 238]] },
    ["dark academia, warm brown, vintage library, autumn", "dark academia, marrón cálido, biblioteca antigua, otoño", "dark academia, marrom quente, biblioteca antiga, outono"]],
  ["Cottagecore", { temp: 14, tint: 4, contrast: -6, vibrance: 8, hsl: { Green: [-10, -10, 5], Yellow: [0, 5, 0] }, curve: [[0, 10], [128, 134], [255, 250]] },
    ["cottagecore, countryside, soft warm greens and gold, flowers", "cottagecore, campo, verdes suaves y dorados, flores", "cottagecore, campo, verdes suaves e dourados, flores"]],
  // la era VSCO y Tumblr (2014-2019)
  ["Feed mate 2016", { temp: 5, contrast: -10, saturation: -18, splitSH: 200, splitSS: 8, curve: [[0, 40], [64, 70], [192, 190], [255, 230]] },
    ["vsco faded matte feed 2016, a6 f2 style, washed out", "feed mate de vsco 2016, desvaído, tipo a6 o f2", "feed fosco do vsco 2016, desbotado, tipo a6 ou f2"]],
  ["Tumblr 2014", { temp: 20, saturation: -15, splitHH: 40, splitHS: 25, splitSH: 20, splitSS: 15, curve: [[0, 30], [128, 128], [255, 235]] },
    ["tumblr aesthetic 2014, warm sepia faded, grunge", "estética tumblr 2014, sepia cálido desvaído", "estética tumblr 2014, sépia quente desbotado"]],
  ["VSCO cálido", { temp: 10, exposure: 0.1, contrast: -5, vibrance: 5, saturation: -8, splitHH: 40, splitHS: 10, curve: [[0, 14], [128, 132], [255, 250]] },
    ["vsco warm clean a6 c1, soft film", "vsco cálido y limpio, tipo a6 o c1", "vsco quente e limpo, tipo a6 ou c1"]],
  ["VSCO apagado", { temp: 6, contrast: -6, saturation: -30, hsl: { Orange: [5, -10, 0] }, curve: [[0, 22], [128, 128], [255, 240]] },
    ["vsco muted retro m5, desaturated rust", "vsco apagado y retro, tipo m5, desaturado", "vsco suave e retrô, tipo m5, dessaturado"]],
  // cámaras de antes en el móvil
  ["Digicam Y2K", { temp: -15, tint: 5, contrast: 15, exposure: 0.15, highlights: 20, saturation: 8, curve: [[0, 0], [64, 60], [192, 210], [255, 255]] },
    ["y2k digicam ccd camera, 2000s digital, cool, harsh flash", "digicam y2k, cámara ccd de los 2000, fría, flash directo", "digicam y2k, câmera ccd dos anos 2000, fria, flash direto"]],
  ["Desechable", { temp: 12, tint: -5, contrast: 10, saturation: 5, splitSH: 150, splitSS: 18, curve: [[0, 12], [128, 132], [255, 245]] },
    ["disposable camera, huji dazz, 90s dispo, green shadows", "cámara desechable, huji o dazz, dispo de los 90", "câmera descartável, huji ou dazz, dispo dos anos 90"]],
  ["Flash de fiesta", { temp: -5, contrast: 25, saturation: 10, highlights: 15, curve: [[0, 0], [64, 50], [192, 210], [255, 255]] },
    ["indie sleaze party flash 2008, harsh flash, saturated", "indie sleaze, flash de fiesta 2008, flash duro y saturado", "indie sleaze, flash de festa 2008, flash duro e saturado"]],
  // Asia
  ["Coreano pastel", { exposure: 0.25, contrast: -20, highlights: -20, shadows: 30, temp: -10, tint: 8, saturation: -8, hsl: { Green: [20, -30, 10], Blue: [-10, -10, 5] }, curve: [[0, 22], [128, 140], [255, 250]] },
    ["korean pastel soft aesthetic, bright hazy, kpop", "coreano pastel, suave y brillante, estilo kpop", "coreano pastel, suave e claro, estilo kpop"]],
  ["Japonés claro", { exposure: 0.3, contrast: -18, temp: -8, saturation: -10, vibrance: 10, splitHH: 180, splitHS: 12, curve: [[0, 18], [128, 140], [255, 252]] },
    ["japanese airy film, bright cool soft, nihon style", "japonés claro y aireado, frío y suave, estilo japonés", "japonês claro e arejado, frio e suave, estilo japonês"]],
  ["Hong Kong 90s", { temp: 18, tint: -8, highlights: -35, shadows: 20, contrast: 15, saturation: 5, splitSH: 160, splitSS: 20, splitHH: 45, splitHS: 22, curve: [[0, 6], [64, 56], [192, 200], [255, 240]] },
    ["hong kong film 90s, wong kar wai, warm yellow green cinematic", "hong kong de los 90, estilo wong kar-wai, amarillo verdoso de cine", "hong kong anos 90, estilo wong kar-wai, amarelo esverdeado de cinema"]],
  ["Ins minimal", { exposure: -0.1, contrast: -20, saturation: -15, curve: [[0, 25], [128, 124], [255, 235]] },
    ["minimal instagram low contrast, ins style, calm muted", "minimalista de instagram, poco contraste, estilo ins, calmado", "minimalista do instagram, pouco contraste, estilo ins, calmo"]],
  // estilos de la cámara del iPhone
  ["Contraste rico", { contrast: 25, shadows: -20, saturation: 10, curve: [[0, 0], [64, 56], [192, 202], [255, 255]] },
    ["rich contrast iphone style, dramatic", "contraste rico tipo iphone, dramático", "contraste rico tipo iphone, dramático"]],
  ["Ámbar", { temp: 20, tint: 5, splitHH: 40, splitHS: 20, vibrance: 5, curve: [[0, 6], [128, 132], [255, 250]] },
    ["amber warm golden iphone style", "ámbar cálido y dorado tipo iphone", "âmbar quente e dourado tipo iphone"]],
  ["Oro rosa", { temp: 8, tint: 12, splitHH: 15, splitHS: 18, curve: [[0, 8], [128, 134], [255, 250]] },
    ["rose gold soft pink warm iphone style", "oro rosa, rosado cálido tipo iphone", "ouro rosa, rosado quente tipo iphone"]],
];

const N = 17, W = N * N, img = new Uint8ClampedArray(W * N * 4);
const blob = [];
for (const [, p] of T) {
  for (let b = 0; b < N; b++) for (let g = 0; g < N; g++) for (let r = 0; r < N; r++) {
    const i = (g * W + b * N + r) * 4, v = (k) => Math.round(k * 255 / (N - 1));
    img[i] = v(r); img[i + 1] = v(g); img[i + 2] = v(b); img[i + 3] = 255;
  }
  const d = new Uint8ClampedArray(img);
  applyRecipe(d, W, N, { ...p, clarity: 0, vignette: 0, grain: 0 });
  for (let b = 0; b < N; b++) for (let g = 0; g < N; g++) for (let r = 0; r < N; r++) { const i = (g * W + b * N + r) * 4; blob.push(d[i], d[i + 1], d[i + 2]); }
}
writeFileSync("H:/coqueta-studio/looks/trends-extra.bin", Buffer.from(blob));
writeFileSync("H:/coqueta-studio/looks/trends-extra.json", JSON.stringify(T.map(([title, p, [en, es, pt]]) => ({ title, p, extra: en, extra_es: es, extra_pt: pt })), null, 1));
console.log(T.length, "estilos", blob.length, "bytes");

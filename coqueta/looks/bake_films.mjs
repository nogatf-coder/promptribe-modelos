// Películas que faltaban (CineStill, Kodak Gold…), hechas en Coqueta como recetas de revelado que imitan su carácter
// (no son tablas oficiales de las marcas) y horneadas en tablas 3D de 17³ con el mismo motor de la web.
// Salida: films-extra.bin (17³×3 bytes por película, en orden) y films-extra.json (nombre, marca, receta).
import { writeFileSync } from "node:fs";
import { applyRecipe } from "file:///H:/promptribe-feed/assets/js/coqueta-foto-looks.js";

const FILMS = [
  // luz de tungsteno: sombras verde azulado, luces algo rojas, negros un poco levantados (su halo rojo es aparte)
  ["CineStill 800T", "CineStill", { temp: -22, tint: -4, contrast: 10, vibrance: 8, saturation: -4, splitSH: 190, splitSS: 26, splitHH: 15, splitHS: 16, splitBal: -10, curve: [[0, 12], [64, 62], [192, 198], [255, 250]] }],
  // luz de día: limpia, algo fría, colores vivos
  ["CineStill 50D", "CineStill", { temp: -8, contrast: 14, vibrance: 20, saturation: 4, splitSH: 205, splitSS: 10, curve: [[0, 4], [64, 60], [192, 200], [255, 254]] }],
  // cálida y dorada, saturada, con luces amarillas
  ["Kodak Gold 200", "Kodak", { temp: 24, tint: 4, contrast: 8, vibrance: 16, saturation: 8, splitHH: 45, splitHS: 24, splitSH: 30, splitSS: 10, curve: [[0, 8], [128, 133], [255, 250]] }],
  // cálida y con más contraste y color
  ["Kodak UltraMax 400", "Kodak", { temp: 15, contrast: 18, vibrance: 22, saturation: 10, splitHH: 40, splitHS: 15, curve: [[0, 4], [64, 58], [192, 202], [255, 252]] }],
  // cálida, desvaída, con los verdes apagados
  ["Kodak ColorPlus 200", "Kodak", { temp: 18, saturation: -5, hsl: { Green: [0, -25, 0], Aqua: [0, -15, 0] }, splitHH: 40, splitHS: 20, curve: [[0, 18], [128, 130], [255, 242]] }],
  // suave, con un toque verde y fresco
  ["Fujicolor C200", "Fuji", { temp: -5, tint: -10, contrast: -6, vibrance: 6, splitSH: 160, splitSS: 14, hsl: { Green: [8, 8, 0] }, curve: [[0, 10], [128, 128], [255, 248]] }],
  // mucho color y contraste, sombras azuladas
  ["Lomography Color 800", "Lomography", { temp: 10, contrast: 25, saturation: 18, vibrance: 10, splitSH: 220, splitSS: 15, curve: [[0, 0], [64, 54], [192, 206], [255, 255]] }],
];

const N = 17, W = N * N, img = new Uint8ClampedArray(W * N * 4);
const blob = [];
for (const [, , p] of FILMS) {
  for (let b = 0; b < N; b++) for (let g = 0; g < N; g++) for (let r = 0; r < N; r++) {
    const i = (g * W + b * N + r) * 4, v = (k) => Math.round(k * 255 / (N - 1));
    img[i] = v(r); img[i + 1] = v(g); img[i + 2] = v(b); img[i + 3] = 255;
  }
  const d = new Uint8ClampedArray(img);
  applyRecipe(d, W, N, { ...p, clarity: 0, vignette: 0, grain: 0 });
  // en el orden de luts.bin: [b][g][r]
  for (let b = 0; b < N; b++) for (let g = 0; g < N; g++) for (let r = 0; r < N; r++) { const i = (g * W + b * N + r) * 4; blob.push(d[i], d[i + 1], d[i + 2]); }
}
writeFileSync("H:/coqueta-studio/looks/films-extra.bin", Buffer.from(blob));
writeFileSync("H:/coqueta-studio/looks/films-extra.json", JSON.stringify(FILMS.map(([title, brand, p]) => ({ title, brand, p })), null, 1));
console.log(FILMS.length, "películas", blob.length, "bytes");

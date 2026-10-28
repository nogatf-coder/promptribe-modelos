# Todo lo que el asistente sabe imitar en un índice: los looks (recetas de revelado) y las películas (tablas de color),
# cada uno con su descripción en inglés convertida en vector de significado (paraphrase-multilingual-MiniLM-L12-v2).
# Así, lo que pide la persona (en cualquier idioma) se compara con las descripciones y salen los más parecidos.
import json, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer

looks = json.load(open('H:/coqueta-studio/looks/looks.json', encoding='utf-8'))
luts = json.load(open('H:/coqueta-studio/looks/luts.json', encoding='utf-8'))

def lut_desc(l):
    m, sd, p02, p98, warm, tint, sat, shr, shg, shb, hir, hig, hib = l['f']
    t = l['title'].lower(); w = []
    brand = l['brand'].replace('CreativePack-1', 'creative')
    if l['bw']: w.append('black and white film')
    if m > 0.03: w.append('bright')
    if m < -0.03: w.append('dark moody')
    if sd > 0.02: w.append('high contrast')
    if sd < -0.02: w.append('soft low contrast')
    if p02 > 0.04: w.append('faded matte blacks')
    if not l['bw']:
        if warm > 0.02: w.append('warm tones')
        if warm < -0.02: w.append('cool blue tones')
        if tint > 0.015: w.append('green tint')
        if tint < -0.015: w.append('magenta tint')
        if sat > 0.03: w.append('vivid saturated colors')
        if sat < -0.03: w.append('muted colors')
        def col(r, g, b):
            import colorsys
            h = colorsys.rgb_to_hls(r + .5, g + .5, b + .5)[0] * 360
            return min([(0, 'red'), (30, 'orange'), (55, 'yellow'), (110, 'green'), (170, 'teal'), (215, 'blue'), (270, 'purple'), (320, 'magenta'), (360, 'red')], key=lambda x: abs(x[0] - h))[1]
        if max(abs(shr), abs(shg), abs(shb)) > 0.015: w.append(col(shr, shg, shb) + ' shadows')
        if max(abs(hir), abs(hig), abs(hib)) > 0.015: w.append(col(hir, hig, hib) + ' highlights')
    kind = 'instant polaroid photo' if 'polaroid' in t or brand == 'Polaroid' else 'expired film' if 'expired' in t else 'cross processed' if 'xpro' in t or 'cross' in t else 'analog film'
    if 'slide' in t or 'velvia' in t or 'provia' in t or 'ektachrome' in t or 'kodachrome' in t: kind = 'slide film'
    if brand == 'creative': kind = 'creative color grade'
    if 'push' in t or '++' in t: w.append('pushed film')
    return f"{l['title']}: {kind}, " + ', '.join(w) + ' look' if w else f"{l['title']}: {kind} look"

items = [{'kind': 'look', 'id': L['id'], 'name': L['name'], 'desc': L['desc']} for L in looks]
# los estilos de redes llevan además sus palabras (en, es, pt): «clean girl», «tumblr», «vsco»…
items += [{'kind': 'lut', 'id': l['id'], 'name': l['title'], 'desc': lut_desc(l) + (' | ' + l['extra'] if l.get('extra') else ''), 'bw': l['bw'], **({'extra_es': l['extra_es'], 'extra_pt': l['extra_pt']} if l.get('extra') else {})} for l in luts]
M = 'H:/promptribe-modelos/minilm/'
tok = Tokenizer.from_file(M + 'tokenizer.json')
so = ort.SessionOptions(); so.log_severity_level = 3
s = ort.InferenceSession(M + 'model_quantized.onnx', so, providers=['CPUExecutionProvider'])
names = [i.name for i in s.get_inputs()]
def emb(text):
    e = tok.encode(text); ids = np.array([e.ids[:128]], np.int64); am = np.array([e.attention_mask[:128]], np.int64)
    feeds = {'input_ids': ids, 'attention_mask': am}
    if 'token_type_ids' in names: feeds['token_type_ids'] = np.zeros_like(ids)
    h = s.run(None, feeds)[0][0]; v = (h * am[0][:, None]).sum(0) / am[0].sum(); return v / np.linalg.norm(v)
V = np.array([emb(it['desc']) for it in items], np.float32)
# vectores en int8 (con su escala) para que el índice pese poco
scale = float(np.abs(V).max()) / 127
q = np.clip(np.round(V / scale), -127, 127).astype(np.int8)
open('H:/coqueta-studio/looks/index.bin', 'wb').write(q.tobytes())
json.dump({'scale': scale, 'dim': int(V.shape[1]), 'items': items}, open('H:/coqueta-studio/looks/index.json', 'w', encoding='utf-8'), separators=(',', ':'))
print(len(items), 'entradas')
for it in items[119:126]: print(it['desc'])
for qtext in ['make it look like a kodak portra photo', 'polaroid instant vintage', 'moody dark teal and orange', 'soft pastel wedding', 'como una foto vieja quemada', 'blanco y negro con mucho contraste', 'vivid summer instagram']:
    v = emb(qtext); sc = V @ v; top = np.argsort(-sc)[:3]
    print(qtext, '->', ' | '.join(f"{items[i]['name']} {sc[i]:.2f}" for i in top))

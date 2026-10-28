# Ajuste de la búsqueda de looks: significado (el mejor de los tres idiomas) + rasgos con nombre (cálido, mate…).
# Mismas reglas que el trabajador de la web (coqueta-foto-ai-worker.js, lookSearch).
import json, re, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer

d = json.load(open('H:/coqueta-studio/looks/index-i18n.json', encoding='utf-8'))
items, dim, L = d['items'], d['dim'], len(d['langs'])
V = np.frombuffer(open('H:/coqueta-studio/looks/index-i18n.bin', 'rb').read(), np.int8).reshape(len(items), L, dim).astype(np.float32) * d['scale']
ITEM = {
    'warm': r'warm|golden|orange (high|shad)|yellow (high|shad)|sunset|golden hour|portra', 'cool': r'cool blue|blue shadows|blue highlights|winter|cold|teal',
    'matte': r'matte|faded', 'bright': r'bright|airy', 'dark': r'dark moody|deep rich blacks|night|dark vignette', 'contrast': r'high contrast|punchy|crisp',
    'soft': r'soft|dreamy', 'vivid': r'vivid|saturated|pop color', 'muted': r'muted|desaturated', 'vintage': r'vintage|retro|expired|faded|polaroid|lomo|analog|sepia',
    'bw': r'black and white', 'polaroid': r'polaroid', 'film': r'film|slide', 'cinematic': r'cinematic|bleach|teal (shad|high).*orange|orange (shad|high).*teal',
    'wedding': r'wedding', 'portrait': r'portrait', 'landscape': r'landscape', 'summer': r'summer|golden hour', 'night': r'night',
    'green': r'green|olive', 'pink': r'pink|magenta', 'sepia': r'sepia',
}
QUERY = {
    'warm': r'c[aá]lid|quente|warm|dorad|dourad|golden|atardecer|p[oô]r do sol|sunset|naranja|laranja', 'cool': r'fr[ií][oa]|cool|cold|azul|blue|invierno|inverno|winter|gelad|helad',
    'matte': r'\bmate\b|fosc|matte|desva[ií]d|desbotad|faded|lavad', 'bright': r'luminos|\bclar[oa]s?\b|bright|airy|aireado|arejad|radiante', 'dark': r'oscur|escur|\bdark|moody|dram[aá]tic|noche|noite|night|sombr[ií]',
    'contrast': r'contrast|punch|intens|fuerte|forte', 'soft': r'suave|soft|delicad|ensue[nñ]o|sonho|dreamy', 'vivid': r'\bviv[oa]s?\b|vibrant|saturad|vivid|\bpop\b|colorid',
    'muted': r'apagad|desaturad|muted|pastel', 'vintage': r'vintage|retro|antig|viej|velh|\bold\b|a[nñ]os (60|70|80|90)|anos (60|70|80|90)|nost[aá]lg|caducad|vencid|expired',
    'bw': r'blanco y negro|b/n|preto e branco|black and white|monocrom', 'polaroid': r'polaroid|instant[aá]ne', 'film': r'pel[ií]cula|filme|\bfilm|anal[oó]g|carrete|rollo',
    'cinematic': r'\bcine\b|cinem|movie', 'wedding': r'boda|casament|wedding|novi[ao]|noiva', 'portrait': r'retrato|portrait|selfi', 'landscape': r'paisaj|paisagem|landscape|monta[nñ]',
    'summer': r'verano|ver[aã]o|summer|playa|praia|beach', 'night': r'noche|noite|night', 'green': r'verde|green|oliv', 'pink': r'\brosa|pink|magenta|rosad', 'sepia': r's[eé]pia',
}
OPP = [('warm', 'cool'), ('bright', 'dark'), ('contrast', 'soft'), ('vivid', 'muted')]
def item_tags(it):
    t = set(k for k, r in ITEM.items() if re.search(r, it['desc'].lower()))
    # el nombre manda: «Cold» es frío y «Warm» cálido, diga lo que diga la medida
    if re.search(r'\bcold\b', it['name'], re.I): t.discard('warm'); t.add('cool')
    if re.search(r'\bwarm', it['name'], re.I): t.discard('cool'); t.add('warm')
    return t
tags = [item_tags(it) for it in items]
M = 'H:/promptribe-modelos/minilm/'
tok = Tokenizer.from_file(M + 'tokenizer.json'); so = ort.SessionOptions(); so.log_severity_level = 3
s = ort.InferenceSession(M + 'model_quantized.onnx', so, providers=['CPUExecutionProvider']); names = [i.name for i in s.get_inputs()]
def emb(text):
    e = tok.encode(text); ids = np.array([e.ids[:128]], np.int64); am = np.array([e.attention_mask[:128]], np.int64)
    feeds = {'input_ids': ids, 'attention_mask': am}
    if 'token_type_ids' in names: feeds['token_type_ids'] = np.zeros_like(ids)
    h = s.run(None, feeds)[0][0]; v = (h * am[0][:, None]).sum(0) / am[0].sum(); return v / np.linalg.norm(v)
def search(q, W=0.14, C=0.18):
    v = emb(q); sem = (V @ v).max(1); qt = set(k for k, r in QUERY.items() if re.search(r, q.lower()))
    out = []
    for i, it in enumerate(items):
        sc = sem[i] + W * len(qt & tags[i])
        for a, b in OPP:
            if (a in qt and b in tags[i] and a not in tags[i]) or (b in qt and a in tags[i] and b not in tags[i]): sc -= C
        if 'bw' in tags[i] and 'bw' not in qt: sc -= 1
        out.append((sc, it['name'], sorted(tags[i] & qt)))
    out.sort(key=lambda x: -x[0]); return qt, out[:4]
for q in ['mate y cálido', 'verano en la playa', 'como una foto vieja', 'blanco y negro con mucho contraste', 'tonos fríos de invierno', 'boda luminosa y suave', 'cine oscuro y dramático', 'cores quentes de pôr do sol', 'polaroid antigua', 'colores vivos y alegres', 'retrato suave y natural', 'foto fosca e fria']:
    qt, top = search(q)
    print(f'{q}  {sorted(qt)}\n   ' + ' | '.join(f'{n} {sc:.2f} {t}' for sc, n, t in top))

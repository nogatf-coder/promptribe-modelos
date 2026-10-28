# El índice de looks y películas con descripciones en inglés, español y portugués: cada entrada lleva un vector de
# significado por idioma (paraphrase-multilingual-MiniLM-L12-v2) y al buscar se queda el que mejor encaja. Así «mate y
# cálido» o «verano en la playa» aciertan igual que en inglés. Parte del índice en inglés (describe_index.py) y traduce
# su vocabulario (unas 70 expresiones fijas).
import json, re, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer

SRC = 'H:/coqueta-studio/looks/index.json'
# expresión → (español, portugués)
P = {
    'bright': ('luminoso', 'luminoso'), 'analog film': ('película analógica', 'filme analógico'), 'high contrast': ('mucho contraste', 'alto contraste'),
    'vivid saturated colors': ('colores vivos y saturados', 'cores vivas e saturadas'), 'instant polaroid photo': ('foto instantánea Polaroid', 'foto instantânea Polaroid'),
    'warm tones': ('tonos cálidos', 'tons quentes'), 'faded matte blacks': ('negros mate desvaídos', 'pretos foscos desbotados'), 'teal shadows': ('sombras verde azulado', 'sombras verde-azuladas'),
    'green tint': ('tinte verde', 'tom esverdeado'), 'soft low contrast': ('suave y con poco contraste', 'suave e com pouco contraste'), 'black and white film': ('película en blanco y negro', 'filme preto e branco'),
    'yellow highlights': ('luces amarillas', 'luzes amarelas'), 'cool blue tones': ('tonos fríos azulados', 'tons frios azulados'), 'blue highlights': ('luces azules', 'luzes azuis'),
    'pushed film': ('película forzada', 'filme puxado'), 'faded matte film': ('película mate desvaída', 'filme fosco desbotado'), 'blue shadows': ('sombras azules', 'sombras azuis'),
    'bright airy': ('luminoso y aireado', 'claro e arejado'), 'purple highlights': ('luces violetas', 'luzes roxas'), 'orange highlights': ('luces naranjas', 'luzes laranja'),
    'orange shadows': ('sombras naranjas', 'sombras laranja'), 'creative color grade': ('etalonaje creativo', 'correção de cor criativa'), 'dark moody': ('oscuro y dramático', 'escuro e dramático'),
    'warm golden tones': ('tonos dorados cálidos', 'tons dourados quentes'), 'magenta tint': ('tinte magenta', 'tom magenta'), 'muted colors': ('colores apagados', 'cores suaves'),
    'teal highlights': ('luces verde azulado', 'luzes verde-azuladas'), 'yellow shadows': ('sombras amarillas', 'sombras amarelas'), 'purple shadows': ('sombras violetas', 'sombras roxas'),
    'black and white': ('blanco y negro', 'preto e branco'), 'pink magenta tint': ('tinte rosa magenta', 'tom rosa magenta'), 'red highlights': ('luces rojas', 'luzes vermelhas'),
    'crisp sharp detail clarity': ('nítido con mucho detalle', 'nítido com muito detalhe'), 'green olive tint': ('tinte verde oliva', 'tom verde-oliva'), 'red shadows': ('sombras rojas', 'sombras vermelhas'),
    'dark vignette': ('viñeta oscura', 'vinheta escura'), 'slide film': ('diapositiva', 'filme de slide'), 'green highlights': ('luces verdes', 'luzes verdes'), 'magenta highlights': ('luces magenta', 'luzes magenta'),
    'muted desaturated colors': ('colores apagados y desaturados', 'cores suaves e dessaturadas'), 'deep rich blacks': ('negros profundos', 'pretos profundos'), 'green shadows': ('sombras verdes', 'sombras verdes'),
    'magenta shadows': ('sombras magenta', 'sombras magenta'), 'film grain': ('grano de película', 'granulação de filme'), 'natural': ('natural', 'natural'), 'cross processed': ('revelado cruzado', 'revelação cruzada'),
    'dreamy soft glow': ('brillo suave de ensueño', 'brilho suave de sonho'), 'high contrast punchy': ('contraste fuerte e intenso', 'contraste forte e marcante'),
    'expired film': ('película caducada', 'filme vencido'),
    # «look for …»: para qué sirve
    'for:wedding': ('boda', 'casamento'), 'for:HDR landscape': ('paisaje HDR', 'paisagem HDR'), 'for:analog film': ('película analógica', 'filme analógico'), 'for:landscape': ('paisaje', 'paisagem'),
    'for:matte': ('mate', 'fosco'), 'for:vintage retro': ('vintage retro', 'vintage retrô'), 'for:portrait': ('retrato', 'retrato'), 'for:cinematic movie': ('cine, película de cine', 'cinema, filme de cinema'),
    'for:fashion editorial': ('editorial de moda', 'editorial de moda'), 'for:bleach bypass': ('bleach bypass, plata retenida', 'bleach bypass, prata retida'), 'for:clean': ('limpio', 'limpo'),
    'for:lomo toy camera': ('lomo, cámara de juguete', 'lomo, câmera de brinquedo'), 'for:winter cold': ('invierno frío', 'inverno frio'), 'for:cross processed': ('revelado cruzado', 'revelação cruzada'),
    'for:golden hour': ('hora dorada, atardecer', 'hora dourada, pôr do sol'), 'for:summer': ('verano, playa', 'verão, praia'), 'for:olive': ('verde oliva', 'verde-oliva'), 'for:sepia': ('sepia', 'sépia'),
    'for:portra film': ('película Portra', 'filme Portra'), 'for:orange': ('naranja', 'laranja'), 'for:pop color': ('colores pop', 'cores pop'), 'for:night': ('noche', 'noite'),
}


def split(desc, kind):
    title = ''
    if kind == 'lut' and ': ' in desc: title, desc = desc.split(': ', 1)
    desc = re.sub(r' look$', '', desc)
    m = re.match(r'(.*?) look for (.*)$', desc)
    if m: return title, [p.strip() for p in m.group(1).split(',') if p.strip()], [p.strip() for p in m.group(2).split(',') if p.strip()]
    return title, [p.strip() for p in desc.split(',') if p.strip()], []


def tr(desc, kind, lang):
    title, parts, uses = split(desc, kind)
    i = 0 if lang == 'es' else 1
    missing = [p for p in parts if p not in P] + [u for u in uses if 'for:' + u not in P]
    if missing: raise SystemExit(f'sin traducir: {missing}')
    words = [P[p][i] for p in parts]
    s = ('estilo ' if lang == 'es' else 'estilo ') + ', '.join(words)
    if uses: s += (' para ' if lang == 'es' else ' para ') + ', '.join(P['for:' + u][i] for u in uses)
    return f'{title}: {s}' if title else s


d = json.load(open(SRC, encoding='utf-8'))
items = d['items']
for it in items:
    it['es'] = tr(it['desc'], it['kind'], 'es')
    it['pt'] = tr(it['desc'], it['kind'], 'pt')
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


LANGS = ['en', 'es', 'pt']
V = np.array([[emb(it['desc'] if L == 'en' else it[L]) for L in LANGS] for it in items], np.float32)   # items × idiomas × dim
scale = float(np.abs(V).max()) / 127
q = np.clip(np.round(V / scale), -127, 127).astype(np.int8)
open('H:/coqueta-studio/looks/index-i18n.bin', 'wb').write(q.tobytes())
json.dump({'scale': scale, 'dim': int(V.shape[2]), 'langs': LANGS, 'items': items}, open('H:/coqueta-studio/looks/index-i18n.json', 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
print(len(items), 'entradas ×', len(LANGS), 'idiomas')
print(items[0]['es']); print(items[150]['pt'])
# comparación: solo inglés frente a los tres idiomas, con peticiones en español y portugués
E = V[:, 0, :]
for qtext in ['mate y cálido', 'verano en la playa', 'como una foto vieja', 'blanco y negro con mucho contraste', 'tonos fríos de invierno', 'boda luminosa y suave', 'cine oscuro y dramático', 'cores quentes de pôr do sol', 'polaroid antigua']:
    v = emb(qtext)
    a = E @ v; b = (V @ v).max(1)
    ta, tb = np.argsort(-a)[:3], np.argsort(-b)[:3]
    print(f'{qtext}\n  antes: ' + ' | '.join(f"{items[i]['name']} {a[i]:.2f}" for i in ta) + '\n  ahora: ' + ' | '.join(f"{items[i]['name']} {b[i]:.2f}" for i in tb))

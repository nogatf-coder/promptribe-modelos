# Ejemplos con licencia libre (CC0 y dominio público) de cada estilo de edición, desde Openverse (la API abierta de
# WordPress). Solo para medir cómo son los estilos (color, tono, viñeta) y aprender a reconocerlos; no se publican.
# Se guarda autor, licencia y página de origen de cada foto (meta.json). Despacio, para respetar el límite anónimo.
import json, os, time, urllib.parse, urllib.request, sys

ROOT = 'H:/coqueta-studio/estilos-aprendidos/datos'
STYLES = {
    'flash': ['flash photography', 'on camera flash', 'party flash photo', 'night flash portrait'],
    'disposable': ['disposable camera', 'disposable camera photo'],
    'cinestill': ['cinestill 800t', 'cinestill'],
    'portra': ['kodak portra 400', 'kodak portra'],
    'gold': ['kodak gold 200', 'kodak ultramax 400'],
    'fuji': ['fujifilm superia', 'fuji 400h', 'fujicolor c200'],
    'lomo': ['lomography', 'lomo lc-a'],
    'bwfilm': ['ilford hp5', 'kodak tri-x', 'black and white film portrait'],
    'cinematic': ['cinematic photography', 'film still', 'cinematic portrait', 'teal and orange'],
    'moody': ['moody portrait', 'dark moody photography'],
    'airy': ['bright airy photography', 'high key portrait'],
    'urban': ['street photography', 'urban portrait', 'streetwear'],
    'interior': ['interior design', 'cozy room interior', 'living room interior'],
    'professional': ['editorial portrait', 'professional headshot', 'fashion photography', 'studio portrait'],
    'neutral': ['smartphone photo', 'snapshot', 'iphone photo', 'casual photo'],
}
TARGET = 110
ua = {'User-Agent': 'MyPrompTribe-CoquetaFoto-research/1.0 (+https://www.mypromptribe.com)'}

def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=60) as r:
                return r.read()
        except Exception as e:
            code = getattr(e, 'code', None)
            if code == 429:
                time.sleep(60 * (k + 1))
            else:
                time.sleep(5 * (k + 1))
    return None

def small(u):
    # Flickr: la versión de 640 px en vez de la original
    if 'staticflickr.com' in u and u.rsplit('.', 1)[0][-2:-1] != '_':
        base, ext = u.rsplit('.', 1)
        return f'{base}_z.{ext}'
    return u

only = sys.argv[1:] or list(STYLES)
for style in only:
    folder = os.path.join(ROOT, style); os.makedirs(folder, exist_ok=True)
    meta_path = os.path.join(folder, 'meta.json')
    meta = json.load(open(meta_path, encoding='utf-8')) if os.path.exists(meta_path) else {}
    for q in STYLES[style]:
        page = 1
        while len(meta) < TARGET and page <= 6:
            url = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode({'q': q, 'license': 'cc0,pdm', 'page_size': 20, 'page': page, 'mature': 'false'})
            raw = get(url)
            time.sleep(4)
            if not raw: break
            res = json.loads(raw).get('results', [])
            if not res: break
            for r in res:
                if r['id'] in meta or len(meta) >= TARGET: continue
                img = get(small(r['url']), tries=2)
                if not img or len(img) < 5000: continue
                name = r['id'] + '.jpg'
                open(os.path.join(folder, name), 'wb').write(img)
                meta[r['id']] = {'file': name, 'title': r.get('title'), 'creator': r.get('creator'), 'license': r.get('license'), 'license_version': r.get('license_version'), 'source': r.get('source'), 'landing': r.get('foreign_landing_url'), 'query': q}
            json.dump(meta, open(meta_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            page += 1
        if len(meta) >= TARGET: break
    print(style, len(meta), flush=True)
print('fin', flush=True)

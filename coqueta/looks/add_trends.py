# Añade al catálogo (luts.bin / luts.json) los estilos de redes de bake_trends.mjs, con sus rasgos medidos y sus
# palabras para el buscador (extra, extra_es, extra_pt). Los que ya estén se sustituyen en su sitio (mismo id); los
# nuevos van al final. Nada de lo anterior cambia de id.
import json, struct, sys, numpy as np
D = 'H:/coqueta-studio/looks/'
sys.path.insert(0, D)
from measure import S, measure
luts = json.load(open(D + 'luts.json', encoding='utf-8'))
raw = open(D + 'luts.bin', 'rb').read()
count, size = struct.unpack('<II', raw[:8]); per = size ** 3 * 3
assert size == S and len(raw) == 8 + count * per
blobs = [raw[8 + i * per: 8 + (i + 1) * per] for i in range(count)]
extra = json.load(open(D + 'trends-extra.json', encoding='utf-8'))
ebin = open(D + 'trends-extra.bin', 'rb').read()
where = {l['title']: i for i, l in enumerate(luts) if l.get('made') == 'Coqueta (estilo)'}
for k, e in enumerate(extra):
    data = ebin[k * per:(k + 1) * per]
    grid = np.frombuffer(data, np.uint8).reshape(S, S, S, 3).astype(np.float32) / 255
    f = measure(grid)
    entry = {'title': e['title'], 'brand': 'creative', 'bw': False, 'f': [round(float(x), 4) for x in f], 'made': 'Coqueta (estilo)', 'extra': e['extra'], 'extra_es': e['extra_es'], 'extra_pt': e['extra_pt']}
    if e['title'] in where:
        i = where[e['title']]; entry['id'] = luts[i]['id']; luts[i] = entry; blobs[i] = data
    else:
        entry['id'] = f'lut{len(luts):03d}'; luts.append(entry); blobs.append(data)
open(D + 'luts.bin', 'wb').write(struct.pack('<II', len(luts), S) + b''.join(blobs))
json.dump(luts, open(D + 'luts.json', 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print(len(luts), 'en total;', ', '.join(f"{l['id']} {l['title']}" for l in luts if l.get('made') == 'Coqueta (estilo)'))

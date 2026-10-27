# Las frases de ejemplo de cada intención → vectores (paraphrase-multilingual-MiniLM-L12-v2, int8, media de los tokens
# y normalizado, igual que transformers.js con pooling «mean» y normalize) → intenciones.json
import json, sys, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
sys.path.insert(0, 'H:/coqueta-studio/intenciones')
from intents import INTENTS
M = 'H:/promptribe-modelos/minilm/'
tok = Tokenizer.from_file(M + 'tokenizer.json')
so = ort.SessionOptions(); so.log_severity_level = 3
s = ort.InferenceSession(M + 'model_quantized.onnx', so, providers=['CPUExecutionProvider'])
names = [i.name for i in s.get_inputs()]
def emb(text):
    e = tok.encode(text); ids = np.array([e.ids], np.int64); am = np.array([e.attention_mask], np.int64)
    feeds = {'input_ids': ids, 'attention_mask': am}
    if 'token_type_ids' in names: feeds['token_type_ids'] = np.zeros_like(ids)
    h = s.run(None, feeds)[0][0]
    v = (h * am[0][:, None]).sum(0) / am[0].sum(); return v / np.linalg.norm(v)
out = {k: {'want': w, 'ex': [[round(float(x), 4) for x in emb(p)] for p in ph]} for k, (ph, w) in INTENTS.items()}
json.dump({'model': 'Xenova/paraphrase-multilingual-MiniLM-L12-v2@2c4055b', 'intents': out}, open('H:/coqueta-studio/intenciones/intenciones.json', 'w'))
# prueba: frases nuevas en varios idiomas
E = [(k, np.array(v['ex'])) for k, v in out.items()]
for q in ['could you brighten it a little', 'necesito que se vea como una película', 'deixa mais quente', 'rends la photo plus nette', 'mach den Hintergrund weg', '背景をぼかして', '让照片更有电影感', 'quiero que parezca sacada con flash en una fiesta', 'the colors are boring', 'hazla para mi perfil de linkedin', 'recórtala para una historia de instagram', 'my skin looks bad', 'la luz es muy amarilla', 'something weird and creative', 'quita el fondo y pon uno blanco']:
    v = emb(q); sc = sorted(((float((m @ v).max()), k) for k, m in E), reverse=True)[:3]
    print(q, '→', ' | '.join(f'{k} {x:.2f}' for x, k in sc))

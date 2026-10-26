# Añade a estilos.json los grupos del entorno (lugar, momento, luz, plano), con el codificador de texto de CLIP
import json, sys, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
sys.path.insert(0, 'H:/coqueta-studio/estilos')
from groups import GROUPS
M = 'H:/promptribe-modelos/clip/'
tok = Tokenizer.from_file(M + 'tokenizer.json')
so = ort.SessionOptions(); so.log_severity_level = 3
s = ort.InferenceSession(M + 'text_model.onnx', so, providers=['CPUExecutionProvider'])
def vec(prompts):
    vs = []
    for p in prompts:
        e = s.run(None, {'input_ids': np.array([tok.encode(p).ids[:77]], np.int64)})[0][0]; vs.append(e / np.linalg.norm(e))
    v = np.mean(vs, 0); v /= np.linalg.norm(v); return [round(float(x), 5) for x in v]
E = json.load(open('estilos.json'))
E['groups'] = {g: {k: vec(p) for k, p in opts.items()} for g, opts in GROUPS.items()}
json.dump(E, open('estilos.json', 'w'))
print({g: list(o) for g, o in E['groups'].items()})

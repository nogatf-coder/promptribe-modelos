# Calcula las frases de cada estilo con el codificador de texto de CLIP ViT-B/16 → estilos.json (media normalizada)
import json, sys, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
sys.path.insert(0, 'H:/coqueta-studio/estilos')
from styles import STYLES
M = 'H:/promptribe-modelos/clip/'
tok = Tokenizer.from_file(M + 'tokenizer.json')
s = ort.InferenceSession(M + 'text_model.onnx', providers=['CPUExecutionProvider'])
out = {}
for k, prompts in STYLES.items():
    vs = []
    for p in prompts:
        ids = tok.encode(p).ids[:77]
        e = s.run(None, {'input_ids': np.array([ids], np.int64)})[0][0]
        vs.append(e / np.linalg.norm(e))
    v = np.mean(vs, 0); v /= np.linalg.norm(v)
    out[k] = [round(float(x), 5) for x in v]
json.dump({'model': 'Xenova/clip-vit-base-patch16@342fdf2', 'scale': 100, 'styles': out}, open('H:/coqueta-studio/estilos/estilos.json', 'w'))
print(len(out), 'estilos', tok.encode('a photo').ids)

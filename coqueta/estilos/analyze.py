# Cada ejemplo → su firma de CLIP ViT-B/16 (la misma que usa el navegador) y sus estadísticas de tono y color.
# Sale datos/analisis.npz: embeddings (N×512), estilo de cada uno, y por imagen cuantiles por canal, saturación,
# contraste y viñeta (luz de las esquinas frente al centro).
import json, os, glob, numpy as np, onnxruntime as ort
from PIL import Image

ROOT = 'H:/coqueta-studio/estilos-aprendidos/datos'
so = ort.SessionOptions(); so.log_severity_level = 3
sess = ort.InferenceSession('H:/promptribe-modelos/clip/vision_model_quantized.onnx', so, providers=['CPUExecutionProvider'])
mean = np.array([0.48145466, 0.4578275, 0.40821073]); std = np.array([0.26862954, 0.26130258, 0.27577711])
Q = [0.02, 0.1, 0.25, 0.5, 0.75, 0.9, 0.98]

def emb(im):
    W, H = im.size; k = 224 / min(W, H)
    im = im.resize((max(224, round(W * k)), max(224, round(H * k))), Image.BICUBIC)
    l, t = (im.width - 224) // 2, (im.height - 224) // 2
    x = (np.asarray(im.crop((l, t, l + 224, t + 224)), np.float32) / 255 - mean) / std
    e = sess.run(None, {'pixel_values': x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    return e / np.linalg.norm(e)

def stats(im):
    a = np.asarray(im.resize((256, round(256 * im.height / im.width)) if im.width >= im.height else (round(256 * im.width / im.height), 256)), np.float32)
    q = np.stack([np.quantile(a[..., c], Q) for c in range(3)])            # 3×7
    mx, mn = a.max(-1), a.min(-1); sat = float(np.mean((mx - mn) / np.maximum(mx, 1)))
    L = a @ [0.299, 0.587, 0.114]; h, w = L.shape
    center = L[h // 3: 2 * h // 3, w // 3: 2 * w // 3].mean()
    corners = np.mean([L[: h // 6, : w // 6].mean(), L[: h // 6, -w // 6:].mean(), L[-h // 6:, : w // 6].mean(), L[-h // 6:, -w // 6:].mean()])
    return q, sat, float(L.std()), float(corners / max(center, 1)), float(np.mean(np.abs(a[..., 0] - a[..., 1]) + np.abs(a[..., 1] - a[..., 2])) < 4)

E, S, QS, SAT, CON, VIG, GRAY, FILES = [], [], [], [], [], [], [], []
for style in sorted(os.listdir(ROOT)):
    for f in sorted(glob.glob(os.path.join(ROOT, style, '*.jpg'))):
        try:
            im = Image.open(f).convert('RGB')
            if min(im.size) < 160: continue
            e = emb(im); q, sat, con, vig, gray = stats(im)
        except Exception as ex:
            print('x', f, ex); continue
        E.append(e); S.append(style); QS.append(q); SAT.append(sat); CON.append(con); VIG.append(vig); GRAY.append(gray); FILES.append(os.path.relpath(f, ROOT))
    print(style, sum(1 for s in S if s == style), flush=True)
np.savez('H:/coqueta-studio/estilos-aprendidos/analisis.npz', E=np.array(E), S=np.array(S), Q=np.array(QS), SAT=np.array(SAT), CON=np.array(CON), VIG=np.array(VIG), GRAY=np.array(GRAY), FILES=np.array(FILES))
print('fin', len(E), flush=True)

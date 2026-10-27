# Lo aprendido de los ejemplos:
# 1) un clasificador de estilos (regresión logística multiclase, numpy) sobre las firmas de CLIP: cuánto se parece una
#    foto a cada estilo. Se mide con un 20 % de ejemplos que no ve al entrenar.
# 2) la receta de color de cada estilo: curvas por canal que llevan los tonos de una foto normal de móvil a los del
#    estilo (cuantiles medianos), saturación y viñeta. Se aplica a medias (el contenido de las fotos también influye).
import json, numpy as np

D = np.load('H:/coqueta-studio/estilos-aprendidos/analisis.npz')
E, S = D['E'], D['S']
MIN = 40
classes = sorted(c for c in set(S) if (S == c).sum() >= MIN)
keep = np.isin(S, classes)
X, y = E[keep], np.array([classes.index(s) for s in S[keep]])
rng = np.random.default_rng(7)

def fit(X, y, C, epochs=600, lr=2.0, l2=1e-3):
    W = np.zeros((C, X.shape[1])); b = np.zeros(C)
    for _ in range(epochs):
        z = X @ W.T + b; z -= z.max(1, keepdims=True); p = np.exp(z); p /= p.sum(1, keepdims=True)
        p[np.arange(len(y)), y] -= 1; p /= len(y)
        W -= lr * (p.T @ X + l2 * W); b -= lr * p.sum(0)
    return W, b

idx = rng.permutation(len(y)); cut = int(len(y) * 0.8)
W, b = fit(X[idx[:cut]], y[idx[:cut]], len(classes))
pred = (X[idx[cut:]] @ W.T + b).argmax(1)
acc = (pred == y[idx[cut:]]).mean()
top2 = np.mean([y[idx[cut:]][i] in np.argsort(-(X[idx[cut:]][i] @ W.T + b))[:2] for i in range(len(pred))])
print(f'precisión con fotos no vistas: {acc:.2f} (entre las 2 primeras: {top2:.2f}); azar = {1 / len(classes):.2f}')
for i, c in enumerate(classes):
    m = y[idx[cut:]] == i
    if m.any(): print(f'  {c:13s} {np.mean(pred[m] == i):.2f}  (n={m.sum()})')
W, b = fit(X, y, len(classes))
head = {'classes': classes, 'W': [[round(float(v), 5) for v in row] for row in W], 'b': [round(float(v), 5) for v in b]}

# 2) recetas de color
Qn = np.median(D['Q'][S == 'neutral'], 0); satn = np.median(D['SAT'][S == 'neutral']); vign = np.median(D['VIG'][S == 'neutral'])
looks = {}
for c in sorted(set(S)):
    if c == 'neutral' or (S == c).sum() < 25: continue
    m = S == c
    Qs = np.median(D['Q'][m], 0); gray = float(np.mean(D['GRAY'][m])) > 0.5
    look = {}
    # el brillo general depende sobre todo de la escena (de noche, de día): se quita el 75 % del desplazamiento medio y
    # se conserva la forma (contraste) y la diferencia entre canales (la dominante de color)
    shift = float(np.mean(Qs - Qn))
    Qs = Qs - 0.75 * shift
    for ch, name in enumerate('rgb'):
        xs, ys = list(Qn[ch]), list(Qs[ch])
        pts = [[0, max(0.0, ys[0] - xs[0] * (ys[1] - ys[0]) / max(1.0, xs[1] - xs[0]))]]
        pts += [[x, y] for x, y in zip(xs, ys)]
        pts.append([255, min(255.0, ys[-1] + (255 - xs[-1]) * (ys[-1] - ys[-2]) / max(1.0, xs[-1] - xs[-2]))])
        # a medias y siempre creciente
        out, last_x, last_y = [], -1, -1
        for x, yv in pts:
            yv = x + float(np.clip(0.6 * (yv - x), -24, 24))
            if x <= last_x + 3: continue
            yv = max(yv, last_y + 0.5); out.append([round(x), round(min(255, max(0, yv)))]); last_x, last_y = x, yv
        look[name] = out
    look['sat'] = 0 if gray else round(float(np.clip(1 + 0.6 * (np.median(D['SAT'][m]) / satn - 1), 0.6, 1.3)), 3)
    look['vignette'] = round(float(np.clip((vign - np.median(D['VIG'][m])) * 0.6, 0, 0.3)), 3)
    if gray: look['gray'] = True
    looks[c] = look
    print(c, 'sat', look['sat'], 'viñeta', look['vignette'], 'gris' if gray else '', 'r', look['r'][3], 'b', look['b'][3])
json.dump({'head': head, 'looks': looks, 'accuracy': round(float(acc), 3)}, open('H:/coqueta-studio/estilos-aprendidos/aprendido.json', 'w'))

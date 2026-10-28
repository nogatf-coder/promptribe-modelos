# Palabras para el buscador de looks (28-10-2026): los nombres de las apps de filtros y de edición rápida, y «foto vieja
# de los 2000», en los looks que se les parecen (en inglés, español y portugués; ver INVESTIGACION-ESTILOS-REDES.md).
# Se añaden a `extra`, `extra_es` y `extra_pt` de luts.json sin repetirlas. Ejecutar después de add_trends.py y
# add_t3mujin.py, y luego describe_index.py y describe_index_i18n.py.
import json

P = 'H:/coqueta-studio/looks/luts.json'
WORDS = {
    # id: (inglés, español, portugués)
    'lut344': ('old photo from the 2000s, early 2000s digital camera photo, nokia, cybershot',
               'foto vieja de los 2000, foto antigua de los años 2000, foto de cámara digital de los dos mil',
               'foto velha dos anos 2000, foto antiga dos anos 2000, foto de câmera digital dos anos 2000'),
    'lut345': ('huji, dazz, dispo app, disposable camera app', 'huji, dazz, app dispo, app de cámara desechable', 'huji, dazz, app dispo, app de câmera descartável'),
    'lut341': ('retrica selfie filter, tumblr selfie', 'filtro de selfie de retrica, selfie de tumblr', 'filtro de selfie do retrica, selfie do tumblr'),
    'lut347': ('b612, snow app, meitu, lemon8, asian selfie app filter', 'b612, snow, meitu, lemon8, filtro de app asiática de selfies', 'b612, snow, meitu, lemon8, filtro de app asiático de selfies'),
    'lut348': ('b612, snow app, soft japanese selfie app', 'b612, snow, app de selfies japonesa suave', 'b612, snow, app de selfies japonês suave'),
    'lut350': ('lemon8 lifestyle, minimal feed', 'lemon8, estilo de vida, feed minimalista', 'lemon8, estilo de vida, feed minimalista'),
    'lut334': ('lightroom preset bright and airy', 'preset de lightroom claro y aireado', 'preset do lightroom claro e arejado'),
    'lut335': ('moody lightroom preset', 'preset de lightroom moody oscuro', 'preset do lightroom moody escuro'),
    'lut342': ('picsart filter, warm vsco filter', 'filtro de picsart, filtro cálido de vsco', 'filtro do picsart, filtro quente do vsco'),
    'lut351': ('snapseed drama, hdr scape, punchy detail', 'snapseed drama, hdr, mucho detalle y fuerza', 'snapseed drama, hdr, muito detalhe e força'),
    'lut193': ('hipstamatic, iphone toy camera app', 'hipstamatic, app de cámara de juguete del iphone', 'hipstamatic, app de câmera de brinquedo do iphone'),
    'lut294': ('afterlight film filter, light leaks and dust', 'filtro de película de afterlight, fugas de luz y polvo', 'filtro de filme do afterlight, vazamentos de luz e poeira'),
    'lut206': ('polaroid instant photo', 'foto instantánea polaroid', 'foto instantânea polaroid'),
    'lut106': ('fujifilm instax instant photo', 'foto instantánea instax de fujifilm', 'foto instantânea instax da fujifilm'),
}
L = json.load(open(P, encoding='utf-8'))
by = {l['id']: l for l in L}
for id, words in WORDS.items():
    l = by[id]
    for key, w in zip(('extra', 'extra_es', 'extra_pt'), words):
        cur = l.get(key, '')
        if w not in cur: l[key] = (cur + ', ' + w) if cur else w
json.dump(L, open(P, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print(len(WORDS), 'looks con palabras de apps')

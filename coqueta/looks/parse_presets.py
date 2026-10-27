# Los ajustes de Lightroom (.lrtemplate, formato Lua) → recetas normalizadas (presets.json)
import os, re, json, glob, hashlib

ROOT = 'H:/coqueta-studio/looks/src/alp_x'
HUES = ['Red', 'Orange', 'Yellow', 'Green', 'Aqua', 'Blue', 'Purple', 'Magenta']
NUM = re.compile(r'^\s*(\w+)\s*=\s*(-?[\d.]+)\s*,?\s*$')
BOOL = re.compile(r'^\s*(\w+)\s*=\s*(true|false)\s*,?\s*$')
STR = re.compile(r'^\s*(\w+)\s*=\s*"([^"]*)"\s*,?\s*$')

def curve(text, name):
    m = re.search(name + r'\s*=\s*\{([^}]*)\}', text)
    if not m: return None
    v = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', m.group(1))]
    pts = [[v[i], v[i + 1]] for i in range(0, len(v) - 1, 2)]
    return pts if len(pts) >= 2 else None

out, seen = [], set()
for f in glob.glob(ROOT + '/**/*.lrtemplate', recursive=True):
    try: text = open(f, encoding='utf-8', errors='ignore').read()
    except Exception: continue
    if 'settings' not in text: continue
    v, b, st = {}, {}, {}
    for line in text.splitlines():
        m = NUM.match(line)
        if m: v[m.group(1)] = float(m.group(2)); continue
        m = BOOL.match(line)
        if m: b[m.group(1)] = m.group(2) == 'true'; continue
        m = STR.match(line)
        if m: st[m.group(1)] = m.group(2)
    g = lambda k, d=0.0: v.get(k + '2012', v.get(k, d))
    p = {
        'exposure': g('Exposure'), 'contrast': g('Contrast'), 'highlights': g('Highlights'), 'shadows': g('Shadows'),
        'whites': g('Whites'), 'blacks': g('Blacks'), 'clarity': g('Clarity'), 'dehaze': v.get('Dehaze', 0.0),
        'vibrance': v.get('Vibrance', 0.0), 'saturation': v.get('Saturation', 0.0),
        'temp': v.get('IncrementalTemperature', 0.0), 'tint': v.get('IncrementalTint', 0.0),
        'pShadows': v.get('ParametricShadows', 0.0), 'pDarks': v.get('ParametricDarks', 0.0), 'pLights': v.get('ParametricLights', 0.0), 'pHighlights': v.get('ParametricHighlights', 0.0),
        'splitSH': v.get('SplitToningShadowHue', 0.0), 'splitSS': v.get('SplitToningShadowSaturation', 0.0),
        'splitHH': v.get('SplitToningHighlightHue', 0.0), 'splitHS': v.get('SplitToningHighlightSaturation', 0.0), 'splitBal': v.get('SplitToningBalance', 0.0),
        'vignette': v.get('PostCropVignetteAmount', 0.0), 'vignetteMid': v.get('PostCropVignetteMidpoint', 50.0),
        'grain': v.get('GrainAmount', 0.0), 'grainSize': v.get('GrainSize', 25.0),
        'gray': bool(b.get('ConvertToGrayscale', False)),
        'hsl': {h: [v.get(h + 'Hue', v.get('HueAdjustment' + h, 0.0)), v.get(h + 'Saturation', v.get('SaturationAdjustment' + h, 0.0)), v.get(h + 'Luminance', v.get('LuminanceAdjustment' + h, 0.0))] for h in HUES},
        'mix': {h: v.get('GrayMixer' + h, 0.0) for h in HUES},
    }
    # Temperatura absoluta (Kelvin) en algunos ajustes: se pasa a un desplazamiento aproximado respecto a 5500 K
    if 'Temperature' in v and not p['temp']: p['temp'] = max(-100, min(100, (v['Temperature'] - 5500) / 45))
    if 'Tint' in v and not p['tint']: p['tint'] = max(-100, min(100, v['Tint']))
    for name, key in [('ToneCurvePV2012', 'curve'), ('ToneCurvePV2012Red', 'curveR'), ('ToneCurvePV2012Green', 'curveG'), ('ToneCurvePV2012Blue', 'curveB')]:
        c = curve(text, name)
        if c and not (len(c) == 2 and c[0] == [0, 0] and c[1] == [255, 255]): p[key] = c
    title = st.get('title') or os.path.basename(f)[:-11]
    sig = hashlib.md5(json.dumps(p, sort_keys=True).encode()).hexdigest()
    if sig in seen: continue
    seen.add(sig)
    coll = os.path.relpath(f, ROOT).split(os.sep)[0]
    out.append({'title': title, 'collection': coll, 'p': p})
json.dump(out, open('H:/coqueta-studio/looks/presets.json', 'w'), indent=0)
print(len(out), 'recetas distintas')
import collections
print(collections.Counter(o['collection'] for o in out).most_common())
nz = lambda k: sum(1 for o in out if abs(o['p'].get(k, 0) if not isinstance(o['p'].get(k), (list, dict, bool)) else 0) > 0.001)
for k in ['exposure', 'contrast', 'highlights', 'shadows', 'whites', 'blacks', 'clarity', 'dehaze', 'vibrance', 'saturation', 'temp', 'tint', 'splitSS', 'splitHS', 'vignette', 'grain']: print(k, nz(k))
print('curva', sum(1 for o in out if 'curve' in o['p']), 'curvas RGB', sum(1 for o in out if 'curveR' in o['p']), 'B/N', sum(1 for o in out if o['p']['gray']))

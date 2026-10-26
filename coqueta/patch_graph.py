# BiRefNet lite → grafo que cabe en cualquier tarjeta con WebGPU (máx. 8 búferes por paso: Concat de ≤7 entradas y
# Split → Slice), con los pesos grandes apuntando a su sitio dentro del archivo original de Hugging Face.
import onnx, sys, numpy as np
from onnx import helper, numpy_helper, TensorProto
src, out, location = sys.argv[1], sys.argv[2], sys.argv[3]
raw = open(src, 'rb').read()
m = onnx.load(src)
g = m.graph
consts = {}
for n in g.node:
    if n.op_type == 'Constant':
        for a in n.attribute:
            if a.name == 'value': consts[n.output[0]] = numpy_helper.to_array(a.t)
for i in g.initializer: consts.setdefault(i.name, None)
init_arr = {i.name: i for i in g.initializer}
def const_val(name):
    if name in init_arr: return numpy_helper.to_array(init_arr[name])
    return consts.get(name)
new_nodes, extra_inits, k = [], [], [0]
def uniq(p):
    k[0] += 1; return f'{p}__cq{k[0]}'
def i64(name, vals):
    t = numpy_helper.from_array(np.array(vals, dtype=np.int64), name); extra_inits.append(t); return name
MAXIN = 7
for n in g.node:
    if n.op_type == 'Concat' and len(n.input) > MAXIN:
        axis = [a.i for a in n.attribute if a.name == 'axis'][0]
        ins = list(n.input)
        while len(ins) > MAXIN:
            nxt = []
            for j in range(0, len(ins), MAXIN):
                grp = ins[j:j + MAXIN]
                if len(grp) == 1: nxt.append(grp[0]); continue
                o = uniq(n.output[0])
                new_nodes.append(helper.make_node('Concat', grp, [o], axis=axis, name=uniq(n.name or 'concat')))
                nxt.append(o)
            ins = nxt
        new_nodes.append(helper.make_node('Concat', ins, list(n.output), axis=axis, name=n.name))
    elif n.op_type == 'Split' and len(n.output) > MAXIN - 1:
        axis = [a.i for a in n.attribute if a.name == 'axis'][0]
        sizes = const_val(n.input[1])
        assert sizes is not None, n.name
        start = 0
        ax = i64(uniq('axes'), [axis])
        for o, s in zip(n.output, sizes.tolist()):
            st = i64(uniq('st'), [start]); en = i64(uniq('en'), [start + s])
            new_nodes.append(helper.make_node('Slice', [n.input[0], st, en, ax], [o], name=uniq(n.name or 'slice')))
            start += s
    else:
        new_nodes.append(n)
# constantes grandes → pesos (para poder dejarlos fuera del grafo)
final = []
for n in new_nodes:
    if n.op_type == 'Constant':
        val = [a.t for a in n.attribute if a.name == 'value']
        if val and len(val[0].raw_data) >= 4096:
            t = onnx.TensorProto(); t.CopyFrom(val[0]); t.name = n.output[0]; extra_inits.append(t); continue
    final.append(n)
new_nodes = final
del g.node[:]
g.node.extend(new_nodes)
g.initializer.extend(extra_inits)
# pesos grandes: fuera del grafo, apuntando a su posición en el archivo original
pos, moved, kept = 0, 0, 0
for t in g.initializer:
    if not t.raw_data or len(t.raw_data) < 4096: kept += 1; continue
    off = raw.find(t.raw_data, pos)
    if off < 0: off = raw.find(t.raw_data)
    assert off >= 0, t.name
    pos = off + len(t.raw_data)
    ln = len(t.raw_data)
    t.ClearField('raw_data')
    t.data_location = TensorProto.EXTERNAL
    del t.external_data[:]
    for key, val in (('location', location), ('offset', str(off)), ('length', str(ln))):
        e = t.external_data.add(); e.key = key; e.value = val
    moved += 1
onnx.save(m, out)
print('movidos', moved, 'dentro', kept, 'nodos', len(g.node))

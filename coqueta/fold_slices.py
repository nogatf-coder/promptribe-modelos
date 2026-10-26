# Los Slice con límites calculados en la ejecución (salen de Shape→…→Unsqueeze) fallan en ONNX Runtime con WebGPU;
# con la entrada fija de 1024×1024 esos valores son siempre los mismos: se calculan una vez y se fijan en el grafo.
import onnx, onnxruntime as ort, numpy as np, sys, collections
from onnx import numpy_helper, helper
ref, targets = sys.argv[1], sys.argv[2:]
def dyn_slices(g):
    const = {i.name for i in g.initializer} | {n.output[0] for n in g.node if n.op_type == 'Constant'}
    return [(n, [x for x in n.input[1:] if x and x not in const]) for n in g.node if n.op_type == 'Slice']
m = onnx.load(ref)
names = sorted({x for n, d in dyn_slices(m.graph) for x in d})
for nm in names: m.graph.output.append(helper.make_tensor_value_info(nm, onnx.TensorProto.INT64, None))
onnx.save(m, 'tmp_ref.onnx')
so = ort.SessionOptions(); so.log_severity_level = 3
s = ort.InferenceSession('tmp_ref.onnx', so, providers=['CPUExecutionProvider'])
x = np.zeros((1, 3, 1024, 1024), np.float32)
vals = dict(zip([o.name for o in s.get_outputs()], s.run(None, {'input_image': x})))
print({k: vals[k].tolist() for k in names[:4]}, len(names))
for t in targets:
    m = onnx.load(t, load_external_data=False)
    have = {i.name for i in m.graph.initializer}
    for nm in names:
        if nm not in have: m.graph.initializer.append(numpy_helper.from_array(vals[nm].astype(np.int64), nm))
    # quitar lo que ya no usa nadie (la cadena Shape→Unsqueeze de esos valores)
    g = m.graph
    for _ in range(20):
        used = {i for n in g.node for i in n.input} | {o.name for o in g.output}
        keep = [n for n in g.node if any(o in used for o in n.output) or not n.output]
        prod = {o for n in keep for o in n.output}
        keep = [n for n in keep if not (set(n.output) & set(names))]
        if len(keep) == len(g.node): break
        del g.node[:]; g.node.extend(keep)
    print(t, 'dinámicos', len([1 for n, d in dyn_slices(g) if d]), 'nodos', len(g.node))
    onnx.save(m, t)

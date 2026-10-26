# Todo Split → Slice (la versión WebGPU no tiene Split para todos los casos y lo mandaba a la CPU).
import onnx, sys, numpy as np
from onnx import helper, numpy_helper
for t in sys.argv[1:]:
    m = onnx.load(t, load_external_data=False)
    g = m.graph
    cv = {i.name: i for i in g.initializer}
    cn = {n.output[0]: n for n in g.node if n.op_type == 'Constant'}
    def val(name):
        if name in cv: return numpy_helper.to_array(cv[name])
        if name in cn: return numpy_helper.to_array([a.t for a in cn[name].attribute if a.name == 'value'][0])
    out, inits, k = [], [], 0
    for n in g.node:
        if n.op_type != 'Split': out.append(n); continue
        axis = ([a.i for a in n.attribute if a.name == 'axis'] or [0])[0]
        sizes = val(n.input[1]) if len(n.input) > 1 and n.input[1] else None
        assert sizes is not None, n.name
        start = 0; k += 1; p = f'/cq_split{k}'
        inits.append(numpy_helper.from_array(np.array([axis], np.int64), p + '_ax'))
        for j, (o, s) in enumerate(zip(n.output, sizes.tolist())):
            inits += [numpy_helper.from_array(np.array([start], np.int64), f'{p}_s{j}'), numpy_helper.from_array(np.array([start + s], np.int64), f'{p}_e{j}')]
            out.append(helper.make_node('Slice', [n.input[0], f'{p}_s{j}', f'{p}_e{j}', p + '_ax'], [o], name=f'{p}_{j}'))
            start += s
    del g.node[:]; g.node.extend(out); g.initializer.extend(inits)
    onnx.save(m, t); print(t, 'Split → Slice', k)

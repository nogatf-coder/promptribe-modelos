# Sum (n entradas) no tiene versión en la tarjeta con ONNX Runtime WebGPU y se iría a la CPU con tensores de cientos de
# MB (la convolución deformable): se rehace como sumas de dos en dos (Add), que sí corren en la tarjeta.
import onnx, sys
from onnx import helper
for t in sys.argv[1:]:
    m = onnx.load(t, load_external_data=False)
    out, k = [], 0
    for n in m.graph.node:
        if n.op_type != 'Sum' or len(n.input) < 2: out.append(n); continue
        ins = list(n.input)
        while len(ins) > 2:
            nxt = []
            for j in range(0, len(ins) - 1, 2):
                k += 1; o = f'/cq_sum{k}'
                out.append(helper.make_node('Add', [ins[j], ins[j + 1]], [o], name=o)); nxt.append(o)
            if len(ins) % 2: nxt.append(ins[-1])
            ins = nxt
        out.append(helper.make_node('Add', ins, list(n.output), name=n.name))
    del m.graph.node[:]; m.graph.node.extend(out)
    onnx.save(m, t); print(t, 'sumas', k)

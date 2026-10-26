# GatherND (batch_dims=2, datos [1,1,H,W,C], índices [1,1,N,2]) falla en ONNX Runtime con WebGPU: se rehace como
# Gather sobre los datos aplanados [H·W, C] con el índice lineal y·W + x (calculado en coma flotante: exacto hasta 2^24).
import onnx, onnxruntime as ort, numpy as np, sys
from onnx import helper, numpy_helper, TensorProto
ref, targets = sys.argv[1], sys.argv[2:]
m = onnx.load(ref, load_external_data=False)
ns = [n for n in m.graph.node if n.op_type == 'GatherND']
for n in ns: m.graph.output.append(onnx.ValueInfoProto(name=n.input[0]))
onnx.save(m, 'tmp_g.onnx')
so = ort.SessionOptions(); so.log_severity_level = 3
s = ort.InferenceSession('tmp_g.onnx', so, providers=['CPUExecutionProvider'])
v = dict(zip([o.name for o in s.get_outputs()], s.run(None, {'input_image': np.random.rand(1, 3, 1024, 1024).astype(np.float32)})))
shapes = {n.name: v[n.input[0]].shape for n in ns}
for t in targets:
    m = onnx.load(t, load_external_data=False)
    g = m.graph
    out, inits, k = [], [], 0
    for n in g.node:
        if n.op_type != 'GatherND': out.append(n); continue
        b0, b1, H, W, C = shapes[n.name]
        assert b0 == 1 and b1 == 1, shapes[n.name]
        k += 1; p = f'/cq_gnd{k}'
        inits += [numpy_helper.from_array(np.array([H * W, C], np.int64), p + '_dshape'),
                  numpy_helper.from_array(np.array([[W], [1]], np.float32), p + '_stride'),
                  numpy_helper.from_array(np.array([1, 1, -1], np.int64), p + '_ishape')]
        out += [helper.make_node('Reshape', [n.input[0], p + '_dshape'], [p + '_data'], name=p + '_r1'),
                helper.make_node('Cast', [n.input[1]], [p + '_f'], to=TensorProto.FLOAT, name=p + '_c1'),
                helper.make_node('MatMul', [p + '_f', p + '_stride'], [p + '_lin'], name=p + '_mm'),
                helper.make_node('Cast', [p + '_lin'], [p + '_li'], to=TensorProto.INT32, name=p + '_c2'),
                helper.make_node('Reshape', [p + '_li', p + '_ishape'], [p + '_idx'], name=p + '_r2'),
                helper.make_node('Gather', [p + '_data', p + '_idx'], list(n.output), axis=0, name=p + '_g')]
    del g.node[:]; g.node.extend(out); g.initializer.extend(inits)
    onnx.save(m, t)
    print(t, 'GatherND rehechos', k)

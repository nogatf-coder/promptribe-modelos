import json, sys, numpy as np, onnxruntime as ort
from PIL import Image
A=json.load(open('H:/coqueta-studio/estilos/estetica.json')); w=np.array(A['w']); b=A['b']
so=ort.SessionOptions(); so.log_severity_level=3
s=ort.InferenceSession('H:/promptribe-modelos/clip/vision_model_quantized.onnx', so, providers=['CPUExecutionProvider'])
mean=np.array([0.48145466,0.4578275,0.40821073]); std=np.array([0.26862954,0.26130258,0.27577711])
def emb(im):
    im=im.convert('RGB'); W,H=im.size; k=224/min(W,H); im=im.resize((max(224,round(W*k)),max(224,round(H*k))),Image.BICUBIC)
    l,t=(im.width-224)//2,(im.height-224)//2; x=(np.asarray(im.crop((l,t,l+224,t+224)),np.float32)/255-mean)/std
    e=s.run(None,{'pixel_values':x.transpose(2,0,1)[None].astype(np.float32)})[0][0]; return e/np.linalg.norm(e)
for f in sys.argv[1:]:
    print(f.split('/')[-1], round(float(emb(Image.open(f))@w+b),2))

# Modelos de MyPrompTribe

Archivos de modelos que usan las herramientas de [MyPrompTribe](https://www.mypromptribe.com) **en el navegador de cada persona**. Todo se ejecuta en su dispositivo: no hay servidor de IA ni se suben fotos.

## `remix/`: fusión con IA de «Remix»

| Archivo | Qué es | Origen y licencia |
| --- | --- | --- |
| `transformer-hf.onnx` | Solo el «mapa» (grafo) del transformer de FLUX.2 [klein] 4B cuantizado a 4 bits, con los pesos apuntando a trozos del archivo original. El navegador descarga esos trozos directamente de Hugging Face. | Derivado de [danyalmalik/FLUX.2-klein-4B-ONNX-WebGPU](https://huggingface.co/danyalmalik/FLUX.2-klein-4B-ONNX-WebGPU) (Apache-2.0), basado en [black-forest-labs/FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) (Apache-2.0). Ningún valor cambia: solo dónde se lee cada tensor. |
| `prompts/*.bin` | Órdenes de texto ya calculadas (rasgos de Qwen3-4B, capas 9/18/27, float16, 512 × 7680) para cada estilo (natural o cinematográfico), color de luz (cálida, fría o neutra) y dirección (detrás, izquierda, derecha o arriba). Así el navegador no necesita el modelo de texto. | Calculadas con el codificador de texto de [cgb/flux2-klein-4b-onnx-webgpu](https://huggingface.co/cgb/flux2-klein-4b-onnx-webgpu) (Apache-2.0). Los textos están en `prompts/prompts.json`. |

El codificador y el decodificador de imagen se descargan directamente de [cgb/flux2-klein-4b-onnx-webgpu](https://huggingface.co/cgb/flux2-klein-4b-onnx-webgpu).

## `coqueta/`: borde fino del recorte de «Coqueta Foto»

| Archivo | Qué es | Origen y licencia |
| --- | --- | --- |
| `birefnet-lite-fp16-cq.onnx`, `birefnet-lite-cq.onnx` | Solo el «mapa» (grafo) de BiRefNet lite (media precisión y completa). Los pasos que unen o parten muchos tensores a la vez (Concat de hasta 1024 entradas, Split de hasta 32 salidas) se rehacen en pasos de 7 como máximo, para que quepan en cualquier tarjeta con WebGPU (muchas solo dejan 8 búferes por paso). Los pesos apuntan a su posición dentro de `model_fp16.onnx` / `model.onnx` originales, que el navegador descarga directamente de Hugging Face. Ningún peso cambia: el resultado es idéntico. | Derivado de [onnx-community/BiRefNet_lite-ONNX](https://huggingface.co/onnx-community/BiRefNet_lite-ONNX) (revisión `de15b22`), de [ZhengPeng7/BiRefNet](https://github.com/ZhengPeng7/BiRefNet) (MIT, © 2024 ZhengPeng). |
| `patch_graph.py` | El guion que rehace el grafo (`python patch_graph.py model_fp16.onnx salida.onnx model_fp16.onnx`). | MIT |

Licencia: Apache-2.0 (ver `LICENSE`), la misma de los modelos de origen; lo de `coqueta/` es MIT, como BiRefNet (ver `coqueta/LICENSE-BiRefNet`).

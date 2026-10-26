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
| `birefnet-lite-fp16-cq.onnx`, `birefnet-lite-cq.onnx` | Solo el «mapa» (grafo) de BiRefNet lite (media precisión y completa), rehecho para que corra entero en la tarjeta con ONNX Runtime WebGPU en cualquier equipo: Concat de hasta 1024 entradas → pasos de 7 como máximo (muchas tarjetas solo dejan 8 búferes por paso); Split → Slice; GatherND (falla en WebGPU) → Gather con el índice lineal; Sum → Add (si no, la convolución deformable se iba a la CPU con cientos de MB); y los límites de 24 Slice, que dependían de la forma, fijados para la entrada de 1024×1024. Los pesos apuntan a su posición dentro de `model_fp16.onnx` / `model.onnx` originales, que el navegador descarga directamente de Hugging Face. Ningún peso cambia: el resultado es idéntico (diferencia 0 comprobada con ONNX Runtime). | Derivado de [onnx-community/BiRefNet_lite-ONNX](https://huggingface.co/onnx-community/BiRefNet_lite-ONNX) (revisión `de15b22`), de [ZhengPeng7/BiRefNet](https://github.com/ZhengPeng7/BiRefNet) (MIT, © 2024 ZhengPeng). |
| `estilos/estilos.json` | Qué estilo o escena es una foto (urbano, noche en la ciudad, neón, playa, desierto…): para cada uno, la media de las frases de `estilos/styles.py` pasadas por el codificador de texto de CLIP ViT-B/16 (vectores de 512, normalizados). El navegador solo ejecuta la parte de imagen de CLIP y compara. Se calculan con `estilos/embed.py`. | [openai/clip-vit-base-patch16](https://huggingface.co/openai/clip-vit-base-patch16) (MIT) en ONNX de [Xenova/clip-vit-base-patch16](https://huggingface.co/Xenova/clip-vit-base-patch16). |
| `patch_graph.py`, `fold_slices.py`, `fix_gathernd.py`, `fix_sum.py`, `fix_split.py` | Los guiones que rehacen el grafo, en ese orden. | MIT |

Licencia: Apache-2.0 (ver `LICENSE`), la misma de los modelos de origen; lo de `coqueta/` es MIT, como BiRefNet (ver `coqueta/LICENSE-BiRefNet`).

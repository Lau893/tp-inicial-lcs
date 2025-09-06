Modelo ONNX para embeddings faciales

Colocá aquí el archivo del modelo ONNX que se usará en el navegador para calcular los embeddings.

Ruta esperada por defecto (configurable):
- /model/face_embedder.onnx

Sugerencias de modelos
- MobileFaceNet / SFace u otro backbone de reconocimiento facial que reciba 112x112 RGB y devuelva un vector 1xN.
- La normalización aplicada en el frontend es (x/127.5 - 1.0) y luego normalización L2 del vector de salida.

Cómo usar
1) Copiá el modelo como `face_embedder.onnx` dentro de esta carpeta.
2) Volvé a construir el servicio Admin:
   - `docker compose -f ../docker-compose.dev.yml build admin`
   - `docker compose -f ../docker-compose.dev.yml up -d admin`
3) Abrí http://localhost:5173 → pestaña “Registrar Rostro” → Iniciar cámara → Capturar y Registrar.

Config avanzada
- Si querés usar otra ruta o nombre, editá `window.CONFIG.MODEL_URL` en `../index.html`.


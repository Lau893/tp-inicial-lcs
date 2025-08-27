from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import numpy as np

import database
import face_utils

app = FastAPI(
    title="API de Reconocimiento Facial de Empleados",
    description="Permite registrar y reconocer empleados a través de sus rostros.",
    version="1.0.0"
)

@app.post("/registrar")
async def registrar_empleado(
    id_empleado: int = Form(...),
    file: UploadFile = File(...)
):
    """
    Registra el rostro de un empleado en la base de datos.

    - **id_empleado**: ID numérico del empleado existente en la tabla `empleado`.
    - **file**: Archivo de imagen (JPG, PNG) con un único rostro visible.
    """
    # Leer el contenido del archivo
    file_content = await file.read()
    
    # Extraer el embedding facial de la imagen
    embedding = face_utils.extraer_embedding_facial(file_content)
    
    if embedding is None:
        raise HTTPException(status_code=400, detail="No se pudo detectar un único rostro en la imagen.")
        
    # Guardar el embedding en la base de datos
    exito = database.guardar_embedding(id_empleado, embedding)
    
    if not exito:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar el embedding. Verifique que el empleado con ID {id_empleado} exista.")
        
    return JSONResponse(
        status_code=201,
        content={"mensaje": f"Rostro del empleado con ID {id_empleado} registrado exitosamente."}
    )

@app.post("/reconocer")
async def reconocer_empleado(file: UploadFile = File(...)):
    """
    Reconoce a un empleado a partir de una imagen.

    - **file**: Archivo de imagen (JPG, PNG) con un rostro para identificar.
    """
    # Leer el contenido del archivo
    file_content = await file.read()
    
    # Extraer el embedding de la cara en la imagen subida
    embedding_a_reconocer = face_utils.extraer_embedding_facial(file_content)
    
    if embedding_a_reconocer is None:
        raise HTTPException(status_code=400, detail="No se pudo detectar un único rostro en la imagen.")
        
    # Obtener todos los embeddings de la base de datos
    embeddings_conocidos = database.obtener_todos_los_embeddings()
    if not embeddings_conocidos:
        raise HTTPException(status_code=404, detail="No hay rostros registrados en la base de datos.")
        
    # Separar los IDs de los embeddings
    ids_empleados, lista_embeddings = zip(*embeddings_conocidos)
    
    # Comparar el rostro subido con todos los rostros en la DB
    coincidencias = face_utils.comparar_rostros(embedding_a_reconocer, list(lista_embeddings))
    
    # Buscar el primer índice donde haya una coincidencia (True)
    for i, es_coincidencia in enumerate(coincidencias):
        if es_coincidencia:
            id_reconocido = ids_empleados[i]
            # Aquí podrías registrar la asistencia
            return JSONResponse(content={"reconocido": True, "id_empleado": id_reconocido})
            
    return JSONResponse(content={"reconocido": False, "id_empleado": None})

@app.get("/")
def root():
    return {"mensaje": "API de Reconocimiento Facial funcionando. Visita /docs para la documentación interactiva."}

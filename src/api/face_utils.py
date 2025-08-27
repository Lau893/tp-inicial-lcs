import face_recognition
import numpy as np
from PIL import Image
import io

def extraer_embedding_facial(file_content: bytes) -> np.ndarray | None:
    """
    Carga una imagen desde contenido en bytes, detecta una cara y 
    retorna su embedding facial de 128 dimensiones.
    Retorna None si no se detectan caras o si hay más de una.
    """
    try:
        # Cargar la imagen desde el contenido en bytes
        image = face_recognition.load_image_file(io.BytesIO(file_content))
        
        # Localizar las caras en la imagen
        face_locations = face_recognition.face_locations(image)
        
        # Se espera una única cara en la imagen para el registro
        if len(face_locations) != 1:
            print(f"Se encontraron {len(face_locations)} caras. Se esperaba 1.")
            return None
            
        # Generar el embedding para la cara encontrada
        face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
        
        return face_encodings[0]
        
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return None

def comparar_rostros(embedding_conocido: np.ndarray, embeddings_desconocidos: list[np.ndarray]) -> np.ndarray:
    """
    Compara un embedding facial conocido con una lista de embeddings desconocidos.
    """
    return face_recognition.compare_faces(embeddings_desconocidos, embedding_conocido)

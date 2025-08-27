import sqlite3
import numpy as np
import json
from pathlib import Path

# Construye la ruta dinámicamente.
# __file__ -> .../labo/src/api/database.py
# .parent -> .../labo/src/api
# .parent -> .../labo/src
# .parent -> .../labo/ (Raíz del proyecto)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = PROJECT_ROOT / "data" / "gestion_produccion.db"

def get_db_connection():
    """Crea y retorna una conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def guardar_embedding(id_empleado: int, embedding: np.ndarray):
    """Guarda un embedding facial en la base de datos."""
    conn = get_db_connection()
    # Convertir el array de numpy a una lista y luego a un string JSON
    embedding_json = json.dumps(embedding.tolist())
    try:
        conn.execute(
            "INSERT INTO embedding (id_empleado, embedding_data) VALUES (?, ?)",
            (id_empleado, embedding_json),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error de integridad: Es posible que el id_empleado {id_empleado} no exista. Detalle: {e}")
        return False
    finally:
        conn.close()
    return True

def obtener_todos_los_embeddings() -> list[tuple[int, np.ndarray]]:
    """Obtiene todos los embeddings de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_empleado, embedding_data FROM embedding")
    embeddings = []
    for row in cursor.fetchall():
        id_empleado = row[0]
        # Convertir el string JSON de vuelta a un array de numpy
        embedding_array = np.array(json.loads(row[1]))
        embeddings.append((id_empleado, embedding_array))
    conn.close()
    return embeddings
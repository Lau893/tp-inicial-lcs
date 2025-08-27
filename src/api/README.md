# API de Reconocimiento Facial

Esta API proporciona los endpoints necesarios para registrar y reconocer empleados a través de imágenes faciales, generando y comparando embeddings de 128 dimensiones.

---

## Requisitos Previos

*   Python 3.8+
*   Un entorno virtual de Python (recomendado).

## Instalación

1.  **Clonar/Descargar el Proyecto:**
    Asegúrate de tener todos los archivos del proyecto en tu máquina.

2.  **Navegar a la Raíz del Proyecto:**
    Abre una terminal en la carpeta principal del proyecto (la que contiene `requirements.txt`).

3.  **Crear y Activar un Entorno Virtual:**
    ```bash
    # Crear el entorno (solo se hace una vez)
    python -m venv venv

    # Activar en Windows
    venv\Scripts\activate

    # Activar en macOS/Linux
    # source venv/bin/activate
    ```

4.  **Instalar Dependencias:**
    Con el entorno activado, instala todas las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

---

## Ejecución

1.  **Navegar al Directorio de la API:**
    Desde la raíz del proyecto, muévete a la carpeta `src/api`.
    ```bash
    cd src/api
    ```

2.  **Iniciar el Servidor:**
    Ejecuta el siguiente comando para iniciar el servidor web Uvicorn.
    ```bash
    uvicorn main:app --reload
    ```
    *   **`uvicorn`**: Es el servidor ASGI que ejecuta la aplicación.
    *   **`main:app`**: Le indica a Uvicorn que debe buscar el objeto `app` dentro del archivo `main.py`.
    *   **`--reload`**: Activa la recarga automática del servidor cada vez que se detecta un cambio en el código, muy útil para el desarrollo.

3.  **Acceder a la API:**
    Una vez que el servidor esté en funcionamiento, la API estará disponible en [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Uso y Pruebas

La forma más sencilla de probar los endpoints es a través de la documentación interactiva (Swagger UI) que FastAPI genera automáticamente.

*   **URL de la Documentación:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Endpoints Principales

*   `POST /registrar`
    *   **Acción:** Registra el rostro de un empleado. 
    *   **Parámetros:** Recibe un `id_empleado` y un archivo de imagen (`file`).
    *   **Proceso:** Genera un embedding facial de la imagen y lo almacena en la base de datos, asociándolo al `id_empleado`.

*   `POST /reconocer`
    *   **Acción:** Reconoce a un empleado a partir de una imagen.
    *   **Parámetros:** Recibe un archivo de imagen (`file`).
    *   **Proceso:** Genera un embedding de la imagen proporcionada y lo compara con todos los embeddings almacenados en la base de datos para encontrar una coincidencia.

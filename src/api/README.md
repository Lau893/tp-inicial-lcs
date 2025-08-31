# API de Reconocimiento Facial

Esta API proporciona los endpoints necesarios para registrar y reconocer empleados a través de imágenes faciales, generando y comparando embeddings de 128 dimensiones a partir de una base de datos SQLite.

---

## Contexto de Ejecución

**Nota Importante:** Esta API no está diseñada para ser ejecutada de forma independiente. Es un servicio que forma parte de una arquitectura multi-contenedor orquestada por Docker Compose.

Para levantar la aplicación completa (incluyendo el frontend y esta API), por favor, consulta las instrucciones en el archivo `README.md` ubicado en la raíz del proyecto.

---

## Endpoints de la API

Una vez que la aplicación completa está en ejecución, la documentación interactiva de la API (Swagger UI) está disponible en la siguiente URL:

-   **URL:** [http://localhost:8000/docs](http://localhost:8000/docs)

### `POST /registrar`

-   **Acción:** Registra el rostro de un empleado.
-   **Parámetros:**
    -   `id_empleado` (Form data): ID numérico del empleado existente en la tabla `empleado`.
    -   `file` (File): Archivo de imagen (JPG, PNG) con un único rostro visible.
-   **Proceso:** Genera un embedding facial de la imagen y lo almacena en la base de datos, asociándolo al `id_empleado`.
-   **Respuesta Exitosa:** `201 Created`

### `POST /reconocer`

-   **Acción:** Reconoce a un empleado a partir de una imagen.
-   **Parámetros:**
    -   `file` (File): Archivo de imagen (JPG, PNG) con un rostro para identificar.
-   **Proceso:** Genera un embedding de la imagen proporcionada y lo compara con todos los embeddings almacenados en la base de datos para encontrar una coincidencia.
-   **Respuesta Exitosa:** `200 OK` con un cuerpo JSON que indica si fue reconocido y el `id_empleado` correspondiente.

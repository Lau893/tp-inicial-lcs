# 1. Imagen Base
# Se utiliza una imagen oficial de Python 3.10 en su versión 'slim', 
# que es ligera y contiene un sistema operativo Debian mínimo.
FROM python:3.11-slim

# 2. Dependencias del Sistema
# Antes de instalar las librerías de Python, se instalan las herramientas
# de compilación necesarias en el sistema operativo.
# - build-essential: Incluye compiladores de C/C++ (como gcc) y otras utilidades.
# - cmake: Requerido específicamente para compilar la librería 'dlib'.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 3. Directorio de Trabajo
# Se establece el directorio de trabajo dentro del contenedor. Todos los
# comandos posteriores (como COPY y CMD) se ejecutarán en este contexto.
WORKDIR /app

# 4. Dependencias de Python
# Se copia primero solo el archivo de requisitos para aprovechar la caché de Docker.
# Si este archivo no cambia, Docker reutilizará la capa de la instalación de 
# dependencias, acelerando las construcciones futuras.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia del Código Fuente y Datos
# Se copia el código de la aplicación y la base de datos ya generada.
COPY api/ ./api

# 6. Exposición del Puerto
# Se informa a Docker que el contenedor escuchará en el puerto 8000 en tiempo de ejecución.
# Este es el puerto por defecto en el que Uvicorn ejecutará la aplicación FastAPI.
EXPOSE 8000

# 7. Comando de Inicio
# Define el comando que se ejecutará cuando el contenedor se inicie.
# - uvicorn: El servidor ASGI que ejecuta la aplicación.
# - src.api.main:app: La ruta al objeto de la aplicación FastAPI.
# - --host 0.0.0.0: Hace que el servidor sea accesible desde fuera del contenedor.
# - --port 8000: El puerto en el que se ejecutará el servidor.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

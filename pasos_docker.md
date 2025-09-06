Pasos Docker (desarrollo)

Comandos básicos para levantar y bajar los servicios del entorno local de desarrollo (db, backend, admin y tótem).

Requisitos
- Tener Docker Desktop en ejecución.
- Ubicación: podés ejecutar los comandos desde la carpeta raíz del repo o entrar en `tp-inicial-lcs/`.

Arrancar servicios
- Desde la raíz del repo:
  - `docker compose -f tp-inicial-lcs/docker-compose.dev.yml up --build`
- Estando dentro de `tp-inicial-lcs/`:
  - `docker compose -f docker-compose.dev.yml up --build`

Importante: se eliminó el archivo `tp-inicial-lcs/docker-compose.yml` (legacy).
No uses `docker-compose up --build` sin `-f`, porque levantaría un stack antiguo.

Arrancar en segundo plano (detached)
- `docker compose -f tp-inicial-lcs/docker-compose.dev.yml up -d --build`

Verificar
- Backend: `http://localhost:8000/healthz`
- Swagger: `http://localhost:8000/docs`
- Admin: `http://localhost:5173`
- Tótem: `http://localhost:5174`

Parar servicios (bajar el stack)
- `docker compose -f tp-inicial-lcs/docker-compose.dev.yml down`
- Si querés borrar los datos de Postgres del volumen (reset total):
  - `docker compose -f tp-inicial-lcs/docker-compose.dev.yml down -v`

Reconstruir solo backend (por cambios de código/requirements)
- `docker compose -f tp-inicial-lcs/docker-compose.dev.yml build backend`
- `docker compose -f tp-inicial-lcs/docker-compose.dev.yml up backend`

Ver logs
- Todos: `docker compose -f tp-inicial-lcs/docker-compose.dev.yml logs -f`
- Backend: `docker compose -f tp-inicial-lcs/docker-compose.dev.yml logs -f backend`
- DB: `docker compose -f tp-inicial-lcs/docker-compose.dev.yml logs -f db`

Reiniciar un servicio
- `docker compose -f tp-inicial-lcs/docker-compose.dev.yml restart backend`

Limpieza de imágenes/capas no usadas (opcional)
- Imágenes huérfanas: `docker image prune -f`
- Limpieza general (más agresiva): `docker system prune -f`

Eliminar la imagen vieja del frontend antiguo (si existe)
- Listar imágenes: `docker images`
- Remover contenedor si queda alguno: `docker rm -f tpilcs-frontend` (ignorar si no existe)
- Borrar imagen por IMAGE_ID: `docker rmi <IMAGE_ID>`

Eliminar recursos legacy (si alguna vez levantaste el stack viejo)
- Contenedores: `docker rm -f backend-api frontend-app` (ignorar si no existen)
- Imágenes asociadas: busca con `docker images` y borralas con `docker rmi <IMAGE_ID>`

Consejos
- Si cambiás `ALLOWED_ORIGINS` u otras variables, reconstruí el backend:
  - `docker compose -f tp-inicial-lcs/docker-compose.dev.yml up -d --build backend`
- Si el puerto 5432 está ocupado, cambiá el mapeo en `docker-compose.dev.yml` (por ejemplo a `5433:5432`).

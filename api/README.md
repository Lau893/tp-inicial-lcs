Backend FastAPI — Documentación

Este backend expone una API mínima para autenticación, gestión de empleados, registro de rostro (embedding) y asistencia. No realiza cómputo de visión: los embeddings se calculan en el navegador.

—

Cómo correr en desarrollo
- Requisitos: Python 3.11+, Postgres accesible.
- Instalar deps: pip install -r requirements.txt
- Variables de entorno: ver README.md (raíz). Mínimo: DATABASE_URL, JWT_SECRET, ADMIN_DNI, ADMIN_PASSWORD, TOTEM_API_KEY, ALLOWED_ORIGINS
- Ejecutar: uvicorn src.api.main:app --reload --port 8000
- Docs: http://localhost:8000/docs

—

Contratos de API (resumen)
- POST /login (admin): { dni, password } → { token, role: 'admin' }
- POST /employees (admin): { dni, nombre, apellido, fecha_nac } → { id }
- GET /employees?dni=... (admin): → { id, dni, nombre, apellido, fecha_nac, embedding }
- POST /registrar_rostro (admin): { dni, embedding:number[] } → { ok: true }
- GET /employees/gallery (tótem): → [{ id, embedding }]  (Header: x-api-key)
- POST /asistencia (tótem): { id_empleado, tipo, distancia, origen } → { ok, id } (Header: x-api-key)
- GET /healthz: { ok: true }

Seguridad
- Admin: JWT HS256. Login contra ADMIN_DNI/ADMIN_PASSWORD.
- Tótem: header x-api-key (TOTEM_API_KEY).
- CORS: restringido a ALLOWED_ORIGINS (URLs de admin y tótem).

Modelo de datos (Postgres)
- empleados(id serial pk, dni text unique, nombre, apellido, fecha_nac date, embedding jsonb)
- asistencias(id bigserial pk, empleado_id fk, ts timestamptz default now, tipo check('ingreso','egreso'), distancia real, origen text, unique(empleado_id, date(ts), tipo))

Notas de implementación
- Código principal: src/api/main.py
- Acceso a datos y modelos ORM: src/api/database.py (SQLAlchemy 2.x + psycopg)
- Schemas Pydantic: src/api/schemas.py
- JWT/API key: src/api/security.py
- Rate limit simple en memoria: src/api/rate_limit.py


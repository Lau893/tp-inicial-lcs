Sistema de Control de Asistencia con Reconocimiento Facial (Web + Render)

Este proyecto implementa un sistema de asistencia donde todo el cómputo de visión sucede en el navegador. El backend solo valida, autentica y persiste en Postgres (Render/Neon/Supabase). El despliegue objetivo son dos sitios estáticos (Admin y Tótem) y un servicio FastAPI en Render.

-----------------------------------------------------------------------
1. Arquitectura
-----------------------------------------------------------------------
- Frontend Admin (sitio estático):
  - Login básico (DNI/Password), dashboard, ABM de empleados por DNI, registrar rostro capturando cámara y calculando embedding en el navegador.
  - Env vars: VITE_API_BASE (URL del backend), usa JWT admin.
- Frontend Tótem (sitio estático):
  - Fullscreen, cámara activa y botones Ingreso/Egreso. Matching local contra una galería descargada del backend. Envía solo eventos de asistencia con x-api-key.
  - Env vars: VITE_API_BASE, VITE_TOTEM_API_KEY.
- Backend (FastAPI):
  - Endpoints mínimos de login, empleados, registrar rostro, asistencia y healthz. Sin lógica de visión.
  - Base de datos Postgres. CORS restringido a Admin y Tótem.

-----------------------------------------------------------------------
2. Backend: API y Contratos
-----------------------------------------------------------------------
- POST /login (admin): recibe { dni, password } y devuelve { token, role: 'admin' }.
- POST /employees (admin): crea empleado { dni, nombre, apellido, fecha_nac } → { id }.
- GET /employees?dni=123 (admin): devuelve { id, dni, nombre, apellido, fecha_nac, embedding }.
- POST /registrar_rostro (admin): { dni, embedding:number[] } → { ok: true }.
- GET /employees/gallery (tótem): devuelve [{ id, embedding }] (sin datos civiles). Header: x-api-key.
- POST /asistencia (tótem): { id_empleado, tipo:'ingreso'|'egreso', distancia, origen } → { ok, id }. Header: x-api-key. Rate limit básico y unicidad por empleado, día y tipo.
- GET /healthz: { ok: true }.

Esquema Postgres:
- empleados(id serial pk, dni text unique, nombre, apellido, fecha_nac date, embedding jsonb)
- asistencias(id bigserial pk, empleado_id fk, ts timestamptz default now, tipo check('ingreso','egreso'), distancia real, origen text, unique(empleado_id, date(ts), tipo))

Implementación en: api/main.py, api/database.py, api/schemas.py, api/security.py.

-----------------------------------------------------------------------
3. Embeddings en el Navegador (referencia)
-----------------------------------------------------------------------
- Modelo: MobileFaceNet/SFace (ONNX) u otro equivalente.
- Preproceso: recorte de rostro a 112x112 RGB, normalización (x/127.5 - 1.0).
- Salida: normalización L2 del embedding.
- Métrica: coseno. Umbral inicial 0.35–0.40. Ventana 5 frames, aceptar si ≥3 cumplen. Intervalo 500–800 ms por frame.
- Si no hay match: mostrar “Desconocido” y no enviar asistencia.

-----------------------------------------------------------------------
4. Variables de Entorno Backend
-----------------------------------------------------------------------
- DATABASE_URL (o database_url): cadena Postgres postgresql+psycopg://user:pass@host:port/db
- JWT_SECRET (o jwt_secret): secreto HS256 para JWT admin.
- ADMIN_DNI / ADMIN_PASSWORD (o minúsculas): credenciales admin.
- TOTEM_API_KEY (o totem_api_key): key para el tótem.
- ALLOWED_ORIGINS (o allowed_origins): lista separada por comas con URLs de Admin y Tótem.

-----------------------------------------------------------------------
5. Ejecución Local
-----------------------------------------------------------------------
Opción A — Sin Docker (rápida):
- pip install -r requirements.txt
- Exportar variables (ver sección 4)
- uvicorn api.main:app --reload --port 8000
- Swagger: http://localhost:8000/docs

Opción B — Docker Compose:
- docker compose up --build
Notas:
- El compose no incluye Postgres; usá un DATABASE_URL a un Postgres gestionado.
- Para pasar variables al contenedor, añadí environment al servicio o usá --env-file.

-----------------------------------------------------------------------
6. Despliegue en Render
-----------------------------------------------------------------------
- Web Service (Python):
  - Build: pip install -r requirements.txt
  - Start: gunicorn -k uvicorn.workers.UvicornWorker -w 1 api.main:app
  - Env: DATABASE_URL, JWT_SECRET, ADMIN_DNI, ADMIN_PASSWORD, TOTEM_API_KEY, ALLOWED_ORIGINS
- Static Sites:
  - Admin: setear VITE_API_BASE al backend.
  - Tótem: setear VITE_API_BASE y VITE_TOTEM_API_KEY.

-----------------------------------------------------------------------
7. Migración de SQLite a Postgres (si aplica)
-----------------------------------------------------------------------
- Exportar tablas a CSV desde data/gestion_produccion.db.
- Importar con psql COPY o usar pgloader.
- Convertir embeddings a JSONB al importar.
- Apuntar el backend a DATABASE_URL y verificar índices/constraints.

-----------------------------------------------------------------------
8. Estructura del Repositorio (resumen)
-----------------------------------------------------------------------
```
tp-inicial-lcs/
├── api/                  # Backend FastAPI (sin visión)
│   ├── main.py           # Endpoints y CORS
│   ├── database.py       # SQLAlchemy, modelos y helpers
│   ├── schemas.py        # Pydantic schemas
│   ├── security.py       # JWT y x-api-key
│   └── rate_limit.py     # Rate limiting básico
├── admin/                # Sitio estático Admin (login, ABM, rostro, reportes)
├── totem/                # Sitio estático Tótem (cámara, asistencia)
├── Dockerfile            # Imagen backend
├── docker-compose.yml    # Orquestación (backend+frontend)
├── requirements.txt      # Dependencias backend
└── README.md             # Este documento
```

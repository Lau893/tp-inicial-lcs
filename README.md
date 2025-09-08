Sistema de Control de Asistencia con Reconocimiento Facial (Web + Render)

Este proyecto implementa un sistema de asistencia donde todo el cómputo de visión sucede en el navegador. El backend solo valida, autentica y persiste en Postgres (Render/Neon/Supabase). El despliegue objetivo son dos sitios estáticos (Admin y Tótem) y un servicio FastAPI en Render.

-----------------------------------------------------------------------
1. Arquitectura
-----------------------------------------------------------------------
- Frontend Admin (sitio estático):
  - Login básico (DNI/Password), dashboard, ABM de empleados por DNI, registrar rostro capturando cámara y calculando embedding en el navegador.
  - Configuración por `window.CONFIG` dentro de `admin/index.html` (no usa Vite): `API_BASE` y `MODEL_URL`.
- Frontend Tótem (sitio estático):
  - Fullscreen, cámara activa y botones Ingreso/Egreso. Matching local contra una galería descargada del backend. Envía solo eventos de asistencia con x-api-key.
  - Configuración por `window.CONFIG` dentro de `totem/index.html`: `API_BASE` y `TOTEM_API_KEY`.
- Backend (FastAPI):
  - Endpoints de login, empleados, registrar rostro, galería para tótem, asistencia y healthz. Sin lógica de visión.
  - Base de datos Postgres (esquema legacy compatible). CORS restringido a Admin y Tótem mediante `ALLOWED_ORIGINS`.

-----------------------------------------------------------------------
2. Backend: API y Contratos
-----------------------------------------------------------------------
- POST /login (admin): recibe { dni, password } y devuelve { token, role: 'admin' }.
- POST /employees (admin): crea empleado { dni, nombre, apellido } → { id }.
- GET /employees?dni=123 (admin): devuelve { id, dni, nombre, apellido, rol, embedding }.
- POST /registrar_rostro (admin): { dni, embedding:number[] } → { ok: true }.
- GET /employees/gallery (tótem): devuelve [{ id, embedding }] (sin datos civiles). Header: x-api-key.
- POST /asistencia (tótem): { id_empleado, tipo:'ingreso'|'egreso', distancia, origen } → { ok, id }. Header: x-api-key. Rate limit básico.
- GET /healthz: { ok: true }.

Nota: el esquema legacy no incluye `fecha_nac` ni PK propia en asistencia; ver “Esquema de datos”.

-----------------------------------------------------------------------
3. Esquema de datos (legacy compatible)
-----------------------------------------------------------------------
Tablas principales (ver `tp-inicial-lcs/scripts/pg_legacy_schema.sql`):
- producto(id_producto, nombre, precio)
- lote(id_lote, id_producto, cantidad, fecha_ingreso, fecha_vto)
- rol(id_rol, nombre)
- empleado(id_empleado, nombre, apellido, documento, id_rol)
- produccion(id_produccion, id_lote, id_empleado, fecha_prod, cantidad_out, tiempo_horas)
- cliente(id_cliente, nombre, documento, direccion)
- venta(id_venta, id_cliente, id_producto, cantidad, fecha_venta)
- asistencia(id_empleado, fecha, tipo in ('entrada','salida'))
- embedding(id_embedding, id_empleado, embedding_data TEXT)  ← JSON serializado (texto)

Índices útiles: `idx_empleado_documento`, `idx_asistencia_emp_fecha`.

Limitaciones conocidas:
- `asistencia` no tiene PK propia; hoy se devuelve un identificador derivado. Si necesitás ID de asistencia, agregá una columna `id bigserial` y ajustá el backend.

-----------------------------------------------------------------------
4. Variables de Entorno Backend
-----------------------------------------------------------------------
- DATABASE_URL (o database_url): Postgres `postgresql+psycopg://user:pass@host:port/db?sslmode=require`
- JWT_SECRET (o jwt_secret): secreto HS256 para JWT admin.
- ADMIN_DNI / ADMIN_PASSWORD (o minúsculas): credenciales admin.
- TOTEM_API_KEY (o totem_api_key): key para el tótem.
- ALLOWED_ORIGINS (o allowed_origins): lista separada por comas con URLs completas de Admin y Tótem.

-----------------------------------------------------------------------
5. Base de datos: inicialización y semillas
-----------------------------------------------------------------------
PowerShell (Render externo):
- Set DB: `$env:DATABASE_URL="postgresql://USER:PASS@HOST:5432/DB?sslmode=require"`
- Crear esquema + inserts estáticos (roles, empleados, productos, clientes):
  `python tp-inicial-lcs/scripts/create_db.py`
- Semilla sintética (lotes, producción, ventas, asistencia):
  - Rápido (prueba): `python -u tp-inicial-lcs/scripts/seed_synthetic.py --truncate --months 1 --lots-min 2 --lots-max 3`
  - Completo: `python -u tp-inicial-lcs/scripts/seed_synthetic.py --months 12 --lots-min 10 --lots-max 20`

El seed imprime progreso y realiza commits parciales; en DB remota puede tardar varios minutos.

-----------------------------------------------------------------------
6. Ejecución Local
-----------------------------------------------------------------------
Opción A — Sin Docker (rápida):
- `cd tp-inicial-lcs && pip install -r requirements.txt`
- Exportar variables (ver sección 4)
- `uvicorn api.main:app --reload --port 8000`
- Swagger: http://localhost:8000/docs

Opción B — Docker Compose (incluye Postgres):
- `docker compose -f tp-inicial-lcs/docker-compose.dev.yml up --build`
- Servicios: DB (5432), backend (8000), admin (5173), tótem (5174)

-----------------------------------------------------------------------
7. Despliegue en Render
-----------------------------------------------------------------------
- Backend (Web Service Python):
  - Build: `pip install -r requirements.txt`
  - Start: `gunicorn -k uvicorn.workers.UvicornWorker -w 1 api.main:app`
  - Env: `DATABASE_URL`, `JWT_SECRET`, `ADMIN_DNI`, `ADMIN_PASSWORD`, `TOTEM_API_KEY`, `ALLOWED_ORIGINS`
  - Health: `GET /healthz`
- Admin (Static Site):
  - Publish dir: `tp-inicial-lcs/admin`
  - Ajustar `tp-inicial-lcs/admin/index.html` → `window.CONFIG = { API_BASE: 'https://<backend>.onrender.com', MODEL_URL: '/model/face_embedder.onnx' }`
  - Asegurar imágenes: copiar `tp-inicial-lcs/data/imagenes_datos` a `tp-inicial-lcs/admin/assets/imagenes_datos`
- Tótem (Static Site):
  - Publish dir: `tp-inicial-lcs/totem`
  - Ajustar `tp-inicial-lcs/totem/index.html` → `window.CONFIG = { API_BASE: 'https://<backend>.onrender.com', TOTEM_API_KEY: '<clave>' }`
  - Asegurar modelo ONNX: `tp-inicial-lcs/totem/model/face_embedder.onnx` (copiar desde `admin/model/`)
- Actualizar `ALLOWED_ORIGINS` del backend con las URLs finales de Admin y Tótem.

-----------------------------------------------------------------------
8. Embeddings en el Navegador (referencia)
-----------------------------------------------------------------------
- Modelo: MobileFaceNet/SFace (ONNX) u otro equivalente.
- Preproceso: recorte 112x112 RGB, normalización (x/127.5 - 1.0).
- Salida: normalización L2.
- Métrica: coseno. Umbral inicial 0.35–0.40. Ventana 5 frames, aceptar si ≥3 cumplen. 500–800 ms por frame.
- Sin match: mostrar “Desconocido” y no enviar asistencia.

-----------------------------------------------------------------------
9. Estructura del Repositorio (resumen)
-----------------------------------------------------------------------
```
tp-inicial-lcs/
├── api/
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   ├── security.py
│   └── rate_limit.py
├── admin/
├── totem/
├── scripts/
│   ├── pg_legacy_schema.sql
│   ├── inserts.sql
│   ├── create_db.py
│   └── seed_synthetic.py
├── Dockerfile
├── docker-compose.dev.yml
├── requirements.txt
└── README.md
```


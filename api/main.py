import os
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .schemas import (
    LoginRequest,
    LoginResponse,
    EmployeeCreate,
    EmployeeOut,
    RegistrarRostroRequest,
    GalleryItem,
    AsistenciaRequest,
    AsistenciaResponse,
    HealthResponse,
)
from .security import create_jwt, require_admin, require_api_key
from .database import (
    init_models,
    get_session,
    create_employee,
    get_employee_by_dni,
    set_employee_embedding_by_dni,
    get_gallery,
    asistencia_exists_today,
    create_asistencia,
)
from .rate_limit import asistencia_limiter


def _map_db_rol_to_api(nombre: str) -> str:
    n = (nombre or "").lower()
    if n.startswith("admin"):
        return "admin"
    if n.startswith("encarg"):
        return "encargado"
    if n.startswith("segur"):
        return "seguridad"
    return "operario"
from sqlalchemy.orm import Session


def get_allowed_origins() -> list[str]:
    raw = (
        os.environ.get("ALLOWED_ORIGINS")
        or os.environ.get("allowed_origins")
        or "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174"
    ).strip()
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(title="Asistencia Facial - Backend", version="1.0.0")

# CORS restringido a sitios admin y tótem
origins = get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_models()


@app.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    """Login de administrador.

    - Modo env: si ADMIN_DNI/ADMIN_PASSWORD coinciden, otorga token admin.
    - Modo DB adicional (legacy): si el DNI pertenece a un empleado cuyo rol en tabla `rol`
      es Administrador, y el password es "<dni>a", también permite el acceso.
    """
    admin_dni = os.environ.get("ADMIN_DNI") or os.environ.get("admin_dni")
    admin_password = os.environ.get("ADMIN_PASSWORD") or os.environ.get("admin_password")

    if admin_dni and admin_password and data.dni == admin_dni and data.password == admin_password:
        token = create_jwt(subject=data.dni, role="admin")
        return LoginResponse(token=token)

    # Fallback: validar contra DB (legacy)
    with get_session() as db:
        emp = get_employee_by_dni(db, data.dni)
        rol_nombre = (emp or {}).get("rol_nombre", "") if emp else ""
        if emp and (rol_nombre.lower().startswith("admin")) and (data.password == f"{emp['dni']}a"):
            token = create_jwt(subject=data.dni, role="admin")
            return LoginResponse(token=token)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")


@app.post("/employees", response_model=dict)
def create_employee_endpoint(payload: EmployeeCreate, _: dict = Depends(require_admin)):
    # Validaciones
    if not payload.dni.isdigit() or len(payload.dni) > 8:
        raise HTTPException(status_code=422, detail="El DNI debe ser numérico y tener hasta 8 dígitos")

    with get_session() as db:
        # DNI único
        if get_employee_by_dni(db, payload.dni):
            raise HTTPException(status_code=409, detail="DNI ya existe")
        emp_id = create_employee(db, payload.dni, payload.nombre, payload.apellido, payload.fecha_nac, payload.rol)
        return {"id": emp_id}


@app.get("/employees", response_model=EmployeeOut)
def get_employee_endpoint(dni: str = Query(...), _: dict = Depends(require_admin)):
    with get_session() as db:
        emp = get_employee_by_dni(db, dni)
        if not emp:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        return EmployeeOut(
            id=emp["id"],
            dni=emp["dni"],
            nombre=emp["nombre"],
            apellido=emp["apellido"],
            fecha_nac=None,
            rol=_map_db_rol_to_api(emp["rol_nombre"]),
            embedding=emp["embedding"],
        )


@app.get("/employees/resolve", response_model=dict)
def resolve_employee_id(dni: str = Query(...), _ok=Depends(require_api_key)):
    """Devuelve {id} para un DNI. Pensado para el tótem (x-api-key), sin datos civiles."""
    with get_session() as db:
        emp = get_employee_by_dni(db, dni)
        if not emp:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        return {"id": emp["id"]}


@app.post("/registrar_rostro", response_model=dict)
def registrar_rostro_endpoint(payload: RegistrarRostroRequest, _: dict = Depends(require_admin)):
    with get_session() as db:
        ok = set_employee_embedding_by_dni(db, payload.dni, payload.embedding)
        if not ok:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        return {"ok": True}


@app.get("/employees/gallery", response_model=list[GalleryItem])
def gallery_endpoint(_ok=Depends(require_api_key)):
    with get_session() as db:
        items = [GalleryItem(id=eid, embedding=emb) for eid, emb in get_gallery(db)]
        return items


@app.post("/asistencia", response_model=AsistenciaResponse)
def asistencia_endpoint(payload: AsistenciaRequest, _ok=Depends(require_api_key)):
    # Rate limit básico por empleado+tipo
    asistencia_limiter.check((str(payload.id_empleado), payload.tipo))
    with get_session() as db:
        if asistencia_exists_today(db, payload.id_empleado, payload.tipo):
            raise HTTPException(status_code=409, detail="Asistencia ya registrada para hoy")
        new_id = create_asistencia(db, payload.id_empleado, payload.tipo, payload.distancia, payload.origen)
        return AsistenciaResponse(id=new_id)


@app.get("/healthz", response_model=HealthResponse)
def health_check():
    return HealthResponse()

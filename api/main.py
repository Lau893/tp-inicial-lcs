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
from sqlalchemy.orm import Session


def get_allowed_origins() -> list[str]:
    raw = (os.environ.get("ALLOWED_ORIGINS") or os.environ.get("allowed_origins") or "").strip()
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(title="Asistencia Facial - Backend", version="1.0.0")

# CORS restringido a sitios admin y tótem
origins = get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],  # permitir * solo en desarrollo si no configuran
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_models()


@app.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    admin_dni = os.environ.get("ADMIN_DNI") or os.environ.get("admin_dni")
    admin_password = os.environ.get("ADMIN_PASSWORD") or os.environ.get("admin_password")
    if not admin_dni or not admin_password:
        raise HTTPException(status_code=500, detail="ADMIN_DNI/ADMIN_PASSWORD no configurados")
    if data.dni != admin_dni or data.password != admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_jwt(subject=data.dni, role="admin")
    return LoginResponse(token=token)


@app.post("/employees", response_model=dict)
def create_employee_endpoint(payload: EmployeeCreate, _: dict = Depends(require_admin)):
    with get_session() as db:
        # DNI único
        if get_employee_by_dni(db, payload.dni):
            raise HTTPException(status_code=409, detail="DNI ya existe")
        emp_id = create_employee(db, payload.dni, payload.nombre, payload.apellido, payload.fecha_nac)
        return {"id": emp_id}


@app.get("/employees", response_model=EmployeeOut)
def get_employee_endpoint(dni: str = Query(...), _: dict = Depends(require_admin)):
    with get_session() as db:
        emp = get_employee_by_dni(db, dni)
        if not emp:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        return EmployeeOut(
            id=emp.id,
            dni=emp.dni,
            nombre=emp.nombre,
            apellido=emp.apellido,
            fecha_nac=emp.fecha_nac,
            embedding=emp.embedding,
        )


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

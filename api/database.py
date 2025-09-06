"""Acceso a datos (Postgres) adaptado al esquema legacy.

Usa las tablas: rol, empleado, embedding, asistencia. Evita crear tablas.
"""

import os
from datetime import date
from typing import Optional, List, Tuple

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("database_url") or "postgresql+psycopg://user:pass@localhost:5432/db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = None  # no ORM models; trabajamos con SQL directo


## No declarative models; consultas con SQL directo al esquema legacy


def init_models():
    return


# Helper de sesión
def get_session() -> Session:
    """Retorna una sesión SQLAlchemy (caller debe cerrar o usar context manager)."""
    return SessionLocal()


# Operaciones de dominio
def _map_api_rol_to_db_name(rol: str) -> str:
    return "Administrador" if rol == "admin" else "Operario"


def _map_db_name_to_api_rol(nombre: Optional[str]) -> str:
    return "admin" if (nombre or "").lower().startswith("admin") else "operario"


def _resolve_id_rol(db: Session, rol_api: str) -> int:
    nombre = _map_api_rol_to_db_name(rol_api)
    row = db.execute(text("SELECT id_rol FROM rol WHERE LOWER(nombre)=LOWER(:n)"), {"n": nombre}).first()
    if row:
        return int(row[0])
    row2 = db.execute(text("INSERT INTO rol (nombre) VALUES (:n) RETURNING id_rol"), {"n": nombre}).first()
    db.commit()
    return int(row2[0])


def create_employee(db: Session, dni: str, nombre: str, apellido: Optional[str], fecha_nac: Optional[date], rol: str = "operario") -> int:
    id_rol = _resolve_id_rol(db, rol)
    row = db.execute(text(
        """
        INSERT INTO empleado (nombre, apellido, documento, id_rol)
        VALUES (:nombre, :apellido, :documento, :id_rol)
        RETURNING id_empleado
        """
    ), {"nombre": nombre, "apellido": apellido or "", "documento": dni, "id_rol": id_rol}).first()
    db.commit()
    return int(row[0])


def get_employee_by_dni(db: Session, dni: str):
    row = db.execute(text(
        """
        SELECT e.id_empleado, e.documento, e.nombre, e.apellido, r.nombre as rol_nombre
        FROM empleado e
        LEFT JOIN rol r ON r.id_rol = e.id_rol
        WHERE e.documento = :dni
        """
    ), {"dni": dni}).first()
    if not row:
        return None
    emp_id = int(row[0])
    emb_row = db.execute(text(
        "SELECT embedding_data FROM embedding WHERE id_empleado=:id ORDER BY id_embedding DESC LIMIT 1"
    ), {"id": emp_id}).first()
    embedding = None
    if emb_row and emb_row[0]:
        try:
            import json
            embedding = json.loads(emb_row[0])
        except Exception:
            embedding = None
    return {
        "id": emp_id,
        "dni": row[1],
        "nombre": row[2] or "",
        "apellido": row[3] or "",
        "rol_nombre": row[4] or "",
        "embedding": embedding,
    }


def set_employee_embedding_by_dni(db: Session, dni: str, embedding: List[float]) -> bool:
    emp = get_employee_by_dni(db, dni)
    if not emp:
        return False
    import json
    db.execute(text("DELETE FROM embedding WHERE id_empleado=:id"), {"id": emp["id"]})
    db.execute(text("INSERT INTO embedding (id_empleado, embedding_data) VALUES (:id,:data)"), {"id": emp["id"], "data": json.dumps(embedding)})
    db.commit()
    return True


def get_gallery(db: Session) -> List[Tuple[int, List[float]]]:
    rows = db.execute(text(
        "SELECT e.id_empleado, em.embedding_data FROM empleado e JOIN embedding em ON em.id_empleado = e.id_empleado"
    )).all()
    out: List[Tuple[int, List[float]]] = []
    import json
    for r in rows:
        try:
            out.append((int(r[0]), json.loads(r[1])))
        except Exception:
            continue
    return out


def asistencia_exists_today(db: Session, empleado_id: int, tipo_api: str) -> bool:
    tipo_db = 'entrada' if tipo_api == 'ingreso' else 'salida'
    q = db.execute(text("SELECT 1 FROM asistencia WHERE id_empleado=:id AND tipo=:t AND date(fecha)=current_date LIMIT 1"), {"id": empleado_id, "t": tipo_db}).first()
    return q is not None


def create_asistencia(db: Session, empleado_id: int, tipo_api: str, distancia: float, origen: str) -> int:
    tipo_db = 'entrada' if tipo_api == 'ingreso' else 'salida'
    db.execute(text("INSERT INTO asistencia (id_empleado, fecha, tipo) VALUES (:id, now(), :t)"), {"id": empleado_id, "t": tipo_db})
    db.commit()
    return empleado_id

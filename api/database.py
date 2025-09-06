"""Capa de acceso a datos (Postgres, SQLAlchemy 2.x).

Define el ORM para las tablas `empleados` y `asistencias`, junto con
helpers de sesión y operaciones de dominio usadas por los endpoints.

Aspectos destacados:
- `embedding` se almacena como JSONB.
- `asistencias` tiene restricción de tipo ('ingreso', 'egreso') y una
  unicidad lógica por (empleado_id, date(ts), tipo), verificada en la
  capa de aplicación por `asistencia_exists_today`.
"""

import os
from datetime import date
from typing import Optional, List, Tuple

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Date,
    DateTime,
    Float,
    ForeignKey,
    CheckConstraint,
    func,
    select,
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship, sessionmaker, Session
from sqlalchemy.dialects.postgresql import JSONB, BIGINT


DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("database_url") or "postgresql+psycopg://user:pass@localhost:5432/db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


class Empleado(Base):
    """Modelo de empleado.

    - `dni` es único e indexado para búsquedas rápidas.
    - `embedding` es un arreglo float (JSONB) calculado en el navegador.
    """

    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dni: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    apellido: Mapped[str] = mapped_column(String, nullable=False)
    fecha_nac: Mapped[date] = mapped_column(Date, nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    asistencias: Mapped[list["Asistencia"]] = relationship(back_populates="empleado")


class Asistencia(Base):
    """Modelo de asistencia.

    - `tipo`: 'ingreso' o 'egreso'.
    - `ts`: timestamp con zona horaria (server default `now()`).
    - Unicidad lógica por día y tipo se valida en la aplicación.
    """

    __tablename__ = "asistencias"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True)
    ts: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    distancia: Mapped[float] = mapped_column(Float, nullable=False)
    origen: Mapped[str] = mapped_column(String, nullable=False)

    empleado: Mapped[Empleado] = relationship(back_populates="asistencias")

    __table_args__ = (
        CheckConstraint("tipo in ('ingreso','egreso')", name="tipo_check"),
    )


def init_models():
    """Crea las tablas si no existen (usado en startup)."""
    Base.metadata.create_all(bind=engine)


# Helper de sesión
def get_session() -> Session:
    """Retorna una sesión SQLAlchemy (caller debe cerrar o usar context manager)."""
    return SessionLocal()


# Operaciones de dominio
def create_employee(db: Session, dni: str, nombre: str, apellido: str, fecha_nac: date) -> int:
    """Crea un empleado y retorna su ID."""
    emp = Empleado(dni=dni, nombre=nombre, apellido=apellido, fecha_nac=fecha_nac)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp.id


def get_employee_by_dni(db: Session, dni: str) -> Optional[Empleado]:
    """Obtiene un empleado por DNI o None si no existe."""
    return db.execute(select(Empleado).where(Empleado.dni == dni)).scalar_one_or_none()


def set_employee_embedding_by_dni(db: Session, dni: str, embedding: List[float]) -> bool:
    """Guarda/actualiza el embedding del empleado identificado por DNI."""
    emp = get_employee_by_dni(db, dni)
    if not emp:
        return False
    emp.embedding = embedding
    db.add(emp)
    db.commit()
    return True


def get_gallery(db: Session) -> List[Tuple[int, List[float]]]:
    """Devuelve la galería para el tótem: lista de (id, embedding) con embedding no nulo."""
    rows = db.execute(select(Empleado.id, Empleado.embedding).where(Empleado.embedding.is_not(None))).all()
    return [(r[0], r[1]) for r in rows]


def asistencia_exists_today(db: Session, empleado_id: int, tipo: str) -> bool:
    """Verifica si ya existe asistencia hoy para (empleado_id, tipo)."""
    q = db.execute(
        select(Asistencia.id).where(
            Asistencia.empleado_id == empleado_id,
            Asistencia.tipo == tipo,
            func.date(Asistencia.ts) == func.current_date(),
        )
    ).first()
    return q is not None


def create_asistencia(db: Session, empleado_id: int, tipo: str, distancia: float, origen: str) -> int:
    """Crea un registro de asistencia y retorna su ID."""
    a = Asistencia(empleado_id=empleado_id, tipo=tipo, distancia=distancia, origen=origen)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a.id

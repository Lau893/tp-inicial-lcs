"""Esquemas (Pydantic) para requests y responses de la API.

Todas las estructuras que el backend expone o consume están definidas aquí
para asegurar contratos claros y validación automática.
"""

from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import date


# Auth
class LoginRequest(BaseModel):
    """Payload para iniciar sesión del admin."""
    dni: str
    password: str


class LoginResponse(BaseModel):
    """Respuesta al login: JWT + rol."""
    token: str
    role: Literal["admin"] = "admin"


# Employees
class EmployeeCreate(BaseModel):
    """Payload para crear un empleado."""
    dni: str
    nombre: str
    apellido: Optional[str] = ""
    fecha_nac: Optional[date] = None
    rol: Literal["admin", "operario", "encargado", "seguridad"] = "operario"


class EmployeeOut(BaseModel):
    """Representación completa de un empleado (incluye embedding si existe)."""
    id: int
    dni: str
    nombre: str
    apellido: Optional[str] = ""
    fecha_nac: Optional[date] = None
    rol: Literal["admin", "operario", "encargado", "seguridad"]
    embedding: Optional[List[float]] = None


class RegistrarRostroRequest(BaseModel):
    """Payload para asociar/actualizar el embedding de un empleado por DNI."""
    dni: str
    embedding: List[float] = Field(min_items=1)


class GalleryItem(BaseModel):
    """Elemento de galería para el tótem (solo id y embedding)."""
    id: int
    embedding: List[float]


# Asistencia
class AsistenciaRequest(BaseModel):
    """Payload para registrar una asistencia del tótem."""
    id_empleado: int
    tipo: Literal["ingreso", "egreso"]
    distancia: float
    origen: str


class AsistenciaResponse(BaseModel):
    """Respuesta exitosa al registrar asistencia."""
    ok: bool = True
    id: int


class HealthResponse(BaseModel):
    """Respuesta del health check."""
    ok: bool = True

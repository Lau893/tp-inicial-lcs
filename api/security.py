"""Seguridad y autenticación del backend.

Este módulo centraliza:
- Creación y validación de JWT para el rol de administrador.
- Dependencias FastAPI para exigir token Bearer (admin) o x-api-key (tótem).

Notas:
- El secreto JWT se toma de `JWT_SECRET` (o `jwt_secret`) y usa HS256.
- La API key del tótem se toma de `TOTEM_API_KEY` (o `totem_api_key`).
"""

import os
import time
from typing import Optional
import jwt
from fastapi import Depends, Header, HTTPException, status


JWT_SECRET = os.environ.get("JWT_SECRET") or os.environ.get("jwt_secret") or "dev-secret"
JWT_ALG = "HS256"


def create_jwt(subject: str, role: str = "admin", ttl_seconds: int = 60 * 60 * 8) -> str:
    """Genera un JWT HS256 con `sub`, `role`, `iat` y `exp`.

    Parámetros:
    - subject: identificador del sujeto (DNI del admin).
    - role: rol incluido en el token (por defecto "admin").
    - ttl_seconds: tiempo de vida del token en segundos (8h por defecto).
    """
    now = int(time.time())
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_jwt(token: str) -> dict:
    """Decodifica y valida un JWT, o lanza 401 si no es válido."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def get_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """Extrae el token Bearer del header Authorization.

    Formato esperado: "Bearer <token>". Si está ausente o mal formado, retorna 401.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta token Bearer")
    return authorization.split(" ", 1)[1]


def require_admin(payload: dict = Depends(lambda token=Depends(get_bearer_token): decode_jwt(token))):
    """Dependency de FastAPI que exige JWT válido con rol 'admin'.

    Devuelve el payload del JWT si es correcto, o 403 si el rol no es válido.
    """
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
    return payload


def require_api_key(x_api_key: Optional[str] = Header(None)):
    """Dependency de FastAPI que valida el header x-api-key para el tótem."""
    expected = os.environ.get("TOTEM_API_KEY") or os.environ.get("totem_api_key")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida")
    return True

"""Inicialización de la base de datos Postgres (tablas legacy).

Aplica el esquema legacy compatible (scripts/pg_legacy_schema.sql) y los inserts
estáticos (scripts/inserts.sql) manteniendo la lógica y estructura original de
las tablas: rol, empleado, cliente, producto, lote, produccion, venta,
asistencia, embedding.

Uso:
- En host (con venv):
  DATABASE_URL=postgresql://user:pass@host:5432/db python scripts/create_db.py
- Con Compose dev (DB local):
  DATABASE_URL=postgresql://appuser:apppass@localhost:5432/appdb python scripts/create_db.py
"""

import os
import sys
from pathlib import Path

import psycopg


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCHEMA_SQL = SCRIPTS / "pg_legacy_schema.sql"
INSERTS_SQL = SCRIPTS / "inserts.sql"


def normalize_dsn(url: str) -> str:
    """Normaliza la URL para psycopg (reemplaza postgresql+psycopg por postgresql)."""
    return url.replace("postgresql+psycopg://", "postgresql://")


def read_sql(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def apply_sql(conn: psycopg.Connection, sql: str):
    with conn.cursor() as cur:
        cur.execute(sql)


def main():
    url = os.environ.get("DATABASE_URL") or os.environ.get("database_url")
    if not url:
        print("Error: Definí DATABASE_URL para conectar a Postgres.", file=sys.stderr)
        sys.exit(1)
    dsn = normalize_dsn(url)

    print(f"Conectando a Postgres: {dsn}")
    try:
        with psycopg.connect(dsn) as conn:
            conn.execute("SELECT 1")
            print("Conexión OK.")

            if not SCHEMA_SQL.exists():
                print(f"No encontrado: {SCHEMA_SQL}", file=sys.stderr)
                sys.exit(2)

            print(f"Aplicando esquema: {SCHEMA_SQL}")
            apply_sql(conn, read_sql(SCHEMA_SQL))

            if INSERTS_SQL.exists():
                print(f"Aplicando inserts estáticos: {INSERTS_SQL}")
                apply_sql(conn, read_sql(INSERTS_SQL))
            else:
                print("Inserts estáticos no encontrados, solo se aplicó el esquema.")

            conn.commit()
            print("Listo. Esquema y semillas aplicados.")
    except Exception as e:
        print(f"Error al inicializar Postgres: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()

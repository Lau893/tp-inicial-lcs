"""Seed sintético para Postgres (esquema legacy).

Adapta la lógica de tu script SQLite a Postgres con psycopg3:
- Genera asistencia con perfiles mensuales de puntualidad (retrasos planificados).
- Genera lotes y su producción asociada.
- Simula merma 10–30% por producto y ventas distribuidas en días hábiles.

Uso (PowerShell):
  $env:DATABASE_URL="postgresql+psycopg://user:pass@host:5432/db?sslmode=require"; \
    python tp-inicial-lcs/scripts/seed_synthetic.py --months 12 --lots-min 10 --lots-max 20

Uso (bash):
  DATABASE_URL='postgresql+psycopg://user:pass@host:5432/db?sslmode=require' \
    python tp-inicial-lcs/scripts/seed_synthetic.py --months 12 --lots-min 10 --lots-max 20

Flags útiles:
  --truncate           Trunca (borra) asistencia, venta, produccion, lote antes de sembrar.
  --no-asistencia      No generar asistencia.
  --no-ventas          No generar ventas (solo lotes + producción).
  --months N           Meses hacia atrás (default 12).
  --lots-min/-max      Lotes por día hábil (default 10..20).
"""

from __future__ import annotations

import os
import sys
import argparse
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Sequence

import psycopg


def normalize_dsn(url: str) -> str:
    """psycopg acepta postgresql://; normalizamos si viene con +psycopg."""
    return url.replace("postgresql+psycopg://", "postgresql://")


def business_days(start: date, end: date) -> list[date]:
    d = start
    out: list[date] = []
    while d <= end:
        if d.weekday() < 5:  # 0..4 Lun..Vie
            out.append(d)
        d += timedelta(days=1)
    return out


def month_range(start: date, end: date) -> list[date]:
    """Primer día de cada mes entre start y end (inclusive si coincide)."""
    cur = date(start.year, start.month, 1)
    out = []
    while cur <= end:
        out.append(cur)
        # avanzar un mes
        y = cur.year + (1 if cur.month == 12 else 0)
        m = 1 if cur.month == 12 else cur.month + 1
        cur = date(y, m, 1)
    return out


def fetch_ids(conn: psycopg.Connection, table: str, id_col: str) -> list[int]:
    with conn.cursor() as cur:
        cur.execute(f"SELECT {id_col} FROM {table}")
        return [r[0] for r in cur.fetchall()]


def fetch_operario_ids(conn: psycopg.Connection) -> list[int]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.id_empleado
            FROM empleado e
            JOIN rol r ON r.id_rol = e.id_rol
            WHERE LOWER(r.nombre) = 'operario'
            """
        )
        return [r[0] for r in cur.fetchall()]


def truncate_targets(conn: psycopg.Connection):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE asistencia, venta, produccion, lote RESTART IDENTITY CASCADE")


@dataclass
class LoteData:
    id_lote: int
    id_producto: int
    ingreso: date
    vto: date
    cantidad_inicial: int
    restante: int


def seed_lotes_y_produccion(
    conn: psycopg.Connection,
    workdays: Sequence[date],
    lots_min: int,
    lots_max: int,
    operario_ids: Sequence[int],
    commit_every_days: int = 5,
    verbose: bool = True,
) -> list[LoteData]:
    product_ids = fetch_ids(conn, "producto", "id_producto")
    if not product_ids:
        print("No hay productos; abortando.", file=sys.stderr)
        return []
    if not operario_ids:
        # fallback: cualquier empleado
        operario_ids = fetch_ids(conn, "empleado", "id_empleado")
    lotes: list[LoteData] = []
    processed_days = 0
    if verbose:
        print(f"[lotes] Inicio: {len(workdays)} días hábiles, {lots_min}..{lots_max} lotes/día", flush=True)
    with conn.cursor() as cur:
        for d in workdays:
            n = random.randint(lots_min, lots_max)
            for _ in range(n):
                pid = random.choice(product_ids)
                ingreso = d
                vto = d + timedelta(days=random.randint(90, 180))
                cantidad_ini = random.randint(500, 2500)
                cur.execute(
                    """
                    INSERT INTO lote (id_producto, cantidad, fecha_ingreso, fecha_vto)
                    VALUES (%s,%s,%s,%s) RETURNING id_lote
                    """,
                    (pid, cantidad_ini, ingreso, vto),
                )
                lote_id = cur.fetchone()[0]
                # Producción asociada
                eid = random.choice(operario_ids)
                horas = round(random.uniform(4.0, 8.0), 2)
                cur.execute(
                    """
                    INSERT INTO produccion (id_lote, id_empleado, fecha_prod, cantidad_out, tiempo_horas)
                    VALUES (%s,%s,%s,%s,%s)
                    """,
                    (lote_id, eid, ingreso, cantidad_ini, horas),
                )
                lotes.append(
                    LoteData(
                        id_lote=lote_id,
                        id_producto=pid,
                        ingreso=ingreso,
                        vto=vto,
                        cantidad_inicial=cantidad_ini,
                        restante=cantidad_ini,
                    )
                )
            processed_days += 1
            if commit_every_days and (processed_days % commit_every_days == 0):
                conn.commit()
                if verbose:
                    print(
                        f"[lotes] Días procesados: {processed_days}/{len(workdays)} — lotes acumulados: {len(lotes)}",
                        flush=True,
                    )
    if commit_every_days:
        conn.commit()
    print(f"Lotes creados: {len(lotes)}; producción generada.", flush=True)
    return lotes


def simulate_merma_y_consumo(lotes: list[LoteData]) -> dict[int, int]:
    """Devuelve por producto la cantidad a vender y actualiza 'restante' en cada lote."""
    total_por_prod: dict[int, int] = defaultdict(int)
    for lt in lotes:
        total_por_prod[lt.id_producto] += lt.cantidad_inicial

    ventas_objetivo: dict[int, int] = {}
    for pid, total in total_por_prod.items():
        merma = random.uniform(0.10, 0.30)
        ventas_objetivo[pid] = int(total * (1 - merma))

    # Consumir stock por producto en orden aleatorio (no FIFO)
    lotes_por_prod: dict[int, list[LoteData]] = defaultdict(list)
    for lt in lotes:
        lotes_por_prod[lt.id_producto].append(lt)
    for pid, arr in lotes_por_prod.items():
        random.shuffle(arr)
        to_sell = ventas_objetivo[pid]
        for lt in arr:
            if to_sell <= 0:
                break
            take = min(lt.restante, to_sell)
            lt.restante -= take
            to_sell -= take
        ventas_objetivo[pid] -= to_sell  # lo que efectivamente quedará pendiente para generar ventas
    return ventas_objetivo


def update_lotes_stock(conn: psycopg.Connection, lotes: list[LoteData]):
    with conn.cursor() as cur:
        for lt in lotes:
            cur.execute("UPDATE lote SET cantidad=%s WHERE id_lote=%s", (lt.restante, lt.id_lote))
    conn.commit()
    print("Stock de lotes actualizado (cantidad=restante).", flush=True)


def seed_ventas(
    conn: psycopg.Connection,
    workdays: Sequence[date],
    ventas_pendientes: dict[int, int],
    commit_every_rows: int = 500,
    verbose: bool = True,
):
    product_ids = list(ventas_pendientes.keys())
    cliente_ids = fetch_ids(conn, "cliente", "id_cliente")
    if not cliente_ids:
        print("No hay clientes; no se generan ventas.", file=sys.stderr, flush=True)
        return
    inserted = 0
    if verbose:
        print("[ventas] Inicio", flush=True)
    with conn.cursor() as cur:
        for day_idx, d in enumerate(workdays, start=1):
            pend = [pid for pid, cant in ventas_pendientes.items() if cant > 0]
            if not pend:
                break
            # Inserciones de ventas simuladas por día
            for _ in range(random.randint(30, 60)):
                pend = [pid for pid, cant in ventas_pendientes.items() if cant > 0]
                if not pend:
                    break
                pid = random.choice(pend)
                max_qty = min(50, ventas_pendientes[pid])
                if max_qty <= 0:
                    continue
                qty = random.randint(1, max_qty)
                cid = random.choice(cliente_ids)
                cur.execute(
                    "INSERT INTO venta (id_cliente, id_producto, cantidad, fecha_venta) VALUES (%s,%s,%s,%s)",
                    (cid, pid, qty, d),
                )
                ventas_pendientes[pid] -= qty
                inserted += 1
                if commit_every_rows and (inserted % commit_every_rows == 0):
                    conn.commit()
                    if verbose:
                        print(f"[ventas] Insertadas: {inserted}", flush=True)
            # Commit y progreso al final de cada día
            conn.commit()
            if verbose:
                print(f"[ventas] Día {day_idx}/{len(workdays)} — acumuladas: {inserted}", flush=True)
    conn.commit()
    if verbose:
        print(f"Ventas insertadas: {inserted}", flush=True)


def seed_asistencia(conn: psycopg.Connection, start: date, end: date, verbose: bool = True):
    emp_ids = fetch_ids(conn, "empleado", "id_empleado")
    if not emp_ids:
        print("No hay empleados; no se genera asistencia.", file=sys.stderr)
        return

    # Definición de perfiles mensuales
    perfiles = {
        "siempre_puntual": (0, 0),
        "puntual": (0, 1),
        "ocasional": (1, 2),
        "recurrente": (2, 4),
    }

    # Asignación por defecto: primeros 16 como en tu script; resto 'puntual'
    asignacion: dict[int, str] = {}
    for idx, eid in enumerate(sorted(emp_ids)):
        mapa = {
            0: "siempre_puntual",
            1: "siempre_puntual",
            2: "puntual",
            3: "ocasional",
            4: "ocasional",
            5: "recurrente",
            6: "puntual",
            7: "recurrente",
            8: "puntual",
            9: "recurrente",
            10: "ocasional",
            11: "ocasional",
            12: "siempre_puntual",
            13: "puntual",
            14: "puntual",
            15: "puntual",
        }
        asignacion[eid] = mapa.get(idx, "puntual")

    # Planificación mensual de retrasos por empleado
    retrasos_planificados: set[tuple[date, int]] = set()
    months = month_range(start, end)
    for m_start in months:
        # fin de mes actual
        if m_start.month == 12:
            m_end = date(m_start.year + 1, 1, 1) - timedelta(days=1)
        else:
            m_end = date(m_start.year, m_start.month + 1, 1) - timedelta(days=1)
        if m_end > end:
            m_end = end
        dias_mes = business_days(m_start, m_end)
        if not dias_mes:
            continue
        for eid in emp_ids:
            perfil = asignacion.get(eid, "puntual")
            min_r, max_r = perfiles[perfil]
            n_retrasos = random.randint(min_r, max_r)
            if n_retrasos > 0:
                dias_sel = random.sample(dias_mes, min(n_retrasos, len(dias_mes)))
                for d in dias_sel:
                    retrasos_planificados.add((d, eid))

    # Generación de registros diarios
    dias = business_days(start, end)
    total_rows = 0
    if verbose:
        print(f"[asistencia] Inicio: {len(dias)} días", flush=True)
    with conn.cursor() as cur:
        for d in dias:
            for eid in emp_ids:
                # 10% ausencias
                if random.random() < 0.10:
                    continue
                # Entrada
                if (d, eid) in retrasos_planificados:
                    entry_var = random.randint(10, 20)
                else:
                    entry_var = random.randint(-10, 0)
                entrada = datetime.combine(d, time(8, 0)) + timedelta(minutes=entry_var)
                salida = datetime.combine(d, time(17, 0)) + timedelta(minutes=random.randint(-5, 5))
                cur.execute(
                    "INSERT INTO asistencia (id_empleado, fecha, tipo) VALUES (%s,%s,%s)",
                    (eid, entrada, "entrada"),
                )
                cur.execute(
                    "INSERT INTO asistencia (id_empleado, fecha, tipo) VALUES (%s,%s,%s)",
                    (eid, salida, "salida"),
                )
                total_rows += 2
                if verbose and (total_rows % 2000 == 0):
                    conn.commit()
                    print(f"[asistencia] Insertadas: {total_rows}", flush=True)
    conn.commit()
    print(f"Asistencias insertadas: {total_rows}", flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Seed sintético para esquema legacy (Postgres)")
    ap.add_argument("--truncate", action="store_true", help="TRUNCATE tablas antes de sembrar")
    ap.add_argument("--no-asistencia", action="store_true", help="No generar asistencia")
    ap.add_argument("--no-ventas", action="store_true", help="No generar ventas")
    ap.add_argument("--months", type=int, default=12, help="Meses hacia atrás (default 12)")
    ap.add_argument("--lots-min", type=int, default=10, help="Mín. lotes por día hábil (default 10)")
    ap.add_argument("--lots-max", type=int, default=20, help="Máx. lotes por día hábil (default 20)")
    args = ap.parse_args(argv)

    url = os.environ.get("DATABASE_URL") or os.environ.get("database_url")
    if not url:
        print("Error: definí DATABASE_URL", file=sys.stderr)
        return 1
    dsn = normalize_dsn(url)

    print(f"Conectando a Postgres: {dsn}")
    with psycopg.connect(dsn) as conn:
        conn.execute("SELECT 1")
        print("Conexión OK.")

        if args.truncate:
            truncate_targets(conn)
            conn.commit()
            print("Tablas truncadas.")

        end = date.today()
        start = end - timedelta(days=int(args.months * 30.4))
        workdays = business_days(start, end)

        operarios = fetch_operario_ids(conn)
        # Lotes + producción con commits intermedios y progreso
        lotes = seed_lotes_y_produccion(
            conn,
            workdays,
            args.lots_min,
            args.lots_max,
            operarios,
            commit_every_days=5,
            verbose=True,
        )

        ventas_pend = simulate_merma_y_consumo(lotes)
        update_lotes_stock(conn, lotes)

        if not args.no_ventas:
            seed_ventas(conn, workdays, ventas_pend, commit_every_rows=1000, verbose=True)

        if not args.no_asistencia:
            seed_asistencia(conn, start, end, verbose=True)

        print("Seed sintético finalizado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

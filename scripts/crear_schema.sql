-- Bloque de limpieza:
-- Se eliminan las tablas en orden inverso a su creación para evitar errores de dependencias (foreign keys).
-- 'IF EXISTS' previene errores si el script se ejecuta y las tablas no existen.
DROP TABLE IF EXISTS asistencia;
DROP TABLE IF EXISTS produccion;
DROP TABLE IF EXISTS venta;
DROP TABLE IF EXISTS lote;
DROP TABLE IF EXISTS empleado;
DROP TABLE IF EXISTS rol;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS embedding;

-- Bloque de creación:
-- Se crean todas las tablas desde cero, asegurando una estructura limpia.

CREATE TABLE IF NOT EXISTS producto (
  id_producto INTEGER PRIMARY KEY, -- Clave primaria autoincremental
  nombre TEXT NOT NULL,
  precio NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS lote (
  id_lote INTEGER PRIMARY KEY,
  id_producto INTEGER REFERENCES producto(id_producto), -- Clave foránea que enlaza con la tabla 'producto'
  cantidad NUMERIC, -- Este campo representará el stock actual del lote
  fecha_ingreso DATE,
  fecha_vto DATE
);

CREATE TABLE IF NOT EXISTS rol (
  id_rol INTEGER PRIMARY KEY,
  nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empleado (
  id_empleado INTEGER PRIMARY KEY,
  nombre TEXT,
  apellido TEXT,
  documento TEXT,
  id_rol INTEGER REFERENCES rol(id_rol) -- Clave foránea que enlaza con la tabla 'rol'
);

CREATE TABLE IF NOT EXISTS produccion (
  id_produccion INTEGER PRIMARY KEY,
  id_lote INTEGER REFERENCES lote(id_lote), -- Clave foránea que enlaza con el lote producido
  id_empleado INTEGER REFERENCES empleado(id_empleado), -- Clave foránea que enlaza con el empleado que produjo
  fecha_prod DATE,
  cantidad_out NUMERIC, -- Cantidad original con la que se creó el lote
  tiempo_horas NUMERIC
);

CREATE TABLE IF NOT EXISTS cliente (
  id_cliente INTEGER PRIMARY KEY,
  nombre TEXT,
  documento TEXT,
  direccion TEXT
);

CREATE TABLE IF NOT EXISTS venta (
  id_venta INTEGER PRIMARY KEY,
  id_cliente INTEGER REFERENCES cliente(id_cliente), -- Clave foránea que enlaza con el cliente
  id_producto INTEGER REFERENCES producto(id_producto), -- Clave foránea que enlaza con el producto vendido
  cantidad NUMERIC,
  fecha_venta DATE
);

CREATE TABLE IF NOT EXISTS asistencia (
  id_empleado INTEGER REFERENCES empleado(id_empleado), -- Clave foránea que enlaza con el empleado
  fecha DATETIME NOT NULL,
  tipo TEXT CHECK (tipo IN ('entrada', 'salida')) NOT NULL -- Restricción para que solo acepte 'entrada' o 'salida'
);

CREATE TABLE embedding (
    id_embedding INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado INTEGER NOT NULL REFERENCES empleado(id_empleado),
    embedding_data TEXT NOT NULL
);
-- AVISO: Legacy (SQLite). No usar para inicializar Postgres del backend actual.
-- Para el backend FastAPI + Postgres usar: scripts/postgres_init.sql

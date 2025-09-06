-- Esquema Postgres compatible con la lógica original (tablas legacy)
-- Mantiene nombres y columnas: rol, empleado, cliente, producto, lote,
-- produccion, venta, asistencia, embedding.

DROP TABLE IF EXISTS asistencia CASCADE;
DROP TABLE IF EXISTS produccion CASCADE;
DROP TABLE IF EXISTS venta CASCADE;
DROP TABLE IF EXISTS lote CASCADE;
DROP TABLE IF EXISTS empleado CASCADE;
DROP TABLE IF EXISTS rol CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS producto CASCADE;
DROP TABLE IF EXISTS embedding CASCADE;

CREATE TABLE IF NOT EXISTS producto (
  id_producto SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  precio NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS lote (
  id_lote SERIAL PRIMARY KEY,
  id_producto INTEGER REFERENCES producto(id_producto),
  cantidad NUMERIC,
  fecha_ingreso DATE,
  fecha_vto DATE
);

CREATE TABLE IF NOT EXISTS rol (
  id_rol SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empleado (
  id_empleado SERIAL PRIMARY KEY,
  nombre TEXT,
  apellido TEXT,
  documento TEXT,
  id_rol INTEGER REFERENCES rol(id_rol)
);

CREATE TABLE IF NOT EXISTS produccion (
  id_produccion SERIAL PRIMARY KEY,
  id_lote INTEGER REFERENCES lote(id_lote),
  id_empleado INTEGER REFERENCES empleado(id_empleado),
  fecha_prod DATE,
  cantidad_out NUMERIC,
  tiempo_horas NUMERIC
);

CREATE TABLE IF NOT EXISTS cliente (
  id_cliente SERIAL PRIMARY KEY,
  nombre TEXT,
  documento TEXT,
  direccion TEXT
);

CREATE TABLE IF NOT EXISTS venta (
  id_venta SERIAL PRIMARY KEY,
  id_cliente INTEGER REFERENCES cliente(id_cliente),
  id_producto INTEGER REFERENCES producto(id_producto),
  cantidad NUMERIC,
  fecha_venta DATE
);

CREATE TABLE IF NOT EXISTS asistencia (
  id_empleado INTEGER REFERENCES empleado(id_empleado),
  fecha TIMESTAMP NOT NULL,
  tipo TEXT CHECK (tipo IN ('entrada', 'salida')) NOT NULL
);

CREATE TABLE IF NOT EXISTS embedding (
    id_embedding SERIAL PRIMARY KEY,
    id_empleado INTEGER NOT NULL REFERENCES empleado(id_empleado),
    embedding_data TEXT NOT NULL
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_empleado_documento ON empleado(documento);
CREATE INDEX IF NOT EXISTS idx_asistencia_emp_fecha ON asistencia(id_empleado, fecha);


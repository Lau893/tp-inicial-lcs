import sqlite3
import os
import sys
import random
from datetime import datetime, timedelta

# ==============================================================================
# CONFIGURACIÓN DE CONSTANTES GLOBALES
# ==============================================================================
DB_FILENAME = 'gestion_produccion.db'
SCHEMA_FILENAME = 'crear_schema.sql'
INSERTS_FILENAME = 'inserts.sql'

# ==============================================================================
# FUNCIONES DE GENERACIÓN DE DATOS DINÁMICOS
# ==============================================================================

def generate_asistencia_sql():
    """
    Genera sentencias SQL para mockear los datos de la tabla de asistencia,
    asegurando que ningún empleado tenga más de 5 llegadas tarde en total.
    
    Returns:
        str: Un string con todas las sentencias INSERT para la asistencia.
    """
    print("Generando datos de asistencia con un límite de 5 llegadas tarde por empleado...")
    
    employee_ids = list(range(1, 17))
    
    # --- LÓGICA DE LÍMITE DE LLEGADAS TARDE ---
    # Se crea un diccionario para contar las llegadas tarde de cada empleado.
    llegadas_tarde_contador = {emp_id: 0 for emp_id in employee_ids}
    MAX_LLEGADAS_TARDE = 5
    
    # Se genera un historial de un año hasta la fecha actual.
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    num_days = (end_date - start_date).days
    simulation_days = [start_date + timedelta(days=i) for i in range(num_days + 1)]
    
    sql_inserts_list = []

    for day in simulation_days:
        if day.weekday() >= 5: # Omitir fines de semana
            continue
        for emp_id in employee_ids:
            # Simular ausencias
            if random.random() < 0.10:
                continue
            
            # --- LÓGICA DE CONTROL DE PUNTUALIDAD ---
            # Se verifica si el empleado ya alcanzó su límite de llegadas tarde.
            if llegadas_tarde_contador[emp_id] >= MAX_LLEGADAS_TARDE:
                # Si ya alcanzó el límite, se fuerza a que llegue a tiempo o temprano.
                entry_variation = random.randint(-10, 0)
            else:
                # Si aún no alcanza el límite, se permite una variación aleatoria.
                # Se ajusta la probabilidad para que las llegadas tarde sean menos frecuentes.
                if random.random() < 0.03: # Probabilidad baja (3%) de llegar tarde en un día dado
                    entry_variation = random.randint(1, 15)
                else:
                    entry_variation = random.randint(-10, 0)

            # Si la variación resultó en una llegada tarde, se incrementa el contador.
            if entry_variation > 0:
                llegadas_tarde_contador[emp_id] += 1
            
            check_in_time = datetime(day.year, day.month, day.day, 8, 0, 0) + timedelta(minutes=entry_variation)
            
            # La hora de salida se mantiene con una variación mínima.
            exit_variation = random.randint(-5, 5)
            check_out_time = datetime(day.year, day.month, day.day, 17, 0, 0) + timedelta(minutes=exit_variation)
            
            sql_inserts_list.append(f"INSERT INTO asistencia (id_empleado, fecha, tipo) VALUES ({emp_id}, '{check_in_time.strftime('%Y-%m-%d %H:%M:%S')}', 'entrada');")
            sql_inserts_list.append(f"INSERT INTO asistencia (id_empleado, fecha, tipo) VALUES ({emp_id}, '{check_out_time.strftime('%Y-%m-%d %H:%M:%S')}', 'salida');")
    
    print(f"Se generaron {len(sql_inserts_list)} registros de asistencia.")
    # Imprimimos el contador final para verificar que la lógica funcionó.
    print("Contador final de llegadas tarde por empleado:", llegadas_tarde_contador)
    return "\n".join(sql_inserts_list)

def generate_lote_venta_produccion_sql():
    """
    Genera sentencias SQL para mockear lotes, producción y ventas, asegurando
    que la merma (stock no vendido) por producto se encuentre entre un 10% y 30%.
    
    Returns:
        str: Un string con todas las sentencias INSERT y UPDATE necesarias.
    """
    print("Generando datos de lotes, producción y ventas con merma controlada...")
    product_ids = list(range(1, 11))
    client_ids = list(range(1, 41))
    operario_ids = list(range(3, 15))

    # --- Configuración del Período de Simulación ---
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    simulation_days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    work_days = [day for day in simulation_days if day.weekday() < 5]

    # --- Estructuras de Datos para la Simulación ---
    lotes_en_memoria = {}
    produccion_total = {p_id: 0 for p_id in product_ids}
    lote_id_counter = 1
    sql_lote_inserts, sql_produccion_inserts, sql_venta_inserts, sql_lote_updates = [], [], [], []

    # --- FASE 1: Simulación de toda la Producción ---
    print("Fase 1: Simulando producción de un año...")
    for day in work_days:
        num_nuevos_lotes = random.randint(10, 20)
        for _ in range(num_nuevos_lotes):
            id_producto = random.choice(product_ids)
            cantidad = random.randint(500, 2500)
            fecha_ingreso = day.strftime('%Y-%m-%d')
            fecha_vto = (day + timedelta(days=random.randint(90, 180))).strftime('%Y-%m-%d')
            
            # Guardar lote y registrar producción total
            lotes_en_memoria[lote_id_counter] = {'id_producto': id_producto, 'cantidad': cantidad, 'fecha_ingreso': fecha_ingreso}
            produccion_total[id_producto] += cantidad
            
            sql_lote_inserts.append(f"INSERT INTO lote (id_lote, id_producto, cantidad, fecha_ingreso, fecha_vto) VALUES ({lote_id_counter}, {id_producto}, {cantidad}, '{fecha_ingreso}', '{fecha_vto}');")
            id_empleado_prod = random.choice(operario_ids)
            tiempo_horas = round(random.uniform(4.0, 8.0), 2)
            sql_produccion_inserts.append(f"INSERT INTO produccion (id_lote, id_empleado, fecha_prod, cantidad_out, tiempo_horas) VALUES ({lote_id_counter}, {id_empleado_prod}, '{fecha_ingreso}', {cantidad}, {tiempo_horas});")
            lote_id_counter += 1
            
    # --- FASE 2: Simulación de Ventas Dirigida por Objetivo ---
    print("Fase 2: Calculando y simulando ventas para alcanzar merma objetivo...")
    # Se calcula el objetivo de ventas para cada producto para que la merma esté entre 10% y 30%.
    ventas_objetivo = {
        p_id: total * random.uniform(0.70, 0.90) for p_id, total in produccion_total.items()
    }

    # Se distribuyen las ventas a lo largo del año.
    for day in work_days:
        num_ventas_dia = random.randint(25, 50)
        for _ in range(num_ventas_dia):
            # Se elige un producto que todavía tenga un objetivo de ventas pendiente.
            productos_vendibles = [p_id for p_id, objetivo in ventas_objetivo.items() if objetivo > 0]
            if not productos_vendibles:
                continue
            id_producto_venta = random.choice(productos_vendibles)
            
            # Se vende una cantidad aleatoria, sin exceder el objetivo restante.
            cantidad_venta = random.randint(5, int(min(100, ventas_objetivo[id_producto_venta])))
            
            # Se busca un lote con stock disponible usando lógica FIFO.
            lotes_disponibles = sorted([(l_id, data) for l_id, data in lotes_en_memoria.items() if data['id_producto'] == id_producto_venta and data['cantidad'] >= cantidad_venta], key=lambda item: item[1]['fecha_ingreso'])
            if not lotes_disponibles:
                continue
                
            lote_a_usar_id, _ = lotes_disponibles[0]
            id_cliente = random.choice(client_ids)
            fecha_venta = day.strftime('%Y-%m-%d')
            
            # Se registra la venta y se actualizan los contadores.
            sql_venta_inserts.append(f"INSERT INTO venta (id_cliente, id_producto, cantidad, fecha_venta) VALUES ({id_cliente}, {id_producto_venta}, {cantidad_venta}, '{fecha_venta}');")
            lotes_en_memoria[lote_a_usar_id]['cantidad'] -= cantidad_venta
            ventas_objetivo[id_producto_venta] -= cantidad_venta

    # --- FASE 3: Generación de Updates Finales ---
    print("Fase 3: Generando sentencias UPDATE para el stock final.")
    for lote_id, data in lotes_en_memoria.items():
        sql_lote_updates.append(f"UPDATE lote SET cantidad = {data['cantidad']} WHERE id_lote = {lote_id};")
    
    print(f"\nProceso de simulación completado:")
    print(f"  - Se generaron {len(sql_lote_inserts)} lotes y registros de producción.")
    print(f"  - Se generaron {len(sql_venta_inserts)} ventas para cumplir el objetivo.")
    return "\n".join(sql_lote_inserts + sql_produccion_inserts + sql_venta_inserts + sql_lote_updates)



# ==============================================================================
# FUNCIONES PRINCIPALES DE GESTIÓN DE DB
# ==============================================================================

def setup_database(db_path, *sql_scripts):
    """
    Establece la conexión con la DB y ejecuta una serie de scripts SQL.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("\nConexión a la base de datos establecida.")
        for i, script in enumerate(sql_scripts):
            if script:
                print(f"Ejecutando script #{i+1}...")
                cursor.executescript(script)
        conn.commit()
        print("Todos los scripts se ejecutaron y los cambios se guardaron exitosamente.")
        return True
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            print("Conexión a la base de datos cerrada.")

def read_sql_file(file_path):
    """
    Lee el contenido de un archivo SQL.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en {file_path}", file=sys.stderr)
        return None

def main():
    """
    Función principal que orquesta todo el proceso.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.join(project_root, DB_FILENAME)
    schema_path = os.path.join(script_dir, SCHEMA_FILENAME)
    inserts_path = os.path.join(script_dir, INSERTS_FILENAME)

    print(f"Ruta de la base de datos: {db_path}")
    
    # --- Lectura y Generación de SQL ---
    sql_schema = read_sql_file(schema_path)
    sql_static_inserts = read_sql_file(inserts_path)
    sql_asistencia = generate_asistencia_sql()
    sql_lote_venta_prod = generate_lote_venta_produccion_sql()

    # --- Ejecución ---
    if all([sql_schema, sql_static_inserts, sql_asistencia, sql_lote_venta_prod]):
        success = setup_database(db_path, sql_schema, sql_static_inserts, sql_asistencia, sql_lote_venta_prod)
        if success:
            print("\nProceso completado exitosamente.")
        else:
            print("\nEl proceso falló.", file=sys.stderr)
    else:
        print("\nNo se ejecutó ninguna acción. Faltan archivos SQL o la generación de datos falló.", file=sys.stderr)

# ==============================================================================
# PUNTO DE ENTRADA DEL SCRIPT
# ==============================================================================
if __name__ == "__main__":
    main()

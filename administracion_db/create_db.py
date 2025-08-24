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
    asegurando una distribución mensual realista de llegadas tarde.
    
    Returns:
        str: Un string con todas las sentencias INSERT para la asistencia.
    """
    print("Generando datos de asistencia con distribución mensual de retrasos...")
    
    employee_ids = list(range(1, 17))
    
    # --- LÓGICA DE PERFILES MENSUALES DE PUNTUALIDAD ---
    # Define el rango de llegadas tarde que un empleado puede tener POR MES.
    # Formato: (min_llegadas_tarde_por_mes, max_llegadas_tarde_por_mes)
    perfiles = {
        'siempre_puntual': (0, 0),
        'puntual': (0, 1),
        'ocasional': (1, 2),
        'recurrente': (2, 4)
    }
    
    # Se asigna un perfil a cada empleado.
    asignacion_perfiles = {
        1: 'siempre_puntual', 2: 'siempre_puntual', 3: 'puntual', 4: 'ocasional',
        5: 'ocasional', 6: 'recurrente', 7: 'puntual', 8: 'recurrente',
        9: 'puntual', 10: 'recurrente', 11: 'ocasional', 12: 'ocasional',
        13: 'siempre_puntual', 14: 'puntual', 15: 'puntual', 16: 'puntual'
    }
    
    # --- Configuración del Período de Simulación ---
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # --- PLANIFICACIÓN DE LLEGADAS TARDE ---
    retrasos_planificados = set()
    
    # Se itera mes por mes para planificar los retrasos
    current_date = start_date
    while current_date <= end_date:
        # Se obtienen los días laborables del mes actual
        month_work_days = []
        d = current_date
        while d.month == current_date.month and d <= end_date:
            if d.weekday() < 5:
                month_work_days.append(d)
            d += timedelta(days=1)
            
        if month_work_days:
            for emp_id in employee_ids:
                perfil = asignacion_perfiles.get(emp_id, 'puntual')
                min_retrasos, max_retrasos = perfiles[perfil]
                
                # Se decide cuántas veces llegará tarde este empleado ESTE MES.
                num_retrasos_mes = random.randint(min_retrasos, max_retrasos)
                
                if num_retrasos_mes > 0:
                    # Se eligen los días de retraso dentro de los días laborables del mes.
                    dias_de_retraso = random.sample(month_work_days, min(num_retrasos_mes, len(month_work_days)))
                    for dia in dias_de_retraso:
                        retrasos_planificados.add((dia.date(), emp_id))
        
        # Avanzar al primer día del siguiente mes
        next_month = (current_date.month % 12) + 1
        next_year = current_date.year + (1 if current_date.month == 12 else 0)
        current_date = current_date.replace(year=next_year, month=next_month, day=1)

    # --- GENERACIÓN DE REGISTROS DE ASISTENCIA ---
    sql_inserts_list = []
    all_work_days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1) if (start_date + timedelta(days=i)).weekday() < 5]

    for day in all_work_days:
        for emp_id in employee_ids:
            if random.random() < 0.10: # Simular ausencias
                continue
            
            if (day.date(), emp_id) in retrasos_planificados:
                entry_variation = random.randint(10, 20)
            else:
                entry_variation = random.randint(-10, 0)
            
            check_in_time = datetime(day.year, day.month, day.day, 8, 0, 0) + timedelta(minutes=entry_variation)
            exit_variation = random.randint(-5, 5)
            check_out_time = datetime(day.year, day.month, day.day, 17, 0, 0) + timedelta(minutes=exit_variation)
            
            sql_inserts_list.append(f"INSERT INTO asistencia (id_empleado, fecha, tipo) VALUES ({emp_id}, '{check_in_time.strftime('%Y-%m-%d %H:%M:%S')}', 'entrada');")
            sql_inserts_list.append(f"INSERT INTO asistencia (id_empleado, fecha, tipo) VALUES ({emp_id}, '{check_out_time.strftime('%Y-%m-%d %H:%M:%S')}', 'salida');")
    
    print(f"Se generaron {len(sql_inserts_list)} registros de asistencia.")
    return "\n".join(sql_inserts_list)



def generate_lote_venta_produccion_sql():
    """
    Genera sentencias SQL para mockear lotes, producción y ventas, garantizando
    una distribución realista de la merma y los vencimientos.
    
    Returns:
        str: Un string con todas las sentencias INSERT necesarias.
    """
    print("Generando datos de lotes, producción y ventas con lógica de vencimiento corregida...")
    product_ids = list(range(1, 11))
    client_ids = list(range(1, 41))
    operario_ids = list(range(3, 15))

    # --- Configuración del Período de Simulación ---
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    simulation_days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    work_days = [day for day in simulation_days if day.weekday() < 5]

    # --- Estructuras de Datos ---
    lotes_data = []
    produccion_total = {p_id: 0 for p_id in product_ids}
    sql_produccion_inserts, sql_venta_inserts, sql_lote_inserts = [], [], []

    # --- FASE 1: Simulación de toda la Producción ---
    print("Fase 1: Simulando producción de un año...")
    for day in work_days:
        num_nuevos_lotes = random.randint(10, 20)
        for _ in range(num_nuevos_lotes):
            lote_id = len(lotes_data) + 1
            id_producto = random.choice(product_ids)
            cantidad_inicial = random.randint(500, 2500)
            fecha_ingreso = day.strftime('%Y-%m-%d')
            fecha_vto = (day + timedelta(days=random.randint(90, 180))).strftime('%Y-%m-%d')
            
            lotes_data.append({
                'id_lote': lote_id, 'id_producto': id_producto, 
                'cantidad_inicial': cantidad_inicial, 'cantidad_final': cantidad_inicial,
                'fecha_ingreso': fecha_ingreso, 'fecha_vto': fecha_vto
            })
            produccion_total[id_producto] += cantidad_inicial
            
            id_empleado_prod = random.choice(operario_ids)
            tiempo_horas = round(random.uniform(4.0, 8.0), 2)
            sql_produccion_inserts.append(f"INSERT INTO produccion (id_lote, id_empleado, fecha_prod, cantidad_out, tiempo_horas) VALUES ({lote_id}, {id_empleado_prod}, '{fecha_ingreso}', {cantidad_inicial}, {tiempo_horas});")
            
    # --- FASE 2: Cálculo del Estado Final del Inventario con Venta Aleatoria ---
    print("Fase 2: Calculando stock final con consumo de lotes aleatorio...")
    total_vendido_por_producto = {p_id: 0 for p_id in product_ids}
    
    for p_id, total_producido in produccion_total.items():
        if total_producido == 0: continue
        
        merma_deseada = random.uniform(0.10, 0.30)
        unidades_a_vender = total_producido * (1 - merma_deseada)
        
        # --- CAMBIO CLAVE: Se obtienen los lotes y se desordenan ---
        indices_lotes_producto = [i for i, lote in enumerate(lotes_data) if lote['id_producto'] == p_id]
        random.shuffle(indices_lotes_producto) # Esto simula un consumo de stock no perfecto (no FIFO)
        
        for i in indices_lotes_producto:
            if unidades_a_vender <= 0: break
            
            cantidad_a_tomar = min(lotes_data[i]['cantidad_final'], unidades_a_vender)
            
            lotes_data[i]['cantidad_final'] -= cantidad_a_tomar
            unidades_a_vender -= cantidad_a_tomar
            total_vendido_por_producto[p_id] += cantidad_a_tomar

    # --- FASE 3: Generación de Registros de Venta ---
    print("Fase 3: Generando registros de venta para coincidir con el stock vendido...")
    ventas_pendientes = total_vendido_por_producto.copy()
    
    for day in work_days:
        productos_con_ventas_pendientes = [p_id for p_id, cant in ventas_pendientes.items() if cant > 0]
        if not productos_con_ventas_pendientes: break
        
        for _ in range(random.randint(30, 60)):
            id_producto_venta = random.choice(productos_con_ventas_pendientes)
            max_venta = min(50, ventas_pendientes[id_producto_venta])
            if max_venta <= 0: continue
            
            cantidad_venta = random.randint(1, int(max_venta))
            
            id_cliente = random.choice(client_ids)
            fecha_venta = day.strftime('%Y-%m-%d')
            
            sql_venta_inserts.append(f"INSERT INTO venta (id_cliente, id_producto, cantidad, fecha_venta) VALUES ({id_cliente}, {id_producto_venta}, {cantidad_venta}, '{fecha_venta}');")
            ventas_pendientes[id_producto_venta] -= cantidad_venta

    # --- FASE 4: Generación de INSERTS Finales para Lotes ---
    print("Fase 4: Generando sentencias INSERT para lotes con su stock final.")
    for lote in lotes_data:
        sql_lote_inserts.append(f"INSERT INTO lote (id_lote, id_producto, cantidad, fecha_ingreso, fecha_vto) VALUES ({lote['id_lote']}, {lote['id_producto']}, {lote['cantidad_final']}, '{lote['fecha_ingreso']}', '{lote['fecha_vto']}');")
    
    print(f"\nProceso de simulación completado:")
    print(f"  - Se generaron {len(sql_produccion_inserts)} registros de producción.")
    print(f"  - Se generaron {len(sql_lote_inserts)} lotes.")
    print(f"  - Se generaron {len(sql_venta_inserts)} ventas para cumplir el objetivo de merma.")
    
    return "\n".join(sql_produccion_inserts + sql_lote_inserts + sql_venta_inserts)




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

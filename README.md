=
    PROYECTO DE SIMULACIÓN Y ANÁLISIS DE DATOS DE PRODUCCIÓN
=

Fecha de Creación: 24 de Agosto de 2025
Versión: 2.0

----------------------------------------------------------------------
1. DESCRIPCIÓN GENERAL
----------------------------------------------------------------------

**Objetivo del Negocio:**
Este proyecto simula un año de operaciones de una empresa de producción para generar un conjunto de datos robusto y coherente. El objetivo final es analizar estos datos para extraer métricas de rendimiento clave (KPIs) que ayuden a responder preguntas de negocio sobre eficiencia operativa, gestión de inventario, recursos humanos y rendimiento de ventas.

**Flujo de Trabajo:**
El proyecto se divide en dos fases principales:

1.  **Generación de Datos (Mockeo):** Un script de Python orquesta la creación de una base de datos SQLite y la puebla con datos simulados que siguen reglas de negocio predefinidas para garantizar su realismo y coherencia.

2.  **Análisis de Datos:** Una Jupyter Notebook se utiliza para explorar los datos generados, realizar análisis estadísticos y crear visualizaciones que permitan interpretar los resultados y tomar decisiones informadas.

----------------------------------------------------------------------
2. ESTRUCTURA DEL PROYECTO
----------------------------------------------------------------------

/ (Carpeta Raíz del Proyecto)
|
|-- administracion_db/
|   |-- crear_schema.sql        # Archivo SQL. Define la estructura de la base de datos (sentencias CREATE TABLE).
|   |-- create_db.py            # Script Python. Orquestador principal que lee los archivos SQL, genera datos dinámicos y construye la base de datos.
|   `-- inserts.sql             # Archivo SQL. Contiene los datos maestros iniciales (catálogo de productos, roles, lista de empleados, etc.).
|
|-- analisis_datos.ipynb        # Jupyter Notebook. Contiene el código de análisis y las visualizaciones.
|
|-- gestion_produccion.db       # Archivo de Base de Datos. Generado por `create_db.py`, contiene todos los datos simulados.
|
`-- README.txt                  # Este archivo de documentación.

----------------------------------------------------------------------
3. GENERACIÓN DE LA BASE DE DATOS (El Proceso de Mockeo)
----------------------------------------------------------------------

**3.a - Creación de la Base de Datos y Estructura**

El script `create_db.py` lee el archivo `crear_schema.sql` para definir la arquitectura de la base de datos. Se eligió **SQLite** por su simplicidad y portabilidad, ya que toda la base de datos reside en un único archivo (`gestion_produccion.db`). Esto facilita su consulta con herramientas externas como "DB Browser for SQLite" o extensiones de Visual Studio Code como "SQLite". El script primero elimina las tablas existentes (`DROP TABLE`) para garantizar una reconstrucción limpia en cada ejecución.

**3.b - El Proceso de Mockeo (Población de Datos)**

Tras crear la estructura e insertar los datos estáticos de `inserts.sql`, el script genera los datos transaccionales de un año. Este proceso es el núcleo de la simulación y se ha diseñado cuidadosamente para que los datos sean coherentes:

* **`generate_asistencia_sql()`**: Esta función simula los registros de asistencia. Para evitar una aleatoriedad poco realista, se implementó una lógica de control estricta:
    * **Límite de Impuntualidad:** Se establece un máximo de 5 llegadas tarde por empleado para todo el año.
    * **Control por Contador:** Un contador interno rastrea las llegadas tarde de cada empleado. Mientras no se alcance el límite, existe una probabilidad baja (3%) de generar un retraso. Al alcanzar el límite, el script fuerza que todas las futuras llegadas de ese empleado sean puntuales o tempranas. Esto crea una distribución de puntualidad mucho más creíble.

* **`generate_lote_venta_produccion_sql()`**: Esta función simula el ciclo de producción y ventas, el cual es propenso a desequilibrios. Para garantizar que la **merma** (stock no vendido) se mantenga en un rango de negocio realista (10%-30%), se implementó una estrategia en dos fases:
    1.  **Fase 1 (Simulación de Producción):** Se simula toda la producción de un año, calculando al final el inventario total fabricado para cada producto.
    2.  **Fase 2 (Simulación de Ventas Dirigida):** Conociendo la producción total, se calcula un **objetivo de ventas** para cada producto (entre el 70% y 90% de lo producido). Luego, el script distribuye de forma inteligente estas ventas a lo largo del año, asegurando que se consuma el stock de manera coherente y se cumpla el objetivo de merma.

----------------------------------------------------------------------
4. ANÁLISIS DE DATOS EN JUPYTER NOTEBOOK
----------------------------------------------------------------------

**¿Por qué usar Jupyter Notebooks en VS Code?**

Visual Studio Code ofrece un soporte nativo excelente para Jupyter Notebooks, combinando la interactividad de las celdas de una notebook con la potencia de un IDE profesional (control de versiones, depuración, etc.). Esto permite un flujo de trabajo integrado para el análisis exploratorio y la comunicación de resultados.

**Librerías Utilizadas:**

* **Pandas:** Es la herramienta central para cargar los datos de la base de datos en **DataFrames**, que son tablas en memoria optimizadas para la limpieza, transformación, filtrado y agregación de datos.
* **NumPy:** Proporciona el soporte para operaciones numéricas eficientes, siendo la base sobre la que se construye Pandas.
* **Matplotlib y Seaborn:** Se usan para la visualización. Matplotlib ofrece control granular, mientras que Seaborn facilita la creación de gráficos estadísticos complejos y estéticamente agradables.

**Análisis Realizados en la Notebook:**

1.  **Análisis de Desperdicios:** Responde a la pregunta: "¿Cuánto dinero estamos perdiendo en productos que vencen en el almacén?". Se identifican los lotes expirados con stock y se calcula el valor monetario de la pérdida.
2.  **Análisis de Asistencia:** Responde a: "¿Cómo es la puntualidad de nuestro equipo?". Se analizan los registros de entrada de un mes específico para medir el retraso promedio y la frecuencia de llegadas tarde por empleado.
3.  **Análisis de Producción:** Responde a: "¿Cuál es la eficiencia de nuestra producción y quiénes son nuestros operarios más productivos?". Se mide la merma promedio por producto y se cuantifican las unidades totales fabricadas por cada operario.
4.  **Análisis de Ventas:** Responde a: "¿Qué productos debemos potenciar?". Se identifican los productos estrella, tanto por volumen de unidades vendidas como por los ingresos totales que generan.

----------------------------------------------------------------------
5. CÓMO USAR ESTE PROYECTO EN VISUAL STUDIO CODE
----------------------------------------------------------------------

**Paso 1: Requisitos Previos**
* Tener Python 3 instalado en tu sistema.
* Tener Visual Studio Code instalado.
* Instalar la extensión oficial de **Python** de Microsoft en VS Code.

**Paso 2: Configuración**
1.  Abre la carpeta del proyecto en Visual Studio Code.
2.  Abre el explorador de extensiones (`Ctrl + Shift + X`).
3.  Busca e instala la extensión **Jupyter** de Microsoft.

No es necesario realizar ninguna otra instalación manual, ya que la primera celda de la Jupyter Notebook (`analisis_datos.ipynb`) contiene los comandos `pip install` para descargar automáticamente todas las librerías necesarias.

**Paso 3: Generar la Base de Datos**
1.  Abre una nueva terminal integrada en VS Code (`Ctrl + Shift + Ñ`).
2.  Ejecuta el script de creación:
    `python administracion_db\create_db.py`

Este comando creará (o recreará) el archivo `gestion_produccion.db` en la carpeta raíz del proyecto.

**Paso 4: Realizar el Análisis**
1.  En el explorador de archivos de VS Code, haz clic en `analisis_datos.ipynb`.
2.  VS Code abrirá la interfaz de Jupyter Notebook.
3.  Ejecuta la primera celda para instalar las dependencias.
4.  Ejecuta las celdas restantes en orden haciendo clic en el botón de "Play" (▶️) que aparece a la izquierda de cada una, o usando el atajo `Shift + Enter`.

# PROYECTO DE PRODUCCIÓN INDUSTRIA ALIMENTICIA

----------------------------------------------------------------------
1. DESCRIPCIÓN GENERAL
----------------------------------------------------------------------

Este proyecto tiene un doble propósito:

1.  **Generación de Datos (Mockeo):** Simular un año de operaciones de una empresa de producción para generar un conjunto de datos robusto y coherente. El objetivo es poder analizar estos datos para extraer métricas de rendimiento clave (KPIs).

2.  **Análisis de Datos:** Utilizar una Jupyter Notebook para explorar los datos generados, realizar análisis estadísticos y crear visualizaciones que permitan interpretar los resultados.

3.  **Aplicación Web Interactiva:** Consumir los datos de los empleados generados para alimentar una aplicación web funcional, construida con una arquitectura moderna, que permite el registro y reconocimiento facial en tiempo real.

----------------------------------------------------------------------
2. ESTRUCTURA DEL PROYECTO
----------------------------------------------------------------------
```text
/ (Carpeta Raíz del Proyecto)
|
|-- data/
|   └── gestion_produccion.db     # Base de Datos SQLite, generada por los scripts.
|
|-- frontend/
|   ├── src/                      # Código fuente de la aplicación React.
|   ├── Dockerfile                # Define el entorno para el contenedor del frontend.
|   └── package.json              # Dependencias del frontend.
|
|-- notebooks/
|   └── analisis_datos.ipynb      # Jupyter Notebook con el análisis de datos.
|
|-- scripts/
|   |-- crear_schema.sql          # Define la estructura de la base de datos.
|   |-- create_db.py              # Orquestador que genera la base de datos.
|   └── inserts.sql               # Contiene los datos maestros iniciales.
|
|-- Dockerfile                    # Define el entorno para el contenedor del backend.
|
|-- docker-compose.yml            # Orquesta la ejecución de la aplicación web.
|
└── README.md                     # Este archivo de documentación.
```
----------------------------------------------------------------------
3. GENERACIÓN DE LA BASE DE DATOS (El Proceso de Mockeo)
----------------------------------------------------------------------

3.a - Creación de la Base de Datos y Estructura

El script `scripts/create_db.py` lee el archivo `scripts/crear_schema.sql` para definir la arquitectura de la base de datos. Se eligió SQLite por su simplicidad y portabilidad. El script primero elimina las tablas existentes (DROP TABLE) para garantizar una reconstrucción limpia en cada ejecución.

3.b - El Proceso de Mockeo (Población de Datos)

Tras crear la estructura e insertar los datos estáticos de `scripts/inserts.sql`, el script genera los datos transaccionales de un año. Este proceso es el núcleo de la simulación y se ha diseñado cuidadosamente para que los datos sean coherentes:

* `generate_asistencia_sql()`: Esta función simula los registros de asistencia. Para garantizar una distribución realista de la impuntualidad, se implementó una lógica de perfiles y planificación mensual:
    * Perfiles de Puntualidad: A cada empleado se le asigna un perfil (ej: "siempre puntual", "ocasional", "recurrente").
    * Planificación Mensual: El script itera mes a mes. Para cada empleado, y según su perfil, decide cuántas veces llegará tarde ese mes en particular. Luego, distribuye esos retrasos en días aleatorios dentro de ese mes.

* `generate_lote_venta_produccion_sql()`: Esta función simula el ciclo de producción y ventas. Para garantizar que la merma (stock no vendido) se mantenga en un rango de negocio realista (10%-30%), se implementó una estrategia en cuatro fases que primero simula toda la producción del año y luego genera ventas dirigidas para consumir el stock de manera coherente.

----------------------------------------------------------------------
4. ANÁLISIS DE DATOS EN JUPYTER NOTEBOOK
----------------------------------------------------------------------

Visual Studio Code ofrece un soporte nativo excelente para Jupyter Notebooks, combinando la interactividad de las celdas con la potencia de un IDE profesional.

Librerías Utilizadas:

* **Pandas:** Es la herramienta central para cargar los datos de la base de datos en DataFrames.
* **NumPy:** Proporciona el soporte para operaciones numéricas eficientes.
* **Matplotlib y Seaborn:** Se usan para la visualización de datos.

Análisis Realizados en la Notebook:

1.  **Análisis de Desperdicios:** Responde a la pregunta: "¿Qué productos y cuánto estamos perdiendo por vencimiento?".
2.  **Análisis de Asistencia:** Responde a: "¿Cómo es la puntualidad de nuestro equipo?".
3.  **Análisis de Producción:** Responde a: "¿Cuál es la eficiencia de nuestra producción y quiénes son nuestros operarios más productivos?".
4.  **Análisis de Ventas:** Responde a: "¿Qué productos y tendencias debemos potenciar?".

----------------------------------------------------------------------
5. CÓMO EJECUTAR EL PROYECTO
----------------------------------------------------------------------

### 5.1. Aplicación Web de Reconocimiento Facial (Método Principal)

Este método utiliza Docker para levantar la aplicación interactiva completa (frontend y backend).

-   **Requisitos Previos:** Tener **Docker** y **Docker Compose** instalados.
-   **Pasos:**
    1.  Abre una terminal en la carpeta raíz del proyecto.
    2.  Ejecuta el comando: `docker-compose up --build`
    3.  Accede a la aplicación en tu navegador en: `http://localhost:3000`
    4.  Para detener la aplicación, presiona `Ctrl + C` o ejecuta `docker-compose down`.

### 5.2. Simulación y Análisis de Datos (Uso Original)

Este método permite ejecutar los scripts originales de forma manual, sin Docker.

-   **Requisitos Previos:** Tener Python 3 y la extensión de Jupyter para VS Code instalados.
-   **Paso 1: Generar la Base de Datos**
    -   En una terminal, ejecuta: `python scripts/create_db.py`
    -   Esto creará o recreará el archivo `data/gestion_produccion.db`.
-   **Paso 2: Realizar el Análisis**
    -   Abre el archivo `notebooks/analisis_datos.ipynb` en VS Code.
    -   Ejecuta las celdas para ver el análisis de datos.

----------------------------------------------------------------------
6. ARQUITECTURA DE DATOS
----------------------------------------------------------------------
El siguiente diagrama entidad-relación ilustra la estructura de la base de datos generada:

<img width="804" height="657" alt="image" src="https://github.com/user-attachments/assets/cd322a31-fec1-4421-9a55-08bcb30765c0" />

----------------------------------------------------------------------
7. ARQUITECTURA DE LA APLICACIÓN WEB
----------------------------------------------------------------------

La aplicación web se construye sobre una arquitectura de microservicios contenerizados:

-   **Backend (API del Servidor):**
    -   **Tecnología:** Python 3.10 con FastAPI.
    -   **Responsabilidad:** Conectarse a la base de datos `gestion_produccion.db` y exponer una API para registrar y reconocer los rostros de los empleados.

-   **Frontend (Interfaz de Usuario):**
    -   **Tecnología:** React.js.
    -   **Responsabilidad:** Proveer una interfaz de usuario avanzada con un sistema de pestañas para separar el modo de "Registro" del modo de "Reconocimiento en Tiempo Real".

-   **Comunicación y Orquestación:**
    -   **Docker Compose:** Orquesta los contenedores y crea una red virtual para que se comuniquen.
    -   **Proxy de React:** La comunicación desde el navegador al backend se logra a través del proxy de desarrollo de React, configurado en `frontend/package.json` para redirigir las peticiones a `http://backend:8000`.


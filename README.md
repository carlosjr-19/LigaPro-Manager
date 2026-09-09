# LigaPro Manager

Sistema profesional de gestiÃ³n de ligas de fÃºtbol desarrollado con Python y Flask. DiseÃ±ado para simplificar la administraciÃ³n de torneos, desde la creaciÃ³n de equipos hasta la generaciÃ³n de reportes y credenciales.

## ð CaracterÃ­sticas Principales

### ð GestiÃ³n Deportiva
*   **Ligas y Torneos:** Crea y administra mÃºltiples ligas con configuraciones personalizadas.
*   **Equipos y Jugadores:** Registro completo con fotos, estadÃ­sticas y perfiles detallados.
*   **Canchas:** AsignaciÃ³n de canchas especÃ­ficas para los encuentros.

### ð Competencia
*   **Calendario Inteligente:** Vista de matriz y nueva agrupaciÃ³n **Por Fechas** para programaciÃ³n rÃ¡pida.
*   **Resultados en Vivo:** ActualizaciÃ³n de marcadores con colores dinÃ¡micos por resultado.
*   **Liguilla (Playoffs):** GeneraciÃ³n automÃ¡tica de cruces interactivos en formato de **Llaves (Brackets)**, con soporte para Repechajes, Cuartos y ahora **Octavos de Final**.

### ð Reportes y Credenciales
*   **Reportes de Resumen:** VisualizaciÃ³n e imÃ¡genes de tabla, prÃ³ximos partidos y resultados recientes con personalizaciÃ³n premium (colores, tamaÃ±os).
*   **Credenciales de Jugador:** GeneraciÃ³n de credenciales imprimibles con fotos y logos de liga.

### ð¥ Roles de Usuario
*   **Gratuito:** GestiÃ³n bÃ¡sica de ligas.
*   **Premium / Ultra:**
    *   Ligas ilimitadas.
    *   PersonalizaciÃ³n de reportes avanzada (colores por resultado, fecha y cancha).
    *   EstadÃ­sticas e Informes financieros detallados con **Filtros MÃºltiples** (selecciÃ³n de mÃºltiples ligas y canchas simultÃ¡neamente) (Ultra).
    *   **Prioridad de Privilegios:** Los usuarios Ultra disfrutan de todas las funciones Premium.

## ð ï¸ TecnologÃ­as

*   **Backend:** Python 3, Flask, SQLAlchemy.
*   **Frontend:** HTML5, Jinja2, Tailwind CSS (DiseÃ±o moderno "Glassmorphism").
*   **Herramientas:** `html2canvas` y `html2pdf.js` (Exportaciones PDF/PNG asÃ­ncronas de escritorio y mÃ³vil), `requests` (Proxy).
*   **Base de Datos:** SQLite (Desarrollo), PostgreSQL (ProducciÃ³n).

## âï¸ InstalaciÃ³n y EjecuciÃ³n

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/carlosjr-19/LigaPro-Manager.git
    cd LigaPro-Manager
    ```

2.  **Crear entorno virtual (Recomendado):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r ligapro_manager/requirements.txt
    ```

4.  **Iniciar la aplicaciÃ³n:**
    ```bash
    python ligapro_manager/ligapro_manager.py
    ```

5.  **Acceso:**
    *   Abre tu navegador en `http://localhost:8001`
    *   Usuario Admin por defecto (si se inicializa): `delegado@ligapro.com` / `password123`

## ð Estructura del Proyecto

*   `ligapro_manager/`: Paquete principal de la aplicaciÃ³n.
    *   `ligapro_manager.py`: Punto de entrada del servidor.
    *   `models/`: Modelos de base de datos (League, Team, Match, User).
    *   `routes/`: LÃ³gica de las rutas (Blueprint).
    *   `templates/`: Archivos HTML con Jinja2.
    *   `static/`: Archivos CSS, JS e imÃ¡genes.
    *   `instance/`: Base de datos SQLite local.
*   `CHANGELOG.md`: Registro de cambios y versiones.
*   `VERSION`: Archivo de control de versiÃ³n actual.

## ð Ãltimas Actualizaciones (v1.0.9)

- **Mejoras UI y Modal de Eliminación (1.0.10)**: Modales personalizados y mejorados para la eliminación de partidos respetando la trazabilidad de las canchas y arreglos visuales a equipos en descanso.
- **GestiÃ³n Financiera de Adeudos (1.0.9)**: Ocultamiento automÃ¡tico de equipos sin deuda en el resumen, resaltado visual de deudores en la Agenda Global y capacidad de borrar jornadas automÃ¡ticas completas.
- **GeneraciÃ³n AutomÃ¡tica de Jornadas (1.0.8)**: Sistema inteligente con Backtracking para emparejamiento automÃ¡tico de jornadas regulares con intervalos de tiempo programables y auto-rellenado de TÃ­tulos en reportes.
- **Liguilla Manual (1.0.7)**: Posibilidad de que los dueÃ±os asignen equipos de forma 1 a 1 para los cruces de Liguilla.
- **ActualizaciÃ³n de EstÃ©tica en Reportes (1.0.6)**: Se incrementÃ³ la visibilidad de los nombres de las canchas en los reportes de rol de juegos y se ajustÃ³ el esquema de colores de la plantilla "Registro 2" de credenciales.
- **Filtros MÃºltiples de Finanzas y UI (1.0.5)**: SelecciÃ³n mÃºltiple e interactiva de ligas y canchas simultÃ¡neamente (Ultra), ademÃ¡s de optimizaciones de "arrastrar y soltar" (drag-and-drop) de ligas en mÃ³viles evitando desorganizaciÃ³n accidental.

---
Desarrollado por **CarlosJr19** | &copy; 2026 LigaPro Manager

# LigaPro Manager

Sistema profesional de gestión de ligas de fútbol desarrollado con Python y Flask. Diseñado para simplificar la administración de torneos, desde la creación de equipos hasta la generación de reportes y credenciales.

## 🚀 Características Principales

### 🏆 Gestión Deportiva
*   **Ligas y Torneos:** Crea y administra múltiples ligas con configuraciones personalizadas.
*   **Equipos y Jugadores:** Registro completo con fotos, estadísticas y perfiles detallados.
*   **Canchas:** Asignación de canchas específicas para los encuentros.

### 📅 Competencia
*   **Calendario Inteligente:** Vista de matriz y nueva agrupación **Por Fechas** para programación rápida.
*   **Resultados en Vivo:** Actualización de marcadores con colores dinámicos por resultado.
*   **Liguilla (Playoffs):** Generación automática de cruces interactivos en formato de **Llaves (Brackets)**, con soporte para Repechajes, Cuartos y ahora **Octavos de Final**.

### 📊 Reportes y Credenciales
*   **Reportes de Resumen:** Visualización e imágenes de tabla, próximos partidos y resultados recientes con personalización premium (colores, tamaños).
*   **Credenciales de Jugador:** Generación de credenciales imprimibles con fotos y logos de liga.

### 👥 Roles de Usuario
*   **Gratuito:** Gestión básica de ligas.
*   **Premium / Ultra:**
    *   Ligas ilimitadas.
    *   Personalización de reportes avanzada (colores por resultado, fecha y cancha).
    *   Estadísticas e Informes financieros detallados con **Filtros Múltiples** (selección de múltiples ligas y canchas simultáneamente) (Ultra).
    *   **Prioridad de Privilegios:** Los usuarios Ultra disfrutan de todas las funciones Premium.

## 🛠️ Tecnologías

*   **Backend:** Python 3, Flask, SQLAlchemy.
*   **Frontend:** HTML5, Jinja2, Tailwind CSS (Diseño moderno "Glassmorphism").
*   **Herramientas:** `html2canvas` y `html2pdf.js` (Exportaciones PDF/PNG asíncronas de escritorio y móvil), `requests` (Proxy).
*   **Base de Datos:** SQLite (Desarrollo), PostgreSQL (Producción).

## ⚙️ Instalación y Ejecución

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

4.  **Iniciar la aplicación:**
    ```bash
    python ligapro_manager/ligapro_manager.py
    ```

5.  **Acceso:**
    *   Abre tu navegador en `http://localhost:8001`
    *   Usuario Admin por defecto (si se inicializa): `delegado@ligapro.com` / `password123`

## 📂 Estructura del Proyecto

*   `ligapro_manager/`: Paquete principal de la aplicación.
    *   `ligapro_manager.py`: Punto de entrada del servidor.
    *   `models/`: Modelos de base de datos (League, Team, Match, User).
    *   `routes/`: Lógica de las rutas (Blueprint).
    *   `templates/`: Archivos HTML con Jinja2.
    *   `static/`: Archivos CSS, JS e imágenes.
    *   `instance/`: Base de datos SQLite local.
*   `CHANGELOG.md`: Registro de cambios y versiones.
*   `VERSION`: Archivo de control de versión actual.

## 🔄 Últimas Actualizaciones (v1.0.9)

- **Gestión Financiera de Adeudos (1.0.9)**: Ocultamiento automático de equipos sin deuda en el resumen, resaltado visual de deudores en la Agenda Global y capacidad de borrar jornadas automáticas completas.
- **Generación Automática de Jornadas (1.0.8)**: Sistema inteligente con Backtracking para emparejamiento automático de jornadas regulares con intervalos de tiempo programables y auto-rellenado de Títulos en reportes.
- **Liguilla Manual (1.0.7)**: Posibilidad de que los dueños asignen equipos de forma 1 a 1 para los cruces de Liguilla.
- **Actualización de Estética en Reportes (1.0.6)**: Se incrementó la visibilidad de los nombres de las canchas en los reportes de rol de juegos y se ajustó el esquema de colores de la plantilla "Registro 2" de credenciales.
- **Filtros Múltiples de Finanzas y UI (1.0.5)**: Selección múltiple e interactiva de ligas y canchas simultáneamente (Ultra), además de optimizaciones de "arrastrar y soltar" (drag-and-drop) de ligas en móviles evitando desorganización accidental.

---
Desarrollado por **CarlosJr19** | &copy; 2026 LigaPro Manager

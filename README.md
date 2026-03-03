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
    *   Estadísticas e Informes financieros detallados (Ultra).
    *   **Prioridad de Privilegios:** Los usuarios Ultra disfrutan de todas las funciones Premium.

## 🛠️ Tecnologías

*   **Backend:** Python 3, Flask, SQLAlchemy.
*   **Frontend:** HTML5, Jinja2, Tailwind CSS (Diseño moderno "Glassmorphism").
*   **Herramientas:** `html2canvas` (Generación de imágenes), `requests` (Proxy de imágenes).
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

## 🔄 Últimas Actualizaciones (v0.9.9.0)

- **Configuración Global por Owner**: Nuevo panel de control inteligente para dueños de ligas donde definir los colores base representativos de cada "Cancha". Todas las competencias heredarán automáticamente dichos lineamientos para ahorro de tiempo y consistencia institucional.
- **Reportes Colorizados Nativos**: El reporte de Agenda Global ahora imprime sus PDF y descarga su "Sábana" de .xlsx aplicando con precisión el color personalizado de cada predio deportivo.
- **Exportación HD Independiente (PNG)**: Además del Excel y PDF, ahora el reporte diario de Agenda ofrece separar automáticamente el tablero de partidos de cada cancha para descargar de forma simultánea múltiples imágenes limpias ideales para compartir por redes.
- **Color de Identidad de Ligas**: Integración de coloreo particular para los nombres de los torneos, reflejado en toda interfaz pública, administrativa y exportaciones fotográficas, permitiendo resaltes ultra-visuales en agendas saturadas.
- **Autollenado Financiero (v0.9.8.4)**: Para las ligas que lo configuren, el alta de nuevos encuentros cobrará automáticamente el costo de arbitraje establecido previamente para aligerar la carga operativa de las asociaciones deportivas.

---
Desarrollado por **CarlosJr19** | &copy; 2026 LigaPro Manager

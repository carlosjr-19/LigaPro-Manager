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

## 🔄 Últimas Actualizaciones (v0.9.10)

- **Suma/Resta de Puntos**: Nueva funcionalidad que permite a los administradores sumar o restar puntos a un equipo. Esta acción queda registrada en el historial de partidos con un comentario explicativo.
- **Desempate por Shutdown**: Posibilidad de designar a un ganador en partidos empatados para otorgar un reparto desigual (2 pts al ganador, 1 al perdedor) en cualquier vista de resultados.
- **Candados Premium a Nivel Capitán**: Validaciones individuales reforzadas para que solo los capitanes que han pagado su cuota puedan imprimir o descargar sus propios registros de jugadores.
- **Seguridad de Prevención de Borrado**: El panel de administrador ahora exige la contraseña base del administrador para autenticar la eliminación de cualquier usuario (propietario o capitán), blindando la plataforma contra desastres accidentales.
- **Eliminación Permanente de Discrepancias**: Los dueños de liga ahora pueden ocultar filas del Resumen General de forma definitiva. La acción se sincroniza con la base de datos, asegurando que las filas eliminadas no aparezcan en futuras consultas, reportes compartidos o exportaciones a Excel.
- **Cámara Cloudinary Directa**: Ahora los capitanes y administradores pueden capturar y subir fotos de jugadores y escudos institucionales usando directamente la cámara de su teléfono, los archivos se almacenan en un bucket nativo de Cloudinary.

---
Desarrollado por **CarlosJr19** | &copy; 2026 LigaPro Manager

# LigaPro Manager

Sistema profesional de gestión de ligas de fútbol desarrollado con Python y Flask. Diseñado para simplificar la administración de torneos, desde la creación de equipos hasta la generación de reportes y credenciales.

## 🚀 Características Principales

### 🏆 Gestión Deportiva
*   **Ligas y Torneos:** Crea y administra múltiples ligas con configuraciones personalizadas.
*   **Equipos y Jugadores:** Registro completo con fotos, estadísticas y perfiles detallados.
*   **Canchas:** Asignación de canchas específicas para los encuentros.

### 📅 Competencia
*   **Calendario Inteligente:** Vista de matriz para programación rápida de partidos.
*   **Resultados en Vivo:** Actualización de marcadores y cálculo automático de tablas de posiciones.
*   **Liguilla (Playoffs):** Generación automática de cruces (Cuartos, Semis, Final) y repechajes.

### 📊 Reportes y Credenciales
*   **Reportes Compartibles:** Genera imágenes descargables de la tabla general, resultados recientes y próximos partidos (con soporte para logos de equipos).
*   **Credenciales de Jugador:** Generación de credenciales imprimibles (PDF/Imagen) con foto y datos del jugador.

### 👥 Roles de Usuario
*   **Gratuito:** Creación de hasta 3 ligas con límites básicos.
*   **Premium (Dueño):**
    *   Ligas ilimitadas y más equipos.
    *   Personalización completa (Logos, Slogans, Colores).
    *   Estadísticas avanzadas (Goleadores, Arqueros).
    *   **Zona de Peligro:** Reinicio de temporadas y borrado de datos.
*   **Capitán:** Gestión de su propio equipo y generación de credenciales (si la liga lo permite).

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

## 🔄 Últimas Actualizaciones (v0.9.1)

*   **Diseño responsivo para dispositivos móviles:** Modificando el diseño responsivo para dispositivos móviles de la plataforma

---
Desarrollado por **CarlosJr19** | &copy; 2026 LigaPro Manager

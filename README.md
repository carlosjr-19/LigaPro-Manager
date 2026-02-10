# LigaPro Manager

Sistema completo de gestión de ligas de fútbol desarrollado con Python y Flask. Permite a los administradores crear ligas, gestionar equipos y jugadores, programar partidos, registrar resultados y generar liguillas (playoffs) automáticamente.

## 🚀 Características Principales

*   **Gestión de Ligas:** Crea y administra múltiples torneos de fútbol.
*   **Equipos y Jugadores:** Registro detallado con estadísticas.
*   **Calendario y Resultados:** Programación de partidos y actualización de marcadores en tiempo real.
*   **Tablas de Posiciones:** Cálculo automático de puntos, diferencia de goles, etc.
*   **Liguilla Automática:**
    *   Generación de cruces (Cuartos, Semifinales, Final) basado en la tabla.
    *   Soporte para Repechaje.
    *   Avance de rondas automático.
*   **Funciones Premium:**
    *   Insignia de usuario Premium.
    *   **Restablecer Temporada:** Opción destructiva para reiniciar una liga manteniendo los equipos (Solo Premium).
*   **Diseño Moderno:** Interfaz responsiva con Tailwind CSS y Glassmorphism.

## 🛠️ Tecnologías

*   **ligapro_manager:** Python 3, Flask, SQLAlchemy.
*   **Base de Datos:** SQLite (persistente en `ligapro_manager/instance/ligapro.db`).
*   **Frontend:** HTML5, Jinja2 Templates, Tailwind CSS (CDN).
*   **Autenticación:** Flask-Login, Flask-Bcrypt.

## ⚙️ Instalación y Ejecución

1.  **Requisitos:**
    *   Python 3.8 o superior.
    *   Pip (gestor de paquetes).

2.  **Instalar dependencias:**
    ```bash
    pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-cors flask-wtf email_validator
    ```

3.  **Iniciar el servidor:**
    Asegúrate de estar en la carpeta raíz del proyecto o en `ligapro_manager`:
    ```bash
    cd ligapro_manager
    python server.py
    ```

4.  **Acceso:**
    Abre tu navegador en `http://localhost:5000`.

## 📂 Estructura del Proyecto

*   `ligapro_manager/app.py`: Lógica principal, modelos de BD y rutas.
*   `ligapro_manager/server.py`: Punto de entrada del servidor.
*   `ligapro_manager/templates/`: Vistas HTML (Login, Dashboard, Detalles de Liga, etc.).
*   `ligapro_manager/static/`: Archivos estáticos (Imágenes, Iconos).
*   `ligapro_manager/instance/`: Base de datos SQLite.

## 💎 Características Premium

El sistema incluye un simulador de suscripción Premium.
*   Al activar Premium, obtienes acceso a herramientas avanzadas de configuración.
*   Editar Jugadores de equipos
*   Tener ligas ilimitadas
*   Añadir más de 12 equipos a una liga
*   Poder establecer cantidad de puntos por vicoria o empate
*   **Zona de Peligro:** Permite borrar ligas o reiniciar temporadas completas manteniendo los equipos registrados.

---
Desarrollado para la gestión profesional de torneos deportivos.
&copy; 2026 LigaPro Manager - CarlosJr19

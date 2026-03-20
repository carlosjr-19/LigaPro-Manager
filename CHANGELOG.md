## 0.12.0

Notas Privadas de Equipos y Control de Restricción para Capitanes.

- **Notas Privadas**: Ahora los dueños de liga pueden marcar notas como "Privadas". Estas notas solo son visibles para el dueño y no para los capitanes. Las notas públicas siguen siendo visibles para ambos.
- **Eliminación de Notas**: Nueva funcionalidad para eliminar notas de equipo (disponible solo para el administrador/dueño).
- **Restricción de Capitanes**: Nueva opción en configuración de liga para permitir o prohibir que los capitanes añadan jugadores.
- **Seguridad en Registros**: Si la opción de añadir jugadores está desactivada para capitanes, también se ocultan automáticamente las herramientas de generación de registros (credenciales) y botones de impresión para dicho rol.
- **Auto-Migración**: El sistema ahora detecta y añade automáticamente las nuevas columnas de base de datos (`allow_captains_add_players`, `is_public`) al iniciar la aplicación en entornos como Railway.
- **Mejora en Gráficas Semanales**: Se actualizaron las leyendas del eje X en las gráficas financieras semanales para usuarios Ultra. Ahora muestran un formato más legible: "Sem. [Nº] (DD/MM)", facilitando la interpretación de las fechas para los clientes.

## Modificado
* `ligapro_manager/models/team.py`
* `ligapro_manager/models/league.py`
* `ligapro_manager/forms/league.py`
* `ligapro_manager/routes/league.py`
* `ligapro_manager/routes/team.py`
* `ligapro_manager/routes/player.py`
* `ligapro_manager/routes/main.py`
* `ligapro_manager/templates/league_detail.html`
* `ligapro_manager/templates/team_detail.html`
* `ligapro_manager/templates/captain_dashboard.html`
* `ligapro_manager/routes/report.py`
* `ligapro_manager/ligapro_manager.py`

## 0.11.0

Refinamiento de Reportes PDF Dinámicos y Filtros Financieros por Liga.

- **Reporte PDF de Una Sola Página**: Optimización total del diseño para que todos los elementos (Cabecera, Tabla, Goleadores, Resultados y Agenda) se ajusten a una sola hoja horizontal, ideal para impresión industrial.
- **Estadísticas Enriquecidas**: Las listas de Goleadores y Arqueros ahora muestran las iniciales del equipo (3 letras en mayúsculas, ej: [DEP]) y el número de dorsal (ej: #10) para una identificación precisa.
- **Filtro por Liga en Finanzas**: El reporte de Finanzas Mensuales ahora permite filtrar por una liga específica, recalculando ingresos, egresos y ganancias netas de forma instantánea.
- **Exportaciones Inteligentes**: Tanto la exportación a Excel como la generación de imagen PNG en Finanzas ahora incluyen el nombre de la liga filtrada en los encabezados.
- **Agenda PDF de Dos Columnas**: Se eliminó el límite de 6 partidos y se implementó un sistema de flujo dinámico en dos columnas para maximizar el espacio, con horarios en color negro para legibilidad de impresión.

## Modificado
* `ligapro_manager/routes/league.py`
* `ligapro_manager/routes/report.py`
* `ligapro_manager/templates/share_report.html`
* `ligapro_manager/templates/report/financials.html`
* `ligapro_manager/templates/report/share_financials.html`

## 0.10.0

Implementación de Partidos de Práctica, Filtros Horarios Financieros y Ajustes de Puntajes.

- **Partidos de Práctica**: Nueva funcionalidad para agendar partidos que no afectan la tabla de posiciones ni estadísticas. Incluye indicadores visuales ("PRÁCTICA") en la lista de partidos, cuadro de resultados (matriz), vista por fechas, agenda global y reportes compartidos.
- **Modificación Manual de Puntajes**: Se añadió una función en el panel para que los administradores puedan sumar o restar puntos directamente a la tabla sin necesidad de crear partidos ficticios, ideal para resoluciones administrativas.
- **Filtro por Hora en Finanzas**: La Agenda Global ahora permite filtrar los partidos por un rango horario específico, facilitando el cálculo de arbitrajes y pagos para turnos parciales de canchas.
- **Nomenclatura "RG" (Regalo)**: Soporte para marcar el pago de arbitraje como "RG" (Regalo). Estos partidos no generan saldo pendiente ni deudas en el historial del equipo ni en el resumen financiero, pero se mantienen visibles en la agenda.
- **Sincronización de Matriz**: El modal del cuadro de partidos ahora incluye el toggle de "Práctica" y se sincroniza correctamente con el backend para guardar el estado.

## Modificado
* `ligapro_manager/models/match.py`
* `ligapro_manager/models/league.py`
* `ligapro_manager/routes/team.py`
* `ligapro_manager/routes/report.py`
* `ligapro_manager/routes/match.py`
* `ligapro_manager/routes/match_matrix.py`
* `ligapro_manager/routes/league.py`
* `ligapro_manager/utils/helpers.py`
* `ligapro_manager/templates/league_detail.html`
* `ligapro_manager/templates/match_form.html`
* `ligapro_manager/templates/match_result_form.html`
* `ligapro_manager/templates/report/global_schedule.html`
* `ligapro_manager/templates/share_report.html`
* `ligapro_manager/templates/report/financials.html`
* `ligapro_manager/static/js/league_detail.js`
* `ligapro_manager/static/js/report_global_schedule.js`
* `ligapro_manager/static/js/share_modal.js`
* `ligapro_manager/ligapro_manager.py`

## 0.9.10

Añadir funcionalidad para sumar o restar puntos a un equipo.

- **Suma/Resta de Puntos**: Nueva funcionalidad que permite a los administradores sumar o restar puntos a un equipo. Esta acción queda registrada en el historial de partidos con un comentario explicativo.

## Modificado
* `ligapro_manager/models/league.py`
* `ligapro_manager/routes/team.py`
* `ligapro_manager/ligapro_manager.py`
* `ligapro_manager/utils/helpers.py`
* `ligapro_manager/static/js/league_detail.js`
* `ligapro_manager/templates/league_detail.html`



## 0.9.9.9

Mejoras de competencia, restricciones avanzadas de planes y seguridad de datos.

- **Desempate por Shutdown**: Nueva funcionalidad opcional en la configuración de ligas para definir un ganador en partidos que terminan en empate, otorgándole 2 puntos al vencedor del "shutdown" y 1 punto al perdedor. Disponible en todos los formularios de resultados (lista, cuadro de matriz).
- **Protección de Funciones Premium para Capitanes**: Los botones para descargar e imprimir los expedientes oficiales de jugadores ahora requieren que el capitán haya pagado su propia cuota ($50), desvinculando la dependencia del estado premium del dueño de liga.
- **Seguridad en la Eliminación de Usuarios**: El sistema ahora demanda doble factor (confirmación con contraseña actual del Administrador) antes de ejecutar el borrado permanente de cualquier rol de usuario, evitando accidentes.

## Modificado
* `ligapro_manager/models/league.py`
* `ligapro_manager/models/match.py`
* `ligapro_manager/forms/league.py`
* `ligapro_manager/routes/league.py`
* `ligapro_manager/routes/match.py`
* `ligapro_manager/routes/match_matrix.py`
* `ligapro_manager/routes/team.py`
* `ligapro_manager/routes/admin.py`
* `ligapro_manager/utils/helpers.py`
* `ligapro_manager/templates/league_form.html`
* `ligapro_manager/templates/league_detail.html`
* `ligapro_manager/templates/match_result_form.html`
* `ligapro_manager/templates/team_detail.html`
* `ligapro_manager/templates/admin/users.html`
* `ligapro_manager/static/js/league_detail.js`
* `ligapro_manager/ligapro_manager.py`

## 0.9.9.8

Personalización Avanzada de Diseños para Reportes y Compartición de Partidos.

- **Diseños y Temas Premium**: Incorporación de un selector visual moderno en las configuraciones de la liga que le permite a dueños Premium escoger entre diseños (`Menta, Esmeralda, Ciberpunk, Granate, Naranja Oscuro y Naranja-Esmeralda`) para darle a sus descargas de reportes un toque institucional e inversivo.
- **Control Centralizado de Desarrollador**: El panel de desarrollo ahora cuenta con interruptores de permiso. El desarrollador puede otorgar o revocar individualmente el derecho de un Dueño de utilizar fondos personalizados, pudiendo forzar a que su liga utilice un estilo asignado por la administración central.
- **Despliegues Automáticos de Estilos**: Al generar reportes y descargar imágenes PNG de marcadores o tablas, la plataforma renderiza y recorta dinámicamente aplicando estos estilos seleccionados sin perder calidad visual y de manera fluida (cross-device).
- **Correcciones UI/UX**: Arreglos estructurales del Modal de Reportes, impidiendo instancias duplicadas y mejorando la integración estandarizada a nivel global en todos los selectos de la página de Detalles.

## Modificado
* `ligapro_manager/models/user.py`
* `ligapro_manager/models/league.py`
* `ligapro_manager/routes/admin.py`
* `ligapro_manager/routes/league.py`
* `ligapro_manager/routes/report.py`
* `ligapro_manager/templates/admin/users.html`
* `ligapro_manager/templates/league_detail.html`
* `ligapro_manager/templates/league_form.html`
* `ligapro_manager/templates/report/settings.html`
* `ligapro_manager/templates/share_report.html`
* `ligapro_manager/templates/report/share_global_schedule.html`

## 0.9.9.7 Implementación de Gráficas Financieras Interactivas para Usuarios Ultra.

- **Dashboard de Gráficas**: Nueva página dedicada con gráficas de línea interactivas (Chart.js) que muestran la evolución de las ganancias netas.
- **Filtros Temporales**: Posibilidad de agrupar y visualizar ganancias por Día, Semana o Mes.
- **Filtrado por Cancha**: Selector dinámico para analizar el rendimiento económico de una cancha específica o de todas en conjunto.
- **API Exclusiva**: Nueva infraestructura de API para la obtención eficiente de estadísticas financieras agregadas.

## Agregado
* `ligapro_manager/templates/report/financial_charts.html` (Nuevo)

## Modificado
* `ligapro_manager/routes/report.py`
* `ligapro_manager/templates/report.html`

## 0.9.9.6

Eliminación permanente de filas en el Resumen General.

- **Eliminación Persistente**: Se implementó la capacidad de ocultar filas de discrepancias en el Resumen General de forma definitiva. Al pulsar la "X", la elección se guarda en la base de datos vinculada al usuario.
- **Filtrado Automático**: Las filas eliminadas se omiten automáticamente tanto en la vista web como en todas las exportaciones (Imagen/PDF y Excel) sin necesidad de parámetros adicionales en el URL.
- **Nueva Infraestructura**: Creación del modelo `IgnoredDiscrepancy` para gestionar los descartes de forma eficiente y segura por cada dueño de liga.

## Modificado
* `ligapro_manager/models/ignored_discrepancy.py` (Nuevo)
* `ligapro_manager/models/__init__.py`
* `ligapro_manager/routes/report.py`
* `ligapro_manager/templates/report/summary.html`

## 0.9.9.5

Agrupamiento financiero por cancha e indicador visual de pagos de arbitraje. Modificación de edición de partidos desde agenda global para poder eliminar partido

- **Reporte Financiero "Por Cancha"**: Nueva configuración en Panel Ultra que agrupa el reporte de finanzas estructurándolo primero por Cancha, y desglosando posteriormente los días jugados. Incluye generación de subtotales independientes por establecimiento.
- **Exportaciones Agrupadas**: Al seleccionar la opción "Por Cancha", tanto la exportación a Excel (.xlsx) como la generación de imagen PNG respetan el formato agrupado (Cancha -> Fechas -> Subtotal).
- **Indicador Visual de Pagos**: En la Agenda Global, los montos de arbitraje ahora se colorean verde oscuro si el equipo cubrió el total establecido, y en rojo si existe un adeudo, agilizando la identificación de morosos. 
- **Ajustes Estéticos**: Reordenamiento de colores en el resumen general para destacar en verde el ingreso total bruto y en azul la ganancia neta.
- **Eliminar partido**: En la agenda global se implemento en editar partido la opción para eliminar el partido.
- **Credenciales Mejoradas**: Se centró el escudo y el nombre del equipo en el formato impreso de credenciales, y se configuró un ícono por defecto ("silueta de persona") para los jugadores que no tienen fotografía cargada. Además, se eliminó el código de barras y se centró la frase del registro de la liga.
- **Filtro de Fechas en Reportes**: Se agregó la funcionalidad para elegir un rango de fechas ("Desde" y "Hasta") aplicable a "***Próximos Partidos***" al momento de generar el reporte de la jornada a compartir (tanto desde Panel General como Liguilla).
- **Reporte de Jornada Limpio por Defecto**: Las casillas de Goleadores, Arqueros y Próximos Partidos ahora vienen desmarcadas por defecto al abrir el menú de Compartir / Generar Reporte. Dejando como principal información la Tabla de Posiciones.

## Modificado
* `ligapro_manager/routes/report.py`
* `ligapro_manager/routes/league.py`
* `ligapro_manager/templates/report/settings.html`
* `ligapro_manager/templates/credentials.html`
* `ligapro_manager/templates/share_modal_fragment.html`
* `ligapro_manager/templates/league_detail.html`
* `ligapro_manager/static/js/share_modal.js`
* `ligapro_manager/static/js/league_detail.js`
* `ligapro_manager/templates/report/financials.html`
* `ligapro_manager/templates/report/share_financials.html`
* `ligapro_manager/templates/report/global_schedule.html`
* `ligapro_manager/templates/report/share_global_schedule.html`
* `ligapro_manager/static/js/report_global_schedule.js`

## 0.9.9.4 

Estabilización de exportaciones y diseño responsivo en interfaces móviles para reportes y resúmenes.

- **Vistas Previas Independientes**: Se implementaron vistas dedicadas (`share_summary.html` y `share_financials.html`) para las exportaciones en imagen/PDF, lo que garantiza el formato estructurado y clásico sin que sea afectado por el tamaño de pantalla del dispositivo desde el cual se descarga.
- **Correcciones Responsivas**: Los botones de acción en las vistas de detalles y previsualizaciones (`Vista Previa PNG`, `Volver`) dejaron de usar posicionamiento estático flotante que bloqueaba la visibilidad en teléfonos móviles. Ahora se emplean selectores flex responsivos (`overflow-x-auto`) que respetan la estructura de la aplicación.
- **Ajustes de Interfaz Limpia**: Se retiró JS incrustado antiguo (`triggerMobilePrint`) causante de errores de renderización, dando paso a librerías asíncronas modernas como `html2pdf.js` y `html2canvas` para los reportes limpios, manteniendo la posibilidad de guardar fotos temáticas o PDFs con fondo blanco tradicional para impresión.

## Modificado
* `ligapro_manager/routes/report.py`
* `ligapro_manager/templates/report/summary.html`
* `ligapro_manager/templates/report/financials.html`
* `ligapro_manager/templates/report/share_summary.html` (Nuevo)
* `ligapro_manager/templates/report/share_financials.html` (Nuevo)

## 0.9.9.3

Integración nativa con Cloudinary para subida y almacenamiento de imágenes desde dispositivos móviles y web.

- **Cámara Directa**: Se inyectó la librería y flujo de Cloudinary permitiendo a capitanes y administradores subir fotos de jugadores, escudos de equipos y logos de ligas usando directamente la cámara de su teléfono móvil o seleccionando archivos locales.
- **Seguridad Backend**: Implementación de inyección de variables de entorno seguras (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_UPLOAD_PRESET`) en el motor de renderizado de Flask sin exponer dependencias ni originar brechas en el respositorio.
- **Ajustes Visuales Premium**: Expandida la zona de *Personalización Visual* dentro de Ligas Premium para incluir subidas directas del Logo.

## Modificado
* `ligapro_manager/config.py`
* `ligapro_manager/ligapro_manager.py` (context processor)
* `ligapro_manager/templates/player_form.html`
* `ligapro_manager/templates/team_form.html`
* `ligapro_manager/templates/league_form.html`
* `ligapro_manager/templates/league_detail.html`

## 0.9.9.2

- **Frase Personalizada en Credenciales**: Se añadió la posibilidad de incluir un eslogan o frase personalizada en la base de la tarjeta de jugador al imprimirse. Si se configura, la foto se adapta orgánicamente y el nombre de la liga incrementa su visibilidad.
- **Formato Oficial PVC**: Se reajustaron las medidas base de las credenciales, unificándolas globalmente a las dimensiones estándar CR80 (8.6cm x 5.4cm) para ser impresas directamente sobre tarjetas plásticas.
- **Impresión Selectiva**: Se agregó una nueva interfaz dentro de los detalles del equipo. Los capitanes dueños de liga Premium ahora encontrarán casillas de selección junto a cada jugador, permitiéndoles generar una hoja de impresión única exclusivamente con las tarjetas seleccionadas (ideal para reposiciones o registros tardíos).

## Modificado
* models/league.py
* forms/league.py
* ligapro_manager.py (migración `credential_phrase`)
* routes/league.py
* routes/team.py
* templates/league_detail.html
* templates/team_detail.html
* templates/credentials.html
* static/css/credentials.css

## 0.9.9.1
Mejoras avanzadas en los Reportes Financieros y exportaciones.

- **Filtro por Rango de Fechas**: Se adaptó el panel general de configuración (`/report/settings`) para que el dueño elija su formato favorito de consulta (Por Mes o Por Fechas). La Tarjeta de Ganancias Netas y los reportes de Exportación modificarán sus encabezados respetando el rango elegido por el usuario (Desde X, Hasta Y). Las validaciones de bases de datos ahora procesan con precisión ambas consultas cruzadas.
- **Exportación en PNG**: Se inyectó e iteró la librería visual `html2canvas` para habilitar el botón "PNG". Este botón descarga instantáneamente una captura fotográfica exacta y nítida ($resolución x2$) de todos los elementos visuales que componen el reporte con su propio color nativo sin afectar el ancho ni las proporciones al hacer scroll en el navegador. 
- **Filtro de Canchas**: Se agregó en la cabecera un nuevo selector en tiempo real que captura inteligentemente la base de datos de los complejos pre-asignados del Dueño. Permite desglosar las variables aislando una Cancha del total (o "Sin Cancha"), recabando sus datos limpios al consultar en el navegador, en Excel y en el botón PNG.
- **Optimización de Interfaz y Totales**: Se ajustó la estética móvil usando librerías nativas `.flex-col` para alinear limpiamente las dos columnas de inputs `Desde` y `Hasta`. Además se integraron nuevas sumatorias totales de las columnas individuales de Ingresos (+), y Egresos (-) para complementar el gran total de Ganancia.
- **Estabilidad de Nombres**: Se unificaron los sufijos automáticos en backend (`filename_suffix`) previniendo excepciones Python ("UnboundLocalError") durante los flujos de impresión con variables incompletas.

## Modificado
* models/user.py
* routes/report.py, ligapro_manager.py
* templates/report/settings.html
* templates/report/financials.html

## 0.9.9.0

- **Configuración Global de Reportes**: Nuevo panel exclusivo para dueños (`/report/settings`) que permite centralizar y definir el color representativo de cada cancha. Las canchas homónimas en distintas ligas heredarán automáticamente esta configuración para mantener consistencia institucional.
- **Exportación de Agenda a Imágenes (PNG)**: Nuevo formato de descarga visual. Al agrupar los partidos del día en la Agenda Global, ahora existe un botón para descargar *porciones independientes* de la sábana de partidos (separadas por cancha) en formato de imagen HD, ideal para compartir por redes sociales o WhatsApp con los administradores de los predios.
- **Personalización de Ligas**: Se habilitó la opción de que cada Liga tenga un color de texto particular para su nombre. Este color se reflejará en el Dashboard, Tablas, Agenda Global y en la propia impresión a PDF o exportación a PNG.
- **Colorización de Exportaciones Analíticas**: La exportación nativa a **Excel (.xlsx)** y a **PDF (Impresión web)** de la "Agenda Global" ahora absorben los mismos colores globales que configures para tus canchas y ligas.
- **Remodelación Arquitectónica**: Eliminación de scripts remanentes de migraciones pre-automatizadas (`alter_db_leagues.py`, etc.) ya que `bootstrap.py` ahora resuelve dinámicamente la construcción de tablas (incluyendo el nuevo modelo `OwnerCourtSetting`) en los despliegues a la nube (Railway).

## Modificado
* models/owner_settings.py (NUEVO), models/__init__.py
* routes/report.py, ligapro_manager.py
* templates/report/*.html (settings, global_schedule, share_global_schedule)
* templates/league_detail.html
* templates/report.html

## 0.9.8.4
Autocompletado de precios y ajustes en Reporte de Finanzas.

- **Autollenar Agenda Global**: Se añadió un nuevo interruptor en la configuración de precios por liga. Si está activado, los partidos nuevos generados (ya sea manuales o por liguilla) heredan automáticamente el costo de arbitraje definido para la liga, marcándose como pagados en la Agenda Global. También aplica al asignar fechas a partidos que previamente tenían costo cero.
- **Edición directa en Agenda Global**: Se agregó un ícono de edición a cada partido dentro de la Agenda Global, permitiendo modificar datos clave (cancha, equipos, hora) por cancelaciones. Al guardar, el sistema redirecciona automáticamente a la agenda para un flujo ininterrumpido.
- **Índice Numérico**: La Agenda Global ahora enumera secuencialmente cada partido por bloque de cancha para un mejor control visual.
- **Claridad de Totales**: Se mejoró la lectura de las sumatorias agregando "Total Ingresos (Local + Visita)" por encima de la ganancia neta.
- **Ajustes de Impresión/PDF**: Las vistas impresas de la Agenda Global ahora empaquetan cada cancha en una hoja nueva (salto de página) y reducen sus proporciones de forma responsiva para evitar cortes horizontales en el margen derecho. Los campos de edición son removidos de la impresión.

## Modificado
* models/league.py
* routes/report.py, routes/match.py, routes/match_matrix.py
* templates/report/config.html, templates/report/global_schedule.html, templates/match_form.html
* ligapro_manager.py (migraciones)

## Removido (Seguro de ignorar en despliegue)
* alter_db.py
* check_db_state.py

## 0.9.8.3

Mejoras de responsividad y UI en móviles.

- **Navegación en Reportes**: Se agregó scroll horizontal a los menús de navegación en la sección de reportes para evitar que se desborden en pantallas pequeñas.
- **Tarjetas de Partidos (Agenda)**: Se ajustó el diseño de las tarjetas de partidos en la vista de lista y de fechas. Los nombres largos de los equipos ahora se truncan correctamente sin empujar los marcadores fuera de la pantalla.
- **Botones de Liguilla**: Se reorganizaron los botones de "Editar / Resultado" en las llaves de Liguilla y Repechaje para que se acomoden en la parte inferior de los nombres de los equipos en vista móvil.
- **Panel de Administrador**: Se optimizó la vista de gestión de usuarios permitiendo que los botones de filtrado y búsqueda se adapten a la pantalla, y se añadió desplazamiento horizontal a todas las tablas (Usuarios, Equipos, Ligas y Dashboard) para evitar recortes en celulares.
- **Reporte para Compartir (Share View)**: La tabla de posiciones y resultados ya no se recorta verticalmente en móviles gracias al scroll panorámico. Se implementó la API nativa de "Compartir" de dispositivos móviles para agilizar la exportación de la imagen.
- **Impresión de Reportes Web en Móviles**: El botón "Imprimir" ahora integra generación inteligente de archivos PDF en dispositivos móviles (Agenda Global y Finanzas) en lugar de usar comandos de navegador inestables.
- **Barra de Navegación de Reportes**: Se arregló definitivamente el menú de navegación (Agenda, Precios, Finanzas, etc.) asegurando que el scroll funcione de extremo a extremo sin apretar los botones.

## Modificado
* templates/report/summary.html
* templates/report/history.html
* templates/report/financials.html
* templates/report/config.html
* templates/report/global_schedule.html
* templates/league_detail.html
* templates/admin/users.html
* templates/admin/teams.html
* templates/admin/leagues.html
* templates/admin/dashboard.html

## 0.9.8.2

Refactorización de plantillas HTML y extracción de recursos estáticos.

- **Organización de Código**: Se extrajo todo el código CSS y JavaScript *in-line* de las plantillas HTML hacia archivos estáticos independientes en las carpetas `static/css/` y `static/js/`.
- **Rendimiento y Mantenibilidad**: Mejora estructural del proyecto separando los lenguajes (HTML, CSS, JS) para facilitar su edición y compresión.
- **Consolidación de Estilos**: Se unificaron estilos repetidos (como visualización de inputs, reportes y vistas de impresión) en archivos CSS compartidos.

## Modificado
* Múltiples plantillas HTML en `templates/` (base, auth, ligas, partidos, reportes, modales, etc.)
* Creación de nuevos archivos CSS en `static/css/` (auth.css, credentials.css, report_financials.css, etc.)
* Creación de nuevos archivos JS en `static/js/` (base.js, league_detail.js, match_form.js, etc.)

## 0.9.8.1

Refinamiento de límites Premium y visibilidad de escudos.

- **Límites Premium Automatizados**: Las ligas ahora regresan automáticamente a los valores por defecto (1 vuelta, 1 cancha, puntaje estándar) cuando expira la suscripción del dueño.
- **Visibilidad de Escudos Mejorada**: Los escudos de los equipos ahora son visibles para todos en el panel, tablas y liguilla. Solo se restringen en las secciones de agenda y resultados del reporte descargable para usuarios gratuitos.
- **Correcciones de Estabilidad**: Se resolvió un error crítico de cálculo en la tabla de posiciones y se mejoró el manejo de datos nulos.

## Modificado
* utils/helpers.py (lógica de tabla y puntos)
* routes/league.py (límites de vueltas y canchas)
* templates/league_detail.html (visibilidad de escudos en dashboard)
* templates/share_report.html (escudos en reporte)

## 0.9.8

Lanzamiento de Planes Ultra Premium y refinamiento de acceso a reportes.

- **Planes Ultra Premium**: Se agregaron opciones de suscripción mensual ($400 MXN) y anual ($3800 MXN) para acceder a funciones avanzadas.
- **Acceso a Reportes Refinado**: La sección de reportes ahora es visible para todos los usuarios.
- **Gated Content**: El contenido de los reportes está restringido a usuarios Ultra, mostrando una invitación a mejorar para los demás.
- **Activación Inmediata**: Los beneficios Ultra se activan de forma instantánea tras completar el pago en Stripe, sin esperar al webhook.
- **Navegación Fluida**: Redireccionamientos internos mejorados para mantener al usuario dentro de la sección de reportes tras intentos de acceso no autorizados.

## Modificado
* routes/premium.py (lógica de checkout y activación inmediata)
* routes/report.py (acceso abierto al index y redirecciones internas)
* templates/premium.html (nuevas tarjetas de precios Ultra)
* templates/report.html (interfaz de acceso restringido y banners)
* templates/base.html (visibilidad permanente del enlace de reportes)
* .env (nuevas variables de precio de Stripe)

## 0.9.7

Visualización de Liguilla (Llaves) y soporte para Octavos de Final.

- **Vista de Llaves (Brackets)**: Nueva visualización gráfica interactiva para los playoffs.
- **Soporte de Octavos de Final**: El sistema ahora permite liguillas de hasta 16 equipos.
- **Cruces de Liguilla Corregidos**: Se implementó el patrón de competencia oficial (1º vs 8º, 2º vs 7º, 3º vs 6º, 4º vs 5º).
- **Agenda por Fechas**: Nueva pestaña en la agenda de partidos para agrupar encuentros por día de juego.
- **Edición de Resultados Flexible**: Se permite editar fecha y cancha de partidos de liguilla sin requerir puntuación obligatoria.
- **Cancha por Defecto**: Asignación automática de la primera cancha registrada al generar liguillas.
- **Persistencia de Vistas**: El navegador ahora recuerda qué vista de partidos o liguilla tenías seleccionada.
- **Unificación de Licencias**: Usuarios con plan Ultra ahora heredan automáticamente todos los beneficios Premium.

## Modificado
* routes/match.py (lógica de generación y avance)
* routes/league.py (agrupación por fechas y manejo de octavos)
* models/user.py (unificación Ultra/Premium)
* forms/match.py (flexibilidad de goles)
* templates/league_detail.html (HTML/CSS/JS de brackets y fechas)
* templates/match_result_form.html (layout de edición)

## 0.9.6

Personalización visual premium para reportes. 

- **Resaltado de Tabla**: Ahora solo se resaltan los números de las posiciones, manteniendo el fondo de la fila limpio.
- **Canchas Individuales**: Se agregó color y alineación personalizable para cada cancha de forma independiente.
- **Fecha de Partido**: Se incluyó personalización de color y tamaño de fuente para las fechas de los partidos en el reporte.
- **Interfaz**: Switches de configuración redondeados para un look más premium.

## Modificado
* league.py (models & routes & forms)
* court.py (models)
* ligapro_manager.py (migrations)
* league_detail.html
* share_report.html

## 0.9.5.1

Se agregó en el reporte de agenda global la opción para colocar el marcador directamente desde allí y esta sincronizado con la agenda de partidos de caad liga.

Se colocó global el número de la versión de la aplicación

## Modificado

* global_schedule.html
* report.py
* base.html
* ligapro_manager.py


## 0.9.5

Se ajusto las fechas de cobro para el reporte de finanzas para establecer si se cobra desde al inicar la liga o desde una fecha especificas

## Modificado
* ligapro_manager.py
* league.py
* report.py
* config.html

## 0.9.4.1

Modificando el diseño responsivo para dispositivos móviles de la plataforma

## Modificado
* base.html
* landing.html
* league_detail.html

## 0.9.4

Se agregó la funcionalidad de incluir notas al generar el rol o reporte de la liga

Se cambiaron los colores de los resultados en el cuadro para ganador de color verde y perdedor de color rojo

## Modificado

* league.py
* league_detail.html
* share_modal_fragment.html
* share_report.html

## 0.9.3

Funcionalidad para generar reportes sobre las ligas y ver balance financiero general o por liga, función únicamente para usuarios con el plan premiun Ultra

## Agregado

* repor.html
* config.html
* global_schedule.html
* history.html
* summary.html

todas páginas para la sección de reporte sobre las ligas

## Modificado

* ligapro_manager.py
* requeriments.txt 
se agrego la libreria openpyxl para la generacion de reportes en formato excel
* league.py
se agrego la funcion de generar reportes de partidos en formato excel
* report.py
* admin.py
* user.py
* match.py



## 0.9.2

## Modificado

* league_detail.html
* league.py
* match.py
* match_matrix.py
* ligapro_manager.py

correción de bug en producción que sobrescribia los resultados del cuadro 2 en el cuadro 1 al agendar partidos

## 0.9.1

##  Modificado

* credentials.html 
Se agrando el logo de la liga en los registros de los jugadores
  
* share_report.html
Se agrando la tabla de posiciones en el reporte de partidos


## 0.9.0

##  Agregado

* VERSION
* CHANGELOG.md

## Modificado

* README.md

##  Removido

* Script check_db_schema.py
* Script migrate_color_root.py




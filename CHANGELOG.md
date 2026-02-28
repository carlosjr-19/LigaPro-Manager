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




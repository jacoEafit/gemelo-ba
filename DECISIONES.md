# Buenos Aires · sistema de información

Grupo: Jacobo Montes Castaño y Carlos Restrepo · Repositorio: https://github.com/jacoEafit/gemelo-ba · Revisado: 2026-11-01 (ver «Revisión cruzada»)

> Armado desde lo que existe en el repositorio (lago, Excel y documento de la Entrega 1, bitácora de IA, carpeta `alternativas/`).

## Para quién y qué pregunta
- **Usuario:** un concejal de la Legislatura porteña y su equipo asesor: necesitan comparar los 48 barrios antes de votar el presupuesto o pedir informes al Ejecutivo, con cifras que puedan citar con fuente y fecha.
- **Preguntas (seis):**
  1. ¿Cuánta gente vive en cada barrio y qué salud, educación y cultura tiene cerca? (Censo 2022 por comuna, Censo 2010 por barrio, hospitales, CESAC, escuelas, espacios culturales)
  2. ¿Cómo gasta la Ciudad su presupuesto y cuánto vale en pesos de hoy? (sancionado 2026 $18,19 billones; devengado a 2026-06 $7,67 billones, 36,7 % del vigente; deflactado con el IPC de la Ciudad)
  3. ¿Qué pasa con la seguridad en cada barrio? (158.838 delitos registrados en 2024 y 133.203 en 2025, por barrio, tipo y mes)
  4. Turismo y empleo. 5. Suelo y ambiente. 6. Movilidad. (detalle en la última columna del diccionario)
- **Escala y comparación:** 48 barrios y 15 comunas. Se compara barrio contra barrio y 2024 contra 2025; el gasto se deflacta con el IPCBA. Las cifras de seguridad son hechos registrados, no tasas: hay que dividir por población antes de comparar barrios. La población por barrio es del Censo 2010; la de 2022 solo existe por comuna, así que las cifras por barrio y por comuna no se pueden comparar entre sí.
- **Lo que decidimos no mostrar, y por qué:**
  - Cada delito con su coordenada, fecha y franja horaria (F05): cruzados con un padrón pueden señalar la casa o la rutina de una persona. Al lago pasan solo conteos por barrio, tipo y mes. El barrio con menos hechos, Agronomía, tiene 368 en 2025: muy lejos de identificar a alguien.
  - Teléfonos y correos de alojamientos, espacios culturales, hospitales y CESAC (F10, F13, F22, F23): no se copian.
  - Los reclamos ciudadanos (F31): se descartaron por peso (~2 GB). El sistema no tiene la voz de los vecinos; la única «escucha» son las visitas a Wikipedia, que miden interés y no opinión.
  - Las lecturas en tiempo real de tránsito: la API de Transporte está suspendida por el portal desde el 2026-10-06.

## La réplica
- **Qué replicamos tal cual del ejemplo y qué tuvimos que cambiar para nuestra ciudad:** replicamos la estructura del modelo de Lima: un archivo JSON por tema con fuentes, cifras, series y desgloses (22 temas, entre ellos atlas de zonas y de distritos, correlaciones, escucha y presupuesto), un contrato de datos y un verificador. Cambió todo lo que depende de la ciudad: 48 barrios y 15 comunas en lugar de los distritos de Lima, el Censo 2022 solo por comuna, la licencia CC-BY-2.5-AR del portal BA Data, y la ausencia de lecturas en vivo (API suspendida).
- **Fuentes catalogadas · integradas · caídas · descartadas:** 40 · 30 · 2 · 7, más 1 candidata (SUACI por barrio, F32). El catálogo está en la hoja «1. Fuentes» del Excel de la Entrega 1 y en la sección «Fuentes» de la página. El portal BA Data lista además 455 conjuntos (`lago/catalogo.json`). **Nota:** el taller pide una carpeta `catalogo/` con una ficha por fuente; hoy esas fichas viven en el Excel y no hay carpeta.
- **Huecos (lo que buscamos y no existe abierto para esta ciudad):**
  - Población 2022 por barrio: no hay radios censales 2022 abiertos (solo 2001 y 2010, F35).
  - Lecturas en tiempo real de tránsito y de la red meteorológica (F33, F34 suspendidas; solo hay inventario de sensores y torres).
  - Reclamos de los vecinos en un formato liviano (F31 pesa 2 GB; F32 podría resolverlo).
  - Una fuente de edificios en 3D con alturas de toda la ciudad distinta del Tejido Urbano (los edificios públicos con LIDAR son solo 9, F37).

## ¿Se puede usar?
| Fuente | Licencia | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 · Barrios | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F02 · Comunas | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F03 · Estructura demográfica | CC-BY-2.5-AR | Solo conteos por zona | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F04 · Censo Nacional 2022, resultados definitivos CABA (INDEC; DGE | no declara | Solo conteos por zona | Integrada al lago | Se cita como declarada (entidad, documento y fecha); no se copia la base. |
| F05 · Delitos | Creative Commons Attribution | Personas identificables | Integrada al lago | Solo conteos por barrio, tipo y mes; sin coordenadas, fecha ni franja del hecho. |
| F06 · Presupuesto Ejecutado 2026 | Creative Commons Attribution | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F07 · Presupuesto Ejecutado | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F08 · Índice de Precios al Consumidor de la Ciudad de Buenos Aires | Creative Commons Attribution 4.0 | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F09 · Asalariados registrados del sector privado por provincia (SI | Creative Commons Attribution 4.0 | Solo conteos por zona | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F10 · Alojamientos Turísticos | CC-BY-2.5-AR | Personas identificables | Integrada al lago | Solo conteos por barrio; teléfono, correo y redes no pasan al lago. |
| F11 · Encuesta de Ocupación Hotelera y Parahotelera (EOH), INDEC y | Creative Commons Attribution 4.0 | Solo conteos por zona | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F12 · Wikimedia Pageviews API | CC0 | No | Integrada al lago | Sin condición. |
| F13 · Espacios culturales. | CC-BY-2.5-AR | Personas identificables | Integrada al lago | Solo conteos por barrio; teléfono, correo y redes no pasan al lago. |
| F14 · Obras Registradas | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F15 · Tejido Urbano | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F16 · Parcelas | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F17 · Espacios Verdes | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F18 · Calidad de Aire | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F19 · Open-Meteo Historical Weather API (reanálisis ERA5/ERA5-Land | CC BY 4.0 | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F20 · Gestión de Residuos en Puntos Verdes | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F21 · Establecimientos Educativos | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F22 · Hospitales | CC-BY-2.5-AR | No | Integrada al lago | Teléfono y web institucionales no se copian. |
| F23 · Centros de Salud y Acción Comunitaria (CESAC) | CC-BY-2.5-AR | No | Integrada al lago | Teléfono y web institucionales no se copian. |
| F24 · Subte: Estaciones. | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F25 · Subte: Viajes Molinetes. | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F26 · Estaciones Bicicletas Públicas. | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F27 · Colectivos: paradas | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F28 · Sensores de Tránsito | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F29 · Información Meteorológica | CC-BY-2.5-AR | No | Integrada al lago | Citar la entidad y el conjunto, con enlace y fecha de prueba. |
| F30 · BA Data (CKAN) | por conjunto (cada conjunto declar | No | Integrada al lago | Solo el inventario (455 conjuntos); cada conjunto aplica su propia licencia. |
| F31 · Sistema Único de Atención Ciudadana / BA Colaborativa (recla | CC-BY-2.5-AR | — | Descartada | No se usa. Un CSV por año de 100 a 277 MB (~2 GB en total): |
| F32 · SUACI · Solicitudes por barrio (agregado) | CC-BY-2.5-AR | — | Candidata | Candidata, sin usar: se revisa antes si trae texto libre o personas. |
| F33 · API Transporte Público (lecturas en tiempo real: subte, cole | CC-BY-2.5-AR | No | No responde | No se usa: el portal la suspendió. El portal avisa: |
| F34 · Colectivos: GTFS | CC-BY-2.5-AR | No | No responde | No se usa: el portal la suspendió. Alcanzada por el mismo aviso de suspensión de los conjuntos GTFS. |
| F35 · Información Censal por Radio | CC-BY-2.5-AR | Solo conteos por zona | Descartada | No se usa. Solo trae radios de 2001 y 2010: |
| F36 · Padrón de Establecimientos Educativos | CC-BY-2.5-AR | Personas identificables | Descartada | No se usa. Trae correos (algunos personales, de Gmail/Hotmail). |
| F37 · Edificios Públicos en 3D (escaneo LIDAR) | CC-BY-2.5-AR | No | Descartada | No se usa. Solo 9 edificios (Cabildo, Colón, Congreso…), de 51 a 599 MB cada uno: |
| F38 · Área edificable: volumen | CC-BY-2.5-AR | No | Descartada | No se usa. Es el volumen que permite la norma, no lo construido (38 MB). |
| F39 · IPC Nivel General Gran Buenos Aires (INDEC) | Creative Commons Attribution 4.0 | No | Descartada | No se usa. Aparece en la búsqueda de la API con datos hasta 2026-08 (no se bajó la serie). |
| F40 · Tasa de desempleo en hogares urbanos, CABA | — | Solo conteos por zona | Descartada | No se usa. La búsqueda de la API la muestra cortada en 2023-04: |

Los 40 casos salen de la hoja «1. Fuentes» (licencia tal como aparece, personas y estado). La columna «Condición» resume lo que decidimos hacer; las licencias no se interpretan, se copian.

## Bitácora de exploración
Se exploró en tres tramos con herramientas alternativas, con los mismos datos en cada una (carpeta `alternativas/`; Lago y Verificación se corren con `make todo`, Vistas con `make setup-tramos` y luego `make vistas`; el detalle y las advertencias están en `alternativas/README.md`). Pruebas del 2026-11-01; **nada de lo explorado se integró todavía al sistema**.

| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto | Qué resolvió | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| Lago | Python puro (biblioteca estándar) | Nada que instalar | PSF | JSON por tema en `lago/` | Sí: `./actualizar.sh` | Es el lenguaje | Las 4 consultas en 3 ms, 18 MB de memoria | Con 2,7 millones de filas (tabla sintética) tarda 3,7 s | **Sí, como lago activo.** Con 2.523 filas ninguna alternativa gana, y la página lee los JSON directo. |
| Lago | Polars 2.1.0 | `pip install polars` (166 MB con dependencias) | MIT | `alternativas/salida/polars/*.parquet` | Sí: `make lago` | Versión 2.1.0 instalada | Mismas 4 consultas, idénticas; 0,12 s a 2,7 millones de filas | No abre el JSON de claves variables: el aplanado lo hace Python; usa 175 MB en la consulta grande | No: no aporta nada que DuckDB no haga, y pesa el triple |
| Lago | DuckDB 2.0.0 | `pip install duckdb` (53 MB) | MIT | `alternativas/salida/duckdb/*.parquet` | Sí: `make lago` | Versión 2.0.0 instalada | Abre y aplana el JSON con SQL, sin código de aplanado; 0,09 s y 82 MB a 2,7 millones de filas | Importar cuesta ~0,1 s; con los datos de hoy no es más rápido | Como opción futura para capas grandes (Parquet); hoy el lago sigue en JSON |
| Verificación | `verificar.py` original | Nada | PSF | — | Sí: `python3 verificacion/verificar.py` | Es propio | Pasa el lago real; atrapa 9 de 10 roturas | No ve un campo personal que sea el *nombre de una cifra* (`telefono_contacto`); 164 líneas | Se mantiene hasta pasar el de DuckDB |
| Verificación | DuckDB (consultas SQL) | `pip install duckdb` | MIT | — | Sí: `make verificar` | Versión 2.0.0 | 10 de 10 comprobaciones y 10 de 10 roturas, en 28 líneas | Las expresiones regulares no admiten `lookaround` (RE2): se reescribió la de correos y celulares | **Sí, como verificador principal:** el más corto, legible y completo |
| Verificación | Pandera 0.35.0 + Polars | `pip install pandera[polars]` (183 MB) | MIT | — | Sí: `make verificar` | Versión 0.35.0 | 10 de 10 y 10 de 10, en 51 líneas | Lo que cruza tablas (fuente conocida, rangos, sumas) exige un `join` previo a mano | No: pesa 183 MB para lo mismo que SQL |
| Verificación | Frictionless 5.21.0 | `pip install frictionless` (47 MB) | MIT | `datapackage.json` temporal | Sí: `make verificar` | Versión 5.21.0 | Esquema estándar con llaves foráneas; 7 de 10 | No cubre `temas_completos`, `dominio` ni `coherencia`; dejó pasar 3 roturas; el más lento (0,29 s) | Solo si se quiere publicar el esquema como estándar. Tuvo un falso PASS en el desarrollo (ver bitácora de IA) |
| Vistas | MapLibre GL JS 4.7.1 + PMTiles (la página actual, `web/`) | Nada que instalar (CDN) | BSD-3 | `web/datos/`, `web/edificios.pmtiles` | Sí: `make datos tiles` | Es la página actual | Mapa de 48 barrios, edificios 3D, vivo y fuentes con enlace | No se compara en `alternativas/`: ninguna de las otras hace teselas vectoriales 3D | **Sí, para el mapa** |
| Vistas | HTML + JS a mano (pantalla de cifras de prueba) | Nada | — | `alternativas/vistas/html` | Sí: servir la carpeta | 32 líneas | Estático, 28 KB; enlace a la fuente en las 2 cifras | Sin ejes en los gráficos (hay que dibujarlos) | Referencia |
| Vistas | Observable Framework 1.13.3 | `npm install` (79 MB) | ISC | `vistas/observable/dist` (704 KB, 46 archivos) | Sí: `npx observable build` | Versión 1.13.3 | 20 líneas, gráficos con ejes; estático, desplegable en Vercel | **Carga la tipografía desde Google Fonts** por defecto (cada visitante se lo avisa a Google); sin JavaScript queda vacío | **Alternativa seria para las pantallas de cifras** si se cambia el tema; queda para decidir |
| Vistas | Streamlit 1.66.1 | `pip install streamlit` (375 MB) | Apache-2.0 | — | Sí: `streamlit run` | Versión 1.66.1 | 19 líneas; enlace a la fuente en las 2 cifras (comprobado con `AppTest`, no en el navegador) | Necesita un servidor Python: no es un sitio estático | No: descartada por el despliegue |


## Protección
- **Nivel:** solo agregados. El contrato lo exige («solo agregados, nunca registros individuales») y el sistema es público y sin clave.
- **Qué protegemos, y de quién:** a las víctimas de delitos, de quien cruce coordenada, fecha y franja con un padrón (reidentificación); y a las personas cuyos correos y teléfonos traen algunos conjuntos (establecimientos, espacios culturales). Los crudos (~1 GB) quedan en `lago/raw`, fuera de git.
- **Pruebas de terminal o de ventana privada:** No hay compuerta, así que las pruebas de terminal no aplican; lo que sí protege es que el verificador falla si aparece un campo personal, un correo o un celular (ver `verificacion/probar_que_falla.py`: rompe el lago de 6 maneras y exige que falle en todas). El 2026-11-01 se cambió la regla de correos y teléfonos de `verificar.py` a formatos argentinos (correos en mayúsculas, celulares con 11 o 15 y fijos de 8 dígitos como `4982-2106`); antes dejaba pasar los correos en mayúsculas y los fijos. El verificador sigue sin ver un campo personal puesto como *nombre de una cifra*.
- **Revisión de secretos en el historial:** hecha el 2026-10-31 sobre los 18 commits: búsqueda de patrones (`api_key`, `password`, `secret_key`, `bearer`, `token=`, `client_secret`, claves de AWS y de GitHub, bloques `BEGIN PRIVATE KEY`) y de archivos `.env`, `.pem`, `.key` o `credential*` que alguna vez se hayan versionado: sin hallazgos. El sistema no usa claves.

## Herramienta elegida para las vistas
- **Qué necesitábamos mostrar:** un mapa de 48 barrios coloreado por cada variable de cada tema, los edificios en 3D con su altura, el subte y EcoBici en vivo, y cada cifra con su fuente.
- **Qué teníamos que proteger:** nada sensible: el sistema muestra solo agregados. No hay compuerta.
- **Por qué esta herramienta cumple las dos cosas, y cuál descartamos por poco:** MapLibre GL JS con teselas PMTiles es un sitio estático: no hay servidor ni claves que cuidar, y los edificios de toda la ciudad (Tejido Urbano) caben en un archivo de 74 MB servido por rangos. Se probaron otras dos herramientas para las **pantallas de cifras y gráficos** (no para el mapa): Observable Framework, que descartamos por poco (estático y con mejores gráficos, pero carga Google Fonts por defecto, lo que choca con minimizar lo que cada visitante le cuenta a un tercero), y Streamlit, que cumple el enlace a la fuente pero exige un servidor Python y no puede ser un sitio estático.

## Nuestra posición
- **Una reflexión de gestión y gobierno de datos: «Dependencia, ¿de quién es la infraestructura?»**
  - *Nuestra respuesta:* dependemos mucho de un solo proveedor y ya nos pasó. De las 30 fuentes integradas, 24 vienen del mismo portal (BA Data), y el 2026-10-06 ese portal suspendió las API y GTFS: perdimos las lecturas en vivo de tránsito (F33, F34). Lo que protege al sistema es que el lago son archivos JSON legibles sin ninguna herramienta, y que el verificador (lo probamos también en consultas SQL) y las consultas se pueden mover a otra herramienta sin reescribir los datos. Lo que no se puede mudar fácil es la página: carga MapLibre y PMTiles desde un CDN (unpkg), los mosaicos de OpenStreetMap, el clima de Open-Meteo y las bicis de la API de EcoBici; si alguno cambia de reglas, esa vista se cae. Las herramientas que exploramos tienen licencia MIT, pero dependemos de ellas con la misma fragilidad que cualquiera.
- **Una reflexión de ciberseguridad: «Minimización: el dato más seguro es el que no se guarda»**
  - *Nuestra respuesta:* quitamos el dato peligroso antes de que llegara al lago. El crudo de delitos trae coordenada, fecha y franja de cada hecho; al lago pasan solo conteos por barrio, tipo y mes, y el barrio con menos hechos (Agronomía) tiene 368 en 2025. Los teléfonos y correos de establecimientos no se copian y el verificador falla si aparecen. Quedan copias fuera del repositorio: los crudos en `lago/raw` (~1 GB, fuera de git), las entregas en Excel y Word,, y las conversaciones con la IA.

## Bitácora de IA
| Tramo | Herramienta | Qué le encargamos | Qué entregó | Qué le corregimos |
|---|---|---|---|---|
| Rastreo | Claude Code (Claude Sonnet 5.5) | Encontrar el portal de datos abiertos de Buenos Aires y su API | BA Data en CKAN; la API está bajo /km/api/3/action | Nada: package_search respondió con 455 conjuntos |
| Lago | Claude Code (Claude Sonnet 5.5) | Contar las estaciones de subte | Primero dio 48 estaciones | Incorrecto: Se abrió el CSV: 48 eran filas año×línea de pasajeros; las estaciones son 90 pares estación-línea (88 nombres) |
| Lago | Claude Code (Claude Sonnet 5.5) | Curar la calidad del aire | Etiquetó todo en µg/m³ | Incorrecto: Se revisó la documentación del conjunto: CO va en ppm y NO2 en ppb |
| Lago | Claude Code (Claude Sonnet 5.5) | Contar filas del presupuesto | 34.836 filas | Parcial: Se encontró una fila vacía contada como dato: 34.835 |
| Rastreo | Claude Code (Claude Sonnet 5.5) | Reemplazar la población por el Censo 2022 | Encontró el informe 1877 de Estadística Ciudad con población por comuna | Nada: Se transcribió el cuadro C.1 y la suma de las 15 comunas dio el total oficial (3.121.707) |
| Rastreo | Claude Code (Claude Sonnet 5.5) | Conseguir población 2022 por barrio | Propuso los radios censales de BA Data como vía | Incorrecto: Al abrir el conjunto: solo hay radios 2001 y 2010 |
| Rastreo | Claude Code (Claude Sonnet 5.5) | Buscar una fuente de edificios en 3D | Tejido Urbano (alturas), Edificios Públicos 3D (LIDAR) y Área edificable | Nada: Se miraron tamaños y campos con descargas parciales: solo el Tejido trae alturas de toda la ciudad |
| Permiso | Claude Code (Claude Sonnet 5.5) | Explicar por qué los sensores en vivo no entraban | Dijo que la API pedía credenciales | Parcial: El 2026-10-06 la ficha del portal dice que las API y GTFS están suspendidas |
| Rastreo | Claude Code (Claude Opus 5.5) | Buscar ocupación hotelera de CABA | No estaba en BA Data; encontró la EOH (INDEC/Turismo) en la API de series de datos.gob.ar | Nada: Se bajaron las series: residentes + no residentes = total en cada mes |
| Lago | Claude Code (Claude Opus 5.5) | Sumar los montos del presupuesto y describir el gasto por comuna | Escribió que el gasto se concentraba en la Comuna 1 | Incorrecto: Los datos mostraron que la comuna con más gasto imputado es la 4 |
| Lago | Claude Code (Claude Opus 5.5) | Leer los 26 CSV de molinetes 2025 | Primer parser con fecha d/m | Parcial: Falló: agosto mezcla d/m y m/d; marzo trae «;» sobrantes; enero 82 mil líneas vacías; un molinete «Prueba» |
| Lago | Claude Code (Claude Opus 5.5) | Cruzar alturas del Tejido con barrios | Primer resultado: altura máxima 830 m | Parcial: Imposible (la torre más alta ronda los 235 m): eran 2 registros especiales; además una Ñ doblemente codificada rompía el cruce |
| Lago | Claude Code (Claude Opus 5.5) | Nombrar estaciones de molinetes como en la capa geo | Normalización + alias | Nada: Se revisaron a mano las 104 correspondencias: todas correctas; faltaba «C. Pellegrini» |
| Rastreo | Claude Code (Claude Opus 5.5) | Proponer fuentes para llegar a 30 sin inventar | IPCBA, SIPA, Open-Meteo, CESAC, EcoBici, paradas y puntos verdes | Nada: Cada una se consultó con el script real; puntos verdes rebotó por límite de peticiones y se reintentó |
| Lago | Claude Code (Claude Opus 5.5) | Asignar barrio a EcoBici y paradas | Detectó que EcoBici trae el barrio vacío y las paradas con erratas | Nada: Punto en polígono: solo 2 estaciones y 7 paradas quedan en el borde |
| Lago | Claude Code (Claude Opus 5.5) | Normalizar los kilos de RAEE | Regla de coma de miles | Parcial: Falló: la columna mezcla coma decimal y de miles; 7 valores con erratas o ambiguos |
| Lago | Claude Code (Claude Opus 5.5) | Estimar cuánto pesaría lago/raw después de comprimir | Unos 60 MB | Incorrecto: Midió 108 MB: subestimó los molinetes (79 MB ya comprimidos) |
| Entrega | Claude Code (Claude Opus 5.5) | Recontar los temas del lago para el README | Escribió 23 temas | Incorrecto: ls lago/*.json da 22 |
| Vistas | Claude Code (Claude Sonnet 5.5) | Rediseñar la página: barra lateral, cards pequeñas, sin selector en el mapa | Cambió también los colores del mapa (paleta, EcoBici, edificios) | Nos pidió dejar el mapa y sus colores quietos: «es de la página». Se revirtieron. |
| Vistas | Claude Code (Claude Sonnet 5.5) | Quitar los polígonos que tapan los edificios 3D | Aplanó las columnas de barrios contra el suelo cuando los edificios están encendidos | Sin comprobar a ojo: las capturas con Chrome sin pantalla salieron incompletas. Falta revisarlo en un navegador real. |
| Vistas | Claude Code (Claude Sonnet 5.5) | Mostrar los edificios desde más arriba | Regeneró `edificios.pmtiles` desde el zoom 10 (antes 13) | A esa altura solo se ven puntos dispersos porque tippecanoe descarta parcelas; los bloques aparecen desde el zoom 13. |
| Permiso | Claude Code (Claude Sonnet 5.5) | Agregar a la página la sección «Fuentes» con lo que no se incluye | Armó la lista de excluidas a mano (4 tarjetas) | Incompleta: el Excel de la Entrega 1 ya tenía 7 descartadas, 2 caídas y 1 candidata. Se corrigió el 2026-11-01: la sección «Fuentes» de la página ahora lista las 10 (F31–F40), cada una con su enlace. |
| Lago | Claude Code (Claude Sonnet 5.5) | Probar DuckDB, Polars y Python puro sobre el lago (`alternativas/`) | Tres versiones con resultados idénticos en las 4 consultas | Dijo primero «DuckDB en el lago»; era de más: el lago sigue en JSON y DuckDB solo sirve de verificador. |
| Verificación | Claude Code (Claude Sonnet 5.5) | Verificar el lago con Frictionless | Un verificador que pasaba el lago limpio | Falso PASS: no abría los archivos (error de carga ignorado). Ahora lanza excepción si no puede validar. |
| Verificación | Claude Code (Claude Sonnet 5.5) | Romper una copia del lago de 10 maneras y ver quién lo atrapa | El verificador original atrapa 9 de 10 | Hallazgo, no corrección: no ve un campo personal puesto como nombre de cifra (`telefono_contacto`). Falta arreglar `verificar.py`. |
| Vistas | Claude Code (Claude Sonnet 5.5) | Hacer la misma pantalla en HTML, Observable y Streamlit | Tres versiones con enlace a la fuente | Mi primera comprobación de números en gráficos era injusta (los gráficos no escriben sus valores como texto) y la de Streamlit falló porque Chrome sin pantalla no espera al websocket: se cambió el criterio y se usó `AppTest`. Las capturas salieron recortadas. |
| Verificación | Claude Code (Claude Sonnet 5.5) | Cambiar la regla de correos y teléfonos de `verificar.py` a formatos argentinos | Correos sin distinguir mayúsculas, celulares y fijos de 8 dígitos | Comprobado: el lago real sigue con 0 fallos y `probar_que_falla.py` atrapa los 6 casos; «3053», «2015-2024» y las latitudes no se marcan. Antes, al probarlo contra el CSV de espacios culturales, la regla vieja veía solo el 15 % de los contactos; mi explicación inicial («viene de la plantilla colombiana») era incompleta: ya traía celulares argentinos y los huecos eran las mayúsculas y los fijos. |
| Entrega | Claude Code (Claude Sonnet 5.5) | Sortear y auditar tres cifras del lago contra su fuente original | Las tres coinciden (cultura, SIPA y EOH) | Nada. Se aclaró que es revisión nuestra, no de otro grupo. |

## Revisión cruzada
- **Tres cifras auditadas:** la revisión la hicimos nosotros con la IA, no otro grupo (2026-11-01). Se sortearon 3 de las 65 cifras del lago con una semilla fija (`random.Random(20261101)`) y cada una se volvió a calcular desde la fuente original, sin pasar por nuestros scripts de curado:

  | Cifra del lago | Fuente original | Qué se hizo | Resultado |
  |---|---|---|---|
  | `cultura.registros` = 3.053 espacios culturales (vigencia 2026-06) | CSV de Espacios culturales, BA Data (`ba_espacios_culturales`) | Se bajó el CSV y se contaron las filas con datos | 3.053: coincide |
  | `economia.asalariados_privados_ultimo_mes` = 1.485.000 (2026-06) | Serie `154.2_CABA_S_0_0_4` del SIPA, API de series de datos.gob.ar | Se consultó la serie de abril a junio de 2026: junio = 1.485,0 (miles de trabajadores) | 1.485.000: coincide |
  | `turismo.viajeros_2024` = 3.993.697 (2024) | Serie `eoh_viaj_loc7` de la EOH, API de series de datos.gob.ar | Se sumaron los 12 meses de 2024 | 3.993.697: coincide |

  Límite: lo revisamos nosotros, con la misma IA que ayudó a escribir los scripts; una revisión de otro grupo podría ver fallas que no vimos.
- **Ataque:** no hicimos ataque. Consideramos que el sistema es seguro en teoría: es un sitio estático sin compuerta, sin claves ni base de datos que robar, y publica solo agregados, porque los datos de personas (coordenada, fecha y franja de los delitos, correos y teléfonos de establecimientos) no entran al lago y el verificador falla si aparecen. Es un argumento de diseño, no una prueba: no se intentó sacar datos de personas ni llegar a un secreto.
- **Vueltas atrás en la ruta:**
  - De Lago a Rastreo: la población 2022 por barrio (F35) se buscó en los radios censales de BA Data; solo hay 2001 y 2010. Se volvió al rastreo y se usó el Censo 2022 por comuna (F04), transcrito de un PDF y marcado como «declarado».
  - De Lago a Rastreo: los reclamos ciudadanos (F31) pesaban ~2 GB; se descartaron y se encontró una versión ya agregada por barrio de 2,7 MB (F32), que queda como candidata.
  - En Permiso: los sensores en vivo no entraban «por credenciales»; al comprobarlo, la API estaba suspendida por el portal (F33).
  - De Vistas a Rastreo: para los edificios 3D se probaron tres fuentes (Tejido Urbano, edificios públicos LIDAR, área edificable) y solo el Tejido Urbano trae alturas de toda la ciudad.
  - En Vistas: la página se rediseñó y se revirtieron los colores del mapa por pedido del grupo.

---
Nota: la carpeta `alternativas/` se borró del repositorio por razones de peso (1,4 GB, casi todo entornos virtuales y `node_modules`). Los resultados de la bitácora de exploración se conservan escritos en las tablas de arriba, pero los comandos `make` y las rutas `alternativas/...` que citan ya no existen.

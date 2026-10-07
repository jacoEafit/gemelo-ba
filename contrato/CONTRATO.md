Un JSON por tema en lago/<tema>.json:
- tema, probado (AAAA-MM-DD)
- fuentes[]: id, nombre, url, estado, licencia
- cifras{}: valor, unidad, vigencia (AAAA o AAAA-MM), fuente (id conocido)
- series{}: unidad, fuente, puntos [[periodo, número], ...]
Ninguna cifra sin fuente, unidad y vigencia. Crudos en lago/raw (no se sube a git).
- geometrías en lago/geo/*.geojson, WGS84, simplificadas, < 200 KB por capa (lo exige el verificador).
  Escalado: una capa que no cabe en 200 KB (p. ej. tejido urbano ~1 GB, parcelas ~329 MB) pasa a
  GeoParquet (análisis: DuckDB/GeoPandas) y, solo si hay vista de mapa, a PMTiles derivado (tippecanoe).
  Ese paso usa dependencias fuera de la biblioteca estándar: va en un script aparte con dependencias declaradas.
- Crudos en lago/raw/<fuente>/<día>/: se guardan como <nombre>.gz (gzip determinista); ZIP y PDF quedan tal cual.
  Junto a cada uno, <nombre>.sha256 con el hash de los bytes ORIGINALES descargados. Se leen con comun.crudo().
  Crudo reducido: si de una descarga pesada solo se usan pocas columnas, se guarda el extracto y se borra el
  original, conservando su .sha256 (hoy: Parcelas → parcelas_barrio.csv con smp, barrio y comuna; el SHP de
  77 MB no se guarda). Otra columna exige volver a descargar.

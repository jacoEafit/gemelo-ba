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

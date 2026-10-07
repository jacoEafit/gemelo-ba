# gemelo-ba
Lago de datos de Buenos Aires.
- `./actualizar.sh`: descarga, cura y verifica.
- `./reconstruir.sh`: reconstruye desde `lago/raw` (sin red). `git diff` vacío = reproducible.
- Un `ingesta/pull_<tema>.py` por tema. Añade `--curar` para no descargar.
- `ingesta/excel_fuentes.py` regenera `fuentes_gemelo_buenos_aires.xlsx` desde el lago (requiere `openpyxl`).
- 18 temas y 23 fuentes vivas (ver el Excel). Contrato en `contrato/CONTRATO.md`; historial de decisiones en `registro/conversacion.md`.
- Pendientes: sensores en vivo (credenciales), geometrías 3D de edificios (alturas por barrio ya en `edificios`;
  la capa de ~1 GB va a GeoParquet/PMTiles, ver contrato),
  población 2022 por barrio (no hay radios 2022 en datos abiertos), reclamos (descartado por peso).

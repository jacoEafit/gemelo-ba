# gemelo-ba
Lago de datos de Buenos Aires.
- `./actualizar.sh`: descarga, cura y verifica.
- `./reconstruir.sh`: reconstruye desde `lago/raw` (sin red). `git diff` vacío = reproducible.
- Un `ingesta/pull_<tema>.py` por tema. Añade `--curar` para no descargar.
- `ingesta/excel_fuentes.py` regenera `fuentes_gemelo_buenos_aires.xlsx` desde el lago (requiere `openpyxl`).
- Contrato en `contrato/CONTRATO.md`; historial de decisiones en `registro/conversacion.md`.
- Pendientes: sensores en vivo (credenciales), edificios 3D (tejido urbano identificado, ver contrato: GeoParquet),
  población 2022 por barrio (no hay radios 2022 en datos abiertos), reclamos (descartado por peso).

# gemelo-ba
Lago de datos de Buenos Aires.
- `./actualizar.sh`: descarga, cura y verifica.
- `./reconstruir.sh`: reconstruye desde `lago/raw` (sin red). `git diff` vacío = reproducible.
- `lago/raw` (~108 MB, fuera de git): crudos en gzip con el sha256 del original; Parcelas guarda solo smp→barrio (ver contrato).
- Un `ingesta/pull_<tema>.py` por tema. Añade `--curar` para no descargar.
- `ingesta/excel_fuentes.py` regenera `fuentes_gemelo_buenos_aires.xlsx` desde el lago (requiere `openpyxl`).
- Entrega 1 (lago y diccionario): `entrega/Diccionario_de_datos_Buenos_Aires.xlsx`, generado desde el lago con `entrega/generar_entrega1.py`.
- 22 temas y 30 fuentes vivas (ver el Excel). Contrato en `contrato/CONTRATO.md`; historial de decisiones en `registro/conversacion.md`.
- Pendientes: sensores en vivo (API de Transporte suspendida por el portal, 2026-10-06), geometrías 3D de edificios (alturas por barrio ya en `edificios`;
  la capa de ~1 GB va a GeoParquet/PMTiles, ver contrato),
  población 2022 por barrio (no hay radios 2022 en datos abiertos), reclamos (los CSV anuales pesan 100-277 MB; candidata: «Solicitudes por barrio», ya agregada, 2,7 MB).

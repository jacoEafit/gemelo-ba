#!/usr/bin/env python3
"""Inventario de sensores abiertos de la Ciudad (sin credenciales): tránsito, torres meteorológicas y estaciones de aire.
Solo inventario (cuántos y dónde por comuna); NO lecturas en tiempo real."""
import sys
from comun import bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

DEF = [("ba_sensores_transito", "sensores-transito", "Sensores", "sensores de tránsito"),
       ("ba_tmi", "informacion-meteorologica", "Torres de Monitoreo", "torres de monitoreo inteligente")]
fuentes, cifras, desgloses, dias = [], {}, {}, []
for F, slug, nombre, unidad in DEF:
    pkg, dia = paquete(F, slug)
    r = elegir(pkg["resources"], ("csv",), nombre)
    if "--curar" not in sys.argv:
        bajar(F, r["url"], "datos.csv")
    f = leer_csv(ultimo_raw(F, "datos.csv")[0])
    dias.append(ultimo_raw(F, "datos.csv")[1])
    vig = pkg["metadata_modified"][:7]
    fuentes.append(fuente_ckan(F, pkg, slug))
    cifras[F] = {"valor": len(f), "unidad": unidad, "vigencia": vig, "fuente": F}
    desgloses[f"{F}_por_comuna"] = desglose(f, "comuna", unidad, F, vig)
escribir_json("lago/sensores.json", {
    "tema": "sensores", "probado": max(dias), "fuentes": fuentes, "cifras": cifras, "series": {}, "desgloses": desgloses,
    "nota": "Inventario estático de dispositivos. Las lecturas en vivo (API de transporte, etc.) requieren credenciales y "
            "siguen pendientes. Las estaciones de calidad del aire están en el tema calidad_aire.",
})
print("sensores:", {k: v["valor"] for k, v in cifras.items()})

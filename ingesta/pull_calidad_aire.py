#!/usr/bin/env python3
"""Calidad del aire: promedio anual por estación y contaminante (ignora 's/d' y vacíos)."""
import collections, sys
from comun import bajar, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_calidad_aire", "calidad-aire"
ANIO = 2025
pkg, dia = paquete(F, SLUG)
r = elegir(pkg["resources"], ("csv",), f"{ANIO} Calidad del Aire")
re_ = elegir(pkg["resources"], ("csv",), "Estaciones ambientales")
if "--curar" not in sys.argv:
    bajar(F, r["url"], "datos.csv")
    bajar(F, re_["url"], "estaciones.csv")
d = ultimo_raw(F, "datos.csv")[0].parent
filas = leer_csv(d / "datos.csv")
n_est = len(leer_csv(d / "estaciones.csv"))
UNIDAD = {"co": "ppm (promedio móvil 8 h)", "no2": "ppb (promedio horario)", "pm10": "µg/m3 (promedio móvil 24 h)"}
suma, cuenta = collections.defaultdict(float), collections.Counter()
for x in filas:
    for k, v in x.items():
        if k in ("fecha", "hora") or not v or v.strip().lower() in ("s/d", ""):
            continue
        try:
            suma[k] += float(v.replace(",", "."))
            cuenta[k] += 1
        except ValueError:
            pass
series = {}
filas_d = {}
for cont, u in UNIDAD.items():
    filas_d[cont] = {"unidad": u, "fuente": F, "vigencia": str(ANIO),
                     "filas": sorted([k[len(cont) + 1:], round(suma[k] / cuenta[k], 2)]
                                     for k in suma if k.startswith(cont + "_"))}
escribir_json("lago/calidad_aire.json", {
    "tema": "calidad_aire", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {"estaciones_ambientales": {"valor": n_est, "unidad": "estaciones ambientales", "vigencia": pkg["metadata_modified"][:7], "fuente": F},
               "lecturas_horarias": {"valor": len(filas), "unidad": "filas fecha-hora", "vigencia": str(ANIO), "fuente": F}},
    "series": {},
    "desgloses": {f"promedio_{c}_por_estacion": v for c, v in filas_d.items()},
    "nota": "Promedio de todas las lecturas válidas del año 2025 (el archivo 2026 existe pero se ignora hasta tener un año cerrado). "
            "CO en ppm y NO2 en ppb, según el diccionario contaminantes.csv del portal (no µg/m3). Estaciones con "
            "lecturas vacías o 's/d' se promedian solo con las válidas; revisar cobertura antes de comparar estaciones.",
})
print("calidad_aire:", {c: v["filas"] for c, v in filas_d.items()})

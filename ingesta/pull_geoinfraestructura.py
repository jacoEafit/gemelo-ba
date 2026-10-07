#!/usr/bin/env python3
"""Red de subte: estaciones (una fila = estación-línea) y pasajeros anuales por línea."""
import sys
from comun import bajar, escribir_json, fuente_ckan, leer_csv, desglose, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_subte_estaciones", "subte-estaciones"
pkg, dia = paquete(F, SLUG)
r_est = elegir(pkg["resources"], ("csv",), "Estaciones de Subte")
r_via = elegir(pkg["resources"], ("csv",), "Total de pasajeros")
if "--curar" not in sys.argv:
    bajar(F, r_est["url"], "estaciones.csv")
    bajar(F, r_via["url"], "viajes_anual.csv")
d = ultimo_raw(F, "estaciones.csv")[0].parent
est, via = leer_csv(d / "estaciones.csv"), leer_csv(d / "viajes_anual.csv")
vig = pkg["metadata_modified"][:7]

por_linea = {}
for x in via:
    por_linea.setdefault(x["linea"], []).append([x["year"], int(x["total"])])
series = {f"pasajeros_linea_{l}": {"unidad": "pasajeros por año", "fuente": F, "puntos": sorted(p)}
          for l, p in sorted(por_linea.items())}

escribir_json("lago/geoinfraestructura.json", {
    "tema": "geoinfraestructura", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {
        "estaciones_linea": {"valor": len(est), "unidad": "pares estación-línea", "vigencia": vig, "fuente": F},
        "estaciones_distintas": {"valor": len({x["estacion"] for x in est}), "unidad": "estaciones (nombres distintos)",
                                 "vigencia": vig, "fuente": F},
        "lineas": {"valor": len({x["linea"] for x in est}), "unidad": "líneas", "vigencia": vig, "fuente": F}},
    "series": series,
    "desgloses": {"estaciones_por_linea": desglose(est, "linea", "estaciones", F, vig)},
    "nota": "Corrige un error previo: el recurso viajes_anual.csv tiene 48 filas (año x línea), NO 48 estaciones. "
            "Las estaciones de combinación aparecen una vez por línea. 2020 refleja la pandemia.",
})
print(f"geoinfraestructura: {len(est)} estación-línea, {len({x['estacion'] for x in est})} nombres")

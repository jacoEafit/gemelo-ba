#!/usr/bin/env python3
"""Hospitales públicos de la Ciudad: conteos por tipo, especialidad y barrio. El crudo trae teléfono y fax: no se copian."""
import sys
from comun import bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_hospitales", "hospitales"
pkg, dia = paquete(F, SLUG)
r = elegir(pkg["resources"], ("csv",))
if "--curar" not in sys.argv:
    bajar(F, r["url"], "hospitales.csv")
f = leer_csv(ultimo_raw(F, "hospitales.csv")[0])
vig = pkg["metadata_modified"][:7]


def barrio(s):
    s = s.strip().upper()
    for a, b in zip("ÁÉÍÓÚÜ", "AEIOUU"):
        s = s.replace(a, b)
    return "LA BOCA" if s == "BOCA" else s or "sin dato"


escribir_json("lago/salud.json", {
    "tema": "salud", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {"registros": {"valor": len(f), "unidad": "hospitales públicos", "vigencia": vig, "fuente": F}},
    "series": {},
    "desgloses": {"por_tipo": desglose(f, "gna", "hospitales", F, vig),
                  "por_especialidad": desglose(f, "esp", "hospitales", F, vig),
                  "por_barrio": desglose(f, "bar", "hospitales", F, vig, norm=barrio)},
    "nota": "Solo hospitales del sistema público de la Ciudad; no incluye CESAC, clínicas privadas ni nacionales "
            "fuera de este listado. Sin camas ni atenciones.",
})
print(f"salud: {len(f)} hospitales")

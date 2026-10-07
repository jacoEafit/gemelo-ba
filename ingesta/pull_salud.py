#!/usr/bin/env python3
"""Salud pública de la Ciudad: hospitales y Centros de Salud y Acción Comunitaria (CESAC), conteos por tipo, especialidad
y barrio. Los crudos traen teléfono, fax y web: no se copian."""
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


C, SC = "ba_cesac", "centros-salud-accion-comunitaria-cesac"
pkg_c, dia_c = paquete(C, SC)
rc = elegir(pkg_c["resources"], ("csv",))
if "--curar" not in sys.argv:
    bajar(C, rc["url"], "cesac.csv")
ce = leer_csv(ultimo_raw(C, "cesac.csv")[0])
vc = pkg_c["metadata_modified"][:7]
escribir_json("lago/salud.json", {
    "tema": "salud", "probado": max(dia, dia_c), "fuentes": [fuente_ckan(F, pkg, SLUG), fuente_ckan(C, pkg_c, SC)],
    "cifras": {"registros": {"valor": len(f), "unidad": "hospitales públicos", "vigencia": vig, "fuente": F},
               "cesac": {"valor": len(ce), "unidad": "Centros de Salud y Acción Comunitaria", "vigencia": vc, "fuente": C}},
    "series": {},
    "desgloses": {"por_tipo": desglose(f, "gna", "hospitales", F, vig),
                  "por_especialidad": desglose(f, "esp", "hospitales", F, vig),
                  "por_barrio": desglose(f, "bar", "hospitales", F, vig, norm=barrio),
                  "cesac_por_barrio": desglose(ce, "barrio", "CESAC", C, vc, norm=barrio),
                  "cesac_por_area_programatica": desglose(ce, "area_progr", "CESAC", C, vc)},
    "nota": "Sistema público de la Ciudad: hospitales y CESAC (atención primaria; cada uno depende del área "
            "programática de un hospital). No incluye clínicas privadas ni centros nacionales. Sin camas ni atenciones.",
})
print(f"salud: {len(f)} hospitales, {len(ce)} CESAC")

#!/usr/bin/env python3
"""Establecimientos educativos: conteos por barrio, nivel y gestión. No se usa el padrón (trae correos)."""
import sys
from comun import bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_establecimientos_educativos", "establecimientos-educativos"
pkg, dia = paquete(F, SLUG)
r = elegir(pkg["resources"], ("csv",), "Establecimientos Educativos")
if "--curar" not in sys.argv:
    bajar(F, r["url"], "establecimientos.csv")
f = leer_csv(ultimo_raw(F, "establecimientos.csv")[0])
vig = pkg["metadata_modified"][:7]


def barrio(s):
    s = s.strip().upper()
    for a, b in zip("ÁÉÍÓÚÜ", "AEIOUU"):
        s = s.replace(a, b)
    return "LA BOCA" if s == "BOCA" else s or "sin dato"


escribir_json("lago/educacion.json", {
    "tema": "educacion", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {"registros": {"valor": len(f), "unidad": "establecimientos educativos (oferta por nivel)", "vigencia": vig, "fuente": F},
               "estatales": {"valor": sum(x["ges"].strip() == "Estatal" for x in f), "unidad": "establecimientos de gestión estatal",
                             "vigencia": vig, "fuente": F}},
    "series": {},
    "desgloses": {"por_barrio": desglose(f, "bar", "establecimientos educativos", F, vig, norm=barrio),
                  "por_gestion": desglose(f, "ges", "establecimientos educativos", F, vig),
                  "por_nivel": desglose(f, "nen_mde", "establecimientos educativos", F, vig)},
    "nota": "Una fila es una oferta (nivel/modalidad) de un establecimiento: un mismo edificio puede contar varias veces. "
            "No hay matrícula (alumnos) en este conjunto.",
})
print(f"educacion: {len(f)} registros")

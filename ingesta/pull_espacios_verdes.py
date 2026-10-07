#!/usr/bin/env python3
"""Espacios verdes públicos: cantidad y superficie (m²) por barrio y por clasificación (plaza, parque, plazoleta…)."""
import collections, sys
from comun import bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_espacios_verdes", "espacios-verdes"
pkg, dia = paquete(F, SLUG)
r = elegir(pkg["resources"], ("csv",), "Espacios Verdes Públicos")
if "--curar" not in sys.argv:
    bajar(F, r["url"], "publicos.csv")
f = leer_csv(ultimo_raw(F, "publicos.csv")[0])
vig = pkg["metadata_modified"][:7]


def barrio(s):
    s = s.strip().upper()
    for a, b in zip("ÁÉÍÓÚÜ", "AEIOUU"):
        s = s.replace(a, b)
    return "LA BOCA" if s == "BOCA" else s or "sin dato"


def m2(clave):
    c = collections.Counter()
    for x in f:
        c[clave(x)] += float(x["area"])  # m², punto decimal en el crudo
    return sorted(([k, round(v)] for k, v in c.items()), key=lambda x: (-x[1], x[0]))


total = round(sum(float(x["area"]) for x in f))
escribir_json("lago/espacios_verdes.json", {
    "tema": "espacios_verdes", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {"registros": {"valor": len(f), "unidad": "espacios verdes públicos", "vigencia": vig, "fuente": F},
               "superficie_m2": {"valor": total, "unidad": "m² de espacio verde público", "vigencia": vig, "fuente": F}},
    "series": {},
    "desgloses": {
        "por_barrio": desglose(f, "barrio", "espacios verdes públicos", F, vig, norm=barrio),
        "m2_por_barrio": {"unidad": "m² de espacio verde público", "fuente": F, "vigencia": vig,
                          "filas": m2(lambda x: barrio(x["barrio"]))},
        "m2_por_clasificacion": {"unidad": "m² de espacio verde público", "fuente": F, "vigencia": vig,
                                 "filas": m2(lambda x: x["clasificac"].strip() or "sin dato")}},
    "nota": "Superficie = campo «area» del crudo (m², calculada sobre el polígono). Incluye canteros y plazoletas: "
            "no todo es verde utilizable. Puerto Madero lidera por la Reserva Ecológica. Para m² por habitante dividir por la población del barrio (Censo 2010).",
})
print(f"espacios_verdes: {len(f)} espacios, {total / 1e6:.1f} km²")

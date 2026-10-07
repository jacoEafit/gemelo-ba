#!/usr/bin/env python3
"""Población residente por comuna (proyección 2017) y por barrio (Censo 2010). Agregados oficiales."""
import pathlib, sys
from comun import bajar, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_demografia", "estructura-demografica"
F_C = "dgeyc_censo2022"  # estado "declarado": leído de un PDF, no de una API
dia_c = ultimo_raw(F_C, "ir_2024_1877.pdf")[1]
pkg, dia = paquete(F, SLUG)
rb = elegir(pkg["resources"], ("csv",), "según barrio")
if "--curar" not in sys.argv:
    bajar(F, rb["url"], "barrios.csv")
d = ultimo_raw(F, "comunas.csv")[0].parent
bar = leer_csv(d / "barrios.csv")
# Censo 2022 definitivo por comuna: transcrito del Anexo 1, cuadro C.1 del informe DGEyC 1877 (19/07/2024,
# crudo en lago/raw/dgeyc_censo2022). El total oficial de la CABA es 3.121.707.
TOTAL_2022 = 3121707
com = leer_csv(pathlib.Path(__file__).with_name("datos") / "censo2022_comunas.csv")
assert sum(int(x["poblacion"]) for x in com) == TOTAL_2022, "la suma de comunas no da el total del Censo 2022"
vig = pkg["metadata_modified"][:7]
tot_c = sum(int(x["poblacion"]) for x in com)
tot_b = sum(int(x["POBLACION"]) for x in bar)
escribir_json("lago/demografia.json", {
    "tema": "demografia", "probado": max(dia, dia_c), "fuentes": [fuente_ckan(F, pkg, SLUG), {
        "id": F_C, "nombre": "Censo Nacional 2022, resultados definitivos CABA (INDEC; DGEyC GCBA, informe 1877)",
        "url": "https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2024/07/ir_2024_1877.pdf",
        "estado": "declarado", "licencia": "sin licencia declarada (publicación oficial; citar fuente)"}],
    "cifras": {
        "poblacion_comunas": {"valor": tot_c, "unidad": "habitantes (Censo 2022 definitivo, suma de comunas)",
                              "vigencia": "2022", "fuente": F_C},
        "poblacion_barrios": {"valor": tot_b, "unidad": "habitantes (Censo 2010, suma de barrios)",
                              "vigencia": "2010", "fuente": F}},
    "series": {},
    "desgloses": {
        "poblacion_por_comuna": {"unidad": "habitantes", "fuente": F, "vigencia": "2022",
                                 "filas": [[f"Comuna {x['comuna']}", int(x["poblacion"])] for x in com]},
        "poblacion_por_barrio": {"unidad": "habitantes", "fuente": F, "vigencia": "2010",
                                 "filas": sorted([x["BARRIO"].strip().upper(), int(x["POBLACION"])] for x in bar)}},
    "nota": "Comunas: Censo 2022 definitivo. Barrios: sigue siendo Censo 2010 (no hay población 2022 por barrio en datos abiertos; "
            "las comunas y los barrios NO son comparables entre sí: 3,12 M vs 2,89 M). Vigencia = año de la cifra, no del portal.",
})
print(f"demografia: comunas {tot_c}, barrios {tot_b}")

#!/usr/bin/env python3
"""Movilidad de superficie: estaciones de bicicletas públicas (EcoBici) y paradas de colectivo, por barrio."""
import sys
from comun import bajar, barrio_de_punto, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir


def barrio(s):
    s = s.strip().upper()
    for a, b in zip("ÁÉÍÓÚÜ", "AEIOUU"):
        s = s.replace(a, b)
    return "LA BOCA" if s == "BOCA" else s or "sin dato"


B, SB = "ba_ecobici_estaciones", "estaciones-bicicletas-publicas"
C, SC = "ba_colectivos_paradas", "colectivos-paradas"
pkg_b, dia_b = paquete(B, SB)
pkg_c, dia_c = paquete(C, SC)
rb = elegir(pkg_b["resources"], ("csv",), "nuevo sistema")
rc = elegir(pkg_c["resources"], ("csv",))
if "--curar" not in sys.argv:
    bajar(B, rb["url"], "estaciones.csv")
    bajar(C, rc["url"], "paradas.csv")
bici = leer_csv(ultimo_raw(B, "estaciones.csv")[0])
par = leer_csv(ultimo_raw(C, "paradas.csv")[0])
vb, vc = pkg_b["metadata_modified"][:7], pkg_c["metadata_modified"][:7]
# El barrio sale de la ubicación: EcoBici lo trae vacío y las paradas tienen erratas («VILLA ORTUZA») y huecos
for x in bici:
    x["barrio_geo"] = barrio_de_punto(float(x["longitud"]), float(x["latitud"])) or ""
for x in par:
    x["barrio_geo"] = barrio_de_punto(float(x["coord_X"]), float(x["coord_Y"])) or ""
lineas = {x[k].strip() for x in par for k in ("L1", "L2", "L3", "L4", "L5", "L6") if (x.get(k) or "").strip()}
escribir_json("lago/movilidad.json", {
    "tema": "movilidad", "probado": max(dia_b, dia_c),
    "fuentes": [fuente_ckan(B, pkg_b, SB), fuente_ckan(C, pkg_c, SC)],
    "cifras": {"estaciones_ecobici": {"valor": len(bici), "unidad": "estaciones de bicicletas públicas", "vigencia": vb, "fuente": B},
               "paradas_colectivo": {"valor": len(par), "unidad": "paradas de colectivo", "vigencia": vc, "fuente": C},
               "lineas_colectivo": {"valor": len(lineas), "unidad": "líneas de colectivo distintas con parada",
                                    "vigencia": vc, "fuente": C}},
    "series": {},
    "desgloses": {"ecobici_por_barrio": desglose(bici, "barrio_geo", "estaciones de bicicletas públicas", B, vb, norm=barrio),
                  "paradas_por_barrio": desglose(par, "barrio_geo", "paradas de colectivo", C, vc, norm=barrio)},
    "nota": "Infraestructura, no uso: no hay viajes en EcoBici ni pasajeros de colectivo en estos conjuntos. Una "
            "parada lista hasta 6 líneas (L1-L6). Barrio por punto en polígono (lago/geo/barrios.geojson); "
            "«sin dato» = cae fuera de los polígonos simplificados (borde o costa).",
})
print(f"movilidad: {len(bici)} estaciones EcoBici, {len(par)} paradas, {len(lineas)} líneas")

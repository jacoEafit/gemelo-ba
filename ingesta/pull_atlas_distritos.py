#!/usr/bin/env python3
import json
from ckan_tema import ejecutar
from comun import crudo


def extra(ruta, fuente, vig):
    fs = [x["properties"] for x in json.loads(crudo(ruta).decode("utf-8-sig"))["features"]]
    return {"area_km2_por_barrio": {"unidad": "km2", "fuente": fuente, "vigencia": vig,
            "filas": sorted([p["nombre"], round(p["area_metro"] / 1e6, 2)] for p in fs)},
            "comuna_por_barrio": {"unidad": "número de comuna", "fuente": fuente, "vigencia": vig,
            "filas": sorted([p["nombre"], p["comuna"]] for p in fs)}}


ejecutar("atlas_distritos", "ba_barrios", "barrios", ("geojson",), unidad="barrios", extra=extra)

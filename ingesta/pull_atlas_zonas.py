#!/usr/bin/env python3
import json
from ckan_tema import ejecutar
from comun import crudo


def extra(ruta, fuente, vig):
    fs = [x["properties"] for x in json.loads(crudo(ruta).decode("utf-8-sig"))["features"]]
    return {"area_km2_por_comuna": {"unidad": "km2", "fuente": fuente, "vigencia": vig,
            "filas": sorted([f"Comuna {p['comuna']}", round(p["area"] / 1e6, 2)] for p in fs)}}


ejecutar("atlas_zonas", "ba_comunas", "comunas", ("json", "geojson"), unidad="comunas", extra=extra)

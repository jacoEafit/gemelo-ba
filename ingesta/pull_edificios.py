#!/usr/bin/env python3
"""Obras registradas (permisos de obra). NO son volúmenes 3D de edificios."""
import collections
from ckan_tema import ejecutar
from comun import desglose, leer_csv


def extra(ruta, fuente, vig):
    f = leer_csv(ruta)
    anios = collections.Counter()
    for x in f:
        partes = (x.get("fecha") or "").split()[0].split("/") if x.get("fecha") else []
        anios[partes[2] if len(partes) == 3 else "sin dato"] += 1
    return {"por_barrio": desglose(f, "barrio", "obras registradas", fuente, vig, norm=lambda s: s.strip().upper()),
            "por_anio": {"unidad": "obras registradas", "fuente": fuente, "vigencia": vig,
                         "filas": sorted([k, v] for k, v in anios.items())}}


ejecutar("edificios", "ba_obras_registradas", "obras-registradas", ("csv",), unidad="obras registradas", extra=extra)

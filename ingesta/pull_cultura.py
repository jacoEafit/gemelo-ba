#!/usr/bin/env python3
from ckan_tema import ejecutar
from comun import desglose, leer_csv


def extra(ruta, fuente, vig):
    f = leer_csv(ruta)
    return {"por_barrio": desglose(f, "BARRIO", "espacios culturales", fuente, vig, norm=lambda s: s.strip().upper()),
            "por_funcion_principal": desglose(f, "FUNCION_PRINCIPAL", "espacios culturales", fuente, vig)}


ejecutar("cultura", "ba_espacios_culturales", "espacios-culturales", ("csv",), unidad="espacios culturales", extra=extra)

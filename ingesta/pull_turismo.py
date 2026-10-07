#!/usr/bin/env python3
"""Turismo: oferta (alojamientos de BA Data, solo conteos; nada de contactos) y demanda (EOH INDEC/Turismo, CABA)."""
import json, sys
from comun import crudo, bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_alojamientos", "alojamientos-turisticos"
pkg, dia = paquete(F, SLUG)
r = elegir(pkg["resources"], ("csv",))
if "--curar" not in sys.argv:
    bajar(F, r["url"], "datos.csv")
f = leer_csv(ultimo_raw(F, "datos.csv")[0])
vig = pkg["metadata_modified"][:7]

# Demanda: Encuesta de Ocupación Hotelera (API de series de tiempo de datos.gob.ar), región/localidad CABA
E = "eoh_caba"
SERIES = {"eoh_plazas_15": ("ocupacion_plazas", "% de plazas ocupadas (hoteles y parahoteles)", 100),
          "eoh_viaj_loc7": ("viajeros_total", "viajeros hospedados por mes", 1),
          "eoh_viaj_loc8": ("viajeros_residentes", "viajeros residentes hospedados por mes", 1),
          "eoh_viaj_loc9": ("viajeros_no_residentes", "viajeros no residentes hospedados por mes", 1),
          "eoh_pern_loc_7": ("pernoctaciones", "pernoctaciones (noches) por mes", 1)}
URL = ("https://apis.datos.gob.ar/series/api/series/?ids=" + ",".join(SERIES)
       + "&start_date=2018-01-01&limit=1000&format=json")
if "--curar" not in sys.argv:
    bajar(E, URL, "series.json")
ruta, dia_e = ultimo_raw(E, "series.json")
datos = json.loads(crudo(ruta).decode("utf-8"))["data"]
series, cifras = {}, {"alojamientos": {"valor": len(f), "unidad": "alojamientos turísticos", "vigencia": vig, "fuente": F}}
for i, (clave, unidad, escala) in enumerate(SERIES.values(), 1):
    puntos = [[fila[0][:7], round(fila[i] * escala, 1) if escala != 1 else int(fila[i])]
              for fila in datos if fila[i] is not None]
    series[clave] = {"unidad": unidad, "fuente": E, "puntos": puntos}
    cifras[f"{clave}_ultimo_mes"] = {"valor": puntos[-1][1], "unidad": unidad, "vigencia": puntos[-1][0], "fuente": E}
anio = max(p[0][:4] for p in series["viajeros_total"]["puntos"] if p[0].endswith("-12"))  # último año completo
cifras[f"viajeros_{anio}"] = {"valor": sum(v for p, v in series["viajeros_total"]["puntos"] if p.startswith(anio)),
                              "unidad": "viajeros hospedados en el año", "vigencia": anio, "fuente": E}

escribir_json("lago/turismo.json", {
    "tema": "turismo", "probado": max(dia, dia_e),
    "fuentes": [fuente_ckan(F, pkg, SLUG),
                {"id": E, "nombre": "Encuesta de Ocupación Hotelera y Parahotelera (EOH), INDEC y Subsecretaría de Turismo",
                 "url": "https://datos.yvera.gob.ar/dataset/encuesta-ocupacion-hotelera-parahotelera-eoh",
                 "estado": "vivo", "licencia": "CC-BY-4.0"}],
    "cifras": cifras, "series": series, "desgloses": {"por_tipo": desglose(f, "tipo", "alojamientos", F, vig)},
    "nota": "Oferta (alojamientos BA Data) y demanda (EOH) no son del mismo universo: la EOH es una encuesta a "
            "establecimientos hoteleros y parahoteleros, no incluye alquileres temporarios. La EOH se publica con "
            "~1 año de rezago y 2020-2021 reflejan la pandemia. El CSV de alojamientos trae teléfono y correo: no se copian.",
})
print("turismo:", {k: v["valor"] for k, v in cifras.items()})

#!/usr/bin/env python3
"""Tema escucha: vistas mensuales del artículo de Wikipedia. Uso: pull_escucha.py [--curar]"""
import json, sys, urllib.parse
from comun import bajar, escribir_json, ultimo_raw

CIUDAD = "Buenos Aires"                # título del artículo en es.wikipedia
DESDE, HASTA = "20250101", "20260831"  # meses completos
FUENTE = "wikimedia_pageviews"

t = urllib.parse.quote(CIUDAD.replace(" ", "_"))
URL = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
       f"es.wikipedia/all-access/user/{t}/monthly/{DESDE}/{HASTA}")

if "--curar" not in sys.argv:
    # un título que coincide no basta: se exige artículo, no desambiguación ni redirección a otra cosa
    resumen = json.loads(bajar(FUENTE, f"https://es.wikipedia.org/api/rest_v1/page/summary/{t}", "resumen.json")[0].read_text())
    assert resumen["type"] == "standard" and resumen["titles"]["canonical"] == CIUDAD.replace(" ", "_"), resumen["type"]
    bajar(FUENTE, URL)

ruta, dia = ultimo_raw(FUENTE)
items = json.loads(ruta.read_text(encoding="utf-8"))["items"]
puntos = [[i["timestamp"][:4] + "-" + i["timestamp"][4:6], i["views"]] for i in items]
ultimo = puntos[-1]

escribir_json("lago/escucha.json", {
    "tema": "escucha",
    "probado": dia,
    "fuentes": [{"id": FUENTE, "nombre": "Wikimedia Pageviews API", "url": URL,
                 "estado": "vivo", "licencia": "CC0"}],
    "cifras": {"vistas_ultimo_mes": {"valor": ultimo[1], "unidad": "vistas de personas",
                                     "vigencia": ultimo[0], "fuente": FUENTE}},
    "series": {"vistas_mensuales": {"unidad": "vistas de personas", "fuente": FUENTE,
                                    "puntos": puntos}},
})
print(f"escucha: {len(puntos)} meses, último {ultimo[0]} = {ultimo[1]}")

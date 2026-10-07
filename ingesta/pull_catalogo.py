#!/usr/bin/env python3
"""Tema catalogo: inventario de conjuntos de BA Data (CKAN). Uso: pull_catalogo.py [--curar]
Comprueba que el endpoint CKAN siga vigente antes de confiar en él."""
import json, sys
from comun import bajar, escribir_json, ultimo_raw

FUENTE = "ba_data_ckan"
URL = "https://data.buenosaires.gob.ar/km/api/3/action/package_search?rows=1000"

if "--curar" not in sys.argv:
    bajar(FUENTE, URL)

ruta, dia = ultimo_raw(FUENTE)
res = json.loads(ruta.read_text(encoding="utf-8"))["result"]
conjuntos = [{
    "id": p["name"],
    "titulo": p.get("title"),
    "licencia": p.get("license_id"),
    "actualizado": (p.get("metadata_modified") or "")[:10],
    "formatos": sorted({(r.get("format") or "").upper() for r in p.get("resources", []) if r.get("format")}),
} for p in res["results"]]

escribir_json("lago/catalogo.json", {
    "tema": "catalogo",
    "probado": dia,
    "fuentes": [{"id": FUENTE, "nombre": "BA Data (CKAN)", "url": URL,
                 "estado": "vivo", "licencia": "por conjunto (ver licencia de cada uno)"}],
    "cifras": {"conjuntos": {"valor": res["count"], "unidad": "conjuntos de datos",
                             "vigencia": dia[:7], "fuente": FUENTE}},
    "series": {},
    "conjuntos": conjuntos,
})
print(f"catalogo: {res['count']} conjuntos ({len(conjuntos)} descargados)")

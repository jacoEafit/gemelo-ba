#!/usr/bin/env python3
"""Capas GeoJSON (WGS84) simplificadas: barrios, comunas, estaciones y red de subte -> lago/geo/*.geojson.
Parte de los crudos de barrios/comunas/subte (los baja si faltan). Douglas-Peucker 0,0001° (~10 m), 5 decimales."""
import json, pathlib, re, sys
from comun import bajar, escribir_json, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

TOL, DEC = 0.0001, 5
OUT = pathlib.Path("lago/geo")


def dp(pts, tol):
    """Douglas-Peucker iterativo (sin recursión: las capas tienen miles de vértices)."""
    if len(pts) < 3:
        return pts
    mantener = [False] * len(pts)
    mantener[0] = mantener[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        i, j = pila.pop()
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2 - x1, y2 - y1
        n2 = dx * dx + dy * dy
        mx, m = -1.0, None
        for k in range(i + 1, j):
            x, y = pts[k]
            if n2 == 0:
                d = ((x - x1) ** 2 + (y - y1) ** 2) ** .5
            else:
                d = abs(dy * (x - x1) - dx * (y - y1)) / n2 ** .5
            if d > mx:
                mx, m = d, k
        if m is not None and mx > tol:
            mantener[m] = True
            pila += [(i, m), (m, j)]
    return [p for p, k in zip(pts, mantener) if k]


def anillo(r):
    s = dp([(x, y) for x, y in r[:-1]], TOL) if r[0] == r[-1] else dp([tuple(p) for p in r], TOL)
    if r[0] == r[-1]:
        if len(s) < 3:
            return None  # el anillo colapsó: se descarta
        s = s + [s[0]]
    return [[round(x, DEC), round(y, DEC)] for x, y in s]


def simplificar(g):
    t, c = g["type"], g["coordinates"]
    if t in ("Polygon", "MultiPolygon"):
        polis = [c] if t == "Polygon" else c
        res = []
        for p in polis:
            anillos = [a for a in (anillo(r) for r in p) if a]
            if anillos:
                res.append(anillos)
        return {"type": "MultiPolygon", "coordinates": res}
    if t in ("LineString", "MultiLineString"):
        lineas = [c] if t == "LineString" else c
        res = [[[round(x, DEC), round(y, DEC)] for x, y in dp([tuple(p[:2]) for p in l], TOL)] for l in lineas]
        return {"type": "MultiLineString", "coordinates": res}
    return {"type": t, "coordinates": [round(v, DEC) for v in c[:2]]}


def capa(nombre, features, meta):
    fc = {"type": "FeatureCollection", "name": nombre, "gemelo": meta, "features": features}
    OUT.mkdir(parents=True, exist_ok=True)
    escribir = lambda p, o: p.write_text(json.dumps(o, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    escribir(OUT / f"{nombre}.geojson", fc)
    kb = (OUT / f"{nombre}.geojson").stat().st_size // 1024
    print(f"geo/{nombre}: {len(features)} elementos, {kb} KB")


def meta(F, pkg, slug, r, dia_archivo, extra=""):
    return {"fuente": F, "url": f"https://data.buenosaires.gob.ar/km/dataset/{slug}",
            "licencia": pkg.get("license_title") or pkg.get("license_id"), "vigencia": pkg["metadata_modified"][:7],
            "probado": dia_archivo, "crs": "WGS84 (EPSG:4326)", "simplificacion": f"Douglas-Peucker {TOL}°, {DEC} decimales {extra}".strip()}


# --- barrios y comunas
for F, slug, archivo, salida, props in [
        ("ba_barrios", "barrios", "datos.geojson", "barrios", ("id", "nombre", "comuna")),
        ("ba_comunas", "comunas", "datos.json", "comunas", ("id", "comuna", "barrios"))]:
    pkg, _ = paquete(F, slug)
    ruta, dia = ultimo_raw(F, archivo)
    crudo = json.loads(ruta.read_text(encoding="utf-8-sig"))
    fs = [{"type": "Feature", "properties": {k: f["properties"][k] for k in props}, "geometry": simplificar(f["geometry"])}
          for f in crudo["features"]]
    capa(salida, fs, meta(F, pkg, slug, None, dia))

# --- subte: estaciones (puntos del CSV, WKT) y líneas
F, slug = "ba_subte_estaciones", "subte-estaciones"
pkg, dia = paquete(F, slug)
est, dia_e = ultimo_raw(F, "estaciones.csv")
fs = []
for x in leer_csv(est):
    lon, lat = map(float, re.search(r"POINT \(([-\d.]+) ([-\d.]+)\)", x["geometry"]).groups())
    fs.append({"type": "Feature", "properties": {"estacion": x["estacion"], "linea": x["linea"]},
               "geometry": {"type": "Point", "coordinates": [round(lon, DEC), round(lat, DEC)]}})
capa("subte_estaciones", fs, meta(F, pkg, slug, None, dia_e, "(puntos sin simplificar)"))
rl = elegir(pkg["resources"], ("json", "geojson"), "Líneas de Subte")
if "--curar" not in sys.argv:
    bajar(F, rl["url"], "red_subte.geojson")
ruta, dia_l = ultimo_raw(F, "red_subte.geojson")
crudo = json.loads(ruta.read_text(encoding="utf-8-sig"))
fs = [{"type": "Feature", "properties": {k: v for k, v in f["properties"].items() if k.lower() in ("linea", "line", "nombre", "name", "id")},
       "geometry": simplificar(f["geometry"])} for f in crudo["features"]]
capa("subte_lineas", fs, meta(F, pkg, slug, None, dia_l))

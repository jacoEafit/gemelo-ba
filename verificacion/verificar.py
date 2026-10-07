#!/usr/bin/env python3
"""Con un solo FAIL no se despliega."""
import glob, json, re, sys

fallos = 0
DIA = re.compile(r"\d{4}-\d{2}-\d{2}")
MES = re.compile(r"\d{4}(-\d{2})?")
PII = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}|(?<!\d)3\d{9}(?!\d)"  # correos y celulares colombianos (plantilla)
                 r"|(?<!\d)(?:\+?54[\s-]?9[\s-]?|0)?(?:11|15)[\s-]?\d{4}[\s-]?\d{4}(?!\d)")  # celulares argentinos
CAMPOS_PERSONALES = re.compile(r"cedula|dni|documento_identidad|telefono|celular|correo|email", re.I)


def check(nombre, ok, detalle=""):
    global fallos
    print(("PASS " if ok else "FAIL ") + nombre + ("" if ok else f"  <- {detalle}"))
    fallos += 0 if ok else 1


def recorre(x, clave=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from recorre(v, k)
    elif isinstance(x, list):
        for v in x:
            yield from recorre(v, clave)
    else:
        yield clave, x


def cifra_ok(c, ids):
    return bool(isinstance(c, dict) and c.get("valor") is not None and c.get("unidad")
                and MES.fullmatch(str(c.get("vigencia"))) and c.get("fuente") in ids)


def serie_ok(s, ids):
    p = s.get("puntos") if isinstance(s, dict) else None
    return bool(isinstance(s, dict) and s.get("unidad") and s.get("fuente") in ids
                and isinstance(p, list) and p
                and all(isinstance(x, list) and len(x) == 2 and isinstance(x[1], (int, float)) for x in p))


def desglose_ok(d, ids):
    f = d.get("filas") if isinstance(d, dict) else None
    return bool(isinstance(d, dict) and d.get("unidad") and d.get("fuente") in ids and MES.fullmatch(str(d.get("vigencia")))
                and isinstance(f, list) and f
                and all(isinstance(x, list) and len(x) == 2 and isinstance(x[1], (int, float)) for x in f))


rutas = sorted(glob.glob("lago/*.json"))
check("hay al menos un archivo en el lago", bool(rutas))
for ruta in rutas:
    lago = json.load(open(ruta, encoding="utf-8"))
    fuentes = lago.get("fuentes", [])
    ids = {f.get("id") for f in fuentes}
    check(f"{ruta}: tiene tema", bool(lago.get("tema")))
    check(f"{ruta}: probado es un día", bool(DIA.fullmatch(str(lago.get("probado")))), lago.get("probado"))
    check(f"{ruta}: fuentes con url, licencia y estado",
          bool(fuentes) and all(f.get("url") and f.get("licencia") and f.get("estado") for f in fuentes))
    for k, c in lago.get("cifras", {}).items():
        check(f"{ruta}: cifra {k}", cifra_ok(c, ids), c)
    for k, s in lago.get("series", {}).items():
        check(f"{ruta}: serie {k}", serie_ok(s, ids), s)
    for k, d in lago.get("desgloses", {}).items():
        check(f"{ruta}: desglose {k}", desglose_ok(d, ids), str(d)[:120])
    pares = list(recorre(lago))
    sosp = sorted({k for k, _ in pares if CAMPOS_PERSONALES.search(k)})
    check(f"{ruta}: sin campos de datos personales", not sosp, sosp)
    hallado = next((v for _, v in pares if isinstance(v, str) and PII.search(v)), None)
    check(f"{ruta}: sin correos ni celulares", hallado is None, hallado)

# Capas GeoJSON: WGS84 dentro de CABA, ligeras, con fuente/vigencia declaradas y sin datos personales
BBOX = (-58.54, -34.72, -58.33, -34.52)  # lon_min, lat_min, lon_max, lat_max de la Ciudad
ESPERADO = {"barrios": 48, "comunas": 15, "subte_estaciones": 90}
def coords(c):
    if c and isinstance(c[0], (int, float)):
        yield c
    else:
        for x in c:
            yield from coords(x)
for ruta in sorted(glob.glob("lago/geo/*.geojson")):
    g = json.load(open(ruta, encoding="utf-8"))
    nombre = g.get("name")
    m = g.get("gemelo", {})
    check(f"{ruta}: FeatureCollection con fuente, url, licencia, vigencia y día", g.get("type") == "FeatureCollection"
          and all(m.get(k) for k in ("fuente", "url", "licencia", "vigencia")) and DIA.fullmatch(str(m.get("probado"))), m)
    pts = [p for f in g["features"] for p in coords(f["geometry"]["coordinates"])]
    check(f"{ruta}: coordenadas WGS84 dentro de la Ciudad", bool(pts) and all(BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3] for x, y in pts),
          [p for p in pts if not (BBOX[0] <= p[0] <= BBOX[2] and BBOX[1] <= p[1] <= BBOX[3])][:3])
    check(f"{ruta}: pesa menos de 200 KB", __import__("os").path.getsize(ruta) < 200_000)
    check(f"{ruta}: sin campos personales", not any(CAMPOS_PERSONALES.search(k) for f in g["features"] for k in f["properties"]))
    if nombre in ESPERADO:
        check(f"{ruta}: {ESPERADO[nombre]} elementos", len(g["features"]) == ESPERADO[nombre], len(g["features"]))

# Comprobaciones de dominio: (tema, mínimo, máximo) de registros
DOMINIO = {("atlas_zonas", "registros"): (15, 15), ("atlas_distritos", "registros"): (48, 48),  # 15 comunas, 48 barrios
           ("geoinfraestructura", "lineas"): (6, 6), ("geoinfraestructura", "estaciones_distintas"): (80, 120),
           ("geoinfraestructura", "estaciones_linea"): (80, 120),  # 48 era el nº de filas de viajes_anual, no estaciones
           ("demografia", "poblacion_comunas"): (2.8e6, 3.4e6), ("demografia", "poblacion_barrios"): (2.8e6, 3.4e6),
           ("seguridad", "meses_con_datos_2024"): (12, 12), ("calidad_aire", "estaciones_ambientales"): (3, 10)}
for (tema, clave), (lo, hi) in DOMINIO.items():
    ruta = f"lago/{tema}.json"
    if glob.glob(ruta):
        n = json.load(open(ruta, encoding="utf-8"))["cifras"][clave]["valor"]
        check(f"dominio {tema}.{clave}: entre {lo} y {hi}", lo <= n <= hi, n)

# Coherencia cruzada: suma por barrio == total; 48 barrios y 15 comunas en los desgloses por barrio/comuna
def tot(tema, k):
    p = f"lago/{tema}.json"
    return sum(v for _, v in json.load(open(p, encoding="utf-8"))["desgloses"][k]["filas"]) if glob.glob(p) else None
for tema, k, c in [("cultura", "por_barrio", "registros"), ("edificios", "por_barrio", "registros"),
                   ("seguridad", "por_barrio_2024", "delitos_2024")]:
    if glob.glob(f"lago/{tema}.json"):
        esperado = json.load(open(f"lago/{tema}.json", encoding="utf-8"))["cifras"][c]["valor"]
        check(f"coherencia {tema}.{k} suma {c}", tot(tema, k) == esperado, (tot(tema, k), esperado))

# Presupuesto: cada desglose del devengado suma el total de su año; la ejecución es un porcentaje
if glob.glob("lago/municipio.json"):
    m = json.load(open("lago/municipio.json", encoding="utf-8"))
    for k in m["desgloses"]:
        anio = k.rsplit("_", 1)[1]
        check(f"coherencia municipio.{k} suma devengado_{anio}", tot("municipio", k) == m["cifras"][f"devengado_{anio}"]["valor"])
    for k, c in m["cifras"].items():
        if k.startswith("ejecucion_"):
            check(f"dominio municipio.{k}: entre 0 y 100", 0 <= c["valor"] <= 100, c["valor"])

# Molinetes: 12 meses; la suma por estación = suma de las series; el total de subte excluye el Premetro
if glob.glob("lago/subte_molinetes.json"):
    sm = json.load(open("lago/subte_molinetes.json", encoding="utf-8"))
    c = {k.rsplit("_", 1)[0]: v["valor"] for k, v in sm["cifras"].items()}
    check("dominio subte_molinetes: 12 meses con datos", c["meses_con_datos"] == 12, c["meses_con_datos"])
    por_linea = {k.rsplit("_", 1)[1]: sum(v for _, v in s["puntos"]) for k, s in sm["series"].items()}
    est = next(iter(sm["desgloses"]))
    check("coherencia subte_molinetes: estaciones suman las series", tot("subte_molinetes", est) == sum(por_linea.values()))
    check("coherencia subte_molinetes: total = líneas A-H", c["pasajeros_subte"] == sum(v for l, v in por_linea.items() if l != "PM"))

# Turismo (EOH): residentes + no residentes = total cada mes; ocupación es un porcentaje
if glob.glob("lago/turismo.json"):
    s = json.load(open("lago/turismo.json", encoding="utf-8"))["series"]
    if "viajeros_total" in s:
        r, nr = dict(s["viajeros_residentes"]["puntos"]), dict(s["viajeros_no_residentes"]["puntos"])
        malos = [p for p, v in s["viajeros_total"]["puntos"] if r.get(p, 0) + nr.get(p, 0) != v]
        check("coherencia turismo: residentes + no residentes = total", not malos, malos[:3])
        check("dominio turismo.ocupacion_plazas: entre 0 y 100",
              all(0 <= v <= 100 for _, v in s["ocupacion_plazas"]["puntos"]))

print(f"\n{fallos} fallos")
sys.exit(1 if fallos else 0)

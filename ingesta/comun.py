import collections, csv, datetime, gzip, hashlib, io, json, pathlib, time, urllib.request

UA = {"User-Agent": "gemelo-ba/1.0 (proyecto universitario)"}
RAW = pathlib.Path("lago/raw")
YA_COMPRIMIDOS = (".zip", ".pdf", ".gz")  # el resto se guarda en raw como <nombre>.gz (gzip determinista, mtime=0)


def comprimido(ruta):
    ruta = pathlib.Path(ruta)
    return ruta.with_name(ruta.name + ".gz")


def existe(ruta):
    """El crudo existe tal cual o comprimido."""
    return pathlib.Path(ruta).exists() or comprimido(ruta).exists()


def crudo(ruta):
    """Bytes originales de un crudo: lee <ruta> o, si no está, descomprime <ruta>.gz."""
    ruta = pathlib.Path(ruta)
    return ruta.read_bytes() if ruta.exists() else gzip.decompress(comprimido(ruta).read_bytes())


def guardar_crudo(destino, datos: bytes):
    """Guarda el crudo (comprimido si conviene) y el sha256 de los bytes ORIGINALES, para trazabilidad."""
    destino = pathlib.Path(destino)
    if destino.suffix.lower() in YA_COMPRIMIDOS:
        escribir(destino, datos)
    else:
        escribir(comprimido(destino), gzip.compress(datos, compresslevel=9, mtime=0))
    escribir(destino.with_name(destino.name + ".sha256"), hashlib.sha256(datos).hexdigest().encode())


def escribir(ruta, datos: bytes):
    ruta = pathlib.Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_bytes(datos)
    tmp.replace(ruta)  # atómico: nunca queda un archivo a medias


def escribir_json(ruta, obj):
    escribir(ruta, json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8"))


def bajar(fuente, url, nombre="respuesta.json"):
    """Guarda la respuesta cruda en lago/raw/<fuente>/<día>/ y devuelve (ruta, día)."""
    hoy = datetime.date.today().isoformat()
    destino = RAW / fuente / hoy / nombre
    if existe(destino):
        return destino, hoy
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                datos = r.read()
            if datos.lstrip()[:1] == b"<" and not nombre.endswith((".html", ".xml")):
                raise ValueError("el servidor devolvió HTML (bloqueo/limite de tasa), no datos")
            break
        except Exception:
            if i == 4:
                raise
            time.sleep(10 * 2 ** i)  # el WAF del portal rechaza ráfagas: espera creciente
    guardar_crudo(destino, datos)
    return destino, hoy


def ultimo_raw(fuente, nombre="respuesta.json"):
    """Raw más reciente (ruta lógica, sin .gz: se lee con crudo()). El día de la carpeta es la fecha 'probado'."""
    carpetas = sorted(p for p in (RAW / fuente).glob("*") if existe(p / nombre))
    if not carpetas:
        raise SystemExit(f"No hay raw de {fuente}: corre el script sin --curar")
    return carpetas[-1] / nombre, carpetas[-1].name


API = "https://data.buenosaires.gob.ar/km/api/3/action"   # CKAN 2.11 bajo /km/ (verifica con el catálogo)
PORTAL = "https://data.buenosaires.gob.ar/km/dataset"


def contar(ruta):
    """Devuelve (número de registros, nombres de campos) de un GeoJSON, JSON o CSV."""
    ruta = pathlib.Path(ruta)
    datos = crudo(ruta)
    if ruta.suffix.lower() in (".geojson", ".json"):
        obj = json.loads(datos.decode("utf-8-sig"))
        filas = obj["features"] if isinstance(obj, dict) and "features" in obj else obj
        if not isinstance(filas, list):
            raise SystemExit(f"{ruta}: no es una lista de registros")
        primero = filas[0] if filas else {}
        return len(filas), sorted((primero.get("properties") or primero).keys())
    if ruta.suffix.lower() == ".csv":
        try:
            texto = datos.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = datos.decode("latin-1")
        cabecera = texto.splitlines()[0]
        sep = max(",;\t", key=cabecera.count)
        filas = [f for f in csv.reader(io.StringIO(texto), delimiter=sep) if any(c.strip() for c in f)]
        return len(filas) - 1, filas[0]
    raise SystemExit(f"{ruta}: formato no soportado")


csv.field_size_limit(10 ** 9)


def leer_csv(ruta):
    """Lista de dicts de un CSV (separador y codificación detectados; filas vacías fuera)."""
    datos = crudo(ruta)
    try:
        texto = datos.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = datos.decode("latin-1")
    cab = texto.splitlines()[0]
    sep = max(",;\t", key=cab.count)
    return [f for f in csv.DictReader(io.StringIO(texto), delimiter=sep) if any((v or "").strip() for v in f.values())]


def desglose(filas, clave, unidad, fuente, vigencia, peso=None, norm=str.strip):
    """Conteo (o suma de `peso`) por valor de `clave`, ordenado. Sin datos personales: solo agregados."""
    c = collections.Counter()
    for f in filas:
        k = norm(f.get(clave) or "") or "sin dato"
        c[k] += int(f[peso]) if peso else 1
    return {"unidad": unidad, "fuente": fuente, "vigencia": vigencia,
            "filas": sorted(([k, v] for k, v in c.items()), key=lambda x: (-x[1], x[0]))}


def fuente_ckan(id_, pkg, slug, estado="vivo"):
    return {"id": id_, "nombre": pkg["title"], "url": f"{PORTAL}/{slug}", "estado": estado,
            "licencia": pkg.get("license_title") or pkg.get("license_id") or "sin licencia declarada"}


def paquete(fuente, slug):
    """package_show del conjunto: lo baja salvo con --curar, y devuelve (pkg, día)."""
    import sys
    if "--curar" not in sys.argv:
        bajar(fuente, f"{API}/package_show?id={slug}", "package.json")
    ruta, dia = ultimo_raw(fuente, "package.json")
    return json.loads(crudo(ruta).decode("utf-8"))["result"], dia


def _dentro(x, y, anillo):
    r = False
    for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            r = not r
    return r


_BARRIOS = None


def barrio_de_punto(x, y):
    """Barrio (MAYÚSCULAS) que contiene el punto WGS84 (lon, lat), según lago/geo/barrios.geojson; None si cae fuera."""
    global _BARRIOS
    if _BARRIOS is None:
        _BARRIOS = json.loads(pathlib.Path("lago/geo/barrios.geojson").read_text(encoding="utf-8"))["features"]
    for b in _BARRIOS:
        g = b["geometry"]
        for pol in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            if _dentro(x, y, pol[0]) and not any(_dentro(x, y, h) for h in pol[1:]):
                return b["properties"]["nombre"].upper()
    return None

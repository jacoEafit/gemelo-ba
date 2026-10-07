import collections, csv, datetime, hashlib, io, json, pathlib, time, urllib.request

UA = {"User-Agent": "gemelo-ba/1.0 (proyecto universitario)"}
RAW = pathlib.Path("lago/raw")


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
    if destino.exists():
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
    escribir(destino, datos)
    escribir(destino.with_name(nombre + ".sha256"), hashlib.sha256(datos).hexdigest().encode())
    return destino, hoy


def ultimo_raw(fuente, nombre="respuesta.json"):
    """Raw más reciente. El día de la carpeta es la fecha 'probado' del contrato."""
    carpetas = sorted(p for p in (RAW / fuente).glob("*") if (p / nombre).exists())
    if not carpetas:
        raise SystemExit(f"No hay raw de {fuente}: corre el script sin --curar")
    return carpetas[-1] / nombre, carpetas[-1].name


API = "https://data.buenosaires.gob.ar/km/api/3/action"   # CKAN 2.11 bajo /km/ (verifica con el catálogo)
PORTAL = "https://data.buenosaires.gob.ar/km/dataset"


def contar(ruta):
    """Devuelve (número de registros, nombres de campos) de un GeoJSON, JSON o CSV."""
    ruta = pathlib.Path(ruta)
    crudo = ruta.read_bytes()
    if ruta.suffix.lower() in (".geojson", ".json"):
        obj = json.loads(crudo.decode("utf-8-sig"))
        filas = obj["features"] if isinstance(obj, dict) and "features" in obj else obj
        if not isinstance(filas, list):
            raise SystemExit(f"{ruta}: no es una lista de registros")
        primero = filas[0] if filas else {}
        return len(filas), sorted((primero.get("properties") or primero).keys())
    if ruta.suffix.lower() == ".csv":
        try:
            texto = crudo.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = crudo.decode("latin-1")
        cabecera = texto.splitlines()[0]
        sep = max(",;\t", key=cabecera.count)
        filas = [f for f in csv.reader(io.StringIO(texto), delimiter=sep) if any(c.strip() for c in f)]
        return len(filas) - 1, filas[0]
    raise SystemExit(f"{ruta}: formato no soportado")


csv.field_size_limit(10 ** 9)


def leer_csv(ruta):
    """Lista de dicts de un CSV (separador y codificación detectados; filas vacías fuera)."""
    crudo = pathlib.Path(ruta).read_bytes()
    try:
        texto = crudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = crudo.decode("latin-1")
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
    return json.loads(ruta.read_text(encoding="utf-8"))["result"], dia

#!/usr/bin/env python3
"""Viajes en subte por molinetes (SBASE). El crudo trae un registro por molinete cada 15 minutos (~1,2 GB sin
comprimir): se lee el zip en streaming y solo se guardan agregados por línea, mes y estación."""
import collections, json, pathlib, re, sys, zipfile
from comun import bajar, barrio_de_punto, escribir, escribir_json, fuente_ckan, paquete, ultimo_raw

F, SLUG, ANIO = "ba_subte_molinetes", "subte-viajes-molinetes", 2025
pkg, dia = paquete(F, SLUG)
if "--curar" not in sys.argv:
    bajar(F, next(r["url"] for r in pkg["resources"] if r["url"].endswith(f"molinetes-{ANIO}.zip")), f"molinetes_{ANIO}.zip")
z = zipfile.ZipFile(ultimo_raw(F, f"molinetes_{ANIO}.zip")[0])

ARCHIVO = re.compile(r"(\d{4})(\d{2})_PAX15min-([A-Z]+)-")
vistos, mes_linea, estacion = set(), collections.Counter(), collections.Counter()
descartadas = 0


def campos(fila):
    """Cada fila llega entera entre comillas; marzo además trae «;;;;;;;;;» sobrantes al final.
    La codificación cambia entre archivos (UTF-8 con o sin BOM, Latin-1)."""
    try:
        fila = fila.decode("utf-8-sig")
    except UnicodeDecodeError:
        fila = fila.decode("latin-1")
    return fila.strip().rstrip(";").strip('"').split(";")


for n in sorted(z.namelist()):
    m = ARCHIVO.search(n)
    if not m:
        continue
    clave = (m[1], m[2], m[3])
    if clave in vistos:  # el zip trae nombres como «... (1).csv»: un mismo mes y grupo no se cuenta dos veces
        raise SystemExit(f"archivo repetido para {clave}: {n}")
    vistos.add(clave)
    with z.open(n) as f:
        lineas = f
        cab = campos(lineas.readline())
        i_fecha, i_linea, i_est, i_tot = (cab.index(c) for c in ("FECHA", "LINEA", "ESTACION", "pax_TOTAL"))
        for fila in lineas:
            if not fila.strip():  # enero (DEH) intercala ~82 mil líneas vacías
                continue
            c = campos(fila)
            if len(c) != len(cab):
                descartadas += 1
                continue
            *dm, a = c[i_fecha].split("/")  # d/m/aaaa, salvo agosto, que mezcla d/m y m/d: el mes sale del archivo
            if a != str(ANIO) or int(m[2]) not in map(int, dm):
                raise SystemExit(f"{n}: fecha fuera del mes del archivo: {c[i_fecha]}")
            linea = c[i_linea].replace("Linea", "")
            if linea == "Prueba":  # molinete de prueba, no es servicio
                continue
            est = c[i_est].strip()
            pax = int(c[i_tot])
            mes_linea[(f"{ANIO}-{m[2]}", linea)] += pax
            estacion[(linea, "sin dato" if est in ("#N/D", "NULL", "") else est)] += pax

if descartadas > 100:
    raise SystemExit(f"{descartadas} filas con formato inesperado: revisar el crudo")
meses = sorted({p for p, _ in mes_linea})
lineas_ = sorted({l for _, l in mes_linea})
series = {f"pasajeros_linea_{l}": {"unidad": "pasajeros por mes (molinetes)", "fuente": F,
                                   "puntos": [[p, mes_linea[(p, l)]] for p in meses if mes_linea[(p, l)]]}
          for l in lineas_}
subte = sum(v for (_, l), v in mes_linea.items() if l != "PM")

# --- Cruce con la capa geo de estaciones (corre después de pull_geometrias) y barrio por punto en polígono ---
def canon(s):
    s = s.lower().replace("°", "").replace("º", "")
    for a, b in zip("áéíóúü", "aeiouu"):
        s = s.replace(a, b)
    s = re.sub(r"[ .][a-h]$", "", s.strip())  # «Callao.B», «Retiro E»: sufijo de línea
    s = re.sub(r"\b(av\.?|avenida|pza\.?|plaza de|plaza|general|gral\.?|c\.|r\.|de|del|los|la|pdte\.?)\b", " ", s)
    return " ".join(s.replace(".", " ").split())


ALIAS = {"flores": "san jose flores", "humberto i": "humberto 1", "patricios": "parque patricios",
         "mariano moreno": "moreno", "carlos pellegrini": "pellegrini", "independencia h": "independencia"}  # «Independencia.H» queda imputada a la E
geo = json.loads(pathlib.Path("lago/geo/subte_estaciones.geojson").read_text(encoding="utf-8"))


claves = collections.defaultdict(set)  # (línea, clave) y clave sola -> estación geo
for f in geo["features"]:
    pr = f["properties"]
    nombre = (pr["linea"], pr["estacion"])
    for parte in [pr["estacion"]] + pr["estacion"].split(" - "):
        k = canon(parte)
        claves[(pr["linea"], k)].add(nombre)
        claves[k].add(nombre)
punto = {(f["properties"]["linea"], f["properties"]["estacion"]): f["geometry"]["coordinates"] for f in geo["features"]}


def a_geo(linea, est):
    k = canon(est)
    k = ALIAS.get(k, k)
    for c in ((linea, k), k):  # primero en su línea; si no, por nombre (molinetes imputados a otra línea)
        if len(claves.get(c, ())) == 1:
            return next(iter(claves[c]))
    cand = {g for kk, gs in claves.items() if isinstance(kk, tuple) and kk[0] == linea and k and k in kk[1] for g in gs}
    return next(iter(cand)) if len(cand) == 1 else None


por_geo, sin_geo = collections.Counter(), collections.Counter()
for (l, e), v in estacion.items():
    if l == "PM":
        continue
    g = a_geo(l, e)
    if g:
        por_geo[g] += v
    else:
        sin_geo[f"{l} · {e}"] += v
barrio_est = {g: barrio_de_punto(*punto[g]) for g in punto}
por_barrio = collections.Counter()
for g, v in por_geo.items():
    por_barrio[barrio_est[g] or "sin dato"] += v
escribir(pathlib.Path("lago/geo/subte_pasajeros.geojson"), json.dumps({
    "type": "FeatureCollection", "name": "subte_pasajeros",
    "gemelo": {**geo["gemelo"], "fuente": F, "url": fuente_ckan(F, pkg, SLUG)["url"], "vigencia": str(ANIO), "probado": dia,
               "nota": f"Puntos de subte_estaciones con pasajeros {ANIO} por molinetes y barrio (punto en polígono)"},
    "features": [{"type": "Feature", "properties": {"estacion": e, "linea": l, "barrio": barrio_est[(l, e)],
                                                    f"pasajeros_{ANIO}": por_geo.get((l, e), 0)},
                  "geometry": {"type": "Point", "coordinates": punto[(l, e)]}} for l, e in sorted(punto)],
}, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))

escribir_json("lago/subte_molinetes.json", {
    "tema": "subte_molinetes", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {f"pasajeros_subte_{ANIO}": {"valor": subte, "unidad": "pasajeros (validaciones en molinetes, líneas A-H)",
                                           "vigencia": str(ANIO), "fuente": F},
               f"meses_con_datos_{ANIO}": {"valor": len(meses), "unidad": "meses", "vigencia": str(ANIO), "fuente": F},
               "lineas": {"valor": len(lineas_), "unidad": "líneas (incluye Premetro PM)", "vigencia": str(ANIO), "fuente": F}},
    "series": series,
    "desgloses": {f"pasajeros_por_estacion_{ANIO}": {
        "unidad": "pasajeros en el año (línea · estación, nombre como viene en el crudo)", "fuente": F, "vigencia": str(ANIO),
        "filas": sorted(([f"{l} · {e}", v] for (l, e), v in estacion.items()), key=lambda x: (-x[1], x[0]))},
        f"pasajeros_por_estacion_geo_{ANIO}": {
            "unidad": "pasajeros en el año (línea · estación como en lago/geo/subte_estaciones)", "fuente": F, "vigencia": str(ANIO),
            "filas": sorted(([f"{l} · {e}", por_geo.get((l, e), 0)] for l, e in punto), key=lambda x: (-x[1], x[0]))},
        f"pasajeros_por_barrio_{ANIO}": {
            "unidad": "pasajeros en el año (estaciones ubicadas en el barrio)", "fuente": F, "vigencia": str(ANIO),
            "filas": sorted(([k, v] for k, v in por_barrio.items()), key=lambda x: (-x[1], x[0]))},
        f"sin_estacion_geo_{ANIO}": {
            "unidad": "pasajeros en el año (molinetes sin estación en la capa geo)", "fuente": F, "vigencia": str(ANIO),
            "filas": sorted(([k, v] for k, v in sin_geo.items()), key=lambda x: (-x[1], x[0])) or [["ninguno", 0]]}},
    "nota": "Cuenta validaciones en molinetes (pagos, pases y franquicias), no personas distintas. Los trasbordos "
            "entre líneas no pasan por molinete y no se cuentan. El Premetro (PM) solo aparece en junio y julio y se "
            "excluye del total de subte. Los nombres de estación vienen como en el crudo (p. ej. «Loria» figura con "
            "pocas validaciones en líneas que no son la A) y no están cruzados con lago/geo/subte_estaciones. "
            "Agosto mezcla fechas d/m y m/d: el mes se toma del nombre del archivo. Frente a 2019 (341 M según "
            "geoinfraestructura) el total 2025 es ~60 %: no se contrastó con una cifra oficial de SBASE para 2025.",
})
print(f"cruce geo: {len(por_geo)}/{len(punto)} estaciones con pasajeros, sin cruce {dict(sin_geo)}, "
      f"{len([b for b in barrio_est.values() if b])} con barrio")
print(f"subte_molinetes: {subte:,} pasajeros {ANIO}, {len(meses)} meses, líneas {lineas_}, {len(estacion)} estaciones, {descartadas} filas descartadas")

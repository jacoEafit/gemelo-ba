#!/usr/bin/env python3
"""Viajes en subte por molinetes (SBASE). El crudo trae un registro por molinete cada 15 minutos (~1,2 GB sin
comprimir): se lee el zip en streaming y solo se guardan agregados por línea, mes y estación."""
import collections, re, sys, zipfile
from comun import bajar, escribir_json, fuente_ckan, paquete, ultimo_raw

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
escribir_json("lago/subte_molinetes.json", {
    "tema": "subte_molinetes", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {f"pasajeros_subte_{ANIO}": {"valor": subte, "unidad": "pasajeros (validaciones en molinetes, líneas A-H)",
                                           "vigencia": str(ANIO), "fuente": F},
               f"meses_con_datos_{ANIO}": {"valor": len(meses), "unidad": "meses", "vigencia": str(ANIO), "fuente": F},
               "lineas": {"valor": len(lineas_), "unidad": "líneas (incluye Premetro PM)", "vigencia": str(ANIO), "fuente": F}},
    "series": series,
    "desgloses": {f"pasajeros_por_estacion_{ANIO}": {
        "unidad": "pasajeros en el año (línea · estación, nombre como viene en el crudo)", "fuente": F, "vigencia": str(ANIO),
        "filas": sorted(([f"{l} · {e}", v] for (l, e), v in estacion.items()), key=lambda x: (-x[1], x[0]))}},
    "nota": "Cuenta validaciones en molinetes (pagos, pases y franquicias), no personas distintas. Los trasbordos "
            "entre líneas no pasan por molinete y no se cuentan. El Premetro (PM) solo aparece en junio y julio y se "
            "excluye del total de subte. Los nombres de estación vienen como en el crudo (p. ej. «Loria» figura con "
            "pocas validaciones en líneas que no son la A) y no están cruzados con lago/geo/subte_estaciones. "
            "Agosto mezcla fechas d/m y m/d: el mes se toma del nombre del archivo. Frente a 2019 (341 M según "
            "geoinfraestructura) el total 2025 es ~60 %: no se contrastó con una cifra oficial de SBASE para 2025.",
})
print(f"subte_molinetes: {subte:,} pasajeros {ANIO}, {len(meses)} meses, líneas {lineas_}, {len(estacion)} estaciones, {descartadas} filas descartadas")

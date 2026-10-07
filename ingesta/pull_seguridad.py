#!/usr/bin/env python3
"""Delitos registrados (agregados por barrio/tipo/mes; no se guardan coordenadas ni ids por hecho)."""
import sys
from comun import bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw

F, SLUG = "ba_delitos", "delitos"
ANIOS = (2024, 2025)
pkg, dia = paquete(F, SLUG)
urls = {a: next(r["url"] for r in pkg["resources"] if str(a) in (r.get("name") or "") and r["format"].lower() == "csv")
        for a in ANIOS}
if "--curar" not in sys.argv:
    for a, u in urls.items():
        bajar(F, u, f"delitos_{a}.csv")
d = ultimo_raw(F, f"delitos_{ANIOS[-1]}.csv")[0].parent
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE",
         "NOVIEMBRE", "DICIEMBRE"]
cifras, series, desgloses = {}, {}, {}
for a in ANIOS:
    f = leer_csv(d / f"delitos_{a}.csv")
    meses = {m for m in (x["mes"] for x in f)}
    cifras[f"delitos_{a}"] = {"valor": sum(int(x["cantidad"]) for x in f), "unidad": "delitos registrados",
                              "vigencia": str(a), "fuente": F}
    cifras[f"meses_con_datos_{a}"] = {"valor": len(meses), "unidad": "meses", "vigencia": str(a), "fuente": F}
    c = {m: 0 for m in MESES}
    for x in f:
        c[x["mes"]] += int(x["cantidad"])
    series[f"delitos_mensuales_{a}"] = {"unidad": "delitos registrados", "fuente": F,
                                        "puntos": [[f"{a}-{i + 1:02d}", c[m]] for i, m in enumerate(MESES) if c[m]]}
    desgloses[f"por_barrio_{a}"] = desglose(f, "barrio", "delitos registrados", F, str(a), peso="cantidad", norm=lambda s: s.strip().upper())
    desgloses[f"por_tipo_{a}"] = desglose(f, "tipo", "delitos registrados", F, str(a), peso="cantidad")
escribir_json("lago/seguridad.json", {
    "tema": "seguridad", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": cifras, "series": series, "desgloses": desgloses,
    "nota": "Son hechos registrados por el Ministerio de Justicia y Seguridad, no tasas: dividir por población para comparar barrios. "
            "Sin latitud/longitud por hecho en el lago. Si un año tiene <12 meses, está incompleto.",
})
print("seguridad:", {k: v["valor"] for k, v in cifras.items()})

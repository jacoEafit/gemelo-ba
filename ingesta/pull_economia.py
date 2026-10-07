#!/usr/bin/env python3
"""Economía de la Ciudad: precios (IPCBA, Estadística Ciudad) y empleo privado registrado (SIPA), desde la API de
series de tiempo de datos.gob.ar. Corre antes que municipio (orden alfabético): el IPCBA deflacta el presupuesto."""
import json, sys
from comun import bajar, crudo, escribir_json, ultimo_raw

API = "https://apis.datos.gob.ar/series/api/series/?ids={}&start_date=2018-01-01&limit=1000&format=json"
FUENTES = {
    "ipcba": ("193.2_NIVEL_GENERAL_2021_0_13_2",
              "Índice de Precios al Consumidor de la Ciudad de Buenos Aires (IPCBA), Estadística Ciudad; "
              "republicado por la Subsecretaría de Programación Macroeconómica",
              "https://www.estadisticaciudad.gob.ar/eyc/?cat=93"),
    "sipa_caba": ("154.2_CABA_S_0_0_4",
                  "Asalariados registrados del sector privado por provincia (SIPA), Ministerio de Economía",
                  "https://www.economia.gob.ar/datos/"),
}
puntos, dias = {}, []
for f, (serie, _, _) in FUENTES.items():
    if "--curar" not in sys.argv:
        bajar(f, API.format(serie), "series.json")
    ruta, dia = ultimo_raw(f, "series.json")
    dias.append(dia)
    puntos[f] = [[p[:7], v] for p, v in json.loads(crudo(ruta).decode("utf-8"))["data"] if v is not None]

ipc, sipa = puntos["ipcba"], puntos["sipa_caba"]
d_ipc = dict(ipc)
ult = ipc[-1][0]
hace_un_anio = f"{int(ult[:4]) - 1}{ult[4:]}"
anio = max(p[:4] for p, _ in ipc if p.endswith("-12"))  # último año completo
promedio = lambda a: sum(v for p, v in ipc if p.startswith(a)) / sum(p.startswith(a) for p, _ in ipc)
escribir_json("lago/economia.json", {
    "tema": "economia", "probado": max(dias),
    "fuentes": [{"id": f, "nombre": n, "url": u, "estado": "vivo", "licencia": "CC-BY-4.0"} for f, (_, n, u) in FUENTES.items()],
    "cifras": {
        "ipcba_ultimo_mes": {"valor": ipc[-1][1], "unidad": "índice IPCBA nivel general", "vigencia": ult, "fuente": "ipcba"},
        "inflacion_interanual": {"valor": round(100 * (d_ipc[ult] / d_ipc[hace_un_anio] - 1), 1),
                                 "unidad": f"% de variación del IPCBA {hace_un_anio} → {ult}", "vigencia": ult, "fuente": "ipcba"},
        f"inflacion_{anio}": {"valor": round(100 * (d_ipc[f"{anio}-12"] / d_ipc[f"{int(anio) - 1}-12"] - 1), 1),
                              "unidad": "% de variación del IPCBA diciembre a diciembre", "vigencia": anio, "fuente": "ipcba"},
        f"ipcba_promedio_{anio}": {"valor": round(promedio(anio), 2), "unidad": "índice IPCBA promedio del año",
                                   "vigencia": anio, "fuente": "ipcba"},
        "asalariados_privados_ultimo_mes": {"valor": round(sipa[-1][1] * 1000), "unidad": "asalariados registrados del sector "
                                            "privado (sin estacionalidad)", "vigencia": sipa[-1][0], "fuente": "sipa_caba"},
    },
    "series": {"ipcba": {"unidad": "índice IPCBA nivel general", "fuente": "ipcba", "puntos": ipc},
               "asalariados_privados": {"unidad": "miles de asalariados registrados del sector privado (sin estacionalidad)",
                                        "fuente": "sipa_caba", "puntos": sipa}},
    "desgloses": {},
    "nota": "SIPA cuenta puestos registrados con lugar de trabajo en CABA, no residentes: incluye a quienes viven en el "
            "conurbano. El IPCBA mide precios de la Ciudad (distinto del IPC-GBA del INDEC).",
})
print("economia:", ult, "IPCBA", ipc[-1][1], "| SIPA", sipa[-1])

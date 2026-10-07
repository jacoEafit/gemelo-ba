#!/usr/bin/env python3
"""Clima de la Ciudad: temperatura y lluvia diarias (Open-Meteo, reanálisis ERA5) agregadas por mes y año.
Punto único en el centro de CABA: es un dato modelado de grilla (~10-25 km), no la lectura de una estación."""
import collections, json, sys
from comun import bajar, crudo, escribir_json, ultimo_raw

F = "open_meteo"
DESDE, HASTA = "2015-01-01", "2025-12-31"  # años completos
URL = ("https://archive-api.open-meteo.com/v1/archive?latitude=-34.6037&longitude=-58.3816"
       f"&start_date={DESDE}&end_date={HASTA}&daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum"
       "&timezone=America/Argentina/Buenos_Aires")
if "--curar" not in sys.argv:
    bajar(F, URL, "diario.json")
ruta, dia = ultimo_raw(F, "diario.json")
d = json.loads(crudo(ruta).decode("utf-8"))["daily"]

mes_t, mes_p = collections.defaultdict(list), collections.Counter()
anio_t, anio_p, calor, max_abs = collections.defaultdict(list), collections.Counter(), collections.Counter(), {}
for f, t, tmax, p in zip(d["time"], d["temperature_2m_mean"], d["temperature_2m_max"], d["precipitation_sum"]):
    if t is None or p is None:
        continue
    mes_t[f[:7]].append(t)
    mes_p[f[:7]] += p
    anio_t[f[:4]].append(t)
    anio_p[f[:4]] += p
    calor[f[:4]] += tmax is not None and tmax >= 32
    max_abs[f[:4]] = max(max_abs.get(f[:4], -99), tmax if tmax is not None else -99)
ult = HASTA[:4]
anios = sorted(anio_t)
escribir_json("lago/clima.json", {
    "tema": "clima", "probado": dia,
    "fuentes": [{"id": F, "nombre": "Open-Meteo Historical Weather API (reanálisis ERA5/ERA5-Land, ECMWF)",
                 "url": "https://open-meteo.com/en/docs/historical-weather-api", "estado": "vivo", "licencia": "CC-BY-4.0"}],
    "cifras": {
        f"temperatura_media_{ult}": {"valor": round(sum(anio_t[ult]) / len(anio_t[ult]), 1), "unidad": "°C (media anual)",
                                     "vigencia": ult, "fuente": F},
        f"precipitacion_{ult}": {"valor": round(anio_p[ult]), "unidad": "mm (total anual)", "vigencia": ult, "fuente": F},
        f"dias_32c_{ult}": {"valor": calor[ult], "unidad": "días con máxima ≥ 32 °C", "vigencia": ult, "fuente": F},
        f"maxima_{ult}": {"valor": round(max_abs[ult], 1), "unidad": "°C (máxima diaria más alta del año)", "vigencia": ult, "fuente": F},
    },
    "series": {
        "temperatura_media_mensual": {"unidad": "°C", "fuente": F,
                                      "puntos": [[m, round(sum(v) / len(v), 1)] for m, v in sorted(mes_t.items())]},
        "precipitacion_mensual": {"unidad": "mm", "fuente": F, "puntos": [[m, round(v, 1)] for m, v in sorted(mes_p.items())]},
        "temperatura_media_anual": {"unidad": "°C", "fuente": F,
                                    "puntos": [[a, round(sum(anio_t[a]) / len(anio_t[a]), 1)] for a in anios]},
        "precipitacion_anual": {"unidad": "mm", "fuente": F, "puntos": [[a, round(anio_p[a])] for a in anios]},
        "dias_32c_anual": {"unidad": "días con máxima ≥ 32 °C", "fuente": F, "puntos": [[a, calor[a]] for a in anios]},
    },
    "desgloses": {},
    "nota": "Reanálisis (modelo + observaciones) en un punto del centro de CABA, no una estación del SMN: suaviza "
            "extremos (las máximas reales suelen ser más altas) y no distingue barrios. Para comparar con las torres "
            "meteorológicas de la Ciudad (tema sensores) hacen falta sus lecturas, que no están en datos abiertos.",
})
print("clima:", {k: v for k, v in zip(("t", "mm", "d32", "max"), (round(sum(anio_t[ult]) / len(anio_t[ult]), 1),
                                                                 round(anio_p[ult]), calor[ult], max_abs[ult]))}, len(mes_t), "meses")

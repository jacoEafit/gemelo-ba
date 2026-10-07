#!/usr/bin/env python3
"""Correlaciones entre temas ya curados (no descarga nada). Corre al final por orden alfabético (zz_).
Spearman por barrio entre variables del lago. Correlación != causalidad; n pequeño, ver cada `n`."""
import json, pathlib


def rangos(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a) ** .5
    sb = sum((y - mb) ** 2 for y in b) ** .5
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else None


def cargar(tema):
    return json.loads(pathlib.Path(f"lago/{tema}.json").read_text(encoding="utf-8"))


def dic(tema, clave):
    return {k.upper(): v for k, v in cargar(tema)["desgloses"][clave]["filas"]}


pob = dic("demografia", "poblacion_por_barrio")
vars_ = {"delitos_2024": dic("seguridad", "por_barrio_2024"), "obras_registradas": dic("edificios", "por_barrio"),
         "espacios_culturales": dic("cultura", "por_barrio"), "area_km2": dic("atlas_distritos", "area_km2_por_barrio")}
pob_vig = cargar("demografia")["desgloses"]["poblacion_por_barrio"]["vigencia"]
def norm(s):
    s = s.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    return "LA BOCA" if s == "BOCA" else s  # algunas fuentes escriben "Boca"
pob = {norm(k): v for k, v in pob.items()}
vars_ = {n: {norm(k): v for k, v in d.items()} for n, d in vars_.items()}
barrios = sorted(set(pob) & set.intersection(*(set(d) for d in vars_.values())))
cifras, filas = {}, []
fuentes = []
for t in ("demografia", "seguridad", "edificios", "cultura", "atlas_distritos"):
    fuentes += [f for f in cargar(t)["fuentes"] if f not in fuentes]
dia = max(cargar(t)["probado"] for t in ("demografia", "seguridad", "edificios", "cultura", "atlas_distritos"))
for n, d in vars_.items():
    if n == "area_km2":
        continue
    tasa = [d[b] / pob[b] * 1000 for b in barrios]          # por 1000 habitantes
    dens = [pob[b] / vars_["area_km2"][b] for b in barrios]   # hab/km2
    r1 = pearson(rangos([d[b] for b in barrios]), rangos([pob[b] for b in barrios]))
    r2 = pearson(rangos(tasa), rangos(dens))
    filas.append([f"{n} vs población", round(r1, 3)])
    filas.append([f"{n} por 1000 hab vs densidad", round(r2, 3)])
vig = "2024"
escribir = __import__("comun").escribir_json
escribir("lago/correlaciones.json", {
    "tema": "correlaciones", "probado": dia, "fuentes": fuentes,
    "cifras": {"barrios_comparados": {"valor": len(barrios), "unidad": "barrios con todas las variables", "vigencia": vig, "fuente": fuentes[0]["id"]}},
    "series": {},
    "desgloses": {"spearman": {"unidad": "coeficiente de Spearman (-1 a 1)", "fuente": fuentes[0]["id"], "vigencia": vig, "filas": filas}},
    "nota": f"Mezcla vigencias distintas: población barrios Censo {pob_vig}, delitos 2024, obras/cultura acumulados a 2026. "
            "Los delitos y obras de barrios turísticos/comerciales (Palermo, Retiro) se inflan respecto al residente: "
            "la tasa por población residente exagera esos barrios. Indicativo, no causal.",
})
print(f"correlaciones: {len(barrios)} barrios;", filas)

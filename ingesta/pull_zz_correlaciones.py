#!/usr/bin/env python3
"""Correlaciones entre temas ya curados (no descarga nada). Corre al final por orden alfabético (zz_).
Spearman por barrio entre indicadores del lago (tasas por habitante, densidad, alturas). Correlación != causalidad;
n = 48 barrios como máximo."""
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


def norm(s):
    s = s.upper()
    for a, b in zip("ÁÉÍÓÚÜ", "AEIOUU"):
        s = s.replace(a, b)
    return "LA BOCA" if s == "BOCA" else s  # algunas fuentes escriben "Boca"


USADOS = {  # nombre: (tema, desglose); las fuentes del JSON salen solo de estos desgloses
    "poblacion": ("demografia", "poblacion_por_barrio"), "area_km2": ("atlas_distritos", "area_km2_por_barrio"),
    "delitos": ("seguridad", "por_barrio_2024"), "obras": ("edificios", "por_barrio"),
    "cultura": ("cultura", "por_barrio"), "verde_m2": ("espacios_verdes", "m2_por_barrio"),
    "escuelas": ("educacion", "por_barrio"), "altura_mediana": ("edificios", "altura_mediana_por_barrio"),
    "pct_mas_30m": ("edificios", "pct_parcelas_mas_30m_por_barrio"),
    "subte": ("subte_molinetes", "pasajeros_por_barrio_2025"),
}
D = {n: {norm(k): v for k, v in cargar(t)["desgloses"][c]["filas"]} for n, (t, c) in USADOS.items()}
ids = {cargar(t)["desgloses"][c]["fuente"] for t, c in USADOS.values()} | {"ba_parcelas", "ba_barrios"}  # barrio de alturas y estaciones
fuentes, dia = [], ""
for t in sorted({t for t, _ in USADOS.values()}):
    j = cargar(t)
    fuentes += [f for f in j["fuentes"] if f["id"] in ids and f not in fuentes]
    dia = max(dia, j["probado"])
barrios = sorted(set(D["poblacion"]) & set(D["area_km2"]))
pob, area = D["poblacion"], D["area_km2"]
POR_MIL = lambda n: {b: D[n].get(b, 0) / pob[b] * 1000 for b in barrios}
IND = {  # indicador: valores por barrio (0 si el barrio no figura: sin estaciones, sin hechos, etc.)
    "densidad (hab/km²)": {b: pob[b] / area[b] for b in barrios},
    "delitos 2024 por 1000 hab": POR_MIL("delitos"),
    "obras registradas por 1000 hab": POR_MIL("obras"),
    "espacios culturales por 1000 hab": POR_MIL("cultura"),
    "escuelas (ofertas) por 1000 hab": POR_MIL("escuelas"),
    "verde público m² por hab": {b: D["verde_m2"].get(b, 0) / pob[b] for b in barrios},
    "altura mediana de parcela (m)": {b: D["altura_mediana"][b] for b in barrios},
    "% parcelas > 30 m": {b: D["pct_mas_30m"][b] for b in barrios},
    "pasajeros de subte por hab": {b: D["subte"].get(b, 0) / pob[b] for b in barrios},
}
filas = []
for n, clave in (("delitos_2024", "delitos"), ("obras_registradas", "obras"), ("espacios_culturales", "cultura")):
    r = pearson(rangos([D[clave].get(b, 0) for b in barrios]), rangos([pob[b] for b in barrios]))
    filas.append([f"{n} vs población", round(r, 3)])
nombres = list(IND)
for i, a in enumerate(nombres):
    for b in nombres[i + 1:]:
        r = pearson(rangos([IND[a][x] for x in barrios]), rangos([IND[b][x] for x in barrios]))
        filas.append([f"{a} vs {b}", round(r, 3)])
fuertes = sorted((f for f in filas[3:] if abs(f[1]) >= 0.5), key=lambda f: -abs(f[1]))
F0 = USADOS["poblacion"]
f0 = cargar(F0[0])["desgloses"][F0[1]]["fuente"]
pob_vig = cargar("demografia")["desgloses"]["poblacion_por_barrio"]["vigencia"]
vig = "2024"
escribir = __import__("comun").escribir_json
escribir("lago/correlaciones.json", {
    "tema": "correlaciones", "probado": dia, "fuentes": fuentes,
    "cifras": {"barrios_comparados": {"valor": len(barrios), "unidad": "barrios con población y área", "vigencia": vig, "fuente": f0},
               "pares_fuertes": {"valor": len(fuertes), "unidad": "pares de indicadores con |Spearman| ≥ 0,5", "vigencia": vig, "fuente": f0}},
    "series": {},
    "desgloses": {"spearman": {"unidad": "coeficiente de Spearman (-1 a 1), n = barrios_comparados", "fuente": f0, "vigencia": vig, "filas": filas},
                  "spearman_fuertes": {"unidad": "coeficiente de Spearman (|r| ≥ 0,5)", "fuente": f0, "vigencia": vig, "filas": fuertes}},
    "nota": f"Mezcla vigencias: población por barrio del Censo {pob_vig}, delitos 2024, subte 2025, alturas 2021, obras/cultura/"
            "verde/escuelas al día del portal. Las tasas usan población residente: barrios con mucha población flotante "
            "(San Nicolás, Monserrat, Retiro, Puerto Madero) quedan inflados en delitos, cultura, escuelas y subte. "
            "Barrios sin estaciones cuentan 0 pasajeros. Indicativo, no causal.",
})
print(f"correlaciones: {len(barrios)} barrios, {len(filas)} pares; fuertes:")
for f in fuertes:
    print("  ", f)

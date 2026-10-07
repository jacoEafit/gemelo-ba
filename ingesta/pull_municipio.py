#!/usr/bin/env python3
"""Presupuesto de la Ciudad: ejecución del año en curso (último trimestre publicado, acumulado) y del último año
cerrado (4.º trimestre del conjunto histórico). Montos en pesos corrientes; nunca se suma texto."""
import json, pathlib, re, sys
from comun import bajar, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw

ACTUAL, HIST = ("ba_presupuesto", "presupuesto-ejecutado-2026"), ("ba_presupuesto_historico", "presupuesto-ejecutado")
PATRON = re.compile(r"presupuesto-ejecutado-(\d{4})-(\d)(?:-trimestre)?\.csv$")


def recursos(pkg):
    """{(año, trimestre): url} de los CSV de ejecución del conjunto."""
    return {(int(m[1]), int(m[2])): r["url"] for r in pkg["resources"] if (m := PATRON.search(r["url"]))}


def pesos(s):
    s = (s or "").strip()
    if not re.fullmatch(r"-?\d{1,3}(\.\d{3})*", s):  # formato del portal: punto de miles, sin decimales
        raise SystemExit(f"monto con formato inesperado: {s!r}")
    return int(s.replace(".", ""))


def ejecucion(fuente, pkg, anio, trim, dia):
    nombre = f"{anio}_trim{trim}.csv"
    if "--curar" not in sys.argv:
        bajar(fuente, recursos(pkg)[(anio, trim)], nombre)
    filas = leer_csv(ultimo_raw(fuente, nombre)[0])
    # «Vigente_Trim2_CONT» en el año en curso, «Vigente» en el histórico; «Sanción» llega con o sin tilde
    col = {k.split("_")[0].lower(): k for k in filas[0]
           if k.split("_")[0].lower() in ("vigente", "definitivo", "devengado")}
    col["sancion"] = next(k for k in filas[0] if k.lower().startswith("sanc"))
    if len(col) != 4:
        raise SystemExit(f"{nombre}: columnas de montos inesperadas {list(filas[0])[-6:]}")
    tot = {k: sum(pesos(f[c]) for f in filas) for k, c in col.items()}
    vig = f"{anio}-{trim * 3:02d}"

    def por(clave):
        c = {}
        for f in filas:
            k = (f[clave] or "").strip() or "sin dato"
            c[k] = c.get(k, 0) + pesos(f[col["devengado"]])
        return {"unidad": f"pesos corrientes devengados (acumulado a {vig})", "fuente": fuente, "vigencia": vig,
                "filas": sorted(([k, v] for k, v in c.items()), key=lambda x: (-x[1], x[0]))}
    return filas, tot, vig, por


cifras, desgloses = {}, {}
pkg_a, dia_a = paquete(*ACTUAL)
anio, trim = max(recursos(pkg_a))
filas, tot, vig, por = ejecucion(ACTUAL[0], pkg_a, anio, trim, dia_a)
cifras["registros"] = {"valor": len(filas), "unidad": f"filas de presupuesto ({anio} T{trim})", "vigencia": vig, "fuente": ACTUAL[0]}
cifras[f"sancionado_{anio}"] = {"valor": tot["sancion"], "unidad": "pesos corrientes (crédito sancionado)",
                                "vigencia": str(anio), "fuente": ACTUAL[0]}
cifras[f"vigente_{anio}"] = {"valor": tot["vigente"], "unidad": f"pesos corrientes (crédito vigente al T{trim})",
                             "vigencia": vig, "fuente": ACTUAL[0]}
cifras[f"devengado_{anio}"] = {"valor": tot["devengado"], "unidad": f"pesos corrientes devengados (acumulado al T{trim})",
                               "vigencia": vig, "fuente": ACTUAL[0]}
cifras[f"ejecucion_{anio}"] = {"valor": round(100 * tot["devengado"] / tot["vigente"], 1),
                               "unidad": f"% del crédito vigente devengado (acumulado al T{trim})", "vigencia": vig, "fuente": ACTUAL[0]}
desgloses[f"devengado_por_finalidad_{anio}"] = por("Desc_Fin")
desgloses[f"devengado_por_jurisdiccion_{anio}"] = por("Desc_Jur")
desgloses[f"devengado_por_ubicacion_{anio}"] = por("Desc_Geo")

pkg_h, dia_h = paquete(*HIST)
cerrado = max(a for a, t in recursos(pkg_h) if t == 4)
_, tot_h, vig_h, por_h = ejecucion(HIST[0], pkg_h, cerrado, 4, dia_h)
cifras[f"vigente_{cerrado}"] = {"valor": tot_h["vigente"], "unidad": "pesos corrientes (crédito vigente al cierre)",
                                "vigencia": str(cerrado), "fuente": HIST[0]}
cifras[f"devengado_{cerrado}"] = {"valor": tot_h["devengado"], "unidad": "pesos corrientes devengados (año completo)",
                                  "vigencia": str(cerrado), "fuente": HIST[0]}
desgloses[f"devengado_por_finalidad_{cerrado}"] = por_h("Desc_Fin")

# Pesos constantes: el devengado del año cerrado llevado a precios del último IPCBA (lago/economia.json, corre antes)
eco = json.loads(pathlib.Path("lago/economia.json").read_text(encoding="utf-8"))
ipc = dict(eco["series"]["ipcba"]["puntos"])
ult = max(ipc)
meses = [v for p, v in ipc.items() if p.startswith(str(cerrado))]
if len(meses) == 12:
    cifras[f"devengado_{cerrado}_a_precios_{ult}"] = {
        "valor": round(tot_h["devengado"] * ipc[ult] / (sum(meses) / 12)),
        "unidad": f"pesos de {ult} (devengado {cerrado} × IPCBA {ult} / IPCBA promedio {cerrado})",
        "vigencia": str(cerrado), "fuente": HIST[0]}

escribir_json("lago/municipio.json", {
    "tema": "municipio", "probado": max(dia_a, dia_h),
    "fuentes": [fuente_ckan(ACTUAL[0], pkg_a, ACTUAL[1]), fuente_ckan(HIST[0], pkg_h, HIST[1])]
               + [f for f in eco["fuentes"] if f["id"] == "ipcba"],
    "cifras": cifras, "series": {}, "desgloses": desgloses,
    "nota": f"Pesos corrientes salvo la cifra «a_precios_»: {cerrado} y {anio} no son comparables sin deflactar. El ajuste usa el "
            "IPCBA promedio del año como aproximación (el gasto no se reparte parejo en el año). "
            f"El trimestre es acumulado desde enero ({anio} T{trim} = enero a {vig}). «Ubicación» es la geográfica del "
            "gasto: incluye comunas, distritos escolares y zona externa. Se concentra en las comunas 4 y 1 porque ahí se "
            "imputa gasto central de la administración: no es gasto «en» esos barrios ni sirve para comparar comunas.",
})
print("municipio:", {k: v["valor"] for k, v in cifras.items()})

#!/usr/bin/env python3
"""Residuos: puntos verdes (reciclaje) por barrio y tipo, y kilos de RAEE (aparatos eléctricos y electrónicos) recibidos."""
import collections, re, sys
from comun import bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw
from ckan_tema import elegir

F, SLUG = "ba_puntos_verdes", "puntos-verdes"
pkg, dia = paquete(F, SLUG)
r_pts = elegir(pkg["resources"], ("csv",), "Puntos Verdes (CSV)")
r_raee = elegir(pkg["resources"], ("csv",), "(2019 - 2026) Pesaje y cantidad de Residuos de Aparatos")
if "--curar" not in sys.argv:
    bajar(F, r_pts["url"], "puntos.csv")
    bajar(F, r_raee["url"], "raee.csv")
d = ultimo_raw(F, "puntos.csv")[0].parent
pts, raee = leer_csv(d / "puntos.csv"), leer_csv(d / "raee.csv")
vig = pkg["metadata_modified"][:7]


def barrio(s):
    s = s.strip().upper()
    for a, b in zip("ÁÉÍÓÚÜ", "AEIOUU"):
        s = s.replace(a, b)
    return "LA BOCA" if s == "BOCA" else s or "sin dato"


ilegibles = []


def kilos(s):
    """El recurso mezcla formatos: «2,577.30» (coma de miles) y «49,4» (coma decimal); «.» o vacío = sin dato.
    Erratas («120.,97») y ambiguos («4,033»: ¿miles o decimal?) no se adivinan: cuentan como ilegibles."""
    s = s.strip()
    if s in ("", ".", "-"):
        return None
    if re.fullmatch(r"\d{1,3}(,\d{3})+\.\d+", s):
        return float(s.replace(",", ""))
    if re.fullmatch(r"\d+(,\d{1,2})?", s) or re.fullmatch(r"\d+\.\d{1,2}", s):
        return float(s.replace(",", "."))
    ilegibles.append(s)
    return None


por_anio = collections.Counter()
sin_dato = 0
for x in raee:
    k = kilos(x["kilos"])
    if k is None:
        sin_dato += 1
        continue
    por_anio[x["año"].strip()] += k
if len(ilegibles) > 20:
    raise SystemExit(f"{len(ilegibles)} kilos ilegibles: revisar el crudo ({ilegibles[:5]})")
anios = sorted(por_anio)
completo = max(a for a in anios if len({x["mes"].strip().upper() for x in raee if x["año"].strip() == a}) == 12)
escribir_json("lago/residuos.json", {
    "tema": "residuos", "probado": dia, "fuentes": [fuente_ckan(F, pkg, SLUG)],
    "cifras": {"puntos_verdes": {"valor": len(pts), "unidad": "puntos verdes", "vigencia": vig, "fuente": F},
               f"raee_kg_{completo}": {"valor": round(por_anio[completo]), "unidad": "kg de RAEE recibidos en el año",
                                       "vigencia": completo, "fuente": F}},
    "series": {"raee_kg_anual": {"unidad": "kg de RAEE recibidos", "fuente": F,
                                 "puntos": [[a, round(por_anio[a])] for a in anios]}},
    "desgloses": {"por_barrio": desglose(pts, "barrio", "puntos verdes", F, vig, norm=barrio),
                  "por_tipo": desglose(pts, "tipo", "puntos verdes", F, vig)},
    "nota": f"El listado trae {len(pts)} puntos verdes (todos «Con Atención»): no incluye necesariamente los puntos sin atención ni campanas. RAEE incluye puntos verdes fijos y móviles; {anios[-1]} puede estar incompleto; {sin_dato} filas sin "
            f"kilos legibles (incluye {len(ilegibles)} erratas o ambiguos como {ilegibles[:2]}). El crudo mezcla coma decimal y coma de miles: se normaliza por patrón. Solo lo que pasa por "
            "puntos verdes: no es el total de residuos de la Ciudad.",
})
print(f"residuos: {len(pts)} puntos verdes, RAEE {[[a, round(por_anio[a])] for a in anios]}")

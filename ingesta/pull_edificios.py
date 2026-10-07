#!/usr/bin/env python3
"""Edificios: obras registradas (permisos de obra, no volúmenes) y alturas del Tejido Urbano por parcela y barrio.
El tejido trae una fila por volumen edificado (altura en m, sin superficie ni barrio): se toma la altura máxima de
cada parcela (smp) y se cruza con Parcelas (barrio) leyendo el .dbf del SHP con la biblioteca estándar."""
import collections, io, json, statistics, struct, sys, zipfile
from ckan_tema import ejecutar
from comun import bajar, desglose, escribir_json, fuente_ckan, leer_csv, paquete, ultimo_raw


def extra(ruta, fuente, vig):
    f = leer_csv(ruta)
    anios = collections.Counter()
    for x in f:
        partes = (x.get("fecha") or "").split()[0].split("/") if x.get("fecha") else []
        anios[partes[2] if len(partes) == 3 else "sin dato"] += 1
    return {"por_barrio": desglose(f, "barrio", "obras registradas", fuente, vig, norm=lambda s: s.strip().upper()),
            "por_anio": {"unidad": "obras registradas", "fuente": fuente, "vigencia": vig,
                         "filas": sorted([k, v] for k, v in anios.items())}}


ejecutar("edificios", "ba_obras_registradas", "obras-registradas", ("csv",), unidad="obras registradas", extra=extra)

# --- Tejido urbano: alturas ---
T, P = ("ba_tejido_urbano", "tejido-urbano"), ("ba_parcelas", "parcelas")
pkg_t, dia_t = paquete(*T)
pkg_p, dia_p = paquete(*P)
if "--curar" not in sys.argv:
    bajar(T[0], next(r["url"] for r in pkg_t["resources"] if r["url"].endswith(".csv")), "tejido.csv")
    bajar(P[0], next(r["url"] for r in pkg_p["resources"] if r["url"].endswith("parcelas_catastrales.zip")), "parcelas_shp.zip")


def smp(s):
    """«055 - 200 - 005» y «55-200-5» son la misma parcela: sin espacios ni ceros a la izquierda.
    El tejido trae la Ñ doblemente codificada («Ã‘»): se repara."""
    s = s.replace("Ã‘", "Ñ").replace("Ã±", "Ñ")
    return "-".join(p.strip().lstrip("0") or "0" for p in s.upper().split("-"))


def barrio(s):
    s = s.strip().upper()
    for a, b in zip("ÁÉÍÓÚÜ", "AEIOUU"):
        s = s.replace(a, b)
    return "LA BOCA" if s == "BOCA" else s


def dbf(datos, enc):
    """Registros de un .dbf (dBase III) como dicts de texto."""
    n, cab, largo = struct.unpack("<IHH", datos[4:12])
    campos, i = [], 32
    while datos[i] != 0x0D:
        campos.append((datos[i:i + 11].split(b"\0")[0].decode("ascii"), datos[i + 16]))
        i += 32
    for r in range(n):
        reg = datos[cab + r * largo: cab + (r + 1) * largo]
        if reg[:1] == b"*":  # registro borrado
            continue
        pos, fila = 1, {}
        for nombre, ancho in campos:
            fila[nombre.lower()] = reg[pos:pos + ancho].decode(enc).strip()
            pos += ancho
        yield fila


z = zipfile.ZipFile(ultimo_raw(P[0], "parcelas_shp.zip")[0])
n_dbf = next(n for n in z.namelist() if n.lower().endswith(".dbf"))
cpg = next((n for n in z.namelist() if n.lower().endswith(".cpg")), None)
enc = z.read(cpg).decode().strip() if cpg else "latin-1"
enc = "utf-8" if enc.upper().replace("-", "") == "UTF8" else enc
barrio_de, manzanas = {}, collections.defaultdict(collections.Counter)
for f in dbf(z.read(n_dbf), enc):
    if f.get("smp") and f.get("barrio"):
        k = smp(f["smp"])
        barrio_de[k] = barrio(f["barrio"])
        manzanas[k.rsplit("-", 1)[0]][barrio_de[k]] += 1
# Si la parcela de 2021 ya no existe en el catastro actual (subdivisiones, unificaciones), vale el barrio de su manzana
barrio_manzana = {m: c.most_common(1)[0][0] for m, c in manzanas.items()}
ALTURA_MAX = 250  # m: el edificio más alto de la Ciudad ronda los 235 m; por encima son errores del tejido

volumenes, descartados, alt = 0, 0, {}
tipos = collections.Counter()
for f in leer_csv(ultimo_raw(T[0], "tejido.csv")[0]):
    volumenes += 1
    h = float(f["altura"])  # punto decimal en el crudo
    if not 0 < h <= ALTURA_MAX:
        descartados += 1
        continue
    tipos[f["tipo"].strip() or "sin dato"] += 1
    k = smp(f["smp"])
    alt[k] = max(h, alt.get(k, 0.0))

por_barrio, via = collections.defaultdict(list), collections.Counter()
for k, h in alt.items():
    b = barrio_de.get(k) or barrio_manzana.get(k.rsplit("-", 1)[0])
    via["parcela" if k in barrio_de else "manzana" if b else "sin cruce"] += 1
    if b:
        por_barrio[b].append(h)
con_barrio = via["parcela"] + via["manzana"]
RANGOS = [(0, 9, "hasta 9 m (≈1-3 pisos)"), (9, 15, "9 a 15 m (≈4-5 pisos)"), (15, 30, "15 a 30 m (≈6-10 pisos)"),
          (30, 60, "30 a 60 m (≈11-20 pisos)"), (60, 1e9, "más de 60 m (>20 pisos)")]
vig = "2021"  # el portal declara datos del tejido hasta 2021
U = "parcelas edificadas"


def filas(f):
    return sorted(([k, v] for k, v in f.items()), key=lambda x: (-x[1], x[0]))


d = json.load(open("lago/edificios.json", encoding="utf-8"))
d["fuentes"] += [fuente_ckan(T[0], pkg_t, T[1]), fuente_ckan(P[0], pkg_p, P[1])]
d["probado"] = max(d["probado"], dia_t, dia_p)
d["cifras"].update({
    "volumenes_edificados": {"valor": volumenes, "unidad": "volúmenes edificados (filas del tejido)", "vigencia": vig, "fuente": T[0]},
    "volumenes_descartados": {"valor": descartados, "unidad": f"volúmenes con altura 0 o mayor a {ALTURA_MAX} m (errores)",
                              "vigencia": vig, "fuente": T[0]},
    "parcelas_edificadas": {"valor": len(alt), "unidad": U, "vigencia": vig, "fuente": T[0]},
    "parcelas_cruzadas_con_barrio": {"valor": con_barrio, "unidad": f"{U} con barrio (por parcela o por manzana)",
                                     "vigencia": vig, "fuente": P[0]},
    "altura_mediana_parcela": {"valor": round(statistics.median(alt.values()), 1),
                               "unidad": "m (mediana de la altura máxima por parcela)", "vigencia": vig, "fuente": T[0]},
    "altura_maxima": {"valor": round(max(alt.values()), 1), "unidad": "m (volumen más alto del tejido)", "vigencia": vig, "fuente": T[0]},
})
d["desgloses"].update({
    "parcelas_por_via_de_cruce": {"unidad": U, "fuente": P[0], "vigencia": vig, "filas": filas(via)},
    "parcelas_por_rango_altura": {"unidad": U, "fuente": T[0], "vigencia": vig, "filas": [
        [nombre, sum(lo <= h < hi for h in alt.values())] for lo, hi, nombre in RANGOS]},
    "volumenes_por_tipo": {"unidad": "volúmenes edificados", "fuente": T[0], "vigencia": vig, "filas": filas(tipos)},
    "parcelas_edificadas_por_barrio": {"unidad": U, "fuente": P[0], "vigencia": vig,
                                       "filas": filas({b: len(v) for b, v in por_barrio.items()})},
    "altura_mediana_por_barrio": {"unidad": "m (mediana de la altura máxima por parcela)", "fuente": T[0], "vigencia": vig,
                                  "filas": filas({b: round(statistics.median(v), 1) for b, v in por_barrio.items()})},
    "pct_parcelas_mas_30m_por_barrio": {"unidad": "% de parcelas edificadas con más de 30 m", "fuente": T[0], "vigencia": vig,
                                        "filas": filas({b: round(100 * sum(h > 30 for h in v) / len(v), 1)
                                                        for b, v in por_barrio.items()})},
})
d["nota"] = ("Obras registradas: vigencia = mes de la última modificación del conjunto; son permisos, no volúmenes. "
             "Tejido urbano: alturas por fotogrametría (Secretaría de Planeamiento) con datos hasta 2021; muchas alturas "
             "son pisos × 2,8 m. La altura de una parcela es la de su volumen más alto. El barrio sale de Parcelas (catastro "
             "actual); si la parcela de 2021 ya no existe, se usa el de su manzana. Sin superficie no hay volumen "
             "construido (m³). Las geometrías 3D (~1 GB) no están en el lago: ver contrato (GeoParquet/PMTiles).")
escribir_json("lago/edificios.json", d)
print(f"edificios/tejido: {volumenes:,} volúmenes ({descartados} descartados), {len(alt):,} parcelas, "
      f"cruce {dict(via)} ({100 * con_barrio / len(alt):.1f} %), {len(por_barrio)} barrios")

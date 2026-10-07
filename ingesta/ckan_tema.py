"""Ingesta genérica de un conjunto de BA Data: descarga el crudo y cura el tema con el contrato."""
import json, sys
from comun import API, PORTAL, bajar, contar, escribir_json, ultimo_raw


def elegir(recursos, formatos, contiene=None):
    for f in formatos:
        for r in recursos:
            if (r.get("format") or "").lower() == f and (contiene is None or contiene in (r.get("name") or "")):
                return r
    raise SystemExit(f"Sin recurso {formatos} (contiene={contiene}). Revisa los recursos del conjunto.")


def ejecutar(tema, fuente, slug, formatos, unidad, contiene=None, extra=None):
    if "--curar" not in sys.argv:
        ruta, _ = bajar(fuente, f"{API}/package_show?id={slug}", "package.json")
        pkg = json.loads(ruta.read_text(encoding="utf-8"))["result"]
        r = elegir(pkg["resources"], formatos, contiene)
        bajar(fuente, r["url"], "datos." + r["format"].lower())

    ruta, dia = ultimo_raw(fuente, "package.json")
    pkg = json.loads(ruta.read_text(encoding="utf-8"))["result"]
    r = elegir(pkg["resources"], formatos, contiene)
    n, campos = contar(ruta.with_name("datos." + r["format"].lower()))

    vig = (pkg.get("metadata_modified") or dia)[:7]
    desgloses = extra(ruta.with_name("datos." + r["format"].lower()), fuente, vig) if extra else {}
    escribir_json(f"lago/{tema}.json", {
        "tema": tema,
        "probado": dia,
        "fuentes": [{"id": fuente, "nombre": pkg["title"], "url": f"{PORTAL}/{slug}",
                     "estado": "vivo",
                     "licencia": pkg.get("license_title") or pkg.get("license_id") or "sin licencia declarada"}],
        "cifras": {"registros": {"valor": n, "unidad": unidad,
                                 "vigencia": vig, "fuente": fuente}},
        "series": {},
        "desgloses": desgloses,
        "campos": campos,
        "recurso": {"nombre": r.get("name"), "url": r["url"], "formato": r["format"]},
        "nota": "vigencia = mes de la última modificación del conjunto en el portal",
    })
    print(f"{tema}: {n} {unidad}")

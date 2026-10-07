#!/usr/bin/env python3
"""Prueba del verificador: rompe una COPIA del lago a propósito y exige que verificar.py falle en cada caso.
No toca lago/. Uso, desde la raíz:  python3 verificacion/probar_que_falla.py
Una verificación que nunca falla no está verificando (lámina del lago, taller)."""
import json, pathlib, shutil, subprocess, sys, tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def romper_cifra_sin_fuente(lago):
    j = json.loads((lago / "seguridad.json").read_text(encoding="utf-8"))
    j["cifras"]["sin_fuente"] = {"valor": 12, "unidad": "personas", "vigencia": "2026"}
    (lago / "seguridad.json").write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")


def romper_correo_y_celular(lago):
    j = json.loads((lago / "escucha.json").read_text(encoding="utf-8"))
    j["nota"] = "dudas: escribir a nombre@ejemplo.com o al 11 4331-0091"
    (lago / "escucha.json").write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")


def romper_suma_por_barrio(lago):
    j = json.loads((lago / "seguridad.json").read_text(encoding="utf-8"))
    j["desgloses"]["por_barrio_2024"]["filas"][0][1] += 1  # un delito de más en un barrio
    (lago / "seguridad.json").write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")


def romper_dominio(lago):
    j = json.loads((lago / "geoinfraestructura.json").read_text(encoding="utf-8"))
    j["cifras"]["estaciones_linea"]["valor"] = 48  # el error histórico: 48 filas de viajes leídas como estaciones
    (lago / "geoinfraestructura.json").write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")


def romper_fecha_con_hora(lago):
    j = json.loads((lago / "clima.json").read_text(encoding="utf-8"))
    j["probado"] = "2026-10-06T21:05:00"
    (lago / "clima.json").write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")


def romper_coordenada_fuera(lago):
    g = json.loads((lago / "geo/subte_estaciones.geojson").read_text(encoding="utf-8"))
    g["features"][0]["geometry"]["coordinates"] = [-34.6, -58.4]  # lon y lat invertidas
    (lago / "geo/subte_estaciones.geojson").write_text(json.dumps(g, ensure_ascii=False), encoding="utf-8")


def romper_ingesta_a_medias(lago):
    (lago / "seguridad.json").unlink()  # una descarga falló: el tema no se generó


CASOS = [romper_ingesta_a_medias, romper_cifra_sin_fuente, romper_correo_y_celular, romper_suma_por_barrio, romper_dominio,
         romper_fecha_con_hora, romper_coordenada_fuera]


def verificar(dir_):
    r = subprocess.run([sys.executable, str(RAIZ / "verificacion/verificar.py")], cwd=dir_, capture_output=True, text=True)
    return r.returncode, [l for l in r.stdout.splitlines() if l.startswith("FAIL")]


malos = 0
with tempfile.TemporaryDirectory() as tmp:
    base = pathlib.Path(tmp)
    shutil.copytree(RAIZ / "lago", base / "lago", ignore=shutil.ignore_patterns("raw"))
    codigo, fallas = verificar(base)
    print(f"lago intacto: {'PASA' if codigo == 0 else 'FALLA'} ({len(fallas)} FAIL)")
    malos += codigo != 0
    for caso in CASOS:
        d = base / caso.__name__
        shutil.copytree(base / "lago", d / "lago")
        caso(d / "lago")
        codigo, fallas = verificar(d)
        atrapado = codigo != 0 and fallas
        malos += not atrapado
        print(f"{caso.__name__}: {'atrapado' if atrapado else 'NO ATRAPADO'}")
        for f in fallas[:2]:
            print("   ", f[:150])
print(f"\n{malos} problemas en la prueba del verificador")
sys.exit(1 if malos else 0)

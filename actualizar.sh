#!/bin/sh
# Descarga lo nuevo, cura y verifica.
set -e
for s in ingesta/pull_*.py; do python3 "$s"; done
python3 verificacion/verificar.py

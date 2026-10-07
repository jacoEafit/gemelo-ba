#!/bin/sh
# Reconstruye el lago curado desde lago/raw. Si git diff sale vacío, es reproducible.
set -e
rm -f lago/*.json lago/geo/*.geojson
for s in ingesta/pull_*.py; do python3 "$s" --curar; done
python3 verificacion/verificar.py
git diff --stat -- lago/

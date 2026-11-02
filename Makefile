# Mapa 3D de Buenos Aires: make tiles && make serve
URL   = https://cdn.buenosaires.gob.ar/datosabiertos/datasets/secretaria-de-desarrollo-urbano/tejido-urbano/tejido.geojson
RAW   = lago/raw/tejido_geo/tejido.geojson
TILES = web/edificios.pmtiles
PORT ?= 8000

.PHONY: all tiles datos serve clean
all: tiles datos

$(RAW):
	mkdir -p $(dir $@)
	curl -L --fail -C - -o $@.part $(URL) && mv $@.part $@

# Teselas vectoriales de edificios (solo altura y parcela). Requiere tippecanoe: brew install tippecanoe
tiles: $(TILES)
$(TILES): $(RAW)
	tippecanoe -o $@ --force -l edificios -Z10 -z16 -y altura -y smp \
	  --drop-densest-as-needed --coalesce-densest-as-needed --simplification=4 $<

# Copia el lago a web/datos para que la página lo lea (no se versiona: sale del lago).
datos:
	mkdir -p web/datos/geo
	cp lago/*.json web/datos/
	cp lago/geo/*.geojson web/datos/geo/

# PMTiles necesita peticiones Range: python -m http.server no las soporta, http-server sí.
serve: datos
	@echo "http://localhost:$(PORT)"
	npx --yes http-server web -p $(PORT) -c-1

clean:
	rm -f $(TILES)
	rm -rf web/datos

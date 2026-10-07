#!/usr/bin/env python3
"""Entrega 1 · llena «Por qué estos datos» (plantilla Word del profesor) con respuestas que citan los ID del Excel.
Uso, desde la raíz:  python3 entrega/generar_preguntas.py   (solo biblioteca estándar)
Las cifras de la prosa salen de lago/*.json, no se escriben a mano: si el lago cambia, se vuelve a correr."""
import json, pathlib, re, shutil, tempfile, zipfile
from xml.sax.saxutils import escape

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "entrega" / "plantilla_Preguntas_por_que_estos_datos.docx"
SALIDA = RAIZ / "entrega" / "Preguntas_por_que_estos_datos_Buenos_Aires.docx"
lago = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (RAIZ / "lago").glob("*.json")}


def c(tema, clave):
    return lago[tema]["cifras"][clave]


def n(x):
    return f"{x:,}".replace(",", ".")


pob22, pob10 = c("demografia", "poblacion_comunas"), c("demografia", "poblacion_barrios")
d24, d25 = c("seguridad", "delitos_2024"), c("seguridad", "delitos_2025")
min_barrio = min((v, b) for b, v in lago["seguridad"]["desgloses"]["por_barrio_2025"]["filas"] if b != "sin dato")
mun_s = c("municipio", "sancionado_2026")["vigencia"]
san, dev, ejec = c("municipio", "sancionado_2026"), c("municipio", "devengado_2026"), c("municipio", "ejecucion_2026")
dev25, dev25r = c("municipio", "devengado_2025"), next(v for k, v in lago["municipio"]["cifras"].items() if "a_precios" in k)
tot_ultimo = c("turismo", "viajeros_total_ultimo_mes")
res_ultimo, nores_ultimo = c("turismo", "viajeros_residentes_ultimo_mes"), c("turismo", "viajeros_no_residentes_ultimo_mes")
probado = max(j["probado"] for j in lago.values())
billones = lambda x: f"${x / 1e12:,.2f} billones".replace(".", ",")

CABECERA = {"Ciudad": "Buenos Aires (Ciudad Autónoma de Buenos Aires, Argentina)", "Fecha": probado}

# Cada respuesta: lista de párrafos; un párrafo es texto o (negrita, texto)
R = {
    "1.": [
        "Para un concejal de la Legislatura porteña y su equipo asesor: necesitan comparar los 48 barrios antes de votar el "
        "presupuesto o pedir informes al Ejecutivo, con cifras que puedan citar con fuente y fecha.",
        ("P1. ", f"¿Cuánta gente vive en cada barrio y qué salud, educación y cultura tiene cerca? Censo 2022 por comuna "
                 f"({n(pob22['valor'])} habitantes, F04), Censo 2010 por barrio (F03), hospitales y CESAC (F22, F23), "
                 "escuelas (F21) y espacios culturales (F13)."),
        ("P2. ", f"¿Cómo gasta la Ciudad su presupuesto y cuánto vale en pesos de hoy? Sancionado {mun_s} {billones(san['valor'])}, "
                 f"devengado a {dev['vigencia']} {billones(dev['valor'])} ({str(ejec['valor']).replace('.', ',')} % del vigente) "
                 f"(F06, F07), deflactado con el IPC de la Ciudad (F08)."),
        ("P3. ", f"¿Qué pasa con la seguridad en cada barrio? {n(d24['valor'])} delitos registrados en 2024 y {n(d25['valor'])} "
                 "en 2025, por barrio, tipo y mes (F05)."),
        "El diccionario usa además tres preguntas más (P4 turismo y empleo, P5 suelo y ambiente, P6 movilidad), en su última columna.",
    ],
    "2.": [
        ("F04 · Censo 2022 por comuna. ", f"Es la única población oficial reciente ({n(pob22['valor'])} habitantes) y la base de "
         "cualquier tasa por habitante. La publica la Dirección de Estadística de la Ciudad con datos del INDEC (informe 1877, "
         "julio de 2024). No declara licencia y vino en PDF: la transcribimos, la marcamos como «declarada» y comprobamos que "
         "las 15 comunas suman el total oficial."),
        ("F05 · Delitos. ", f"Es el único dato de seguridad por barrio y por mes. Lo publica el Ministerio de Justicia y Seguridad "
         f"porteño con licencia «Creative Commons Attribution»; 2024 y 2025 están completos (12 meses cada uno). Son hechos "
         "registrados, no tasas: por eso los cruzamos con población antes de comparar barrios."),
        ("F06 y F07 · Presupuesto ejecutado. ", "Es la única fuente del gasto real (no del aprobado): por jurisdicción, finalidad "
         "y ubicación. Lo publica el Ministerio de Hacienda porteño cada trimestre, con licencia Creative Commons; el último "
         f"corte es {dev['vigencia']}. Lo deflactamos con F08: el gasto 2025 ({billones(dev25['valor'])}) equivale a "
         f"{billones(dev25r['valor'])} de {dev25r['unidad'].split()[2]}."),
    ],
    "3.": [
        ("F31 · Reclamos ciudadanos (SUACI / BA Colaborativa). ", "Lo descartamos por peso: un CSV por año de 100 a 277 MB, "
         "unos 2 GB en total, para un lago que en limpio pesa menos de 1 MB. Perdimos la voz de los vecinos: qué reclaman y "
         "dónde (baches, luminarias, ruido). Hoy la única «escucha» del sistema son las visitas a Wikipedia (F12), que miden "
         "interés, no opinión."),
        "Al revisar el mismo conjunto encontramos un archivo ya agregado por barrio, de 2,7 MB (F32). Lo dejamos como "
        "candidata: podría devolver los reclamos al sistema sin la descarga pesada, después de abrirlo y revisar si trae "
        "texto libre o datos de personas.",
    ],
    "4.": [
        ("Nos ayudó (Bitácora IA, fila 9, F11). ", "La ocupación hotelera no estaba en el portal de la Ciudad. La IA la buscó "
         "en la API de series de datos.gob.ar y encontró la Encuesta de Ocupación Hotelera del INDEC. La comprobamos con los "
         f"propios datos: residentes más no residentes da el total en cada mes ({n(res_ultimo['valor'])} + "
         f"{n(nores_ultimo['valor'])} = {n(tot_ultimo['valor'])} en {tot_ultimo['vigencia']}), y hoy esa suma es una regla "
         "del verificador."),
        ("Se equivocó (Bitácora IA, fila 2, F24). ", "Contó 48 estaciones de subte. Nos pareció sospechoso para una red de 6 líneas y lo anotamos como problema "
         "conocido; al abrir el CSV vimos que eran "
         "48 filas de pasajeros por año y línea; las estaciones son 90 pares estación-línea (88 nombres). La cifra era "
         "verosímil, y por eso pasó. Hoy el verificador falla si vuelve a aparecer un 48 ahí. Otros errores registrados: "
         "las unidades del aire (fila 3), la comuna con más gasto (fila 10) y una altura de 830 m (fila 12)."),
    ],
    "5.": [
        ("El campo: las coordenadas, la fecha y la franja horaria de cada delito (F05). ", "Ninguno dice quién es la víctima, "
         "pero cruzados con un padrón o un mapa de direcciones pueden señalar la casa o la rutina de una persona: dónde y a qué "
         "hora le robaron. El crudo los trae hecho por hecho."),
        ("Lo que decidimos: agregarlo por zona. ", "Al lago solo pasan conteos por barrio, por tipo y por mes, en tablas "
         "separadas, sin coordenadas ni identificadores (diccionario: seguridad · por_barrio_<año>, por_tipo_<año>, "
         f"delitos_mensuales_<año>). El grupo más chico es {min_barrio[1].title()} con {n(min_barrio[0])} delitos en 2025: "
         "muy lejos de identificar a nadie. El crudo queda en lago/raw, que no se sube al repositorio. Hicimos lo mismo con "
         "los teléfonos y correos de alojamientos y espacios culturales (F10, F13): no se copian."),
    ],
    "6.": [
        ("Población 2022 por barrio. ", f"No existe abierta: el Censo 2022 se publicó por comuna (F04) y los radios censales "
         f"del portal son de 2001 y 2010 (F35, descartada). La reemplazamos con el Censo 2010 por barrio "
         f"({n(pob10['valor'])} habitantes, F03), con dos costos: las tasas por habitante de cada barrio usan población de hace "
         "16 años, y las cifras por barrio y por comuna no se pueden comparar entre sí. Para saberlo habría que conseguir los "
         "radios 2022 del INDEC y agregarlos a los límites de barrio."),
        ("Lecturas en tiempo real. ", "La API de Transporte (F33) está suspendida por el portal: de sensores y torres "
         "meteorológicas solo tenemos el inventario. La pregunta «¿cómo está el tránsito ahora?» queda sin responder."),
    ],
}


def parrafo(item):
    runs = []
    if isinstance(item, tuple):
        runs.append(f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">{escape(item[0])}</w:t></w:r>')
        item = item[1]
    runs.append(f'<w:r><w:t xml:space="preserve">{escape(item)}</w:t></w:r>')
    return '<w:p><w:pPr><w:spacing w:after="100"/></w:pPr>' + "".join(runs) + "</w:p>"


VACIO = re.compile(r'<w:p [^>]*><w:pPr><w:spacing w:after="40"/></w:pPr><w:r>(?:<w:lastRenderedPageBreak/>)?<w:t xml:space="preserve"> </w:t></w:r></w:p>')  # Word marca saltos de página

with tempfile.TemporaryDirectory() as tmp:
    with zipfile.ZipFile(PLANTILLA) as z:
        z.extractall(tmp)
    doc = pathlib.Path(tmp, "word", "document.xml")
    x = doc.read_text(encoding="utf-8")
    for etiqueta, valor in CABECERA.items():
        i = x.index(f"<w:t>{etiqueta}</w:t>")
        m = VACIO.search(x, i)
        x = x[:m.start()] + parrafo(valor).replace('w:after="100"', 'w:after="40"') + x[m.end():]
    for num, parrafos in R.items():
        i = x.index(f"<w:t>{num} ")
        fin_celda = x.index("</w:tc>", i)
        celda = x[i:fin_celda]
        vacios = list(VACIO.finditer(celda))
        if len(vacios) != 6:
            raise SystemExit(f"Pregunta {num}: se esperaban 6 renglones vacíos y hay {len(vacios)}")
        nueva = celda[:vacios[0].start()] + "".join(parrafo(p) for p in parrafos) + celda[vacios[-1].end():]
        x = x[:i] + nueva + x[fin_celda:]
    doc.write_text(x, encoding="utf-8")
    tmpzip = pathlib.Path(tmp) / "salida.docx"
    with zipfile.ZipFile(PLANTILLA) as orig, zipfile.ZipFile(tmpzip, "w", zipfile.ZIP_DEFLATED) as out:
        for info in orig.infolist():  # mismo orden de entradas que la plantilla ([Content_Types].xml primero)
            out.write(pathlib.Path(tmp, info.filename), info.filename)
    shutil.copy(tmpzip, SALIDA)
print(f"{SALIDA.name}: cabecera {list(CABECERA)}, {sum(len(p) for p in R.values())} párrafos en {len(R)} preguntas")

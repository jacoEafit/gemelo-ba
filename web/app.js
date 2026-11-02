'use strict';
const TEMAS = [
  ['demografia', 'Población'], ['seguridad', 'Seguridad'], ['movilidad', 'Movilidad'], ['subte_molinetes', 'Subte'],
  ['sensores', 'Sensores'], ['edificios', 'Edificios'], ['espacios_verdes', 'Espacios verdes'], ['salud', 'Salud'],
  ['educacion', 'Educación'], ['cultura', 'Cultura'], ['residuos', 'Residuos'], ['calidad_aire', 'Calidad del aire'],
  ['clima', 'Clima'], ['economia', 'Economía'], ['turismo', 'Turismo'], ['municipio', 'Presupuesto'],
  ['escucha', 'Escucha ciudadana'], ['geoinfraestructura', 'Infraestructura'], ['atlas_distritos', 'Territorio']
];
const MAPA = 'mapa', FUENTES = 'fuentes';
const PALETA = ['#1b2a6b', '#3b4cc0', '#7b3fa0', '#d1495b', '#f7a440', '#fdf2b3'];
const LINEA = { A: '#18c5e8', B: '#e8312f', C: '#1f5fbf', D: '#1faa59', E: '#8e44ad', H: '#e6b800', PM: '#888' };
const GBFS = 'https://buenosaires.publicbikesystem.net/ube/gbfs/v1/en/';
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const fmt = v => typeof v === 'number' ? v.toLocaleString('es-AR', { maximumFractionDigits: Math.abs(v) < 10 ? 2 : 0 }) : esc(v);
const humano = k => k.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase().replace(/\s+/g, ' ').trim()
  .replace(/^COMUNA /, '').replace(/^BOCA$/, 'LA BOCA');

const cache = {}, geo = {};
const getJson = async url => cache[url] ??= await (await fetch(url)).json();

function color(t) {
  const x = Math.min(Math.max(t, 0), 1) * (PALETA.length - 1), i = Math.min(Math.floor(x), PALETA.length - 2), f = x - i;
  const a = PALETA[i], b = PALETA[i + 1], p = (s, o) => parseInt(s.slice(o, o + 2), 16);
  return '#' + [1, 3, 5].map(o => Math.round(p(a, o) + (p(b, o) - p(a, o)) * f).toString(16).padStart(2, '0')).join('');
}

/* ── Métricas territoriales: desgloses cuyas filas cruzan con barrios o comunas ── */
function metricas(d) {
  const out = [];
  for (const [k, v] of Object.entries(d.desgloses || {})) {
    const filas = (v.filas || []).filter(r => typeof r[1] === 'number');
    if (!filas.length) continue;
    for (const nivel of ['barrio', 'comuna']) {
      const claves = new Set(geo[nivel].features.map(f => norm(f.properties[nivel === 'barrio' ? 'nombre' : 'comuna'])));
      const ok = filas.filter(r => claves.has(norm(r[0]))).length;
      if (ok >= Math.min(8, filas.length * 0.6)) { out.push({ k, nivel, desglose: v, filas }); break; }
    }
  }
  return out;
}

/* ── Vista de un tema ── */
let tema, datos, mets, metActual;

/* El id de fuente de una cifra o desglose lleva a la página del conjunto en internet. */
function enlaceFuente(id, fuentes = datos && datos.fuentes) {
  const f = (fuentes || []).find(x => x.id === id);
  return f && f.url ? `<a href="${esc(f.url)}" target="_blank" rel="noopener" title="${esc(f.nombre || id)}">${esc(id)} ↗</a>` : esc(id || '');
}

function barras(titulo, v, filas, met) {
  const top = [...filas].sort((a, b) => b[1] - a[1]).slice(0, 8), max = Math.max(...top.map(r => r[1])) || 1;
  const boton = met ? `<button class="ver" data-met="${esc(met.k)}">${metActual === met ? 'En el mapa' : 'Ver en el mapa'}</button>` : '';
  return `<div class="card bloque"><h2>${esc(titulo)} ${boton}</h2>` +
    top.map(r => `<div class="fila" data-k="${esc(norm(r[0]))}"><span class="n" title="${esc(r[0])}">${esc(r[0])}</span><span class="b"><i style="width:${Math.max(r[1] / max * 100, 1)}%"></i></span><span class="x">${fmt(r[1])}</span></div>`).join('') +
    `<div class="fuentes pie">${esc(v.unidad || '')} · ${enlaceFuente(v.fuente)} · vigencia ${esc(v.vigencia || '—')}</div></div>`;
}

function linea(nombre, s) {
  const p = (s.puntos || []).filter(q => typeof q[1] === 'number');
  if (p.length < 2) return '';
  const ys = p.map(q => q[1]), mn = Math.min(...ys), mx = Math.max(...ys), W = 220, H = 60, sx = i => 4 + i / (p.length - 1) * (W - 8), sy = y => H - 4 - (y - mn) / ((mx - mn) || 1) * (H - 10);
  const pts = p.map((q, i) => `${sx(i).toFixed(1)},${sy(q[1]).toFixed(1)}`).join(' ');
  return `<div class="card serie"><div class="t">${esc(humano(nombre))}</div><svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><polygon points="4,${H} ${pts} ${W - 4},${H}" fill="#9db4bd1f"/><polyline points="${pts}" fill="none" stroke="#9db4bd" stroke-width="1.6" vector-effect="non-scaling-stroke"/></svg>` +
    `<div class="r"><span>${esc(p[0][0])}: ${fmt(p[0][1])}</span><span>${esc(p.at(-1)[0])}: ${fmt(p.at(-1)[1])}</span></div><div class="r">${esc(s.unidad || '')}</div></div>`;
}

function render() {
  const nombre = TEMAS.find(t => t[0] === tema)[1], d = datos;
  const cifras = Object.entries(d.cifras || {}).map(([k, c]) =>
    `<div class="card kpi"><div class="v">${fmt(c.valor)}</div><div class="u">${esc(c.unidad || humano(k))}</div><div class="f fuentes">${enlaceFuente(c.fuente)} · vigencia ${esc(c.vigencia || '—')} · probado ${esc(d.probado || '—')}</div></div>`).join('');
  const bloques = Object.entries(d.desgloses || {}).filter(([, v]) => (v.filas || []).some(r => typeof r[1] === 'number')).slice(0, 8)
    .map(([k, v]) => barras(humano(k), v, v.filas.filter(r => typeof r[1] === 'number'), mets.find(m => m.k === k))).join('');
  const series = Object.entries(d.series || {}).slice(0, 8).map(([k, s]) => linea(k, s)).join('');
  const fuentes = (d.fuentes || []).map(f => `<li><a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.nombre)}</a> · ${esc(f.estado)} · ${esc(f.licencia)}</li>`).join('');
  $('vista').innerHTML = `<h1>${esc(nombre)}</h1><p class="nota">${esc(d.nota || '')}</p>` +
    (cifras ? `<div class="kpis">${cifras}</div>` : '') +
    (bloques ? `<div class="rejilla">${bloques}</div>` : '') +
    (series ? `<div class="rejilla series">${series}</div>` : '') +
    `<details class="card bloque fuentes-det"><summary>Fuentes (${(d.fuentes || []).length}) · probado ${esc(d.probado || '—')}</summary><ul class="fuentes">${fuentes}</ul></details>`;
  for (const b of document.querySelectorAll('.ver')) b.onclick = () => { elegir(mets.find(m => m.k === b.dataset.met)); render(); };
  for (const f of document.querySelectorAll('.fila')) {
    f.onmouseenter = () => map.getLayer('zonas-hl') && map.setFilter('zonas-hl', ['==', ['get', 'k'], f.dataset.k]);
    f.onmouseleave = () => map.getLayer('zonas-hl') && map.setFilter('zonas-hl', ['==', ['get', 'k'], '']);
  }
}

/* ── Mapa ── */
const proto = new pmtiles.Protocol(); maplibregl.addProtocol('pmtiles', proto.tile);
const map = new maplibregl.Map({
  container: 'map', center: [-58.435, -34.615], zoom: 10.7, pitch: 50, bearing: -15, maxPitch: 75,
  style: { version: 8, sources: { base: { type: 'raster', tileSize: 256, maxzoom: 19, attribution: '© OpenStreetMap',
    tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'] } },
    layers: [{ id: 'fondo', type: 'background', paint: { 'background-color': '#0b0f17' } },
      { id: 'base', type: 'raster', source: 'base', paint: { 'raster-saturation': -1, 'raster-brightness-max': 0.42, 'raster-contrast': 0.1 } }] }
});
map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
map.addControl(new maplibregl.FullscreenControl({ container: document.getElementById('mapa-card') }), 'top-right');
map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
const listo = new Promise(r => map.on('load', r));
new ResizeObserver(() => map.resize()).observe(document.getElementById('map'));
const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
const vacio = { type: 'FeatureCollection', features: [] };

async function prepararMapa() {
  await listo;
  map.setLight({ anchor: 'viewport', color: '#fff', intensity: 0.35, position: [1.4, 210, 55] });
  map.addSource('zonas', { type: 'geojson', data: vacio });
  map.addLayer({ id: 'zonas', type: 'fill-extrusion', source: 'zonas', paint: { 'fill-extrusion-color': ['get', 'c'], 'fill-extrusion-height': ['get', 'h'], 'fill-extrusion-opacity': 0.9 } });
  map.addLayer({ id: 'zonas-line', type: 'line', source: 'zonas', paint: { 'line-color': '#9fb3d9', 'line-opacity': 0.4, 'line-width': 0.8 } });
  map.addLayer({ id: 'zonas-hl', type: 'line', source: 'zonas', filter: ['==', ['get', 'k'], ''], paint: { 'line-color': '#fff', 'line-width': 3 } });
  map.addSource('subte', { type: 'geojson', data: 'datos/geo/subte_lineas.geojson' });
  const lc = ['match', ['slice', ['get', 'nombre'], 6], ...Object.entries(LINEA).flat(), '#fff'];
  map.addLayer({ id: 'subte', type: 'line', source: 'subte', layout: { visibility: 'none', 'line-cap': 'round' }, paint: { 'line-color': lc, 'line-width': 3 } });
  map.addSource('pasajeros', { type: 'geojson', data: 'datos/geo/subte_pasajeros.geojson' });
  map.addLayer({ id: 'pasajeros', type: 'circle', source: 'pasajeros', layout: { visibility: 'none' }, paint: {
    'circle-radius': ['interpolate', ['linear'], ['get', 'pasajeros_2025'], 0, 3, 3e6, 8, 16e6, 22],
    'circle-color': ['match', ['get', 'linea'], ...Object.entries(LINEA).flat(), '#fff'], 'circle-opacity': 0.8, 'circle-stroke-color': '#fff', 'circle-stroke-width': 1 } });
  map.addSource('bici', { type: 'geojson', data: vacio });
  map.addLayer({ id: 'bici', type: 'circle', source: 'bici', layout: { visibility: 'none' }, paint: {
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 10, 2.5, 15, 9],
    'circle-color': ['interpolate', ['linear'], ['get', 'r'], 0, '#ef4444', 0.35, '#fbbf24', 0.75, '#34d399'],
    'circle-stroke-color': '#0b0f17', 'circle-stroke-width': 1 } });

  map.on('mousemove', 'zonas', e => {
    const p = e.features[0].properties; map.getCanvas().style.cursor = 'pointer';
    popup.setLngLat(e.lngLat).setHTML(`<b>${esc(p.nombre)}</b><br>${p.v === undefined || p.v === 'null' ? 'sin dato' : fmt(+p.v) + ' ' + esc(p.u || '')}`).addTo(map);
    map.setFilter('zonas-hl', ['==', ['get', 'k'], p.k]);
  });
  map.on('mouseleave', 'zonas', () => { map.getCanvas().style.cursor = ''; popup.remove(); map.setFilter('zonas-hl', ['==', ['get', 'k'], '']); });
  map.on('click', 'bici', e => { const p = e.features[0].properties;
    new maplibregl.Popup({ closeButton: false }).setLngLat(e.lngLat).setHTML(`<b>${esc(p.name)}</b><br>${p.bikes} bicis · ${p.docks} lugares libres (capacidad ${p.cap})`).addTo(map); });
  map.on('click', 'pasajeros', e => { const p = e.features[0].properties;
    new maplibregl.Popup({ closeButton: false }).setLngLat(e.lngLat).setHTML(`<b>${esc(p.estacion)}</b> · línea ${esc(p.linea)}<br>${fmt(+p.pasajeros_2025)} pasajeros en 2025`).addTo(map); });
}

function elegir(m) {
  metActual = m;
  if (!m) { map.getSource('zonas').setData(vacio); $('leyenda').innerHTML = ''; return; }
  const vals = m.filas.map(r => r[1]), mn = Math.min(...vals), mx = Math.max(...vals);
  const porClave = new Map(m.filas.map(r => [norm(r[0]), r[1]]));
  const fs = geo[m.nivel].features.map(f => {
    const nombre = m.nivel === 'barrio' ? f.properties.nombre : 'Comuna ' + f.properties.comuna, k = norm(nombre), v = porClave.get(k);
    const t = v === undefined ? null : (v - mn) / ((mx - mn) || 1);
    return { type: 'Feature', geometry: f.geometry, properties: { k, nombre, u: m.desglose.unidad || '',
      ...(v === undefined ? {} : { v }), c: t === null ? '#2a3347' : color(t), h: t === null ? 15 : 60 + Math.pow(t, 0.85) * 1700 } };
  });
  map.getSource('zonas').setData({ type: 'FeatureCollection', features: fs });
  $('leyenda').innerHTML = `<div class="bar" style="background:linear-gradient(90deg,${PALETA.join(',')})"></div><div class="esc"><span>${fmt(mn)}</span><span>${esc(m.desglose.unidad || '')}</span><span>${fmt(mx)}</span></div>` +
    `<div class="esc"><span class="fuentes">${enlaceFuente(m.desglose.fuente)} · vigencia ${esc(m.desglose.vigencia || '—')}</span></div>`;
}

/* ── Capas en vivo ── */
let timerBici = null;
async function cargarBici() {
  try {
    const [inf, est] = await Promise.all([fetch(GBFS + 'station_information').then(r => r.json()), fetch(GBFS + 'station_status').then(r => r.json())]);
    const st = new Map(est.data.stations.map(s => [s.station_id, s]));
    let bicis = 0;
    const fs = inf.data.stations.filter(s => st.get(s.station_id)?.is_renting !== undefined).map(s => {
      const e = st.get(s.station_id), b = e.num_bikes_available, cap = s.capacity || (b + e.num_docks_available) || 1; bicis += b;
      return { type: 'Feature', geometry: { type: 'Point', coordinates: [s.lon, s.lat] }, properties: { name: s.name, bikes: b, docks: e.num_docks_available, cap, r: Math.min(b / cap, 1) } };
    });
    map.getSource('bici').setData({ type: 'FeatureCollection', features: fs });
    $('vivo-pie').innerHTML = `EcoBici en vivo · ${fs.length} estaciones · ${fmt(bicis)} bicis disponibles · ${new Date(est.last_updated * 1000).toLocaleTimeString('es-AR')} · rojo = vacía, verde = llena`;
  } catch (e) { $('vivo-pie').textContent = 'EcoBici: no se pudo leer el feed en vivo (' + e.message + ')'; }
}
function bici(on) {
  clearInterval(timerBici);
  map.setLayoutProperty('bici', 'visibility', on ? 'visible' : 'none');
  if (on) { cargarBici(); timerBici = setInterval(cargarBici, 60000); } else $('vivo-pie').textContent = '';
}
async function clima() {
  try {
    const c = (await (await fetch('https://api.open-meteo.com/v1/forecast?latitude=-34.6&longitude=-58.4&current=temperature_2m,wind_speed_10m,precipitation')).json()).current;
    $('clima').textContent = `Ahora en BA · ${c.temperature_2m} °C · viento ${c.wind_speed_10m} km/h · lluvia ${c.precipitation} mm`;
  } catch { $('clima').textContent = 'Clima en vivo no disponible'; }
}

let pmt = false;
async function edificios(on) {
  await listo;
  if (on && !pmt) {
    map.addSource('edif', { type: 'vector', url: 'pmtiles://edificios.pmtiles' });
    map.addLayer({ id: 'edif', type: 'fill-extrusion', source: 'edif', 'source-layer': 'edificios', minzoom: 10, paint: {
      'fill-extrusion-height': ['coalesce', ['get', 'altura'], 3],
      'fill-extrusion-color': ['interpolate', ['linear'], ['coalesce', ['get', 'altura'], 0], 0, '#1b2a6b', 8, '#3b4cc0', 20, '#7b3fa0', 40, '#d1495b', 70, '#f7a440', 110, '#fdf2b3'],
      'fill-extrusion-opacity': 0.93 } });
    pmt = true;
  }
  if (pmt) map.setLayoutProperty('edif', 'visibility', on ? 'visible' : 'none');
  if (on) map.easeTo({ zoom: Math.max(map.getZoom(), 12.6), center: map.getCenter(), duration: 700 });
  /* Con edificios 3D, las columnas de barrios se aplanan contra el suelo para no taparlos. */
  map.setPaintProperty('zonas', 'fill-extrusion-height', on ? 2 : ['get', 'h']);
  map.setPaintProperty('zonas', 'fill-extrusion-opacity', on ? 0.4 : 0.9);
}

/* ── Navegación ── */
function subte(on) {
  for (const l of ['subte', 'pasajeros']) map.setLayoutProperty(l, 'visibility', on ? 'visible' : 'none');
}

/* ── Sección «Fuentes»: todas las del lago y lo que no se incluyó ── */
const EXCLUIDAS = [  // [nombre, estado, por qué, enlace]; salen de la hoja «1. Fuentes» (F31–F40) del Excel de la Entrega 1
  ['Reclamos ciudadanos (SUACI / BA Colaborativa)', 'descartada', 'Un CSV por año de 100 a 277 MB (~2 GB en total): se descartó por peso. No se abrió el contenido, así que no se sabe si trae datos de personas.', 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/atencion-ciudadana/sistema-unico-atencion-ciudadana/sistema-unico-de-atencion-ciudadana-2025.csv'],
  ['SUACI: solicitudes por barrio (agregado)', 'candidata', 'Pesa 2,7 MB y ya viene agregada por barrio: resolvería el hueco de reclamos. Falta abrirla y ver su periodo, y si trae texto libre o personas.', 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/sistema-unico-de-atencion-ciudadana/gcba_suaci_barrios.csv'],
  ['API de Transporte: subte, colectivos, EcoBici y tránsito en tiempo real', 'no responde', 'El portal avisa que todos los conjuntos con formato API y GTFS están suspendidos, «en revisión y corrección» (2026-10-06). Por eso «Tráfico» está deshabilitado y los sensores son solo inventario.', 'https://api-transporte.buenosaires.gob.ar/'],
  ['Colectivos: GTFS', 'no responde', 'Alcanzada por el mismo aviso de suspensión de los conjuntos GTFS. No se intentó la descarga.', 'https://data.buenosaires.gob.ar/km/dataset/colectivos-gtfs'],
  ['Información censal por radio', 'descartada', 'Solo trae radios de 2001 y 2010: no da población 2022 por barrio, que era para lo que se buscaba. Se usa el Censo 2022 por comuna, como cifra declarada.', 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/direccion-general-de-estadisticas-y-censos/informacion-censal-por-radio/informacion-censal-por-radio-2010.csv'],
  ['Padrón de establecimientos educativos', 'descartada', 'Trae correos, algunos personales (Gmail, Hotmail). Se usó «Establecimientos educativos», que no los trae.', 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ministerio-de-educacion/establecimientos-educativos/padron-establecimientos.csv'],
  ['Edificios públicos en 3D (escaneo LIDAR)', 'descartada', 'Solo 9 edificios (Cabildo, Colón, Congreso…), de 51 a 599 MB cada uno: sirve de muestra, no para la ciudad.', 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/secretaria-de-desarrollo-urbano/edificios-publicos-3d/cabildo.zip'],
  ['Área edificable: volumen', 'descartada', 'Es el volumen que permite la norma, no lo construido (38 MB). Para alturas reales se usó Tejido Urbano.', 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/secretaria-de-desarrollo-urbano/area-edificable-volumen/volumen_edif.csv'],
  ['IPC nivel general, Gran Buenos Aires (INDEC)', 'descartada', 'Mide el aglomerado GBA y no la Ciudad: se prefirió el IPCBA. Aparece en la API de series con datos hasta 2026-08 (no se bajó la serie).', 'https://apis.datos.gob.ar/series/api/series/?ids=145.3_INGGBAGBA_DICI_M_10'],
  ['Tasa de desempleo en hogares urbanos, CABA', 'descartada', 'La búsqueda de la API la muestra cortada en 2023-04: vieja para el sistema. Se usó el empleo registrado (SIPA). Licencia no revisada.', 'https://apis.datos.gob.ar/series/api/series/?ids=obras_13_08_02']
];
const ESTADO_FUENTE = { vivo: 'vivo', declarado: 'declarado' };

async function abrirFuentes() {
  document.body.classList.remove('modo-mapa'); setTimeout(() => map.resize(), 50);
  tema = FUENTES; datos = null;
  for (const b of document.querySelectorAll('nav button')) b.classList.toggle('on', b.dataset.id === FUENTES);
  $('vista').innerHTML = '<div class="vacio">Cargando…</div>';
  const nombres = [...TEMAS.map(t => t[0]), 'correlaciones', 'atlas_zonas', 'catalogo'];
  const todos = await Promise.all(nombres.map(n => getJson(`datos/${n}.json`).then(d => [n, d], () => null)));
  const uni = new Map();
  for (const par of todos.filter(Boolean)) for (const f of par[1].fuentes || []) {
    const e = uni.get(f.id) || { ...f, temas: [] };
    if (!e.temas.includes(par[0])) e.temas.push(par[0]);
    uni.set(f.id, e);
  }
  const lista = [...uni.values()].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
  const prueba = todos.filter(Boolean).map(p => p[1].probado).filter(Boolean).sort().at(-1) || '—';
  const nombreTema = id => (TEMAS.find(t => t[0] === id) || [id, humano(id)])[1];
  const tarjeta = f => `<div class="card fcard"><div class="ft"><b>${esc(f.nombre)}</b><span class="est ${esc(f.estado)}">${esc(ESTADO_FUENTE[f.estado] || f.estado)}</span></div>` +
    `<div class="fm">${esc(f.licencia || 'sin licencia declarada')}</div>` +
    `<div class="fm">${f.temas.map(t => TEMAS.some(x => x[0] === t) ? `<a href="#/${esc(t)}">${esc(nombreTema(t))}</a>` : esc(humano(t))).join(' · ')}</div>` +
    `<a class="fl" href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.url.replace(/^https?:\/\//, '').slice(0, 58))} ↗</a></div>`;
  const vivas = lista.filter(f => f.estado === 'vivo').length;
  $('vista').innerHTML = `<h1>Fuentes</h1><p class="nota">Todas las fuentes que alimentan el lago, cada una con su enlace a la página original, su licencia y los temas donde se usa. Abajo, lo que no se incluyó y por qué. Última fecha de prueba: ${esc(prueba)}.</p>` +
    `<div class="kpis"><div class="card kpi"><div class="v">${lista.length}</div><div class="u">fuentes en el lago</div></div>` +
    `<div class="card kpi"><div class="v">${vivas}</div><div class="u">vivas (responden)</div></div>` +
    `<div class="card kpi"><div class="v">${lista.length - vivas}</div><div class="u">declaradas</div></div>` +
    `<div class="card kpi"><div class="v">${EXCLUIDAS.length}</div><div class="u">no incluidas</div></div></div>` +
    `<h2 class="sec">En el lago</h2><div class="rejilla fuentes-grid">${lista.map(tarjeta).join('')}</div>` +
    `<h2 class="sec">Fuera del lago, en vivo</h2><div class="rejilla fuentes-grid">` +
      `<div class="card fcard"><div class="ft"><b>EcoBici (GBFS)</b><span class="est vivo">en vivo</span></div><div class="fm">Lectura directa desde el navegador, sin guardar en el lago.</div><a class="fl" href="https://buenosaires.publicbikesystem.net/ube/gbfs/v1/en/station_status" target="_blank" rel="noopener">buenosaires.publicbikesystem.net/ube/gbfs ↗</a></div>` +
      `<div class="card fcard"><div class="ft"><b>Tejido Urbano (edificios 3D)</b><span class="est vivo">teselas</span></div><div class="fm">Se baja con <code>make tiles</code> y se sirve como PMTiles; el lago solo guarda las alturas por barrio.</div><a class="fl" href="https://data.buenosaires.gob.ar/km/dataset/tejido-urbano" target="_blank" rel="noopener">data.buenosaires.gob.ar/km/dataset/tejido-urbano ↗</a></div></div>` +
    `<h2 class="sec">Lo que no se incluye</h2><div class="rejilla fuentes-grid">${EXCLUIDAS.map(e => `<div class="card fcard"><div class="ft"><b>${esc(e[0])}</b><span class="est fuera">${esc(e[1])}</span></div><div class="fm">${esc(e[2])}</div><a class="fl" href="${esc(e[3])}" target="_blank" rel="noopener">${esc(e[3].replace(/^https?:\/\//, '').slice(0, 58))} ↗</a></div>`).join('')}` +
      `<div class="card fcard"><div class="ft"><b>Resto del catálogo del portal</b><span class="est fuera">sin conectar</span></div><div class="fm">El portal lista 455 conjuntos y solo 23 están conectados al lago; los otros no se usan.</div></div></div>`;
  await listo;
  metActual = null; elegir(null); $('leyenda').innerHTML = '';
  $('c-bici').checked = false; bici(false); $('c-subte').checked = false; subte(false);
}

/* Categoría «Mapa»: el mapa ocupa la pantalla y solo sirve para moverse (sin tema ni métrica). */
let mapaVisto = false;
async function abrirMapa() {
  document.body.classList.add('modo-mapa');
  for (const b of document.querySelectorAll('nav button')) b.classList.toggle('on', b.dataset.id === MAPA);
  await listo;
  metActual = null; elegir(null);
  $('leyenda').innerHTML = ''; $('vivo-pie').textContent = '';
  $('c-bici').checked = false; bici(false);
  $('c-subte').checked = false; subte(false);
  if (!mapaVisto) { mapaVisto = true; $('c-edif').checked = true; edificios(true); }
  setTimeout(() => map.resize(), 50);
}

async function abrir(id) {
  document.body.classList.toggle('modo-fuentes', id === FUENTES);
  if (id === MAPA) return abrirMapa();
  if (id === FUENTES) return abrirFuentes();
  if (document.body.classList.contains('modo-mapa')) { document.body.classList.remove('modo-mapa'); setTimeout(() => map.resize(), 50); }
  tema = TEMAS.some(t => t[0] === id) ? id : TEMAS[0][0];
  for (const b of document.querySelectorAll('nav button')) b.classList.toggle('on', b.dataset.id === tema);
  $('vista').innerHTML = '<div class="vacio">Cargando…</div>';
  datos = await getJson(`datos/${tema}.json`);
  mets = metricas(datos);
  metActual = mets[0] || null;
  render();
  await listo;
  elegir(metActual);
  const esSubte = tema === 'subte_molinetes';
  $('c-subte').checked = esSubte; subte(esSubte);
  $('c-bici').checked = tema === 'movilidad'; bici($('c-bici').checked);
  render();
}

(async function () {
  $('temas').innerHTML = [[MAPA, 'Mapa'], [FUENTES, 'Fuentes'], ...TEMAS].map(([id, n]) => `<button data-id="${id}"${id === MAPA ? ' class="mapa-tab"' : ''}>${n}</button>`).join('');
  for (const b of document.querySelectorAll('nav button')) b.onclick = () => { location.hash = '#/' + b.dataset.id; };
  $('c-bici').onchange = e => bici(e.target.checked);
  $('c-subte').onchange = e => subte(e.target.checked);
  $('c-edif').onchange = e => edificios(e.target.checked);
  [geo.barrio, geo.comuna] = await Promise.all(['barrios', 'comunas'].map(n => getJson(`datos/geo/${n}.geojson`)));
  clima(); setInterval(clima, 600000);
  prepararMapa();
  window.onhashchange = () => abrir(location.hash.replace('#/', ''));
  abrir(location.hash.replace('#/', ''));
})();

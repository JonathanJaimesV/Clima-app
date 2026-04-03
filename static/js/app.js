/**
 * app.js — Atmosfera
 * Maneja el menú interactivo, búsqueda con API + IA y renderizado.
 * Handles interactive menu, API + AI search and rendering.
 */

/* ── Referencias DOM / DOM References ────────── */
const menuSection      = document.getElementById('menu-section');
const resultadoSection = document.getElementById('resultado-section');
const busquedaSection  = document.getElementById('busqueda-section');
const reporteSection   = document.getElementById('reporte-section');
const salidaSection    = document.getElementById('salida-section');
const resultadoTitulo  = document.getElementById('resultado-titulo');
const resultadoGrid    = document.getElementById('resultado-grid');
const errorMsg         = document.getElementById('error-msg');
const consoleField     = document.getElementById('console-field');
const recsSection      = document.getElementById('recs-section');
const recsGrid         = document.getElementById('recs-grid');
const topbarLoader     = document.getElementById('topbar-loader');

const SECTIONS = [resultadoSection, busquedaSection, reporteSection, salidaSection];
const REC_ICONS = ['👔', '☂️', '🏃', '🚗', '💧', '✨'];

/* ── Partículas de fondo / Background particles ─ */
(function () {
  const canvas = document.getElementById('bg-canvas');
  const ctx = canvas.getContext('2d');
  let W, H, pts;
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  function mk(n = 60) {
    return Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.2 + 0.2,
      vx: (Math.random() - 0.5) * 0.12, vy: (Math.random() - 0.5) * 0.12,
      a: Math.random() * 0.25 + 0.05,
    }));
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200,168,122,${p.a})`; ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  resize(); pts = mk(); draw();
  window.addEventListener('resize', () => { resize(); pts = mk(); });
})();

/* ── Navegación / Navigation ─────────────────── */
function ocultarTodo() {
  SECTIONS.forEach(s => s.classList.add('hidden'));
  menuSection.classList.add('hidden');
}
function mostrarSeccion(sec) { ocultarTodo(); sec.classList.remove('hidden'); }
window.volver = function () { ocultarTodo(); menuSection.classList.remove('hidden'); hideError(); };
window.mostrarSalida   = function () { mostrarSeccion(salidaSection); };
window.mostrarBusqueda = function () { mostrarSeccion(busquedaSection); };

/* ── Búsqueda principal con API + IA ─────────── */
window.buscarCiudad = async function (ciudad) {
  if (!ciudad.trim()) return;
  topbarLoader.classList.remove('hidden');

  try {
    const res  = await fetch(`/api/buscar?ciudad=${encodeURIComponent(ciudad)}`);
    const data = await res.json();

    if (data.error) {
      alert(data.error); topbarLoader.classList.add('hidden'); return;
    }

    // Actualizar sidebar con datos nuevos / Update sidebar with new data
    const w = data.weather;
    document.getElementById('s-ciudad').textContent  = w.ciudad;
    document.getElementById('s-pais').textContent    = w.pais;
    document.getElementById('s-temp').textContent    = w.temp;
    document.getElementById('s-desc').textContent    = w.descripcion;
    document.getElementById('s-sens').textContent    = w.sensacion + '°';
    document.getElementById('s-hum').textContent     = w.humedad + '%';
    document.getElementById('s-viento').textContent  = w.viento;

    // Actualizar KPIs del topbar / Update topbar KPIs
    const tf  = Math.round(w.temp * 9/5 + 32);
    const idx = Math.round((w.temp + w.humedad * 0.1) * 10) / 10;
    const dif = Math.round((w.sensacion - w.temp) * 10) / 10;
    document.getElementById('t-f').textContent   = tf + '°F';
    document.getElementById('t-idx').textContent = idx;
    document.getElementById('t-dif').textContent = '+' + dif + '°';
    document.getElementById('t-vis').textContent = w.visibilidad + ' km';
    document.getElementById('t-nub').textContent = w.nubosidad + '%';

    // Mostrar recomendaciones de IA / Show AI recommendations
    if (data.recomendaciones && data.recomendaciones.length) {
      recsGrid.innerHTML = '';
      data.recomendaciones.forEach((rec, i) => {
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.innerHTML = `<span class="rec-card__icon">${REC_ICONS[i] ?? '💡'}</span><span>${escapeHtml(rec)}</span>`;
        recsGrid.appendChild(card);
      });
      // Actualizar rec en sidebar / Update rec in sidebar
      document.getElementById('s-rec').textContent = data.recomendaciones[0] ?? '';
      recsSection.classList.remove('hidden');
    }

  } catch (e) {
    console.error(e);
  } finally {
    topbarLoader.classList.add('hidden');
  }
};

/* ── Input sidebar / Sidebar input ───────────── */
document.getElementById('sidebar-btn').addEventListener('click', () => {
  const v = document.getElementById('sidebar-input').value.trim();
  if (v) buscarCiudad(v);
});
document.getElementById('sidebar-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const v = e.target.value.trim();
    if (v) buscarCiudad(v);
  }
});

/* ── Menú opciones / Menu options ────────────── */
window.ejecutar = async function (opcion) {
  hideError();
  if (opcion === 8) { mostrarSalida(); return; }
  if (opcion < 1 || opcion > 7) { showError(); return; }
  try {
    const res  = await fetch(`/opcion/${opcion}`);
    const data = await res.json();
    mostrarResultado(data.titulo, data.datos);
  } catch { showError(); }
};

window.ejecutarConsola = function () {
  const val = parseInt(consoleField.value);
  if (isNaN(val) || val < 1 || val > 8) { showError(); return; }
  if (val === 6) { mostrarBusqueda(); consoleField.value = ''; return; }
  if (val === 7) { ejecutarReporte(); consoleField.value = ''; return; }
  ejecutar(val); consoleField.value = '';
};
consoleField.addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarConsola(); });

/* ── Renderizar resultado / Render result ────── */
function mostrarResultado(titulo, datos) {
  resultadoTitulo.textContent = titulo;
  resultadoGrid.innerHTML = '';
  datos.forEach(item => {
    const f = document.createElement('div');
    f.className = 'resultado-fila';
    f.innerHTML = `<span class="resultado-fila__label">${item.label}</span>
                   <span class="resultado-fila__valor">${item.valor}</span>`;
    resultadoGrid.appendChild(f);
  });
  mostrarSeccion(resultadoSection);
}

/* ── Búsqueda en diccionario / Dictionary search */
window.ejecutarBusqueda = async function () {
  const termino = document.getElementById('search-input').value;
  if (!termino.trim()) return;
  try {
    const res  = await fetch(`/opcion/6?q=${encodeURIComponent(termino)}`);
    const data = await res.json();
    const grid = document.getElementById('search-result');
    grid.innerHTML = '';
    data.datos.forEach(item => {
      const f = document.createElement('div');
      f.className = 'resultado-fila';
      f.innerHTML = `<span class="resultado-fila__label">${item.label}</span>
                     <span class="resultado-fila__valor">${item.valor}</span>`;
      grid.appendChild(f);
    });
  } catch (e) { console.error(e); }
};
document.addEventListener('DOMContentLoaded', () => {
  const si = document.getElementById('search-input');
  if (si) si.addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarBusqueda(); });
});

/* ── Reporte / Report ────────────────────────── */
window.ejecutarReporte = async function () {
  mostrarSeccion(reporteSection);
  try {
    const res  = await fetch('/reporte');
    const data = await res.json();
    document.getElementById('reporte-pre').textContent = data.lineas.join('\n');
  } catch (e) { console.error(e); }
};

/* ── Helpers ─────────────────────────────────── */
function showError() { errorMsg.classList.remove('hidden'); }
function hideError() { errorMsg.classList.add('hidden'); }
function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

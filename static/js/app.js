/**
 * app.js — Atmosfera
 * Menú interactivo con todas las actividades integradas.
 * Interactive menu with all activities integrated.
 */

const menuSection      = document.getElementById('menu-section');
const resultadoSection = document.getElementById('resultado-section');
const busquedaSection  = document.getElementById('busqueda-section');
const reporteSection   = document.getElementById('reporte-section');
const salidaSection    = document.getElementById('salida-section');
const resultadoTitulo  = document.getElementById('resultado-titulo');
const resultadoGrid    = document.getElementById('resultado-grid');
const errorMsg         = document.getElementById('error-msg');
const consoleField     = document.getElementById('console-field');

const SECTIONS = [resultadoSection, busquedaSection, reporteSection, salidaSection];

/* ── Partículas de fondo / Background particles ── */
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

/* ── Navegación / Navigation ── */
function ocultarTodo() {
  SECTIONS.forEach(s => s.classList.add('hidden'));
  menuSection.classList.add('hidden');
}

function mostrarSeccion(sec) {
  ocultarTodo();
  sec.classList.remove('hidden');
}

window.volver = function () {
  ocultarTodo();
  menuSection.classList.remove('hidden');
  hideError();
};

window.mostrarSalida  = function () { mostrarSeccion(salidaSection); };
window.mostrarBusqueda = function () { mostrarSeccion(busquedaSection); };

/* ── Menú principal / Main menu ── */
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
  ejecutar(val);
  consoleField.value = '';
};

consoleField.addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarConsola(); });

/* ── Renderizar resultado / Render result ── */
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

/* ── Búsqueda de ciudad (Actividad 5) / City search ── */
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

/* ── Reporte profesional (Actividad 5) / Professional report ── */
window.ejecutarReporte = async function () {
  mostrarSeccion(reporteSection);
  try {
    const res  = await fetch('/reporte');
    const data = await res.json();
    document.getElementById('reporte-pre').textContent = data.lineas.join('\n');
  } catch (e) { console.error(e); }
};

/* ── Error / validación ── */
function showError() { errorMsg.classList.remove('hidden'); }
function hideError() { errorMsg.classList.add('hidden'); }

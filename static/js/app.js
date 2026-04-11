/**
 * app.js — Atmosfera
 * Menú interactivo, búsqueda con API + IA, drawer móvil y animaciones.
 * Interactive menu, API + AI search, mobile drawer and animations.
 */

/* ── DOM refs ────────────────────────────────── */
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
const sidebar          = document.getElementById('sidebar');
const mobileMenuBtn    = document.getElementById('mobile-menu-btn');
const mobileOverlay    = document.getElementById('mobile-overlay');

const SECTIONS = [resultadoSection, busquedaSection, reporteSection, salidaSection];
const REC_ICONS = ['👔', '☂️', '🏃', '🚗', '💧', '✨'];

/* ══════════════════════════════════════════════
   DRAWER MÓVIL / MOBILE DRAWER
   Abre y cierra el sidebar en pantallas pequeñas.
   Opens and closes sidebar on small screens.
   ══════════════════════════════════════════════ */
function openDrawer() {
  sidebar.classList.add('open');
  mobileOverlay.classList.add('active');
  mobileMenuBtn.classList.add('open');
  document.body.style.overflow = 'hidden';   // Bloquea scroll / Block scroll
}

function closeDrawer() {
  sidebar.classList.remove('open');
  mobileOverlay.classList.remove('active');
  mobileMenuBtn.classList.remove('open');
  document.body.style.overflow = '';
}

mobileMenuBtn.addEventListener('click', () => {
  sidebar.classList.contains('open') ? closeDrawer() : openDrawer();
});

mobileOverlay.addEventListener('click', closeDrawer);

// Cerrar drawer con Escape / Close drawer with Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });

// Cerrar drawer al seleccionar ciudad / Close drawer on city select
function cerrarDrawerSiMovil() {
  if (window.innerWidth <= 768) closeDrawer();
}

/* ══════════════════════════════════════════════
   PARTÍCULAS DE FONDO / BACKGROUND PARTICLES
   ══════════════════════════════════════════════ */
(function () {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, pts, animId;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function mk(n = 55) {
    return Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.3 + 0.2,
      vx: (Math.random() - 0.5) * 0.11,
      vy: (Math.random() - 0.5) * 0.11,
      a: Math.random() * 0.22 + 0.04,
    }));
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200,168,122,${p.a})`;
      ctx.fill();
    });
    animId = requestAnimationFrame(draw);
  }

  resize(); pts = mk(); draw();
  window.addEventListener('resize', () => { resize(); pts = mk(); });

  // Pausa animación cuando la tab no es visible (ahorra batería en móvil)
  // Pause animation when tab not visible (saves battery on mobile)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cancelAnimationFrame(animId);
    else draw();
  });
})();

/* ══════════════════════════════════════════════
   NAVEGACIÓN / NAVIGATION
   ══════════════════════════════════════════════ */
function ocultarTodo() {
  SECTIONS.forEach(s => s.classList.add('hidden'));
  menuSection.classList.add('hidden');
}

function mostrarSeccion(sec) {
  ocultarTodo();
  sec.classList.remove('hidden');
  // Scroll al tope en móvil / Scroll to top on mobile
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.volver = function () {
  ocultarTodo();
  menuSection.classList.remove('hidden');
  hideError();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

window.mostrarSalida   = function () { mostrarSeccion(salidaSection); };
window.mostrarBusqueda = function () { mostrarSeccion(busquedaSection); };

/* ══════════════════════════════════════════════
   BÚSQUEDA PRINCIPAL CON API + IA
   MAIN SEARCH WITH API + AI
   ══════════════════════════════════════════════ */
window.buscarCiudad = async function (ciudad) {
  if (!ciudad || !ciudad.trim()) return;

  topbarLoader.classList.remove('hidden');
  cerrarDrawerSiMovil();

  try {
    const res  = await fetch(`/api/buscar?ciudad=${encodeURIComponent(ciudad.trim())}`);
    const data = await res.json();

    if (data.error) {
      showToast(data.error, 'error');
      topbarLoader.classList.add('hidden');
      return;
    }

    const w = data.weather;

    // Actualizar sidebar con animación / Update sidebar with animation
    animateValue('s-ciudad', w.ciudad);
    animateValue('s-pais',   w.pais);
    animateValue('s-temp',   w.temp);
    animateValue('s-desc',   w.descripcion);
    animateValue('s-sens',   w.sensacion + '°');
    animateValue('s-hum',    w.humedad + '%');
    animateValue('s-viento', w.viento);

    // Actualizar KPIs topbar / Update topbar KPIs
    const tf  = Math.round(w.temp * 9 / 5 + 32);
    const idx = Math.round((w.temp + w.humedad * 0.1) * 10) / 10;
    const dif = Math.round((w.sensacion - w.temp) * 10) / 10;
    animateValue('t-f',   tf + '°F');
    animateValue('t-idx', idx);
    animateValue('t-dif', '+' + dif + '°');
    animateValue('t-vis', w.visibilidad + ' km');
    animateValue('t-nub', w.nubosidad + '%');

    // Mostrar recomendaciones IA / Show AI recommendations
    if (data.recomendaciones && data.recomendaciones.length) {
      recsGrid.innerHTML = '';
      data.recomendaciones.forEach((rec, i) => {
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.style.animationDelay = `${i * 0.06}s`;
        card.innerHTML = `<span class="rec-card__icon">${REC_ICONS[i] ?? '💡'}</span><span>${escapeHtml(rec)}</span>`;
        recsGrid.appendChild(card);
      });
      document.getElementById('s-rec').textContent = data.recomendaciones[0] ?? '';
      recsSection.classList.remove('hidden');
    }

    showToast(`✓ ${w.ciudad} actualizada`, 'success');

  } catch (e) {
    showToast('Error de conexión. Intenta de nuevo.', 'error');
  } finally {
    topbarLoader.classList.add('hidden');
  }
};

/* ── Input sidebar ──────────────────────────── */
document.getElementById('sidebar-btn').addEventListener('click', () => {
  const v = document.getElementById('sidebar-input').value.trim();
  if (v) buscarCiudad(v);
});
document.getElementById('sidebar-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    buscarCiudad(e.target.value.trim());
    e.target.value = '';
  }
});

/* ══════════════════════════════════════════════
   MENÚ OPCIONES / MENU OPTIONS
   ══════════════════════════════════════════════ */
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

/* ══════════════════════════════════════════════
   RENDERIZADO / RENDERING
   ══════════════════════════════════════════════ */
function mostrarResultado(titulo, datos) {
  resultadoTitulo.textContent = titulo;
  resultadoGrid.innerHTML = '';
  datos.forEach((item, i) => {
    const f = document.createElement('div');
    f.className = 'resultado-fila';
    f.style.animationDelay = `${i * 0.04}s`;
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
    data.datos.forEach((item, i) => {
      const f = document.createElement('div');
      f.className = 'resultado-fila';
      f.style.animationDelay = `${i * 0.04}s`;
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

/* ── Reporte / Report */
window.ejecutarReporte = async function () {
  mostrarSeccion(reporteSection);
  try {
    const res  = await fetch('/reporte');
    const data = await res.json();
    document.getElementById('reporte-pre').textContent = data.lineas.join('\n');
  } catch (e) { console.error(e); }
};

/* ══════════════════════════════════════════════
   UTILIDADES / UTILITIES
   ══════════════════════════════════════════════ */

// Animar cambio de valor con fade / Animate value change with fade
function animateValue(id, newValue) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.opacity = '0';
  el.style.transform = 'translateY(4px)';
  setTimeout(() => {
    el.textContent = newValue;
    el.style.transition = 'opacity 0.3s, transform 0.3s';
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
  }, 150);
}

// Toast de notificación / Notification toast
function showToast(msg, type = 'success') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.textContent = msg;
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.add('toast--visible');
    setTimeout(() => {
      toast.classList.remove('toast--visible');
      setTimeout(() => toast.remove(), 400);
    }, 2800);
  });
}

function showError() {
  errorMsg.classList.remove('hidden');
  errorMsg.style.animation = 'none';
  requestAnimationFrame(() => { errorMsg.style.animation = ''; });
}
function hideError() { errorMsg.classList.add('hidden'); }
function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

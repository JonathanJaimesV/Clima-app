/**
 * app.js — Atmosfera
 * Menú interactivo: equivalente al while True: if/elif de consola Python.
 */

const menuSection      = document.querySelector('.menu-section');
const resultadoSection = document.getElementById('resultado-section');
const salidaSection    = document.getElementById('salida-section');
const resultadoTitulo  = document.getElementById('resultado-titulo');
const resultadoGrid    = document.getElementById('resultado-grid');
const errorMsg         = document.getElementById('error-msg');
const consoleField     = document.getElementById('console-field');

/* ── Canvas partículas ── */
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
      a: Math.random() * 0.3 + 0.05,
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

/* ── Menú ── */
window.ejecutar = async function (opcion) {
  hideError();
  if (opcion === 6) { mostrarSalida(); return; }
  if (opcion < 1 || opcion > 5) { showError(); return; }
  try {
    const res  = await fetch(`/opcion/${opcion}`);
    const data = await res.json();
    mostrarResultado(data.titulo, data.datos);
  } catch { showError(); }
};

window.ejecutarConsola = function () {
  const val = parseInt(consoleField.value);
  if (isNaN(val) || val < 1 || val > 6) { showError(); return; }
  ejecutar(val);
  consoleField.value = '';
};

consoleField.addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarConsola(); });

/* ── Renderizado ── */
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
  menuSection.classList.add('hidden');
  salidaSection.classList.add('hidden');
  resultadoSection.classList.remove('hidden');
}

window.mostrarSalida = function () {
  menuSection.classList.add('hidden');
  resultadoSection.classList.add('hidden');
  salidaSection.classList.remove('hidden');
};

window.volver = function () {
  resultadoSection.classList.add('hidden');
  salidaSection.classList.add('hidden');
  menuSection.classList.remove('hidden');
  hideError();
};

function showError() { errorMsg.classList.remove('hidden'); }
function hideError() { errorMsg.classList.add('hidden'); }

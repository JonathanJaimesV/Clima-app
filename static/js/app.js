/* app.js — Atmosfera MVP — Actividades 1, 2 & 3 */

// ── Partículas de fondo ──────────────────────────────────
(function () {
  const canvas = document.getElementById('bg-canvas');
  const ctx    = canvas.getContext('2d');
  let W, H, particles;
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  function createParticles(n = 50) {
    return Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.4 + 0.3,
      vx: (Math.random() - 0.5) * 0.15, vy: (Math.random() - 0.5) * 0.15,
      a: Math.random() * 0.4 + 0.1,
    }));
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(201,169,110,${p.a})`; ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  resize(); particles = createParticles(); draw();
  window.addEventListener('resize', () => { resize(); particles = createParticles(); });
})();

// ── DOM ──────────────────────────────────────────────────
const menuCard         = document.querySelector('.menu-card');
const resultadoSection = document.getElementById('resultado-section');
const salidaSection    = document.getElementById('salida-section');
const resultadoTitulo  = document.getElementById('resultado-titulo');
const resultadoGrid    = document.getElementById('resultado-grid');
const errorMsg         = document.getElementById('error-msg');
const consoleField     = document.getElementById('console-field');

// ── Ejecutar opción — equivalente al if/elif de consola ──
window.ejecutar = async function (opcion) {
  hideError();
  if (opcion === 6) { salir(); return; }
  if (opcion < 1 || opcion > 5) { showError(); return; }
  try {
    const res  = await fetch(`/opcion/${opcion}`);
    const data = await res.json();
    mostrarResultado(data.titulo, data.datos);
  } catch { showError(); }
};

// ── Input consola — equivalente al input() de Python ────
window.ejecutarConsola = function () {
  const val = parseInt(consoleField.value);
  if (isNaN(val) || val < 1 || val > 6) { showError(); return; }
  ejecutar(val);
  consoleField.value = '';
};

consoleField.addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarConsola(); });

// ── Mostrar resultado ────────────────────────────────────
function mostrarResultado(titulo, datos) {
  resultadoTitulo.textContent = titulo;
  resultadoGrid.innerHTML = '';
  datos.forEach(item => {
    const fila = document.createElement('div');
    fila.className = 'resultado-fila';
    fila.innerHTML = `<span class="resultado-fila__label">${item.label}</span><span class="resultado-fila__valor">${item.valor}</span>`;
    resultadoGrid.appendChild(fila);
  });
  menuCard.classList.add('hidden');
  salidaSection.classList.add('hidden');
  resultadoSection.classList.remove('hidden');
  resultadoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

window.salir  = function () { menuCard.classList.add('hidden'); resultadoSection.classList.add('hidden'); salidaSection.classList.remove('hidden'); salidaSection.scrollIntoView({ behavior: 'smooth' }); };
window.volver = function () { resultadoSection.classList.add('hidden'); salidaSection.classList.add('hidden'); menuCard.classList.remove('hidden'); hideError(); consoleField.value = ''; };
function showError() { errorMsg.classList.remove('hidden'); }
function hideError() { errorMsg.classList.add('hidden'); }

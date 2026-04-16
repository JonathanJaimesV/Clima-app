/**
 * app.js — Atmosfera
 * Incluye: intro con globo 3D, historial persistente, menú, búsqueda con API+IA.
 * Includes: 3D globe intro, persistent history, menu, API+AI search.
 */

/* ════════════════════════════════════════════════════
   PLANETA TIERRA 3D — PANTALLA DE INTRO
   3D EARTH — INTRO SCREEN
   Usa Three.js (r128) para renderizar un globo terráqueo
   con atmósfera, nubes procedurales y rotación suave.
   Uses Three.js (r128) to render an Earth globe with
   atmosphere, procedural clouds and smooth rotation.
   ════════════════════════════════════════════════════ */
(function initGlobe() {
  const canvas = document.getElementById('globe-canvas');
  if (!canvas || typeof THREE === 'undefined') {
    finishIntro(); return;
  }

  // Agregar glow atmosférico / Add atmospheric glow
  const glow = document.createElement('div');
  glow.className = 'globe-glow';
  document.getElementById('intro-screen').appendChild(glow);

  // Escena, cámara y renderer / Scene, camera and renderer
  const scene    = new THREE.Scene();
  const camera   = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 2.6;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x000000, 0);

  // ── Iluminación / Lighting ──
  // Luz solar desde la derecha / Sun light from the right
  const sunLight = new THREE.DirectionalLight(0xfff4e0, 1.6);
  sunLight.position.set(3, 1, 2);
  scene.add(sunLight);

  // Luz ambiental azulada (cielo) / Blue ambient light (sky)
  const ambientLight = new THREE.AmbientLight(0x1a3a6a, 0.5);
  scene.add(ambientLight);

  // Luz de relleno fría / Cool fill light
  const fillLight = new THREE.DirectionalLight(0x2255aa, 0.3);
  fillLight.position.set(-2, -1, -1);
  scene.add(fillLight);

  // ── Globo terrestre / Earth globe ──
  // Geometría esférica con suficientes segmentos para suavidad
  // Spherical geometry with enough segments for smoothness
  const earthGeo = new THREE.SphereGeometry(1, 64, 64);

  // Creamos la textura de la Tierra proceduralmente con canvas 2D
  // We create the Earth texture procedurally with 2D canvas
  const earthTex = createEarthTexture();
  const earthMat = new THREE.MeshPhongMaterial({
    map:          earthTex,
    shininess:    25,
    specular:     new THREE.Color(0x224466),
  });

  const earth = new THREE.Mesh(earthGeo, earthMat);
  scene.add(earth);

  // ── Capa de nubes / Cloud layer ──
  const cloudGeo = new THREE.SphereGeometry(1.018, 48, 48);
  const cloudTex = createCloudTexture();
  const cloudMat = new THREE.MeshPhongMaterial({
    map:         cloudTex,
    transparent: true,
    opacity:     0.55,
    depthWrite:  false,
  });
  const clouds = new THREE.Mesh(cloudGeo, cloudMat);
  scene.add(clouds);

  // ── Atmósfera exterior / Outer atmosphere ──
  const atmGeo = new THREE.SphereGeometry(1.06, 32, 32);
  const atmMat = new THREE.MeshPhongMaterial({
    color:       0x3388cc,
    transparent: true,
    opacity:     0.08,
    side:        THREE.FrontSide,
    depthWrite:  false,
  });
  scene.add(new THREE.Mesh(atmGeo, atmMat));

  // ── Estrellas de fondo / Background stars ──
  const starGeo = new THREE.BufferGeometry();
  const starCount = 1800;
  const starPos   = new Float32Array(starCount * 3);
  for (let i = 0; i < starCount * 3; i++) {
    starPos[i] = (Math.random() - 0.5) * 200;
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.12, sizeAttenuation: true });
  scene.add(new THREE.Points(starGeo, starMat));

  // ── Inclinación del eje (23.5°) / Axis tilt (23.5°) ──
  earth.rotation.z  = THREE.MathUtils.degToRad(23.5);
  clouds.rotation.z = THREE.MathUtils.degToRad(23.5);

  // ── Animación / Animation ──
  let animId;
  let startTime = performance.now();
  let phase = 'zoom-in'; // zoom-in → idle → zoom-out

  function animate() {
    animId = requestAnimationFrame(animate);
    const elapsed = (performance.now() - startTime) / 1000;

    // Rotación continua / Continuous rotation
    earth.rotation.y  += 0.0018;
    clouds.rotation.y += 0.0022;

    // Zoom inicial suave / Smooth initial zoom
    if (phase === 'zoom-in') {
      const t = Math.min(elapsed / 1.5, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      camera.position.z = 4.5 - ease * 1.9;   // 4.5 → 2.6
      if (t >= 1) phase = 'idle';
    }

    renderer.render(scene, camera);
  }
  animate();

  // ── Resize handler ──
  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
  window.addEventListener('resize', onResize);

  // ── Finalizar intro tras 2.8s / Finish intro after 2.8s ──
  setTimeout(() => {
    cancelAnimationFrame(animId);
    window.removeEventListener('resize', onResize);
    finishIntro();
  }, 2800);
})();

/* ── Generador de textura terrestre / Earth texture generator ── */
function createEarthTexture() {
  const size = 1024;
  const c = document.createElement('canvas');
  c.width = size; c.height = size / 2;
  const ctx = c.getContext('2d');

  // Océano base / Base ocean
  const ocean = ctx.createLinearGradient(0, 0, 0, c.height);
  ocean.addColorStop(0,    '#0a1a3a');
  ocean.addColorStop(0.3,  '#0d2855');
  ocean.addColorStop(0.5,  '#0e3060');
  ocean.addColorStop(0.7,  '#0d2855');
  ocean.addColorStop(1,    '#0a1a3a');
  ctx.fillStyle = ocean;
  ctx.fillRect(0, 0, size, c.height);

  // Continentes simplificados / Simplified continents
  ctx.fillStyle = '#2d5a27';

  // América del Norte / North America
  drawBlob(ctx, 180, 120, 110, 90, '#3a6b2f');
  drawBlob(ctx, 160, 200, 70, 80, '#2d5a27');

  // América del Sur / South America
  drawBlob(ctx, 220, 280, 70, 100, '#3a6b2f');

  // Europa / Europe
  drawBlob(ctx, 480, 110, 55, 55, '#3a7a2f');

  // África / Africa
  drawBlob(ctx, 490, 200, 75, 110, '#4a8a35');

  // Asia / Asia
  drawBlob(ctx, 620, 100, 170, 110, '#3a6b2f');
  drawBlob(ctx, 700, 180, 80, 60, '#2d5a27');

  // Australia / Australia
  drawBlob(ctx, 730, 290, 65, 50, '#c8a060');

  // Antártida / Antarctica
  ctx.fillStyle = '#ddeeff';
  ctx.fillRect(0, c.height - 38, size, 38);

  // Casquetes polares / Polar ice caps
  ctx.fillStyle = '#ddeeff';
  ctx.fillRect(0, 0, size, 22);

  return new THREE.CanvasTexture(c);
}

function drawBlob(ctx, x, y, rx, ry, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
  ctx.fill();
  // Textura de vegetación / Vegetation texture
  ctx.fillStyle = 'rgba(0,40,0,0.15)';
  for (let i = 0; i < 8; i++) {
    ctx.beginPath();
    ctx.ellipse(
      x + (Math.random() - 0.5) * rx * 1.5,
      y + (Math.random() - 0.5) * ry * 1.5,
      rx * 0.2, ry * 0.15, Math.random() * Math.PI, 0, Math.PI * 2
    );
    ctx.fill();
  }
}

/* ── Generador de textura de nubes / Cloud texture generator ── */
function createCloudTexture() {
  const size = 512;
  const c = document.createElement('canvas');
  c.width = size; c.height = size / 2;
  const ctx = c.getContext('2d');
  ctx.clearRect(0, 0, size, c.height);

  // Nubes procedurales / Procedural clouds
  for (let i = 0; i < 60; i++) {
    const x  = Math.random() * size;
    const y  = Math.random() * c.height;
    const rx = 20 + Math.random() * 60;
    const ry = 8  + Math.random() * 25;
    const a  = 0.25 + Math.random() * 0.45;
    ctx.fillStyle = `rgba(255,255,255,${a})`;
    ctx.beginPath();
    ctx.ellipse(x, y, rx, ry, Math.random() * Math.PI, 0, Math.PI * 2);
    ctx.fill();
  }
  return new THREE.CanvasTexture(c);
}

/* ── Finalizar intro / Finish intro ── */
function finishIntro() {
  const intro  = document.getElementById('intro-screen');
  const appRoot = document.getElementById('app-root');

  intro.classList.add('hiding');
  appRoot.classList.remove('hidden');

  // Inicializar partículas y app luego de mostrar el app-root
  // Initialize particles and app after showing app-root
  setTimeout(() => {
    intro.style.display = 'none';
    initApp();
  }, 820);
}


/* ════════════════════════════════════════════════════
   HISTORIAL DE BÚSQUEDAS — PERSISTENTE
   SEARCH HISTORY — PERSISTENT
   Guarda las últimas 8 búsquedas en localStorage.
   Saves the last 8 searches in localStorage.
   ════════════════════════════════════════════════════ */
const HISTORY_KEY = 'atm_history_v2';

function getHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }
  catch { return []; }
}

function saveToHistory(ciudad, temp, pais) {
  let hist = getHistory();
  // Eliminar duplicado si ya existe / Remove duplicate if exists
  hist = hist.filter(h => h.ciudad.toLowerCase() !== ciudad.toLowerCase());
  // Agregar al inicio / Add to beginning
  hist.unshift({
    ciudad,
    temp,
    pais,
    time: new Date().toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' }),
    date: new Date().toLocaleDateString('es', { day: '2-digit', month: 'short' }),
  });
  // Máximo 8 entradas / Maximum 8 entries
  if (hist.length > 8) hist = hist.slice(0, 8);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(hist));
  renderHistory();
}

function renderHistory() {
  const hist     = getHistory();
  const listEl   = document.getElementById('history-list');
  const panelEl  = document.getElementById('search-history-panel');
  const histWrap = document.getElementById('sidebar-history');

  if (!listEl) return;

  if (!hist.length) {
    histWrap.style.display = 'none';
    if (panelEl) panelEl.innerHTML = '';
    return;
  }

  histWrap.style.display = '';

  // Historial en sidebar — lista vertical / Sidebar history — vertical list
  listEl.innerHTML = hist.map(h => `
    <div class="history-item" onclick="buscarCiudad('${escapeHtml(h.ciudad)}')">
      <span class="history-item__name">${escapeHtml(h.ciudad)}</span>
      <span class="history-item__temp">${h.temp}°C</span>
      <span class="history-item__time">${h.time}</span>
    </div>
  `).join('');

  // Historial en sección búsqueda — chips / Search section history — chips
  if (panelEl) {
    panelEl.innerHTML = `
      <p class="search-history-panel__title">🕐 Búsquedas recientes</p>
      <div class="search-history-chips">
        ${hist.map(h => `
          <button class="history-chip" onclick="buscarCiudad('${escapeHtml(h.ciudad)}')">
            ${escapeHtml(h.ciudad)}
            <span class="history-chip__temp">${h.temp}°</span>
          </button>
        `).join('')}
      </div>
    `;
  }
}


/* ════════════════════════════════════════════════════
   INICIALIZACIÓN DE LA APP / APP INITIALIZATION
   Se llama después de que la intro termina.
   Called after the intro finishes.
   ════════════════════════════════════════════════════ */
function initApp() {
  initParticles();
  initMobileDrawer();
  initSidebarSearch();
  initConsole();
  initSearchSection();
  renderHistory();
}


/* ── Partículas de fondo / Background particles ── */
function initParticles() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, pts, animId;

  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  function mk(n = 55) {
    return Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.2 + 0.2,
      vx: (Math.random() - 0.5) * 0.11, vy: (Math.random() - 0.5) * 0.11,
      a: Math.random() * 0.2 + 0.04,
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
    animId = requestAnimationFrame(draw);
  }
  resize(); pts = mk(); draw();
  window.addEventListener('resize', () => { resize(); pts = mk(); });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cancelAnimationFrame(animId); else draw();
  });
}


/* ── Drawer móvil / Mobile drawer ── */
function initMobileDrawer() {
  const sidebar       = document.getElementById('sidebar');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileOverlay = document.getElementById('mobile-overlay');
  if (!sidebar || !mobileMenuBtn) return;

  function openDrawer() {
    sidebar.classList.add('open');
    mobileOverlay.classList.add('active');
    mobileMenuBtn.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    sidebar.classList.remove('open');
    mobileOverlay.classList.remove('active');
    mobileMenuBtn.classList.remove('open');
    document.body.style.overflow = '';
  }

  mobileMenuBtn.addEventListener('click', () =>
    sidebar.classList.contains('open') ? closeDrawer() : openDrawer()
  );
  mobileOverlay.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });

  window._closeDrawer = closeDrawer;
}


/* ── Buscador del sidebar / Sidebar search ── */
function initSidebarSearch() {
  const btn   = document.getElementById('sidebar-btn');
  const input = document.getElementById('sidebar-input');
  if (!btn || !input) return;

  btn.addEventListener('click', () => {
    const v = input.value.trim();
    if (v) { buscarCiudad(v); input.value = ''; }
  });
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      buscarCiudad(e.target.value.trim());
      e.target.value = '';
    }
  });
}


/* ── Console bar ── */
function initConsole() {
  const field = document.getElementById('console-field');
  if (field) field.addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarConsola(); });
}


/* ── Sección de búsqueda / Search section ── */
function initSearchSection() {
  const si = document.getElementById('search-input');
  if (si) si.addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarBusqueda(); });
}


/* ════════════════════════════════════════════════════
   DOM REFS (necesitan app-root visible / need visible app-root)
   ════════════════════════════════════════════════════ */
function $id(id) { return document.getElementById(id); }

const SECTIONS  = ['resultado-section','busqueda-section','reporte-section','salida-section'];
const REC_ICONS = ['👔','☂️','🏃','🚗','💧','✨'];


/* ════════════════════════════════════════════════════
   NAVEGACIÓN / NAVIGATION
   ════════════════════════════════════════════════════ */
function ocultarTodo() {
  SECTIONS.forEach(id => $id(id)?.classList.add('hidden'));
  $id('menu-section')?.classList.add('hidden');
}
function mostrarSeccion(id) {
  ocultarTodo();
  $id(id)?.classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.volver = function () {
  ocultarTodo();
  $id('menu-section')?.classList.remove('hidden');
  hideError();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};
window.mostrarSalida   = () => mostrarSeccion('salida-section');
window.mostrarBusqueda = () => {
  mostrarSeccion('busqueda-section');
  renderHistory();   // Actualizar chips al abrir / Update chips on open
};


/* ════════════════════════════════════════════════════
   BÚSQUEDA PRINCIPAL CON API + IA
   MAIN SEARCH WITH API + AI
   ════════════════════════════════════════════════════ */
window.buscarCiudad = async function (ciudad) {
  if (!ciudad?.trim()) return;
  const loader = $id('topbar-loader');
  loader?.classList.remove('hidden');
  if (window._closeDrawer) window._closeDrawer();

  try {
    const res  = await fetch(`/api/buscar?ciudad=${encodeURIComponent(ciudad.trim())}`);
    const data = await res.json();

    if (data.error) { showToast(data.error, 'error'); return; }

    const w = data.weather;

    // Actualizar sidebar con animación / Update sidebar with animation
    animateValue('s-ciudad', w.ciudad);
    animateValue('s-pais',   w.pais);
    animateValue('s-temp',   w.temp);
    animateValue('s-desc',   w.descripcion);
    animateValue('s-sens',   w.sensacion + '°');
    animateValue('s-hum',    w.humedad + '%');
    animateValue('s-viento', w.viento);

    // Actualizar KPIs / Update KPIs
    animateValue('t-f',   Math.round(w.temp * 9/5 + 32) + '°F');
    animateValue('t-idx', Math.round((w.temp + w.humedad * 0.1) * 10) / 10);
    animateValue('t-dif', '+' + Math.round((w.sensacion - w.temp) * 10) / 10 + '°');
    animateValue('t-vis', w.visibilidad + ' km');
    animateValue('t-nub', w.nubosidad + '%');

    // Guardar en historial / Save to history
    saveToHistory(w.ciudad, w.temp, w.pais);

    // Mostrar recomendaciones / Show recommendations
    const recsSection = $id('recs-section');
    const recsGrid    = $id('recs-grid');
    if (data.recomendaciones?.length && recsGrid) {
      recsGrid.innerHTML = '';
      data.recomendaciones.forEach((rec, i) => {
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.style.animationDelay = `${i * 0.06}s`;
        card.innerHTML = `<span class="rec-card__icon">${REC_ICONS[i] ?? '💡'}</span><span>${escapeHtml(rec)}</span>`;
        recsGrid.appendChild(card);
      });
      animateValue('s-rec', data.recomendaciones[0] ?? '');
      recsSection?.classList.remove('hidden');
    }

    showToast(`✓ ${w.ciudad} actualizada`, 'success');

  } catch {
    showToast('Error de conexión. Intenta de nuevo.', 'error');
  } finally {
    loader?.classList.add('hidden');
  }
};


/* ════════════════════════════════════════════════════
   MENÚ Y OPCIONES / MENU AND OPTIONS
   ════════════════════════════════════════════════════ */
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
  const field = $id('console-field');
  const val   = parseInt(field?.value);
  if (isNaN(val) || val < 1 || val > 8) { showError(); return; }
  if (val === 6) { mostrarBusqueda(); field.value = ''; return; }
  if (val === 7) { ejecutarReporte(); field.value = ''; return; }
  ejecutar(val);
  if (field) field.value = '';
};

function mostrarResultado(titulo, datos) {
  const tituloEl = $id('resultado-titulo');
  const gridEl   = $id('resultado-grid');
  if (!tituloEl || !gridEl) return;
  tituloEl.textContent = titulo;
  gridEl.innerHTML = '';
  datos.forEach((item, i) => {
    const f = document.createElement('div');
    f.className = 'resultado-fila';
    f.style.animationDelay = `${i * 0.04}s`;
    f.innerHTML = `<span class="resultado-fila__label">${item.label}</span>
                   <span class="resultado-fila__valor">${item.valor}</span>`;
    gridEl.appendChild(f);
  });
  mostrarSeccion('resultado-section');
}

window.ejecutarBusqueda = async function () {
  const termino = $id('search-input')?.value;
  if (!termino?.trim()) return;
  try {
    const res  = await fetch(`/opcion/6?q=${encodeURIComponent(termino)}`);
    const data = await res.json();
    const grid = $id('search-result');
    if (!grid) return;
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

window.ejecutarReporte = async function () {
  mostrarSeccion('reporte-section');
  try {
    const res  = await fetch('/reporte');
    const data = await res.json();
    const pre  = $id('reporte-pre');
    if (pre) pre.textContent = data.lineas.join('\n');
  } catch (e) { console.error(e); }
};


/* ════════════════════════════════════════════════════
   UTILIDADES / UTILITIES
   ════════════════════════════════════════════════════ */
function animateValue(id, newValue) {
  const el = $id(id);
  if (!el) return;
  el.style.transition = 'none';
  el.style.opacity    = '0';
  el.style.transform  = 'translateY(5px)';
  requestAnimationFrame(() => {
    el.textContent  = newValue;
    el.style.transition = 'opacity 0.35s, transform 0.35s';
    el.style.opacity    = '1';
    el.style.transform  = 'translateY(0)';
  });
}

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
  const el = $id('error-msg');
  if (!el) return;
  el.classList.remove('hidden');
  el.style.animation = 'none';
  requestAnimationFrame(() => { el.style.animation = ''; });
}
function hideError() { $id('error-msg')?.classList.add('hidden'); }

function escapeHtml(s) {
  if (typeof s !== 'string') return String(s);
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

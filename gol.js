// Conway's Game of Life — interactive website background

// ── Config ──────────────────────────────────────────────
const CELL_SIZE         = 12;
const TICK_INTERVAL     = 100;    // ms between simulation steps
const BASE_OPACITY      = 0.50;   // max cell opacity
const FADE_IN_GENS      = 8;      // generations to reach full opacity
const FADE_TICKS_NORMAL = 12;     // render frames to fade on natural death
const FADE_TICKS_AGE    = 50;     // render frames to fade on age-kill (visible ~800ms)
const INIT_DENSITY      = 0.22;
const RESPAWN_THRESHOLD = 0.025;
const HOVER_RADIUS      = 1;
const HOVER_DENSITY     = 0.10;
const BRUSH_RADIUS      = 3;
const BURST_RADIUS      = 5;
const BURST_DENSITY     = 0.55;
const CELL_COLOR        = '0, 210, 110';

// Age limit: 80 ticks × 100ms = 8 seconds.
// PRE-DEATH DIM: cells start fading visually at AGE_DIM_START (60% of max)
// so there's a visible warning before they die.
const MAX_CELL_AGE  = 80;
const AGE_DIM_START = 48;   // start dimming at tick 48 (60% of 80)

// After age-kill, a position is blocked from rebirth for this many ticks.
// This prevents still-life cells from immediately being reborn with age=0.
const BLOCKED_TTL = 30;


// ── State ───────────────────────────────────────────────
let canvas, ctx;
let ROWS = 0, COLS = 0;

let alive   = new Set();   // "row,col" → live cells
let cellAge = new Map();   // "row,col" → generations alive
let dying   = new Map();   // "row,col" → remaining fade ticks
let blocked = new Map();   // "row,col" → ticks until rebirth allowed

let mouseX = -999, mouseY = -999;
let lastHoverRow = -1, lastHoverCol = -1;
let isLeftDown  = false;
let isRightDown = false;
let lastTick    = 0;


// ── Helpers ─────────────────────────────────────────────

function key(row, col)  { return `${row},${col}`; }

function parseKey(k) {
  const i = k.indexOf(',');
  return [parseInt(k, 10), parseInt(k.slice(i + 1), 10)];
}

function getNeighbors(row, col) {
  return [
    [row-1, col-1], [row-1, col], [row-1, col+1],
    [row,   col-1],               [row,   col+1],
    [row+1, col-1], [row+1, col], [row+1, col+1],
  ];
}

// Compute render opacity for a live cell given its age.
// Fades in from 0→BASE over FADE_IN_GENS, holds, then dims from BASE→0.3×BASE
// as the cell approaches MAX_CELL_AGE (pre-death visual warning).
function liveOpacity(age) {
  if (age < FADE_IN_GENS) {
    return BASE_OPACITY * (age + 1) / FADE_IN_GENS;
  }
  if (age >= AGE_DIM_START) {
    const t = (age - AGE_DIM_START) / (MAX_CELL_AGE - AGE_DIM_START); // 0→1
    return BASE_OPACITY * (1 - t * 0.75); // dims to 25% of full opacity
  }
  return BASE_OPACITY;
}


// ── Grid logic ───────────────────────────────────────────

function nextGeneration() {
  // Step 1: count alive neighbours for every relevant cell
  const counts = new Map();
  for (const k of alive) {
    const [r, c] = parseKey(k);
    for (const [nr, nc] of getNeighbors(r, c)) {
      const nk = key(nr, nc);
      counts.set(nk, (counts.get(nk) || 0) + 1);
    }
  }

  // Step 2: apply Conway's rules
  const nextAlive = new Set();
  const nextAge   = new Map();

  for (const [k, count] of counts) {
    if (alive.has(k)) {
      if (count === 2 || count === 3) {
        nextAlive.add(k);
        nextAge.set(k, (cellAge.get(k) || 0) + 1);
      } else {
        dying.set(k, FADE_TICKS_NORMAL);
      }
    } else {
      // Dead cell birth — skip if this position is blocked after an age-kill
      if (count === 3 && !blocked.has(k)) {
        nextAlive.add(k);
        nextAge.set(k, 0);
        dying.delete(k);
      }
    }
  }

  // Underpopulation: alive cells with 0 neighbours (not in counts)
  for (const k of alive) {
    if (!nextAlive.has(k) && !dying.has(k)) {
      dying.set(k, FADE_TICKS_NORMAL);
    }
  }

  // Step 3: age-kill — collect first, then remove (never modify a Set mid-loop)
  const overAge = [];
  for (const k of nextAlive) {
    if ((nextAge.get(k) || 0) >= MAX_CELL_AGE) overAge.push(k);
  }
  for (const k of overAge) {
    nextAlive.delete(k);
    nextAge.delete(k);
    dying.set(k, FADE_TICKS_AGE);   // slow fade so destruction is clearly visible
    blocked.set(k, BLOCKED_TTL);    // prevent immediate rebirth → block reforms
  }

  // Step 4: tick down blocked positions
  for (const [k, ttl] of blocked) {
    if (ttl <= 1) blocked.delete(k);
    else blocked.set(k, ttl - 1);
  }

  alive   = nextAlive;
  cellAge = nextAge;
}


// ── Seeding ──────────────────────────────────────────────

function seedAt(row, col, radius, density) {
  for (let r = row - radius; r <= row + radius; r++) {
    for (let c = col - radius; c <= col + radius; c++) {
      if (r < 0 || r >= ROWS || c < 0 || c >= COLS) continue;
      if (Math.sqrt((r - row) ** 2 + (c - col) ** 2) > radius) continue;
      if (Math.random() > density) continue;
      const k = key(r, c);
      if (!alive.has(k)) {
        alive.add(k);
        cellAge.set(k, 0);
        dying.delete(k);
        blocked.delete(k);  // manual seed overrides block
      }
    }
  }
}

function eraseAt(row, col, radius) {
  for (let r = row - radius; r <= row + radius; r++) {
    for (let c = col - radius; c <= col + radius; c++) {
      const k = key(r, c);
      alive.delete(k);
      cellAge.delete(k);
    }
  }
}

function randomGrid(density = INIT_DENSITY) {
  alive.clear();
  cellAge.clear();
  dying.clear();
  blocked.clear();
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (Math.random() < density) {
        const k = key(r, c);
        alive.add(k);
        // Stagger starting ages (0 – 70% of max) so initial population
        // doesn't all expire at the same tick.
        cellAge.set(k, Math.floor(Math.random() * (MAX_CELL_AGE * 0.7)));
      }
    }
  }
}

function checkRespawn() {
  if (alive.size < ROWS * COLS * RESPAWN_THRESHOLD) {
    const r = Math.floor(Math.random() * ROWS);
    const c = Math.floor(Math.random() * COLS);
    seedAt(r, c, 10, 0.22);
  }
}


// ── Mouse influence ──────────────────────────────────────

function applyMouseInfluence() {
  const row = Math.floor(mouseY / CELL_SIZE);
  const col = Math.floor(mouseX / CELL_SIZE);

  if (isRightDown) { eraseAt(row, col, BRUSH_RADIUS); return; }
  if (isLeftDown)  { seedAt(row, col, BRUSH_RADIUS, 0.9); return; }

  if (row === lastHoverRow && col === lastHoverCol) return;
  lastHoverRow = row;
  lastHoverCol = col;
  seedAt(row, col, HOVER_RADIUS, HOVER_DENSITY);
}


// ── Rendering ────────────────────────────────────────────

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Fading-out dead / age-killed cells
  const remove = [];
  for (const [k, ticks] of dying) {
    const [r, c]  = parseKey(k);
    // Use whichever fade budget was set (NORMAL or AGE)
    const budget  = ticks > FADE_TICKS_NORMAL ? FADE_TICKS_AGE : FADE_TICKS_NORMAL;
    const opacity = BASE_OPACITY * (ticks / budget);
    ctx.fillStyle = `rgba(${CELL_COLOR},${opacity.toFixed(3)})`;
    ctx.fillRect(c * CELL_SIZE + 1, r * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1);
    const next = ticks - 1;
    if (next <= 0) remove.push(k); else dying.set(k, next);
  }
  for (const k of remove) dying.delete(k);

  // Live cells — with pre-death dimming baked into liveOpacity()
  for (const k of alive) {
    const [r, c]  = parseKey(k);
    const age     = cellAge.get(k) || 0;
    const opacity = liveOpacity(age);
    ctx.fillStyle = `rgba(${CELL_COLOR},${opacity.toFixed(3)})`;
    ctx.fillRect(c * CELL_SIZE + 1, r * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1);
  }
}


// ── Game loop ────────────────────────────────────────────

function loop(timestamp) {
  if (timestamp - lastTick >= TICK_INTERVAL) {
    applyMouseInfluence();
    nextGeneration();
    checkRespawn();
    lastTick = timestamp;
  }
  render();
  requestAnimationFrame(loop);
}


// ── Resize ───────────────────────────────────────────────

function resize() {
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;

  const newRows = Math.ceil(canvas.height / CELL_SIZE);
  const newCols = Math.ceil(canvas.width  / CELL_SIZE);
  if (newRows === ROWS && newCols === COLS) return;

  const prevAlive = new Set(alive);
  const prevAge   = new Map(cellAge);

  ROWS = newRows;
  COLS = newCols;
  alive.clear();
  cellAge.clear();

  for (const k of prevAlive) {
    const [r, c] = parseKey(k);
    if (r < ROWS && c < COLS) {
      alive.add(k);
      cellAge.set(k, prevAge.get(k) || 0);
    }
  }

  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const k = key(r, c);
      if (!alive.has(k) && Math.random() < 0.03) {
        alive.add(k);
        cellAge.set(k, Math.floor(Math.random() * 20));
      }
    }
  }
}


// ── Init ─────────────────────────────────────────────────

function init() {
  canvas = document.getElementById('gol-canvas');
  ctx    = canvas.getContext('2d');

  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
  ROWS = Math.ceil(canvas.height / CELL_SIZE);
  COLS = Math.ceil(canvas.width  / CELL_SIZE);

  randomGrid();

  document.addEventListener('mousemove', e => { mouseX = e.clientX; mouseY = e.clientY; });
  document.addEventListener('mousedown', e => { if (e.button === 0) isLeftDown = true;  if (e.button === 2) isRightDown = true; });
  document.addEventListener('mouseup',   e => { if (e.button === 0) isLeftDown = false; if (e.button === 2) isRightDown = false; });
  document.addEventListener('click', e => {
    const r = Math.floor(e.clientY / CELL_SIZE);
    const c = Math.floor(e.clientX / CELL_SIZE);
    seedAt(r, c, BURST_RADIUS, BURST_DENSITY);
  });
  document.addEventListener('contextmenu', e => e.preventDefault());
  window.addEventListener('resize', resize);

  requestAnimationFrame(loop);
}

document.addEventListener('DOMContentLoaded', init);

// ── Data ──────────────────────────────────────────────────────────────────────

const NODE_TYPES = {
  datacenter: { color: '#7b2ff7', radius: 14, label: 'Data Center' },
  isp:        { color: '#00d2ff', radius: 10, label: 'ISP' },
  exchange:   { color: '#f368e0', radius: 12, label: 'IX Point' },
  cdn:        { color: '#ff6b6b', radius: 9,  label: 'CDN Edge' },
  user:       { color: '#1dd1a1', radius: 7,  label: 'End User' },
  dns:        { color: '#feca57', radius: 10, label: 'DNS Server' },
};

const INITIAL_NODES = [
  { id: 0,  type: 'datacenter', name: 'AWS US-East',        x: 0.25, y: 0.30 },
  { id: 1,  type: 'datacenter', name: 'Google Cloud EU',    x: 0.55, y: 0.20 },
  { id: 2,  type: 'datacenter', name: 'Azure Asia',         x: 0.78, y: 0.35 },
  { id: 3,  type: 'exchange',   name: 'DE-CIX Frankfurt',   x: 0.50, y: 0.30 },
  { id: 4,  type: 'exchange',   name: 'AMS-IX Amsterdam',   x: 0.48, y: 0.22 },
  { id: 5,  type: 'isp',        name: 'Comcast',            x: 0.20, y: 0.50 },
  { id: 6,  type: 'isp',        name: 'Vodafone',           x: 0.55, y: 0.45 },
  { id: 7,  type: 'isp',        name: 'NTT',                x: 0.82, y: 0.50 },
  { id: 8,  type: 'cdn',        name: 'Cloudflare Edge 1',  x: 0.35, y: 0.40 },
  { id: 9,  type: 'cdn',        name: 'Akamai Edge 1',      x: 0.65, y: 0.40 },
  { id: 10, type: 'dns',        name: 'Root DNS A',         x: 0.40, y: 0.15 },
  { id: 11, type: 'dns',        name: 'Root DNS J',         x: 0.70, y: 0.18 },
  { id: 12, type: 'user',       name: 'NYC User',           x: 0.15, y: 0.65 },
  { id: 13, type: 'user',       name: 'London User',        x: 0.50, y: 0.60 },
  { id: 14, type: 'user',       name: 'Tokyo User',         x: 0.85, y: 0.65 },
  { id: 15, type: 'datacenter', name: 'AWS EU-West',        x: 0.42, y: 0.35 },
  { id: 16, type: 'cdn',        name: 'Fastly Edge',        x: 0.30, y: 0.55 },
  { id: 17, type: 'isp',        name: 'AT&T',               x: 0.12, y: 0.45 },
];

const INITIAL_LINKS = [
  [0, 3], [0, 8], [0, 5], [0, 15],
  [1, 3], [1, 4], [1, 9],
  [2, 7], [2, 9], [2, 11],
  [3, 4], [3, 6], [3, 15],
  [4, 10],
  [5, 8], [5, 12], [5, 17],
  [6, 9], [6, 13],
  [7, 14], [7, 2],
  [8, 16], [8, 15],
  [9, 11],
  [10, 11],
  [12, 17],
  [13, 6],
  [14, 7],
  [15, 1],
  [16, 12],
];

// ── State ─────────────────────────────────────────────────────────────────────

let nodes = [];
let links = [];
let packets = [];
let nextId = 0;
let totalPackets = 0;
let dragNode = null;
let hoverNode = null;
let mouse = { x: 0, y: 0 };

// ── Canvas setup ──────────────────────────────────────────────────────────────

const canvas = document.getElementById('network-canvas');
const ctx = canvas.getContext('2d');

function resize() {
  canvas.width = canvas.clientWidth * devicePixelRatio;
  canvas.height = canvas.clientHeight * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
}
window.addEventListener('resize', resize);
resize();

// ── Helpers ───────────────────────────────────────────────────────────────────

function screenX(frac) { return frac * canvas.clientWidth; }
function screenY(frac) { return frac * canvas.clientHeight; }
function dist(ax, ay, bx, by) { return Math.hypot(ax - bx, ay - by); }

function nodeAt(mx, my) {
  for (let i = nodes.length - 1; i >= 0; i--) {
    const n = nodes[i];
    const r = NODE_TYPES[n.type].radius + 4;
    if (dist(screenX(n.x), screenY(n.y), mx, my) < r) return n;
  }
  return null;
}

// ── Initialization ────────────────────────────────────────────────────────────

function init() {
  nodes = INITIAL_NODES.map(n => ({
    ...n,
    vx: 0, vy: 0,
    connections: 0,
    trafficIn: 0,
    trafficOut: 0,
    status: 'online',
    latency: Math.floor(Math.random() * 80) + 5,
    uptime: (99 + Math.random()).toFixed(2) + '%',
  }));
  nextId = nodes.length;

  links = INITIAL_LINKS.map(([a, b]) => ({ source: a, target: b }));

  // Count connections
  links.forEach(l => {
    const s = nodes.find(n => n.id === l.source);
    const t = nodes.find(n => n.id === l.target);
    if (s) s.connections++;
    if (t) t.connections++;
  });

  packets = [];
  totalPackets = 0;
  updateStats();
}

// ── Packets (animated traffic) ────────────────────────────────────────────────

function spawnPacket(link) {
  const dir = Math.random() > 0.5 ? 1 : -1;
  packets.push({
    link,
    t: dir === 1 ? 0 : 1,
    dir,
    speed: 0.004 + Math.random() * 0.008,
    color: Math.random() > 0.5 ? '#00d2ff' : '#7b2ff7',
  });
  totalPackets++;
}

function updatePackets() {
  for (let i = packets.length - 1; i >= 0; i--) {
    const p = packets[i];
    p.t += p.dir * p.speed;
    if (p.t > 1 || p.t < 0) {
      // Update traffic stats
      const src = nodes.find(n => n.id === p.link.source);
      const tgt = nodes.find(n => n.id === p.link.target);
      if (p.dir === 1 && tgt) tgt.trafficIn++;
      if (p.dir === -1 && src) src.trafficIn++;
      packets.splice(i, 1);
    }
  }
}

// ── Auto traffic ──────────────────────────────────────────────────────────────

function autoTraffic() {
  if (links.length === 0) return;
  // Spawn 1-3 packets on random links
  const count = 1 + Math.floor(Math.random() * 3);
  for (let i = 0; i < count; i++) {
    const link = links[Math.floor(Math.random() * links.length)];
    spawnPacket(link);
  }
}

setInterval(autoTraffic, 400);

// ── Drawing ───────────────────────────────────────────────────────────────────

function drawGrid() {
  ctx.strokeStyle = 'rgba(123, 47, 247, 0.04)';
  ctx.lineWidth = 1;
  const step = 40;
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  for (let x = 0; x < w; x += step) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
  }
  for (let y = 0; y < h; y += step) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }
}

function drawLinks() {
  links.forEach(l => {
    const s = nodes.find(n => n.id === l.source);
    const t = nodes.find(n => n.id === l.target);
    if (!s || !t) return;
    const sx = screenX(s.x), sy = screenY(s.y);
    const tx = screenX(t.x), ty = screenY(t.y);

    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.lineTo(tx, ty);
    ctx.strokeStyle = 'rgba(123, 47, 247, 0.15)';
    ctx.lineWidth = 1;
    ctx.stroke();
  });
}

function drawPackets() {
  packets.forEach(p => {
    const s = nodes.find(n => n.id === p.link.source);
    const t = nodes.find(n => n.id === p.link.target);
    if (!s || !t) return;
    const x = screenX(s.x) + (screenX(t.x) - screenX(s.x)) * p.t;
    const y = screenY(s.y) + (screenY(t.y) - screenY(s.y)) * p.t;

    ctx.beginPath();
    ctx.arc(x, y, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();

    // Glow
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    const g = ctx.createRadialGradient(x, y, 0, x, y, 6);
    g.addColorStop(0, p.color + '55');
    g.addColorStop(1, 'transparent');
    ctx.fillStyle = g;
    ctx.fill();
  });
}

function drawNodes() {
  nodes.forEach(n => {
    const cfg = NODE_TYPES[n.type];
    const x = screenX(n.x), y = screenY(n.y);
    const isHover = hoverNode === n;
    const r = cfg.radius + (isHover ? 3 : 0);

    // Outer glow
    ctx.beginPath();
    ctx.arc(x, y, r + 8, 0, Math.PI * 2);
    const glow = ctx.createRadialGradient(x, y, r, x, y, r + 8);
    glow.addColorStop(0, cfg.color + '30');
    glow.addColorStop(1, 'transparent');
    ctx.fillStyle = glow;
    ctx.fill();

    // Node circle
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = cfg.color + (isHover ? 'dd' : '99');
    ctx.fill();
    ctx.strokeStyle = cfg.color;
    ctx.lineWidth = isHover ? 2 : 1;
    ctx.stroke();

    // Label
    ctx.font = '10px system-ui, sans-serif';
    ctx.fillStyle = '#c8d6e5';
    ctx.textAlign = 'center';
    ctx.fillText(n.name, x, y + r + 14);
  });
}

function draw() {
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  drawGrid();
  drawLinks();
  drawPackets();
  drawNodes();
}

// ── Stats ─────────────────────────────────────────────────────────────────────

function updateStats() {
  document.getElementById('stat-nodes').textContent = 'Nodes: ' + nodes.length;
  document.getElementById('stat-links').textContent = 'Links: ' + links.length;
  document.getElementById('stat-packets').textContent = 'Packets: ' + totalPackets;
}

// ── Loop ──────────────────────────────────────────────────────────────────────

function loop() {
  updatePackets();
  draw();
  updateStats();
  requestAnimationFrame(loop);
}

// ── Mouse interaction ─────────────────────────────────────────────────────────

canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = e.clientX - rect.left;
  mouse.y = e.clientY - rect.top;

  if (dragNode) {
    dragNode.x = mouse.x / canvas.clientWidth;
    dragNode.y = mouse.y / canvas.clientHeight;
    return;
  }

  const n = nodeAt(mouse.x, mouse.y);
  hoverNode = n;
  canvas.style.cursor = n ? 'pointer' : 'default';

  const tooltip = document.getElementById('tooltip');
  if (n) {
    const cfg = NODE_TYPES[n.type];
    tooltip.innerHTML = `<strong>${n.name}</strong><br>${cfg.label}<br>Latency: ${n.latency}ms &middot; Uptime: ${n.uptime}`;
    tooltip.style.left = (mouse.x + 16) + 'px';
    tooltip.style.top = (mouse.y - 10) + 'px';
    tooltip.classList.remove('hidden');
  } else {
    tooltip.classList.add('hidden');
  }
});

canvas.addEventListener('mousedown', e => {
  const n = nodeAt(mouse.x, mouse.y);
  if (n) { dragNode = n; canvas.style.cursor = 'grabbing'; }
});

canvas.addEventListener('mouseup', () => {
  if (dragNode) { canvas.style.cursor = 'pointer'; dragNode = null; }
});

canvas.addEventListener('click', e => {
  if (dragNode) return;
  const n = nodeAt(mouse.x, mouse.y);
  if (n) showPanel(n);
});

// ── Info panel ────────────────────────────────────────────────────────────────

function showPanel(n) {
  const cfg = NODE_TYPES[n.type];
  document.getElementById('panel-title').textContent = n.name;
  document.getElementById('panel-body').innerHTML = `
    <div class="field"><div class="label">Type</div>${cfg.label}</div>
    <div class="field"><div class="label">Status</div>${n.status}</div>
    <div class="field"><div class="label">Latency</div>${n.latency} ms</div>
    <div class="field"><div class="label">Uptime</div>${n.uptime}</div>
    <div class="field"><div class="label">Connections</div>${n.connections}</div>
    <div class="field"><div class="label">Traffic In</div>${n.trafficIn} packets</div>
    <div class="field"><div class="label">ID</div>${n.id}</div>
  `;
  document.getElementById('info-panel').classList.remove('hidden');
}

document.getElementById('panel-close').addEventListener('click', () => {
  document.getElementById('info-panel').classList.add('hidden');
});

// ── Buttons ───────────────────────────────────────────────────────────────────

document.getElementById('btn-add').addEventListener('click', () => {
  const types = Object.keys(NODE_TYPES);
  const type = types[Math.floor(Math.random() * types.length)];
  const id = nextId++;
  const node = {
    id, type,
    name: NODE_TYPES[type].label + ' ' + id,
    x: 0.2 + Math.random() * 0.6,
    y: 0.2 + Math.random() * 0.6,
    vx: 0, vy: 0,
    connections: 0,
    trafficIn: 0,
    trafficOut: 0,
    status: 'online',
    latency: Math.floor(Math.random() * 80) + 5,
    uptime: (99 + Math.random()).toFixed(2) + '%',
  };
  nodes.push(node);

  // Connect to 1-3 nearest existing nodes
  const sorted = nodes.filter(n => n.id !== id)
    .map(n => ({ n, d: dist(node.x, node.y, n.x, n.y) }))
    .sort((a, b) => a.d - b.d);
  const count = Math.min(1 + Math.floor(Math.random() * 3), sorted.length);
  for (let i = 0; i < count; i++) {
    links.push({ source: id, target: sorted[i].n.id });
    node.connections++;
    sorted[i].n.connections++;
  }
});

document.getElementById('btn-pulse').addEventListener('click', () => {
  // Send a burst of traffic across all links
  links.forEach(l => {
    spawnPacket(l);
    if (Math.random() > 0.5) spawnPacket(l);
  });
});

document.getElementById('btn-reset').addEventListener('click', () => {
  init();
});

// ── Start ─────────────────────────────────────────────────────────────────────

init();
loop();

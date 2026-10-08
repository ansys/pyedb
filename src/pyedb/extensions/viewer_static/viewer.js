import * as THREE from 'three';
import { OrbitControls } from 'orbit';

// PyEDB layout viewer: renders the binary scene produced by pyedb.extensions.layout_viewer.
const BOOT = window.PYEDB_VIEWER;
const $ = (id) => document.getElementById(id);
const state = { mode: BOOT.mode, color: BOOT.color, zs: BOOT.zScale, op: 0.75, hl: '', diel: BOOT.dielectrics,
  vias: true, comps: true, hidden: new Set() };
window.addEventListener('error', (e) => { $('msg').textContent = 'Error: ' + e.message; });
window.addEventListener('unhandledrejection', (e) => { $('msg').textContent = 'Error: ' + e.reason; });
const GRAY = [0.47, 0.49, 0.52];
const DIM = 0.16;
let head = null, pal = [], hlSet = null, version = -1, needsRender = true, first = true;

// ---------------------------------------------------------------- renderer / cameras
const view = $('view');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
view.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1b1e23);
scene.add(new THREE.HemisphereLight(0xffffff, 0x303540, 1.2));
const sun = new THREE.DirectionalLight(0xffffff, 1.8);
scene.add(sun, sun.target);
const world = new THREE.Group();
scene.add(world);

const persp = new THREE.PerspectiveCamera(40, 1, 0.1, 1000);
persp.up.set(0, 0, 1);
const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 1000);
let orthoHalf = 1;
const ctl3d = new OrbitControls(persp, renderer.domElement);
const ctl2d = new OrbitControls(ortho, renderer.domElement);
ctl3d.screenSpacePanning = ctl2d.screenSpacePanning = true;
ctl3d.zoomToCursor = ctl2d.zoomToCursor = true;
ctl2d.enableRotate = false;
ctl2d.mouseButtons = { LEFT: THREE.MOUSE.PAN, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };
ctl2d.touches = { ONE: THREE.TOUCH.PAN, TWO: THREE.TOUCH.DOLLY_PAN };
for (const c of [ctl3d, ctl2d]) c.addEventListener('change', () => { needsRender = true; });
const is2d = () => state.mode === '2d';
const camera = () => (is2d() ? ortho : persp);
const controls = () => (is2d() ? ctl2d : ctl3d);

function resize() {
  const w = Math.max(view.clientWidth, 1), h = Math.max(view.clientHeight, 1);
  renderer.setSize(w, h, false);
  persp.aspect = w / h; persp.updateProjectionMatrix();
  const a = w / h;
  ortho.left = -orthoHalf * a; ortho.right = orthoHalf * a; ortho.top = orthoHalf; ortho.bottom = -orthoHalf;
  ortho.updateProjectionMatrix();
  needsRender = true;
}
new ResizeObserver(resize).observe(view);

function fit() {
  if (!head) return;
  const [x0, y0, x1, y1] = head.bounds;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, ext = Math.max(x1 - x0, y1 - y0, 1e-3);
  const a = Math.max(view.clientWidth, 1) / Math.max(view.clientHeight, 1);
  orthoHalf = Math.max((y1 - y0) / 2, (x1 - x0) / 2 / a, 1e-3) * 1.08;
  ortho.zoom = 1; ortho.near = 0.01; ortho.far = ext * 10;
  ortho.position.set(cx, cy, ext * 2);
  ctl2d.target.set(cx, cy, 0);
  ctl2d.update();
  const zmid = ((head.zmin + head.zmax) / 2) * state.zs;
  persp.near = ext / 1000; persp.far = ext * 50;
  persp.position.set(cx, cy - ext * 0.9, zmid + ext * 0.8);
  ctl3d.target.set(cx, cy, zmid);
  ctl3d.update();
  resize();
}

// ---------------------------------------------------------------- scene building
function disposeWorld() {
  world.traverse((o) => {
    if (o.geometry) o.geometry.dispose();
    if (o.material) o.material.dispose();
  });
  world.clear();
}

function build(buf) {
  const hl = new DataView(buf).getUint32(0, true);
  head = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 4, hl)));
  const base = 4 + hl;
  const F = (o, n) => new Float32Array(buf, base + o, n);
  const I = (o, n) => new Int32Array(buf, base + o, n);
  const U = (o, n) => new Uint8Array(buf, base + o, n);
  const hex = (h) => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
  pal = head.netColors.map(hex);
  disposeWorld();
  if (state.zs == null) state.zs = head.zScale;
  const layers = Object.fromEntries(head.layers.map((l) => [l.name, l]));
  const metal = head.layers.filter((l) => l.kind === 'metal');

  for (const m of head.meshes) {
    const li = layers[m.layer];
    const xy = F(m.xy, m.nv * 2), top = U(m.top, m.nv);
    const faces = new Uint32Array(buf, base + m.faces, m.nf * 3);
    const n = m.nf * 3, pos = new Float32Array(n * 3);
    for (let t = 0; t < n; t++) {
      const v = faces[t];
      pos[3 * t] = xy[2 * v]; pos[3 * t + 1] = xy[2 * v + 1]; pos[3 * t + 2] = top[v] ? li.z1 : li.z0;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.computeBoundingSphere();
    const mat = new THREE.MeshStandardMaterial({ color: li.color, flatShading: true, side: THREE.DoubleSide,
      metalness: 0.25, roughness: 0.6 });
    const mesh = new THREE.Mesh(g, mat);
    mesh.userData = { kind: 'layer', layer: m.layer, fnet: I(m.fnet, m.nf), rgb: hex(li.color),
      order: metal.length - metal.findIndex((l) => l.name === m.layer) };
    world.add(mesh);
  }

  if (head.vias) {
    const v = head.vias, n = v.n;
    const xy = F(v.xy, n * 2), d = F(v.d, n), z = F(v.z, n * 2);
    const geo = new THREE.CylinderGeometry(0.5, 0.5, 1, 12);
    geo.rotateX(Math.PI / 2);
    const im = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.6,
      roughness: 0.4 }), n);
    const mtx = new THREE.Matrix4(), q = new THREE.Quaternion(), p = new THREE.Vector3(), s = new THREE.Vector3();
    for (let i = 0; i < n; i++) {
      p.set(xy[2 * i], xy[2 * i + 1], (z[2 * i] + z[2 * i + 1]) / 2);
      s.set(d[i], d[i], Math.max(z[2 * i + 1] - z[2 * i], 1e-4));
      mtx.compose(p, q, s);
      im.setMatrixAt(i, mtx);
    }
    im.userData = { kind: 'via', net: I(v.net, n), order: 100 };
    world.add(im);
  }

  if (head.comps) {
    const c = head.comps, n = c.n;
    const bb = F(c.bbox, n * 4), z = F(c.z, n * 2);
    const box = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1),
      new THREE.MeshStandardMaterial({ color: 0x8a95aa, metalness: 0.2, roughness: 0.7 }), n);
    const mtx = new THREE.Matrix4(), q = new THREE.Quaternion(), p = new THREE.Vector3(), s = new THREE.Vector3();
    const CX = [0, 1, 1, 0, 0, 1, 1, 0], CY = [0, 0, 1, 1, 0, 0, 1, 1], CZ = [0, 0, 0, 0, 1, 1, 1, 1];
    const E = [0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7];
    const lp = new Float32Array(n * 24 * 3);
    for (let i = 0; i < n; i++) {
      const x0 = bb[4 * i], y0 = bb[4 * i + 1], x1 = bb[4 * i + 2], y1 = bb[4 * i + 3];
      const za = z[2 * i], zb = z[2 * i + 1];
      p.set((x0 + x1) / 2, (y0 + y1) / 2, (za + zb) / 2);
      s.set(Math.max(x1 - x0, 1e-4), Math.max(y1 - y0, 1e-4), Math.max(zb - za, 1e-4));
      mtx.compose(p, q, s);
      box.setMatrixAt(i, mtx);
      for (let k = 0; k < 24; k++) {
        const j = E[k], o = (i * 24 + k) * 3;
        lp[o] = CX[j] ? x1 : x0; lp[o + 1] = CY[j] ? y1 : y0; lp[o + 2] = CZ[j] ? zb : za;
      }
    }
    box.userData = { kind: 'comp', names: c.names, order: 50 };
    world.add(box);
    const lg = new THREE.BufferGeometry();
    lg.setAttribute('position', new THREE.BufferAttribute(lp, 3));
    const lines = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0xffffff }));
    lines.frustumCulled = false;
    lines.userData = { kind: 'complines', order: 101 };
    world.add(lines);
  }

  if (head.outline) {
    const o = head.outline;
    const sp = F(o.seg, o.n * 4), pos = new Float32Array(o.n * 6);
    for (let i = 0; i < o.n; i++) {
      pos.set([sp[4 * i], sp[4 * i + 1], head.zmax, sp[4 * i + 2], sp[4 * i + 3], head.zmax], i * 6);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const ol = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xaabbcc }));
    ol.frustumCulled = false;
    ol.userData = { kind: 'outline', order: 99 };
    world.add(ol);
  }

  const [x0, y0, x1, y1] = head.bounds;
  for (const l of head.layers) {
    if (l.kind !== 'dielectric') continue;
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, Math.max(l.z1 - l.z0, 1e-4)),
      new THREE.MeshStandardMaterial({ color: l.color, transparent: true, opacity: 0.12, depthWrite: false }));
    m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (l.z0 + l.z1) / 2);
    m.userData = { kind: 'diel', order: 0 };
    world.add(m);
  }
  buildPanel();
  applyAll();
}

// ---------------------------------------------------------------- state -> scene
function netRGB(n) { return n < 0 || n >= pal.length ? GRAY : pal[n]; }

function applyColors() {
  const byNet = state.color === 'net';
  const dim = (c, n) => (hlSet && !hlSet.has(n) ? c.map((x) => x * DIM) : c);
  for (const o of world.children) {
    const u = o.userData;
    if (u.kind === 'layer') {
      const useVC = byNet || !!hlSet;
      const mat = o.material, g = o.geometry;
      if (mat.vertexColors !== useVC) { mat.vertexColors = useVC; mat.needsUpdate = true; }
      if (!useVC) { mat.color.set(0xffffff).multiply(new THREE.Color(...u.rgb)); continue; }
      mat.color.set(0xffffff);
      const nf = u.fnet.length;
      let col = g.getAttribute('color');
      if (!col) { col = new THREE.BufferAttribute(new Float32Array(nf * 9), 3); g.setAttribute('color', col); }
      const a = col.array;
      for (let f = 0; f < nf; f++) {
        const n = u.fnet[f], c = dim(byNet ? netRGB(n) : u.rgb, n);
        for (let k = 0; k < 3; k++) { const o9 = f * 9 + k * 3; a[o9] = c[0]; a[o9 + 1] = c[1]; a[o9 + 2] = c[2]; }
      }
      col.needsUpdate = true;
    } else if (u.kind === 'via') {
      const n = u.net.length, c = new THREE.Color();
      for (let i = 0; i < n; i++) {
        const net = u.net[i], rgb = dim(byNet ? netRGB(net) : [0.83, 0.69, 0.22], net);
        c.setRGB(rgb[0], rgb[1], rgb[2]);
        o.setColorAt(i, c);
      }
      if (o.instanceColor) o.instanceColor.needsUpdate = true;
    }
  }
  needsRender = true;
}

function applyMode() {
  const flat = is2d();
  world.scale.z = flat ? 1e-4 : state.zs;
  for (const o of world.children) {
    const u = o.userData, m = o.material;
    m.depthTest = !flat; m.depthWrite = !flat && u.kind !== 'diel';
    m.transparent = flat || u.kind === 'diel';
    m.opacity = u.kind === 'diel' ? 0.12 : (flat && u.kind === 'layer' ? state.op : 1);
    o.renderOrder = flat ? u.order : 0;
    m.needsUpdate = true;
  }
  $('b2d').className = flat ? 'on' : '';
  $('b3d').className = flat ? '' : 'on';
  applyVisibility();
}

function applyVisibility() {
  const flat = is2d();
  for (const o of world.children) {
    const u = o.userData;
    if (u.kind === 'layer') o.visible = !state.hidden.has(u.layer);
    else if (u.kind === 'via') o.visible = state.vias;
    else if (u.kind === 'comp') o.visible = state.comps && !flat;
    else if (u.kind === 'complines') o.visible = state.comps;
    else if (u.kind === 'diel') o.visible = state.diel && !flat;
  }
  needsRender = true;
}

function applyAll() {
  const q = state.hl.trim().toLowerCase();
  hlSet = null;
  if (q && head) {
    hlSet = new Set();
    head.nets.forEach((n, i) => { if (n.toLowerCase().includes(q)) hlSet.add(i); });
  }
  $('bcol').textContent = 'Color: ' + state.color;
  applyColors();
  applyMode();
}

function buildPanel() {
  const box = $('layers');
  box.innerHTML = '';
  for (const l of head.layers.filter((x) => x.kind === 'metal')) {
    const lab = document.createElement('label');
    const cb = document.createElement('input');
    cb.type = 'checkbox'; cb.checked = !state.hidden.has(l.name);
    cb.onchange = () => { cb.checked ? state.hidden.delete(l.name) : state.hidden.add(l.name); applyVisibility(); };
    const sw = document.createElement('span');
    sw.className = 'sw'; sw.style.background = l.color;
    lab.append(cb, sw, document.createTextNode(l.name));
    box.append(lab);
  }
  $('netlist').innerHTML = head.nets.slice(0, 5000).map((n) => '<option value="' + n.replace(/"/g, '&quot;') + '">').join('');
  const zs = $('zs');
  zs.max = Math.max(50, state.zs); zs.value = state.zs;
  const s = head.stats;
  $('info').textContent = `${s.nets} nets, ${s.primitives} primitives, ${s.padstack_instances} vias/pads`;
  $('msg').textContent = '';
}

// ---------------------------------------------------------------- interaction
$('b2d').onclick = () => { state.mode = '2d'; applyMode(); fit(); };
$('b3d').onclick = () => { state.mode = '3d'; applyMode(); fit(); };
$('bcol').onclick = () => { state.color = state.color === 'layer' ? 'net' : 'layer'; applyAll(); };
$('bfit').onclick = fit;
$('cvias').onchange = (e) => { state.vias = e.target.checked; applyVisibility(); };
$('ccomps').onchange = (e) => { state.comps = e.target.checked; applyVisibility(); };
$('cdiel').onchange = (e) => { state.diel = e.target.checked; applyVisibility(); };
$('cdiel').checked = state.diel;
$('zs').oninput = (e) => { state.zs = parseFloat(e.target.value); if (!is2d()) { world.scale.z = state.zs; needsRender = true; } };
$('op').oninput = (e) => { state.op = parseFloat(e.target.value); applyMode(); };
$('hl').oninput = (e) => { state.hl = e.target.value; applyAll(); };

const ray = new THREE.Raycaster();
const tip = $('tip');
let hoverTimer = null, pointer = null;
renderer.domElement.addEventListener('pointermove', (e) => {
  pointer = e; tip.style.display = 'none';
  clearTimeout(hoverTimer);
  hoverTimer = setTimeout(pick, 120);
});
renderer.domElement.addEventListener('pointerleave', () => { tip.style.display = 'none'; clearTimeout(hoverTimer); });

function pick() {
  if (!pointer || !head) return;
  const r = renderer.domElement.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((pointer.clientX - r.left) / r.width) * 2 - 1,
    -((pointer.clientY - r.top) / r.height) * 2 + 1), camera());
  const objs = world.children.filter((o) => o.visible && ['layer', 'via', 'comp'].includes(o.userData.kind)
    && !(is2d() && o.userData.kind === 'comp'));
  const hit = ray.intersectObjects(objs, false)[0];
  if (!hit) return;
  const u = hit.object.userData, net = (n) => (n >= 0 ? head.nets[n] : '<no net>');
  let txt = '';
  if (u.kind === 'layer') txt = `${net(u.fnet[hit.faceIndex])}  (${u.layer})`;
  else if (u.kind === 'via') txt = `${net(u.net[hit.instanceId])}  (via / pad)`;
  else txt = u.names[hit.instanceId];
  tip.textContent = txt;
  tip.style.left = pointer.clientX - r.left + 14 + 'px';
  tip.style.top = pointer.clientY - r.top + 14 + 'px';
  tip.style.display = 'block';
}

function animate() {
  requestAnimationFrame(animate);
  if (!needsRender || !head) return;
  needsRender = false;
  const cam = camera();
  sun.position.copy(cam.position);
  sun.target.position.copy(controls().target);
  renderer.render(scene, cam);
}

// ---------------------------------------------------------------- loading / live updates
function decode64(s) {
  const bin = atob(s), out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out.buffer;
}

async function load() {
  const r = await fetch('/scene');
  version = parseInt(r.headers.get('X-Scene-Version'), 10);
  build(await r.arrayBuffer());
  if (first) { first = false; fit(); }
}

async function poll() {
  try {
    const j = await (await fetch('/version')).json();
    if (j.version !== version) {
      $('msg').textContent = 'Updating...';
      await load();
    }
  } catch (e) { $('msg').textContent = 'Disconnected'; }
  setTimeout(poll, 400);
}

animate();
if (BOOT.scene) {
  build(decode64(BOOT.scene)); first = false; fit();
} else {
  load().then(poll).catch((e) => { $('msg').textContent = 'Error: ' + e; });
}


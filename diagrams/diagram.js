// Shared bits for the workshop diagrams: SVG helpers, the pieces they're drawn with (pills, arrows, icons) and the
// step-through controls. A plain script, not a module, so the pages also open straight from disk (file://).
// The look follows ByteByteGo: charcoal background, thin white lines, cyan and yellow line icons, green tint for the
// good path, red for blocked. Each phase builds in under a second, then holds while you talk.
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.getElementById('stage');
  let uid = 0;

  function el(tag, attrs = {}, parent = svg) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    parent.appendChild(e);
    return e;
  }
  function txt(s, attrs, parent) { const t = el('text', attrs, parent); t.textContent = s; return t; }
  const clipId = () => 'c' + uid++;

  // A rounded label box: outline, dark fill, text. show(tl, pos) wipes it in from the left.
  function pill(parent, x, y, label, { stroke = 'var(--line)', fill = 'var(--bg)', color = 'var(--fg)', size = 26, mono } = {}) {
    const g = el('g', {}, parent);
    const r = el('rect', { rx: (size + 24) / 2, fill, stroke, 'stroke-width': 2 }, g);
    const t = txt(label, { x, y: y + size * 0.35, 'text-anchor': 'middle', 'font-size': size, fill: color, class: mono ? 'mono' : '' }, g);
    const w = t.getBBox().width + 44, h = size + 24;
    Object.entries({ x: x - w / 2, y: y - h / 2, width: w, height: h }).forEach(([k, v]) => r.setAttribute(k, v));
    const id = clipId();
    const clip = el('rect', { x: x - w / 2 - 4, y: y - h / 2 - 4, width: 0, height: h + 8 }, el('clipPath', { id }, parent));
    g.setAttribute('clip-path', `url(#${id})`);
    return { g, w, h, show: (tl, pos) => tl.to(clip, { attr: { width: w + 8 }, duration: 0.35, ease: 'power2.out' }, pos),
             open() { g.removeAttribute('clip-path'); return this; } };
  }

  // A straight arrow from (x1, y1) to (x2, y2): a dot at the sender, the line draws towards the receiver, then the
  // label wipes in at the middle. A mask draws it, so dashed lines draw on too. Returns tl => adds the build to tl.
  function arrow({ x1, y1, x2, y2, label, code, dashed, color = 'var(--line)', parent = svg, labelSize = 26, dot = true }) {
    const len = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / len, uy = (y2 - y1) / len;
    const g = el('g', {}, parent);
    const id = clipId();
    const mask = el('mask', { id, maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 1920, height: 1080 }, g);
    const reveal = el('line', { x1, y1, x2, y2, stroke: '#fff', 'stroke-width': 40, 'stroke-dasharray': len, 'stroke-dashoffset': len }, mask);
    const draw = el('g', { mask: `url(#${id})` }, g);
    el('line', { x1, y1, x2: x2 - ux * 14, y2: y2 - uy * 14, stroke: color, 'stroke-width': 2.5, 'stroke-dasharray': dashed ? '10 8' : 'none' }, draw);
    const px = -uy * 9, py = ux * 9, bx = x2 - ux * 18, by = y2 - uy * 18;
    el('polygon', { points: `${x2},${y2} ${bx + px},${by + py} ${bx - px},${by - py}`, fill: color }, draw);
    const d = dot && el('circle', { cx: x1, cy: y1, r: 6, fill: color, opacity: 0 }, g);
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const p = label && pill(g, mx, my, label, { size: labelSize });
    const sub = code && txt(code, { x: mx, y: my + labelSize + 20, 'text-anchor': 'middle', 'font-size': 18, class: 'mono halo', fill: 'var(--muted)', opacity: 0 }, g);
    return (tl, pos) => {
      if (d) tl.to(d, { opacity: 1, duration: 0.15 }, pos);
      tl.to(reveal, { attr: { 'stroke-dashoffset': 0 }, duration: Math.min(0.7, 0.25 + len / 1500), ease: 'power1.inOut' }, d ? undefined : pos);
      if (p) p.show(tl, '-=0.3');
      if (sub) tl.to(sub, { opacity: 1, duration: 0.3 }, '-=0.1');
    };
  }

  // Pop in: a quick scale up from 85% with a fade, around the element's own centre.
  function pop(tl, target, pos, dur = 0.3) {
    const b = target.getBBox();
    tl.fromTo(target, { opacity: 0, scale: 0.85, svgOrigin: `${b.x + b.width / 2} ${b.y + b.height / 2}` },
              { opacity: 1, scale: 1, duration: dur, ease: 'back.out(2)', immediateRender: false }, pos);
  }

  // Line-art icons, cyan with a yellow detail, centred on (x, y).
  const S = { fill: 'none', stroke: 'var(--cyan)', 'stroke-width': 3 };
  const Y = { fill: 'none', stroke: 'var(--yellow)', 'stroke-width': 3 };
  const icon = {
    script(g, x, y) {
      el('rect', { x: x - 62, y: y - 46, width: 124, height: 80, rx: 8, ...S }, g);
      el('path', { d: `M${x - 80} ${y + 46} L${x + 80} ${y + 46} L${x + 66} ${y + 34} L${x - 66} ${y + 34} Z`, ...S }, g);
      txt('.py', { x, y: y + 6, 'text-anchor': 'middle', 'font-size': 30, class: 'mono', fill: 'var(--yellow)' }, g);
    },
    browser(g, x, y) {
      el('rect', { x: x - 70, y: y - 52, width: 140, height: 104, rx: 10, ...S }, g);
      el('line', { x1: x - 70, y1: y - 28, x2: x + 70, y2: y - 28, ...S }, g);
      [0, 1, 2].forEach(i => el('circle', { cx: x - 54 + i * 13, cy: y - 40, r: 4, ...S, 'stroke-width': 2 }, g));
      el('circle', { cx: x, cy: y + 12, r: 30, ...Y }, g);
      el('ellipse', { cx: x, cy: y + 12, rx: 13, ry: 30, ...Y }, g);
      el('line', { x1: x - 30, y1: y + 12, x2: x + 30, y2: y + 12, ...Y }, g);
    },
    proxy(g, x, y) {
      el('circle', { cx: x, cy: y, r: 48, ...S }, g);
      txt('IP', { x, y: y + 12, 'text-anchor': 'middle', 'font-size': 34, class: 'mono', fill: 'var(--yellow)' }, g);
      el('path', { d: `M${x - 76} ${y - 10} l12 10 l-12 10 M${x + 64} ${y - 10} l12 10 l-12 10`, ...S }, g);
    },
    site(g, x, y) {
      [-34, -4, 26].forEach(dy => el('path', { d: `M${x - 56} ${y + dy} q56 -26 112 0 v18 q-56 26 -112 0 Z`, ...S, fill: 'var(--bg)' }, g));
      el('circle', { cx: x - 30, cy: y + 38, r: 4, fill: 'var(--yellow)' }, g);
    },
    model(g, x, y) {   // a chip with a spark: the model
      el('rect', { x: x - 44, y: y - 44, width: 88, height: 88, rx: 14, ...S }, g);
      [-24, 0, 24].forEach(d => {
        el('line', { x1: x + d, y1: y - 44, x2: x + d, y2: y - 58, ...S }, g); el('line', { x1: x + d, y1: y + 44, x2: x + d, y2: y + 58, ...S }, g);
        el('line', { x1: x - 44, y1: y + d, x2: x - 58, y2: y + d, ...S }, g); el('line', { x1: x + 44, y1: y + d, x2: x + 58, y2: y + d, ...S }, g);
      });
      el('path', { d: `M${x} ${y - 24} Q${x + 4} ${y - 4} ${x + 24} ${y} Q${x + 4} ${y + 4} ${x} ${y + 24} Q${x - 4} ${y + 4} ${x - 24} ${y} Q${x - 4} ${y - 4} ${x} ${y - 24} Z`, ...Y, fill: '#dfc76533' }, g);
    },
  };

  // Step-through controls. build(tl, api) adds every phase to the paused timeline and calls api.stop() after each.
  // api.say(el, text) changes a text at this point of the timeline; it's keyed by time, so ← and restart put the
  // right text back. Space, → or a click plays the next phase and holds, ← jumps back one, r restarts.
  // ?auto=1 plays it all through with holds, for recording.
  function run(build, { hold = 2.5 } = {}) {
    document.fonts.ready.then(() => {
      const tl = gsap.timeline({ paused: true });
      const stops = [], says = [];
      const api = {
        // the spacer makes '<' in the next phase mean "at this stop", not "with the last tween of this phase"
        stop() { stops.push(tl.duration()); tl.to({}, { duration: 0.001 }); },
        say(e, s, at = tl.duration()) { says.push([e, at, s]); },
        refresh() {},
      };
      build(tl, api);
      const initial = new Map();
      says.forEach(([e]) => initial.has(e) || initial.set(e, e.textContent));
      const refresh = () => {
        const t = tl.time() + 1e-6;
        initial.forEach((s, e) => { e.textContent = s; });
        says.filter(([, at]) => at <= t).sort((a, b) => a[1] - b[1]).forEach(([e, , s]) => { e.textContent = s; });
        api.refresh(t);
      };
      tl.eventCallback('onUpdate', refresh);

      const auto = new URLSearchParams(location.search).has('auto');
      if (auto) document.body.classList.add('auto');
      const stepEl = document.getElementById('step');
      let at = 0, playing = null;
      const go = i => {
        if (i < 0 || i >= stops.length) return;
        // a press while a phase is still playing finishes that phase at once, then plays the next one
        if (playing) { playing.kill(); playing = null; tl.pause().seek(stops[at]); refresh(); }
        if (i === at + 1 || (i === 0 && at === 0))
          playing = tl.tweenTo(stops[i], { onComplete: () => { playing = null; if (auto) gsap.delayedCall(hold, () => go(at + 1)); } });
        else { tl.pause().seek(stops[i]); refresh(); }
        at = i;
        if (stepEl) stepEl.textContent = `${at + 1} / ${stops.length}`;
      };
      document.addEventListener('keydown', e => {
        if (e.key === ' ' || e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); go(at + 1); }
        if (e.key === 'ArrowLeft' || e.key === 'PageUp') go(at - 1);
        if (e.key === 'r') { if (playing) playing.kill(); playing = null; tl.pause().seek(0); refresh(); at = 0; go(0); }
      });
      svg.addEventListener('click', () => go(at + 1));
      refresh();
      go(0);
    });
  }

  window.D = { svg, el, txt, pill, arrow, pop, icon, run };
})();

import './style.css';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// ================================================================
// BOOT
// ================================================================
document.addEventListener('DOMContentLoaded', () => {
  initHero();
  initStarfield();
  initBinary();
  initNav();
  initScrollReveal();
  initDistributionCharts();
  initBrierBars();
  initFeatureBars();
});

// ================================================================
// HERO — entrance animation
// ================================================================
function initHero() {
  if (prefersReducedMotion) {
    document.querySelectorAll('.hero-label, .hero-title, .hero-sub, .hero-cue')
      .forEach(el => (el.style.opacity = '1'));
    return;
  }
  gsap.timeline({ delay: 0.2 })
    .to('#js-hero-label', { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' })
    .to('#js-hero-title',  { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, '-=0.2')
    .to('#js-hero-sub',    { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, '-=0.3')
    .to('#js-hero-cue',    { opacity: 1, duration: 0.5 }, '-=0.1');
}

// ================================================================
// STARFIELD
// ================================================================
function initStarfield() {
  const canvas = document.getElementById('js-starfield');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H;
  const stars = [];

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize, { passive: true });

  for (let i = 0; i < 200; i++) {
    stars.push({
      x: Math.random(),
      y: Math.random(),
      r: Math.random() * 1.4 + 0.3,
      alpha: Math.random() * 0.6 + 0.2,
      speed: Math.random() * 0.004 + 0.001,
      phase: Math.random() * Math.PI * 2,
    });
  }

  function drawStars(t) {
    ctx.clearRect(0, 0, W, H);
    for (const s of stars) {
      const a = prefersReducedMotion
        ? s.alpha
        : s.alpha * (0.6 + 0.4 * Math.sin(t * s.speed + s.phase));
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200,220,255,${a})`;
      ctx.fill();
    }
  }

  let last = 0;
  function frame(t) {
    drawStars(t - last < 5000 ? t : last);
    last = t;
    requestAnimationFrame(frame);
  }
  if (prefersReducedMotion) drawStars(0);
  else requestAnimationFrame(frame);
}

// ================================================================
// ECLIPSING BINARY ANIMATION — edge-on observer view
//
// Science: two stars orbit each other. The orbit is viewed nearly
// edge-on from Earth (observer at left). When the secondary passes
// in front of the primary, it blocks some light → primary eclipse
// (deeper dip). When the primary is in front → secondary eclipse
// (shallower dip). This is what a real eclipsing binary looks like
// from the observer's perspective.
// ================================================================
function initBinary() {
  const orbCanvas = document.getElementById('js-binary-orbital');
  const lcCanvas  = document.getElementById('js-binary-lc');
  if (!orbCanvas || !lcCanvas) return;

  const OW = 500, OH = 180;
  const LW = 500, LH = 130;
  orbCanvas.width  = OW; orbCanvas.height = OH;
  lcCanvas.width   = LW; lcCanvas.height  = LH;

  const orbCtx = orbCanvas.getContext('2d');
  const lcCtx  = lcCanvas.getContext('2d');

  // Orbital geometry (edge-on: major axis horizontal, minor axis very small)
  const cx = OW / 2, cy = OH / 2;
  const a  = 115;   // semi-major axis — horizontal spread of orbit
  const b  = 14;    // semi-minor axis — tiny vertical extent (nearly edge-on)
  const r1 = 22;    // primary radius (larger, hotter → blue)
  const r2 = 10;    // secondary radius (smaller, cooler → amber)
  const COL_PRI = '#5ab4ff';
  const COL_SEC = '#fbbf24';

  // Phase φ ∈ [0, 1)
  // At φ=0:   secondary is directly in front of primary (primary eclipse / primary minimum)
  // At φ=0.5: secondary is directly behind primary (secondary eclipse / secondary minimum)
  // x_sec = cx - a·cos(2π·φ)   ← negative at φ=0 → secondary is LEFT of primary = in front
  // y_sec = cy - b·sin(2π·φ)
  function getSecPos(φ) {
    const θ = 2 * Math.PI * φ;
    return { x: cx - a * Math.cos(θ), y: cy - b * Math.sin(θ) };
  }

  // Secondary is in front (between observer on left and primary) when x_sec < cx
  // x_sec = cx - a·cos(2π·φ) < cx  ↔  cos(2π·φ) > 0
  function isInFront(φ) { return Math.cos(2 * Math.PI * φ) > 0; }

  // Brightness model: dips when secondary is DIRECTLY IN FRONT (φ=0.25) or BEHIND (φ=0.75).
  // The secondary reaches x=cx (transit center) at φ=0.25 and φ=0.75 because:
  //   x_sec = cx - a·cos(2π·φ) → x_sec = cx when cos(2π·φ) = 0 → φ = 0.25 or 0.75
  function brightness(φ) {
    const d25 = Math.min(Math.abs(φ - 0.25), Math.abs(φ - 0.25 + 1), Math.abs(φ - 0.25 - 1));
    const d75 = Math.min(Math.abs(φ - 0.75), Math.abs(φ - 0.75 + 1), Math.abs(φ - 0.75 - 1));
    const pDip = 0.21 * Math.exp(-(d25 * d25) / (2 * 0.018));  // primary: secondary in front
    const sDip = 0.08 * Math.exp(-(d75 * d75) / (2 * 0.018));  // secondary: primary in front
    return 1.0 - pDip - sDip;
  }

  const LC_N    = 300;
  const lcCurve = Array.from({ length: LC_N }, (_, i) => brightness(i / LC_N));

  function drawStar(ctx, x, y, r, col) {
    // Glow aura
    const g = ctx.createRadialGradient(x, y, 0, x, y, r * 2.8);
    g.addColorStop(0,    col);
    g.addColorStop(0.45, col + '55');
    g.addColorStop(1,    'transparent');
    ctx.beginPath(); ctx.arc(x, y, r * 2.8, 0, Math.PI * 2);
    ctx.fillStyle = g; ctx.fill();
    // Core
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = col; ctx.fill();
  }

  function drawOrbital(φ) {
    orbCtx.clearRect(0, 0, OW, OH);

    // Observer label (far left)
    orbCtx.font = '8px JetBrains Mono, monospace';
    orbCtx.fillStyle = '#2a3a5a';
    orbCtx.textAlign = 'left';
    orbCtx.fillText('OBSERVER', 4, cy - 8);
    orbCtx.fillText('(EARTH)', 4, cy + 4);

    // Arrow: line of sight toward the stars
    orbCtx.save();
    orbCtx.setLineDash([3, 5]);
    orbCtx.strokeStyle = '#17263d';
    orbCtx.lineWidth = 1;
    orbCtx.beginPath();
    orbCtx.moveTo(62, cy);
    orbCtx.lineTo(cx - a - r1 - 10, cy);
    orbCtx.stroke();
    orbCtx.restore();

    // Orbit path
    orbCtx.save();
    orbCtx.strokeStyle = 'rgba(77,166,255,0.09)';
    orbCtx.lineWidth = 0.75;
    orbCtx.beginPath();
    orbCtx.ellipse(cx, cy, a, b, 0, 0, Math.PI * 2);
    orbCtx.stroke();
    orbCtx.restore();

    const sec   = getSecPos(φ);
    const front = isInFront(φ);

    // Draw in z-order based on which is in front
    if (front) {
      drawStar(orbCtx, cx,     cy,     r1, COL_PRI);
      drawStar(orbCtx, sec.x,  sec.y,  r2, COL_SEC);
    } else {
      drawStar(orbCtx, sec.x,  sec.y,  r2, COL_SEC);
      drawStar(orbCtx, cx,     cy,     r1, COL_PRI);
    }

    // Eclipse label — only show when stars are actually within visual overlap range
    const distToCenter = Math.abs(sec.x - cx);
    if (distToCenter < r1 + r2 + 8) {
      const primary = front;  // secondary in front = primary eclipse
      orbCtx.font = '8px JetBrains Mono, monospace';
      orbCtx.textAlign = 'center';
      orbCtx.fillStyle = primary ? '#4da6ff' : '#fbbf24';
      orbCtx.fillText(primary ? 'PRIMARY ECLIPSE' : 'SECONDARY ECLIPSE', cx, OH - 8);
    }
  }

  function drawLightCurve(φ) {
    lcCtx.clearRect(0, 0, LW, LH);

    const p  = { l: 8, r: 8, t: 10, b: 30 };
    const cw = LW - p.l - p.r;
    const ch = LH - p.t - p.b;
    const bMin = Math.min(...lcCurve) - 0.01;
    const bMax = 1.02;
    const toY  = (v) => p.t + ch * (1 - (v - bMin) / (bMax - bMin));

    // Normal-brightness guide line
    lcCtx.save();
    lcCtx.setLineDash([2, 5]);
    lcCtx.strokeStyle = '#1a2a3a';
    lcCtx.lineWidth = 0.75;
    lcCtx.beginPath();
    lcCtx.moveTo(p.l, toY(1.0));
    lcCtx.lineTo(p.l + cw, toY(1.0));
    lcCtx.stroke();
    lcCtx.restore();

    // Area under curve
    const baseY = toY(bMin);
    lcCtx.beginPath();
    for (let i = 0; i < LC_N; i++) {
      const x = p.l + (i / (LC_N - 1)) * cw;
      const y = toY(lcCurve[i]);
      i === 0 ? lcCtx.moveTo(x, y) : lcCtx.lineTo(x, y);
    }
    lcCtx.lineTo(p.l + cw, baseY);
    lcCtx.lineTo(p.l, baseY);
    lcCtx.closePath();
    lcCtx.fillStyle = 'rgba(77,166,255,0.07)';
    lcCtx.fill();

    // Curve line
    lcCtx.beginPath();
    for (let i = 0; i < LC_N; i++) {
      const x = p.l + (i / (LC_N - 1)) * cw;
      const y = toY(lcCurve[i]);
      i === 0 ? lcCtx.moveTo(x, y) : lcCtx.lineTo(x, y);
    }
    lcCtx.strokeStyle = '#4da6ff';
    lcCtx.lineWidth = 1.5;
    lcCtx.stroke();

    // Current position dot
    const curX = p.l + φ * cw;
    const curY = toY(brightness(φ));
    lcCtx.beginPath();
    lcCtx.arc(curX, curY, 4, 0, Math.PI * 2);
    lcCtx.fillStyle = '#ffffff';
    lcCtx.fill();
    lcCtx.strokeStyle = '#4da6ff';
    lcCtx.lineWidth = 1.5;
    lcCtx.stroke();

    // Axis labels
    lcCtx.font = '8px JetBrains Mono, monospace';
    lcCtx.fillStyle = '#2a3a5a';
    lcCtx.textAlign = 'center';
    lcCtx.fillText('Orbital phase', p.l + cw / 2, LH - 8);
    lcCtx.textAlign = 'left';
    lcCtx.fillText('Bright', p.l, p.t + 2);
    lcCtx.fillText('0.0', p.l, LH - 16);
    lcCtx.textAlign = 'right';
    lcCtx.fillText('1.0', p.l + cw, LH - 16);
  }

  let phase = 0;
  function step() {
    phase = (phase + 0.0015) % 1;
    drawOrbital(phase);
    drawLightCurve(phase);
    requestAnimationFrame(step);
  }

  if (prefersReducedMotion) {
    // Show the secondary mid-transit so the eclipse is visible
    drawOrbital(0.05);
    drawLightCurve(0.05);
  } else {
    requestAnimationFrame(step);
  }
}

// ================================================================
// NAV — progress bar + active link
// ================================================================
function initNav() {
  const bar   = document.getElementById('js-progress-bar');
  const links = document.querySelectorAll('.nav-link[data-section]');

  // Progress bar
  if (bar) {
    window.addEventListener('scroll', () => {
      const pct = window.scrollY / (document.body.scrollHeight - window.innerHeight) * 100;
      bar.style.width = Math.min(pct, 100) + '%';
    }, { passive: true });
  }

  // Active link — observer on each section
  if (!links.length) return;
  const sectionIds = [...links].map(l => l.dataset.section).filter(Boolean);
  const sections   = sectionIds.map(id => document.getElementById(id)).filter(Boolean);

  if (!sections.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        links.forEach(l => l.classList.toggle('is-active', l.dataset.section === e.target.id));
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });

  sections.forEach(s => io.observe(s));
}

// ================================================================
// SCROLL REVEAL — .reveal and .reveal-tr
// ================================================================
function initScrollReveal() {
  if (prefersReducedMotion) {
    document.querySelectorAll('.reveal, .reveal-tr').forEach(el => {
      el.classList.add('is-visible');
    });
    return;
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        io.unobserve(e.target);
      }
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });

  document.querySelectorAll('.reveal, .reveal-tr').forEach(el => io.observe(el));
}

// ================================================================
// DISTRIBUTION CHARTS — period and eclipse duration
// ================================================================
async function initDistributionCharts() {
  let data;
  try {
    const r = await fetch('/data/distributions.json');
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    data = await r.json();
  } catch {
    return; // Charts simply won't render — page still works
  }

  drawDistChart('js-period-chart', data.period_days, 'Period (days)', 12);
  drawDistChart('js-ecl-chart',    data.ecl_duration_pf ?? data.eclipse_duration, 'Eclipse duration (phase fraction)', 0.6);
}

function drawDistChart(canvasId, chartData, xLabel, xMax) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !chartData) return;

  // Fix canvas pixel size to actual rendered size
  canvas.width  = canvas.offsetWidth  || 800;
  canvas.height = canvas.offsetHeight || 200;
  const ctx = canvas.getContext('2d');
  const W   = canvas.width;
  const H   = canvas.height;

  const tessBins   = chartData.tess?.bins   || [];
  const tessCounts = chartData.tess?.counts || [];
  const gaiaBins   = chartData.gaia?.bins   || [];
  const gaiaCounts = chartData.gaia?.counts || [];

  if (!tessBins.length && !gaiaBins.length) return;

  const pad = { l: 8, r: 8, t: 14, b: 28 };
  const cw  = W - pad.l - pad.r;
  const ch  = H - pad.t - pad.b;

  // Normalize both so their max bar = full chart height
  const tessMax = Math.max(...tessCounts, 1);
  const gaiaMax = Math.max(...gaiaCounts, 1);

  // Determine x-range from bins
  const allBins = [...tessBins, ...gaiaBins];
  const minBin  = Math.min(...allBins);
  const maxBin  = Math.max(...allBins, xMax);
  const xRange  = maxBin - minBin || 1;

  function toX(bin) { return pad.l + ((bin - minBin) / xRange) * cw; }

  // Typical bin width
  const binWidth = tessBins.length > 1 ? (tessBins[1] - tessBins[0]) : (gaiaBins[1] - gaiaBins[0]) || 0.1;
  const barW     = Math.max(2, (binWidth / xRange) * cw * 0.45);

  // Draw TESS bars
  ctx.fillStyle = 'rgba(77,166,255,0.55)';
  for (let i = 0; i < tessBins.length; i++) {
    const h  = (tessCounts[i] / tessMax) * ch;
    const x  = toX(tessBins[i]) - barW;
    ctx.fillRect(x, pad.t + ch - h, barW, h);
  }

  // Draw Gaia bars
  ctx.fillStyle = 'rgba(180,122,255,0.55)';
  for (let i = 0; i < gaiaBins.length; i++) {
    const h = (gaiaCounts[i] / gaiaMax) * ch;
    const x = toX(gaiaBins[i]);
    ctx.fillRect(x, pad.t + ch - h, barW, h);
  }

  // Axis line
  ctx.strokeStyle = '#1a2540';
  ctx.lineWidth   = 1;
  ctx.beginPath();
  ctx.moveTo(pad.l, pad.t + ch);
  ctx.lineTo(pad.l + cw, pad.t + ch);
  ctx.stroke();

  // X-axis labels
  ctx.font      = '8px JetBrains Mono, monospace';
  ctx.fillStyle = '#2a3a5a';
  ctx.textAlign = 'center';
  ctx.fillText(xLabel, pad.l + cw / 2, H - 6);

  // Legend
  ctx.fillStyle = 'rgba(77,166,255,0.8)';
  ctx.fillRect(pad.l, pad.t, 8, 8);
  ctx.fillStyle = '#3a5a7a';
  ctx.textAlign = 'left';
  ctx.fillText('TESS', pad.l + 11, pad.t + 8);

  ctx.fillStyle = 'rgba(180,122,255,0.8)';
  ctx.fillRect(pad.l + 55, pad.t, 8, 8);
  ctx.fillStyle = '#3a5a7a';
  ctx.fillText('Gaia', pad.l + 66, pad.t + 8);

  ctx.fillStyle = '#4a6a9a';
  ctx.textAlign = 'center';
  ctx.fillText('(normalized to peak)', pad.l + cw / 2, pad.t + 8);
}

// ================================================================
// BRIER BARS — animate on scroll
// ================================================================
function initBrierBars() {
  const bars = document.querySelectorAll('.bc-bar[style]');
  if (!bars.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        // Trigger CSS transition by briefly setting width to 0 then restoring
        const target = e.target.style.width;
        e.target.style.width = '0';
        requestAnimationFrame(() => {
          requestAnimationFrame(() => { e.target.style.width = target; });
        });
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  bars.forEach(b => io.observe(b));
}

// ================================================================
// FEATURE IMPORTANCE BARS — animate on scroll
// ================================================================
function initFeatureBars() {
  const fills = document.querySelectorAll('.fib-fill[data-w]');
  if (!fills.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.width = e.target.dataset.w + '%';
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  fills.forEach(f => {
    f.style.width = '0';
    io.observe(f);
  });
}

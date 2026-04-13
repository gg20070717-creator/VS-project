$ErrorActionPreference = 'Stop'

$manifestPath = 'd:\VS project\cultural_technology\123\slides_manifest.json'
$outPath = 'd:\VS project\cultural_technology\123\pre2.html'
$manifest = Get-Content -Raw $manifestPath

$template = @'
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>校园舆情分析 - PPT Web</title>
  <style>
    :root {
      --bg-a: #e6ecef;
      --bg-b: #d7e0e4;
      --glass: rgba(255, 255, 255, 0.2);
      --glass-border: rgba(255, 255, 255, 0.34);
      --hud-text: #1e2a31;
      --shadow-soft: 0 30px 90px rgba(18, 39, 52, 0.18);
      --transition: 860ms cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    * {
      box-sizing: border-box;
    }

    html,
    body {
      width: 100%;
      height: 100%;
      margin: 0;
      overflow: hidden;
      font-family: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(1200px 700px at 10% 10%, rgba(255, 255, 255, 0.75), transparent 62%),
        radial-gradient(900px 600px at 90% 90%, rgba(255, 255, 255, 0.45), transparent 60%),
        linear-gradient(140deg, var(--bg-a), var(--bg-b));
      color: #1f2b33;
    }

    .ambient {
      position: fixed;
      inset: -20%;
      pointer-events: none;
      filter: blur(70px);
      opacity: 0.55;
      background:
        radial-gradient(35% 35% at 25% 30%, rgba(141, 190, 177, 0.45), transparent 70%),
        radial-gradient(35% 35% at 70% 70%, rgba(129, 155, 201, 0.4), transparent 68%),
        radial-gradient(30% 30% at 80% 20%, rgba(206, 183, 143, 0.28), transparent 70%);
      animation: drift 14s ease-in-out infinite alternate;
      transform: translateZ(0);
    }

    @keyframes drift {
      from { transform: translate3d(-1.5%, -1%, 0) scale(1); }
      to { transform: translate3d(1.5%, 1.2%, 0) scale(1.05); }
    }

    .app {
      position: relative;
      width: 100%;
      height: 100%;
      display: grid;
      place-items: center;
      perspective: 2200px;
      padding: min(2.2vw, 24px);
    }

    .deck-shell {
      position: relative;
      width: min(96vw, calc(96vh * 16 / 9));
      aspect-ratio: 16 / 9;
      border-radius: 20px;
      background: rgba(245, 250, 252, 0.13);
      border: 1px solid var(--glass-border);
      backdrop-filter: blur(16px) saturate(120%);
      -webkit-backdrop-filter: blur(16px) saturate(120%);
      box-shadow: var(--shadow-soft);
      overflow: hidden;
      transform-style: preserve-3d;
    }

    #deck {
      position: absolute;
      inset: 0;
      transform-style: preserve-3d;
      isolation: isolate;
    }

    .slide {
      position: absolute;
      inset: 0;
      opacity: 0;
      transform: translate3d(0, 0, -120px) scale(0.985);
      transform-origin: center center;
      transition: transform var(--transition), opacity 520ms ease, filter var(--transition);
      filter: blur(8px) saturate(0.95);
      overflow: hidden;
      background: transparent;
      backface-visibility: hidden;
      will-change: transform, opacity, filter;
    }

    .slide.active {
      opacity: 1;
      transform: translate3d(0, 0, 0) scale(1);
      filter: blur(0px) saturate(1);
      z-index: 4;
    }

    .slide.leaving-next {
      opacity: 0;
      transform: translate3d(-7%, 0, -190px) rotateY(7deg) scale(0.96);
      filter: blur(12px) saturate(0.9);
      z-index: 3;
    }

    .slide.leaving-prev {
      opacity: 0;
      transform: translate3d(7%, 0, -190px) rotateY(-7deg) scale(0.96);
      filter: blur(12px) saturate(0.9);
      z-index: 3;
    }

    .slide.entering-next {
      opacity: 1;
      transform: translate3d(7%, 0, -180px) rotateY(-7deg) scale(0.97);
      filter: blur(10px) saturate(0.92);
      z-index: 4;
    }

    .slide.entering-prev {
      opacity: 1;
      transform: translate3d(-7%, 0, -180px) rotateY(7deg) scale(0.97);
      filter: blur(10px) saturate(0.92);
      z-index: 4;
    }

    .slide-layer {
      position: absolute;
      inset: 0;
    }

    .elem {
      position: absolute;
      transform-origin: center center;
      pointer-events: auto;
    }

    .shape {
      overflow: hidden;
    }

    .shape.roundRect {
      border-radius: 20px;
    }

    .shape.soft-round {
      border-radius: 14px;
    }

    .img {
      object-fit: fill;
      user-select: none;
      -webkit-user-drag: none;
      pointer-events: none;
    }

    .textbox {
      width: 100%;
      height: 100%;
      outline: none;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.12;
      caret-color: #f5f7ff;
      transform: translateZ(1px);
    }

    .textbox:focus {
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(3px);
      border-radius: 6px;
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.16);
    }

    .textbox p {
      margin: 0;
    }

    .hud {
      position: fixed;
      left: 50%;
      bottom: 18px;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(255, 255, 255, 0.48);
      color: var(--hud-text);
      border: 1px solid rgba(255, 255, 255, 0.6);
      border-radius: 999px;
      padding: 8px 12px;
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      box-shadow: 0 10px 24px rgba(21, 31, 37, 0.15);
      z-index: 20;
      user-select: none;
    }

    .hud button {
      appearance: none;
      border: 0;
      background: rgba(12, 28, 36, 0.08);
      color: #1f2b33;
      width: 30px;
      height: 30px;
      border-radius: 999px;
      cursor: pointer;
      font-size: 17px;
      line-height: 30px;
      transition: background 200ms ease, transform 200ms ease;
    }

    .hud button:hover {
      background: rgba(12, 28, 36, 0.16);
      transform: translateY(-1px);
    }

    .hud .count {
      min-width: 84px;
      text-align: center;
      font-size: 13px;
      letter-spacing: 0.2px;
      font-weight: 600;
    }

    .hint {
      position: fixed;
      top: 12px;
      left: 50%;
      transform: translateX(-50%);
      padding: 8px 14px;
      border-radius: 999px;
      font-size: 12px;
      color: rgba(22, 38, 47, 0.85);
      background: rgba(255, 255, 255, 0.38);
      border: 1px solid rgba(255, 255, 255, 0.6);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 20;
      pointer-events: none;
    }

    @media (max-width: 880px) {
      .app {
        padding: 8px;
      }

      .deck-shell {
        width: 100vw;
        border-radius: 14px;
      }

      .hud {
        bottom: 10px;
      }
    }
  </style>
</head>
<body>
  <div class="ambient" aria-hidden="true"></div>
  <div class="app">
    <div class="deck-shell">
      <div id="deck"></div>
    </div>
  </div>

  <div class="hint">方向键 / 鼠标滚轮切页 · 文本框可直接编辑</div>
  <div class="hud">
    <button id="prevBtn" aria-label="上一页">&#8249;</button>
    <div class="count" id="countText">1 / 1</div>
    <button id="nextBtn" aria-label="下一页">&#8250;</button>
  </div>

  <script>
    const manifest = __MANIFEST__;

    const deck = document.getElementById('deck');
    const countText = document.getElementById('countText');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    const EMU_W = manifest.widthEmu;
    const EMU_H = manifest.heightEmu;

    const slides = manifest.slides
      .slice()
      .sort((a, b) => a.slide - b.slide)
      .map((slide) => createSlide(slide));

    slides.forEach((el) => deck.appendChild(el));

    let current = 0;
    let animating = false;

    function emuToPctX(v) {
      return (v / EMU_W) * 100;
    }

    function emuToPctY(v) {
      return (v / EMU_H) * 100;
    }

    function rgbaFromColor(color, fallback = 'transparent') {
      if (!color || !color.hex) return fallback;
      const hex = color.hex.padStart(6, '0');
      const r = parseInt(hex.slice(0, 2), 16);
      const g = parseInt(hex.slice(2, 4), 16);
      const b = parseInt(hex.slice(4, 6), 16);
      const a = typeof color.alpha === 'number' ? color.alpha : 1;
      return `rgba(${r}, ${g}, ${b}, ${a})`;
    }

    function mapAlign(a) {
      if (a === 'ctr') return 'center';
      if (a === 'r') return 'right';
      if (a === 'just') return 'justify';
      return 'left';
    }

    function createSlide(slideData) {
      const slideEl = document.createElement('section');
      slideEl.className = 'slide';
      slideEl.dataset.slide = String(slideData.slide);

      const layer = document.createElement('div');
      layer.className = 'slide-layer';

      slideEl.style.background = rgbaFromColor(slideData.background, 'transparent');

      for (const elem of slideData.elements) {
        if (elem.type === 'image') {
          const img = document.createElement('img');
          img.className = 'elem img';
          img.loading = 'eager';
          img.decoding = 'async';
          img.src = elem.src;
          positionElement(img, elem);
          layer.appendChild(img);
          continue;
        }

        if (elem.type === 'shape') {
          const shape = document.createElement('div');
          shape.className = 'elem shape';

          if (elem.prst === 'roundRect') {
            shape.classList.add('roundRect');
          }
          if (elem.prst === 'snip2SameRect' || elem.prst === 'round1Rect') {
            shape.classList.add('soft-round');
          }

          positionElement(shape, elem);

          if (!elem.noFill && elem.fill) {
            shape.style.background = rgbaFromColor(elem.fill, 'transparent');
          } else {
            shape.style.background = 'transparent';
          }

          const hasText = Array.isArray(elem.paragraphs) && elem.paragraphs.some((p) => (p.runs || []).length > 0);
          if (hasText) {
            const box = document.createElement('div');
            box.className = 'textbox';
            box.contentEditable = 'true';
            box.spellcheck = false;
            box.dataset.role = 'editable-textbox';

            const allFonts = [];
            let maxColor = null;

            for (const para of elem.paragraphs) {
              const p = document.createElement('p');
              p.style.textAlign = mapAlign(para.align);

              for (const run of para.runs || []) {
                const span = document.createElement('span');
                span.textContent = run.text || '';
                span.style.fontFamily = `"${run.font || 'Noto Sans SC'}", "PingFang SC", sans-serif`;
                span.style.fontSize = `${(run.sz || 1600) / 100}px`;
                span.style.fontWeight = run.b ? '700' : '400';
                span.style.fontStyle = run.i ? 'italic' : 'normal';
                span.style.textDecoration = run.u && run.u !== 'none' ? 'underline' : 'none';
                if (run.spc) {
                  span.style.letterSpacing = `${run.spc / 1000}px`;
                }
                span.style.color = rgbaFromColor(run.color, 'rgba(20,20,20,0.95)');
                p.appendChild(span);

                if (run.font) allFonts.push(run.font);
                if (!maxColor && run.color) maxColor = run.color;
              }

              if (!p.textContent) {
                p.appendChild(document.createElement('br'));
              }

              box.appendChild(p);
            }

            if (maxColor) {
              box.style.caretColor = rgbaFromColor(maxColor, '#ffffff');
            }

            shape.appendChild(box);
          }

          layer.appendChild(shape);
        }
      }

      slideEl.appendChild(layer);
      return slideEl;
    }

    function positionElement(node, elem) {
      node.style.left = `${emuToPctX(elem.x)}%`;
      node.style.top = `${emuToPctY(elem.y)}%`;
      node.style.width = `${emuToPctX(elem.w)}%`;
      node.style.height = `${emuToPctY(elem.h)}%`;
      node.style.transform = `rotate(${elem.rot || 0}deg)`;
    }

    function syncCounter() {
      countText.textContent = `${current + 1} / ${slides.length}`;
    }

    function setInitial() {
      slides.forEach((s, i) => {
        s.classList.remove('active', 'entering-next', 'entering-prev', 'leaving-next', 'leaving-prev');
        if (i === 0) {
          s.classList.add('active');
        }
      });
      syncCounter();
    }

    function goTo(index) {
      if (animating) return;
      if (index < 0 || index >= slides.length || index === current) return;

      animating = true;
      const oldIndex = current;
      const dir = index > oldIndex ? 'next' : 'prev';
      const oldSlide = slides[oldIndex];
      const newSlide = slides[index];

      newSlide.classList.remove('active', 'leaving-next', 'leaving-prev');
      newSlide.classList.add(dir === 'next' ? 'entering-next' : 'entering-prev');

      requestAnimationFrame(() => {
        oldSlide.classList.remove('active');
        oldSlide.classList.add(dir === 'next' ? 'leaving-next' : 'leaving-prev');

        newSlide.classList.remove('entering-next', 'entering-prev');
        newSlide.classList.add('active');
      });

      window.setTimeout(() => {
        oldSlide.classList.remove('leaving-next', 'leaving-prev');
        current = index;
        syncCounter();
        animating = false;
      }, 900);
    }

    function next() {
      goTo(current + 1);
    }

    function prev() {
      goTo(current - 1);
    }

    prevBtn.addEventListener('click', prev);
    nextBtn.addEventListener('click', next);

    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === 'PageDown') next();
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') prev();
    });

    let wheelLock = false;
    window.addEventListener('wheel', (e) => {
      if (wheelLock) return;
      if (Math.abs(e.deltaY) < 14) return;
      wheelLock = true;
      if (e.deltaY > 0) next();
      else prev();
      window.setTimeout(() => {
        wheelLock = false;
      }, 520);
    }, { passive: true });

    setInitial();
  </script>
</body>
</html>
'@

$html = $template.Replace('__MANIFEST__', $manifest)
Set-Content -Path $outPath -Value $html -Encoding UTF8

Write-Output "HTML built: $outPath"

async function fetchJSON(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }
  return response.json();
}

function renderFaculty(items) {
  const grid = document.getElementById("faculty-grid");
  grid.innerHTML = items
    .map(
      (item, index) => `
      <a class="card-link" href="/detail?type=faculty&id=${index}">
      <article class="card faculty-card">
        <span class="label">${item.label}</span>
        <h3>${item.name}</h3>
        <p>${item.title}</p>
        <p>${item.field}</p>
      </article>
      </a>
    `
    )
    .join("");
}

function renderNews(items) {
  const list = document.getElementById("news-list");
  renderTimeline(list, items, "news");
}

function renderTimeline(container, items, type) {
  if (!container) {
    return;
  }

  container.innerHTML = items
    .map(
      (item, index) => `
      <a class="news-link" href="/detail?type=${type}&id=${index}">
      <article class="news-item">
        <div class="news-meta">${item.date} · ${item.tag}</div>
        <h3 class="news-title">${item.title}</h3>
        <p>${item.summary}</p>
      </article>
      </a>
    `
    )
    .join("");
}

function renderProgram(program) {
  const el = document.getElementById("program-content");
  el.innerHTML = `
    <p>${program.description}</p>
    <div class="program-grid">
      <article class="card">
        <h3><a href="/detail?type=program&block=highlights">培养亮点</a></h3>
        <ul>${program.highlights.map((v) => `<li>${v}</li>`).join("")}</ul>
      </article>
      <article class="card">
        <h3><a href="/detail?type=program&block=paths">就业方向</a></h3>
        <ul>${program.paths.map((v) => `<li>${v}</li>`).join("")}</ul>
      </article>
    </div>
  `;
}

function setupMenu() {
  const toggle = document.getElementById("menu-toggle");
  const panel = document.getElementById("menu-panel");
  const closeBtn = document.getElementById("menu-close");
  if (!toggle || !panel) {
    return;
  }

  // Enforce default collapsed state on page load.
  panel.hidden = true;
  toggle.setAttribute("aria-expanded", "false");

  function closeMenu() {
    toggle.setAttribute("aria-expanded", "false");
    panel.hidden = true;
  }

  function openMenu() {
    panel.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    if (window.gsap) {
      gsap.fromTo(
        panel,
        { opacity: 0, y: -8, scale: 0.98 },
        { opacity: 1, y: 0, scale: 1, duration: 0.26, ease: "power2.out" }
      );
    }
  }

  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    if (isOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (!panel.hidden && !panel.contains(event.target) && event.target !== toggle) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) {
      closeMenu();
    }
  });

  panel.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      closeMenu();
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", closeMenu);
  }
}

function animatePage() {
  gsap.registerPlugin(ScrollTrigger);

  gsap.to(".reveal", {
    y: 0,
    opacity: 1,
    duration: 0.8,
    stagger: 0.14,
    ease: "power3.out",
  });

  gsap.utils.toArray(".reveal-block").forEach((block) => {
    gsap.to(block, {
      y: 0,
      opacity: 1,
      duration: 0.9,
      ease: "power3.out",
      scrollTrigger: {
        trigger: block,
        start: "top 82%",
      },
    });
  });

  gsap.utils.toArray(".card, .news-item").forEach((item, i) => {
    gsap.fromTo(
      item,
      { opacity: 0, y: 18 },
      {
        opacity: 1,
        y: 0,
        delay: i * 0.04,
        duration: 0.7,
        ease: "power2.out",
        scrollTrigger: {
          trigger: item,
          start: "top 88%",
        },
      }
    );
  });
}

async function init() {
  try {
    const [faculty, news, notices, events, studentAffairs, program] = await Promise.all([
      fetchJSON("/api/faculty"),
      fetchJSON("/api/news"),
      fetchJSON("/api/notices"),
      fetchJSON("/api/events"),
      fetchJSON("/api/student-affairs"),
      fetchJSON("/api/program"),
    ]);

    renderFaculty(faculty);
    renderNews(news);
    renderTimeline(document.getElementById("notice-list"), notices, "notices");
    renderTimeline(document.getElementById("event-list"), events, "events");
    renderTimeline(document.getElementById("student-affairs-list"), studentAffairs, "students");
    renderProgram(program);
    setupMenu();
    animatePage();
  } catch (error) {
    console.error(error);
    document.body.insertAdjacentHTML(
      "beforeend",
      "<p style='text-align:center;color:#b91c1c'>页面数据加载失败，请稍后重试。</p>"
    );
  }
}

init();

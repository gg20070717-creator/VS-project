async function fetchJSON(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }
  return response.json();
}

function param(name) {
  return new URLSearchParams(window.location.search).get(name);
}

function safeIndex(raw, max) {
  if (raw === null) return null;
  const index = Number(raw);
  if (!Number.isInteger(index) || index < 0 || index >= max) {
    return null;
  }
  return index;
}

function typeMeta(type) {
  if (type === "faculty") {
    return {
      label: "师资队伍",
      subtitle: "聚焦学术方向、代表成果与产学协同能力。",
      prev: "/detail?type=about",
      next: "/detail?type=news",
    };
  }

  if (type === "news") {
    return {
      label: "学院新闻",
      subtitle: "发布学院治理、交流合作、学生发展与重要活动动态。",
      prev: "/detail?type=faculty",
      next: "/detail?type=notices",
    };
  }

  if (type === "notices") {
    return {
      label: "通知公告",
      subtitle: "发布招生、答辩、评审和论坛征稿等官方通知。",
      prev: "/detail?type=news",
      next: "/detail?type=events",
    };
  }

  if (type === "events") {
    return {
      label: "学术活动",
      subtitle: "展示高端讲座、学术论坛与研究共同体活动成果。",
      prev: "/detail?type=notices",
      next: "/detail?type=students",
    };
  }

  if (type === "students") {
    return {
      label: "学生事务",
      subtitle: "面向学生培养过程与奖助体系的服务信息。",
      prev: "/detail?type=events",
      next: "/detail?type=program",
    };
  }

  if (type === "program") {
    return {
      label: "人才培养",
      subtitle: "展示培养目标、课程体系和职业发展路径。",
      prev: "/detail?type=students",
      next: "/detail?type=about",
    };
  }

  return {
    label: "学院概况",
    subtitle: "围绕学院定位、学科方向与办学特色展开说明。",
    prev: "/detail?type=program",
    next: "/detail?type=faculty",
  };
}

function setShellInfo(type, titleText) {
  const breadcrumb = document.getElementById("breadcrumb");
  const subtitle = document.getElementById("detail-subtitle");
  const prevLink = document.getElementById("prev-link");
  const nextLink = document.getElementById("next-link");
  const meta = typeMeta(type);

  if (breadcrumb) {
    breadcrumb.textContent = `首页 / ${meta.label} / ${titleText}`;
  }
  if (subtitle) {
    subtitle.textContent = meta.subtitle;
  }
  if (prevLink) {
    prevLink.href = meta.prev;
    prevLink.textContent = `上一篇：${typeMeta(new URL(meta.prev, window.location.origin).searchParams.get("type") || "about").label}`;
  }
  if (nextLink) {
    nextLink.href = meta.next;
    nextLink.textContent = `下一篇：${typeMeta(new URL(meta.next, window.location.origin).searchParams.get("type") || "faculty").label}`;
  }
}

function renderAbout() {
  return `
    <article class="card detail-card">
      <h3>学院概况</h3>
      <p>媒体与传播学院以“学科交叉、技术赋能、社会责任”为办学导向，围绕智能传播、平台治理、国际传播与文化产业管理形成特色发展路径。</p>
      <p>学院坚持研究与实践并重，推动课程体系、科研平台与行业协同联动，服务国家战略与城市文化发展需求。</p>
    </article>
  `;
}

function renderFacultyList(items, index) {
  if (index !== null) {
    const item = items[index];
    return `
      <article class="card detail-card">
        <span class="label">${item.label}</span>
        <h3>${item.name}</h3>
        <p>${item.title}</p>
        <p>${item.field}</p>
        <p>研究方向延伸：以文化数据分析、产业政策评估与跨媒介叙事为核心，持续推动产学研合作。</p>
      </article>
      <p><a class="inline-detail-link" href="/detail?type=faculty">查看全部师资</a></p>
    `;
  }

  return items
    .map(
      (item, i) => `
      <a class="card-link" href="/detail?type=faculty&id=${i}">
        <article class="card detail-card">
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

function renderNewsList(items, index) {
  if (index !== null) {
    const item = items[index];
    return `
      <article class="card detail-card">
        <div class="news-meta">${item.date} · ${item.tag}</div>
        <h3>${item.title}</h3>
        <p>${item.summary}</p>
        <p>详情解读：该项目关注文化科技融合的实施路径，强调“内容创新 + 组织协同 + 场景验证”的三阶段推进模式。</p>
      </article>
      <p><a class="inline-detail-link" href="/detail?type=news">查看全部新闻</a></p>
    `;
  }

  return items
    .map(
      (item, i) => `
      <a class="card-link" href="/detail?type=news&id=${i}">
        <article class="card detail-card">
          <div class="news-meta">${item.date} · ${item.tag}</div>
          <h3>${item.title}</h3>
          <p>${item.summary}</p>
        </article>
      </a>
    `
    )
    .join("");
}

function renderInfoList(items, type, singularTitle, listTitle) {
  const index = safeIndex(param("id"), items.length);
  if (index !== null) {
    const item = items[index];
    return {
      html: `
        <article class="card detail-card">
          <div class="news-meta">${item.date} · ${item.tag}</div>
          <h3>${item.title}</h3>
          <p>${item.summary}</p>
        </article>
        <p><a class="inline-detail-link" href="/detail?type=${type}">查看全部${listTitle}</a></p>
      `,
      title: `${singularTitle} · ${item.title}`,
    };
  }

  return {
    html: items
      .map(
        (item, i) => `
        <a class="card-link" href="/detail?type=${type}&id=${i}">
          <article class="card detail-card">
            <div class="news-meta">${item.date} · ${item.tag}</div>
            <h3>${item.title}</h3>
            <p>${item.summary}</p>
          </article>
        </a>
      `
      )
      .join(""),
    title: singularTitle,
  };
}

function renderProgram(program, block) {
  if (block === "highlights") {
    return `
      <article class="card detail-card">
        <h3>培养亮点</h3>
        <ul>${program.highlights.map((v) => `<li>${v}</li>`).join("")}</ul>
      </article>
      <p><a class="inline-detail-link" href="/detail?type=program">返回专业总览</a></p>
    `;
  }

  if (block === "paths") {
    return `
      <article class="card detail-card">
        <h3>就业方向</h3>
        <ul>${program.paths.map((v) => `<li>${v}</li>`).join("")}</ul>
      </article>
      <p><a class="inline-detail-link" href="/detail?type=program">返回专业总览</a></p>
    `;
  }

  return `
    <article class="card detail-card">
      <h3>${program.name}</h3>
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
    </article>
  `;
}

function animateDetail() {
  gsap.registerPlugin(ScrollTrigger);
  gsap.to(".reveal-block", {
    y: 0,
    opacity: 1,
    duration: 0.9,
    ease: "power3.out",
  });

  gsap.utils.toArray(".detail-card").forEach((card, i) => {
    gsap.fromTo(
      card,
      { opacity: 0, y: 16 },
      {
        opacity: 1,
        y: 0,
        duration: 0.6,
        delay: i * 0.05,
        ease: "power2.out",
      }
    );
  });
}

async function init() {
  const type = param("type") || "about";
  const detailTitle = document.getElementById("detail-title");
  const content = document.getElementById("detail-content");

  try {
    if (type === "about") {
      detailTitle.textContent = "学院概况详情";
      content.innerHTML = renderAbout();
      setShellInfo(type, "学院概况详情");
    } else if (type === "faculty") {
      const faculty = await fetchJSON("/api/faculty");
      const index = safeIndex(param("id"), faculty.length);
      detailTitle.textContent = index === null ? "师资队伍详情" : `师资详情 · ${faculty[index].name}`;
      content.innerHTML = renderFacultyList(faculty, index);
      setShellInfo(type, detailTitle.textContent);
    } else if (type === "news") {
      const news = await fetchJSON("/api/news");
      const index = safeIndex(param("id"), news.length);
      detailTitle.textContent = index === null ? "学院新闻详情" : `新闻详情 · ${news[index].title}`;
      content.innerHTML = renderNewsList(news, index);
      setShellInfo(type, detailTitle.textContent);
    } else if (type === "notices") {
      const notices = await fetchJSON("/api/notices");
      const result = renderInfoList(notices, "notices", "通知公告详情", "通知");
      detailTitle.textContent = result.title;
      content.innerHTML = result.html;
      setShellInfo(type, detailTitle.textContent);
    } else if (type === "events") {
      const events = await fetchJSON("/api/events");
      const result = renderInfoList(events, "events", "学术活动详情", "学术活动");
      detailTitle.textContent = result.title;
      content.innerHTML = result.html;
      setShellInfo(type, detailTitle.textContent);
    } else if (type === "students") {
      const students = await fetchJSON("/api/student-affairs");
      const result = renderInfoList(students, "students", "学生事务详情", "学生事务");
      detailTitle.textContent = result.title;
      content.innerHTML = result.html;
      setShellInfo(type, detailTitle.textContent);
    } else {
      const program = await fetchJSON("/api/program");
      const block = param("block");
      detailTitle.textContent = "人才培养详情";
      content.innerHTML = renderProgram(program, block);
      setShellInfo(type, detailTitle.textContent);
    }

    animateDetail();
  } catch (error) {
    console.error(error);
    content.innerHTML = "<p style='color:#b91c1c'>详情内容加载失败，请稍后重试。</p>";
  }
}

init();

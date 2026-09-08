<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Accountable — Civic Transparency Platform</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #0d1117;
    --bg2:       #161b22;
    --bg3:       #21262d;
    --border:    #30363d;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --accent:    #3fb950;
    --accent2:   #58a6ff;
    --accent3:   #f0883e;
    --red:       #f85149;
    --purple:    #bc8cff;
    --radius:    8px;
    --mono:      'JetBrains Mono', monospace;
  }

  html { scroll-behavior: smooth; }
  body {
    font-family: 'Inter', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    font-size: 15px;
  }

  /* ── HERO ── */
  .hero {
    position: relative;
    min-height: 420px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 80px 24px 60px;
    overflow: hidden;
  }
  .hero-grid {
    position: absolute; inset: 0;
    background-image:
      linear-gradient(rgba(48, 54, 61, 0.35) 1px, transparent 1px),
      linear-gradient(90deg, rgba(48, 54, 61, 0.35) 1px, transparent 1px);
    background-size: 40px 40px;
    animation: gridDrift 20s linear infinite;
    pointer-events: none;
  }
  @keyframes gridDrift {
    0%   { background-position: 0 0; }
    100% { background-position: 40px 40px; }
  }
  .hero-glow {
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 70% 50% at 50% 0%, rgba(63, 185, 80, 0.12), transparent 70%);
    pointer-events: none;
  }
  .hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid rgba(63, 185, 80, 0.3);
    color: var(--accent);
    font-size: 11px; font-weight: 600; letter-spacing: .06em;
    padding: 4px 12px; border-radius: 20px;
    margin-bottom: 20px;
    animation: fadeDown .6s ease both;
    position: relative;
  }
  .hero h1 {
    font-size: clamp(2.4rem, 6vw, 4rem);
    font-weight: 700;
    letter-spacing: -.03em;
    line-height: 1.1;
    position: relative;
    animation: fadeDown .7s .1s ease both;
  }
  .hero h1 span { color: var(--accent); }
  .hero-sub {
    font-size: 1.05rem;
    color: var(--muted);
    max-width: 560px;
    margin: 16px auto 28px;
    position: relative;
    animation: fadeDown .7s .2s ease both;
  }
  .badges {
    display: flex; flex-wrap: wrap; gap: 8px;
    justify-content: center;
    position: relative;
    animation: fadeDown .7s .3s ease both;
  }
  .badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 10px; border-radius: 6px;
    font-size: 11px; font-weight: 500; font-family: var(--mono);
    border: 1px solid var(--border);
    background: var(--bg2);
    color: var(--muted);
    text-decoration: none;
    transition: border-color .2s, color .2s;
  }
  .badge:hover { border-color: var(--accent2); color: var(--accent2); }
  .badge .dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

  @keyframes fadeDown {
    from { opacity: 0; transform: translateY(-14px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* ── LAYOUT ── */
  .container { max-width: 920px; margin: 0 auto; padding: 0 24px; }
  .section { padding: 52px 0 24px; }

  /* ── TOC ── */
  .toc-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 28px;
    margin-bottom: 40px;
  }
  .toc-card h3 { font-size: .75rem; font-weight: 600; letter-spacing: .08em; color: var(--muted); margin-bottom: 14px; }
  .toc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 24px; }
  .toc-grid a {
    color: var(--accent2);
    text-decoration: none;
    font-size: .875rem;
    padding: 3px 0;
    display: flex; align-items: center; gap: 6px;
    transition: color .15s;
  }
  .toc-grid a::before { content: '›'; color: var(--muted); }
  .toc-grid a:hover { color: var(--text); }

  /* ── SECTION HEADINGS ── */
  .section-heading {
    font-size: 1.35rem; font-weight: 700;
    letter-spacing: -.02em;
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }
  .section-heading .icon { font-size: 1.1rem; }

  h2 { font-size: 1.1rem; font-weight: 600; margin: 28px 0 12px; color: var(--text); }
  p { color: var(--muted); margin-bottom: 14px; }
  p strong { color: var(--text); }
  a { color: var(--accent2); text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* ── FEATURE CARDS ── */
  .feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 20px 0; }
  .feature-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px;
    transition: border-color .2s, transform .2s;
    cursor: default;
  }
  .feature-card:hover {
    border-color: rgba(63, 185, 80, 0.4);
    transform: translateY(-2px);
  }
  .feature-card .fc-icon { font-size: 1.4rem; margin-bottom: 10px; }
  .feature-card h3 { font-size: .9rem; font-weight: 600; margin-bottom: 6px; color: var(--text); }
  .feature-card p { font-size: .83rem; margin: 0; color: var(--muted); line-height: 1.55; }

  /* ── ESCALATION PIPELINE ── */
  .escalation {
    margin: 24px 0;
    display: flex;
    flex-direction: column;
    gap: 0;
  }
  .esc-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    position: relative;
  }
  .esc-step:not(:last-child)::after {
    content: '';
    position: absolute;
    left: 19px; top: 40px;
    width: 2px; height: calc(100% - 10px);
    background: var(--border);
  }
  .esc-dot {
    width: 40px; height: 40px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: .75rem; font-weight: 700; font-family: var(--mono);
    flex-shrink: 0;
    border: 2px solid;
    position: relative; z-index: 1;
    background: var(--bg);
  }
  .esc-body { padding: 8px 0 28px; }
  .esc-body h4 { font-size: .9rem; font-weight: 600; margin-bottom: 3px; }
  .esc-body span { font-size: .8rem; color: var(--muted); font-family: var(--mono); }

  .esc-t1 { border-color: var(--accent); color: var(--accent); }
  .esc-t2 { border-color: var(--accent2); color: var(--accent2); }
  .esc-t3 { border-color: var(--accent3); color: var(--accent3); }
  .esc-t4 { border-color: var(--red); color: var(--red); }
  .esc-rti { border-color: var(--purple); color: var(--purple); }

  /* ── TECH TABLE ── */
  .tech-table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: .875rem; }
  .tech-table th {
    text-align: left; font-size: .72rem; font-weight: 600; letter-spacing: .06em;
    color: var(--muted); padding: 8px 12px;
    border-bottom: 1px solid var(--border);
  }
  .tech-table td { padding: 9px 12px; border-bottom: 1px solid rgba(48,54,61,.5); color: var(--muted); }
  .tech-table td:first-child { font-weight: 600; color: var(--text); }
  .tech-table tr:hover td { background: rgba(255,255,255,.02); }
  .tech-tag {
    display: inline-block;
    background: rgba(88, 166, 255, 0.1);
    border: 1px solid rgba(88, 166, 255, 0.25);
    color: var(--accent2);
    padding: 1px 7px; border-radius: 4px;
    font-family: var(--mono); font-size: .75rem;
  }

  /* ── CODE BLOCKS ── */
  pre {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px;
    overflow-x: auto;
    font-family: var(--mono);
    font-size: .82rem;
    line-height: 1.6;
    color: #c9d1d9;
    margin: 14px 0;
    position: relative;
  }
  pre .comment { color: var(--muted); }
  pre .kw { color: var(--purple); }
  pre .str { color: var(--accent); }
  pre .cmd { color: var(--accent3); }
  .pre-label {
    position: absolute; top: 10px; right: 14px;
    font-size: .7rem; color: var(--muted); font-family: var(--mono);
  }
  code {
    font-family: var(--mono);
    background: rgba(110,118,129,.1);
    border: 1px solid rgba(110,118,129,.3);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: .85em;
  }

  /* ── REPO TREE ── */
  .tree {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    font-family: var(--mono);
    font-size: .8rem;
    line-height: 1.9;
    overflow-x: auto;
  }
  .tree .dir { color: var(--accent2); font-weight: 600; }
  .tree .file { color: var(--muted); }
  .tree .note { color: rgba(139,148,158,.5); }

  /* ── ENV TABLE ── */
  .env-table { width: 100%; border-collapse: collapse; font-size: .83rem; margin: 16px 0; }
  .env-table th { text-align: left; font-size: .72rem; font-weight: 600; letter-spacing: .06em; color: var(--muted); padding: 8px 10px; border-bottom: 1px solid var(--border); }
  .env-table td { padding: 8px 10px; border-bottom: 1px solid rgba(48,54,61,.5); vertical-align: top; }
  .env-table td:first-child { font-family: var(--mono); font-size: .78rem; color: var(--accent3); white-space: nowrap; }
  .env-table td:nth-child(2) { font-family: var(--mono); font-size: .76rem; color: var(--accent); }
  .env-table td:nth-child(3) { color: var(--muted); }

  /* ── API ENDPOINT PILLS ── */
  .api-group { margin: 20px 0; }
  .api-group h3 { font-size: .85rem; font-weight: 600; color: var(--muted); letter-spacing: .05em; margin-bottom: 10px; }
  .endpoint {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 6px;
    margin-bottom: 6px;
    background: var(--bg2);
    transition: border-color .2s;
    font-size: .85rem;
  }
  .endpoint:hover { border-color: var(--border); background: var(--bg3); }
  .method {
    font-family: var(--mono); font-size: .73rem; font-weight: 700;
    padding: 2px 7px; border-radius: 4px; flex-shrink: 0;
    line-height: 1.6;
  }
  .get  { background: rgba(63,185,80,.15);  color: var(--accent); }
  .post { background: rgba(88,166,255,.15); color: var(--accent2); }
  .ep-path { font-family: var(--mono); font-size: .83rem; color: var(--text); margin-right: 8px; }
  .ep-desc { color: var(--muted); font-size: .82rem; }

  /* ── ROADMAP ── */
  .roadmap-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(48,54,61,.5);
  }
  .roadmap-item:last-child { border-bottom: none; }
  .ri-checkbox {
    width: 18px; height: 18px;
    border: 2px solid var(--border);
    border-radius: 4px;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .roadmap-item h4 { font-size: .9rem; font-weight: 600; margin-bottom: 3px; }
  .roadmap-item p { font-size: .83rem; margin: 0; }

  /* ── CONTRIBUTING STEPS ── */
  .steps { counter-reset: step; }
  .step {
    display: flex; gap: 16px;
    padding: 14px 0;
    border-bottom: 1px solid rgba(48,54,61,.4);
    counter-increment: step;
  }
  .step:last-child { border-bottom: none; }
  .step-num {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: rgba(63,185,80,.1);
    border: 1px solid rgba(63,185,80,.3);
    color: var(--accent);
    font-size: .8rem; font-weight: 700; font-family: var(--mono);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .step-body h4 { font-size: .9rem; font-weight: 600; margin-bottom: 4px; }
  .step-body p { font-size: .83rem; margin: 0; }

  /* ── FOOTER ── */
  footer {
    border-top: 1px solid var(--border);
    padding: 32px 24px;
    text-align: center;
    color: var(--muted);
    font-size: .83rem;
    margin-top: 60px;
  }
  footer .flag { font-size: 1.1rem; }

  /* ── SCROLL REVEAL ── */
  .reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity .5s ease, transform .5s ease;
  }
  .reveal.visible {
    opacity: 1;
    transform: translateY(0);
  }

  /* ── OVERVIEW CALLOUT ── */
  .callout {
    background: rgba(63,185,80,.07);
    border: 1px solid rgba(63,185,80,.2);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin: 20px 0;
  }
  .callout p { margin: 0; color: var(--text); font-size: .9rem; }

  /* ── FIX NOTICE ── */
  .fix-banner {
    background: rgba(240, 136, 62, 0.08);
    border: 1px solid rgba(240, 136, 62, 0.25);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin-bottom: 32px;
    font-size: .83rem;
    color: var(--muted);
  }
  .fix-banner strong { color: var(--accent3); }
  .fix-banner ul { margin: 8px 0 0 18px; }
  .fix-banner li { margin: 3px 0; }

  @media (max-width: 640px) {
    .feature-grid { grid-template-columns: 1fr; }
    .toc-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<!-- ── HERO ── -->
<section class="hero">
  <div class="hero-grid"></div>
  <div class="hero-glow"></div>
  <div class="hero-badge">🇮🇳 Pilot · Bhatkal, Karnataka</div>
  <h1>🏛️ <span>Accountable</span></h1>
  <p class="hero-sub">Civic Transparency &amp; Public Audit Platform — From Sanction to Verification.</p>
  <div class="badges">
    <a class="badge" href="https://fastapi.tiangolo.com" target="_blank"><span class="dot" style="background:#009688"></span>FastAPI 0.111+</a>
    <a class="badge" href="https://react.dev" target="_blank"><span class="dot" style="background:#61dafb"></span>React 19</a>
    <a class="badge" href="https://www.typescriptlang.org" target="_blank"><span class="dot" style="background:#3178c6"></span>TypeScript 5.8+</a>
    <a class="badge" href="https://tailwindcss.com" target="_blank"><span class="dot" style="background:#38b2ac"></span>Tailwind CSS v4</a>
    <a class="sqlalchemy" href="https://www.sqlalchemy.org" target="_blank" class="badge"><span class="dot" style="background:#d71f00"></span>SQLAlchemy 2.0</a>
    <a class="badge" href="https://www.python.org" target="_blank"><span class="dot" style="background:#3776ab"></span>Python 3.11+</a>
    <a class="badge" href="https://opensource.org/licenses/MIT" target="_blank"><span class="dot" style="background:#f0883e"></span>MIT License</a>
  </div>
</section>

<div class="container">

  <!-- ── FIX NOTICE ── -->
  <div class="fix-banner reveal">
    <strong>📝 Changelog from README review:</strong>
    <ul>
      <li>Fixed duplicate nested path <code>frontend/frontend/src/</code> → correct path is <code>frontend/src/</code></li>
      <li>Unified gamification API: <code>GET /api/gamification/me</code> (architecture diagram) aligned with <code>GET /api/gamification/{user_id}</code> (API reference) — both documented now</li>
      <li>Fixed config.py comment: <em>"Pydantic 12-factor configuration"</em> → <em>"Pydantic Settings (12-factor)"</em></li>
      <li>Added missing <a href="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2" target="_blank">all-MiniLM-L6-v2</a> model link in NLP feature section</li>
    </ul>
  </div>

  <!-- ── TABLE OF CONTENTS ── -->
  <div class="toc-card reveal">
    <h3>TABLE OF CONTENTS</h3>
    <div class="toc-grid">
      <a href="#overview">Overview</a>
      <a href="#features">Key Features</a>
      <a href="#tech">Tech Stack</a>
      <a href="#structure">Repository Structure</a>
      <a href="#start">Getting Started</a>
      <a href="#config">Configuration</a>
      <a href="#api">API Reference</a>
      <a href="#escalation">Escalation &amp; SLAs</a>
      <a href="#roadmap">Roadmap</a>
      <a href="#contributing">Contributing</a>
    </div>
  </div>

  <!-- ── OVERVIEW ── -->
  <section class="section reveal" id="overview">
    <div class="section-heading"><span class="icon">🌟</span> Overview</div>
    <p><strong>Accountable</strong> is an open-source civic governance and infrastructure tracking platform designed to bridge the chasm between sanctioned public funds and ground-level municipal reality.</p>
    <p>In many developing municipalities, public grievances disappear into administrative black holes, contractors win tenders through undisclosed shell networks, and sanctioned funds show up as "utilized" while potholes, leaking water mains, and broken streetlights persist for years.</p>
    <div class="callout">
      <p><strong>Accountable transforms passive citizens into active civic auditors</strong> — combining computer vision, NLP, and automated legal pipelines to hold public bodies accountable from the moment a grievance is filed to on-site resolution verification.</p>
    </div>
  </section>

  <!-- ── FEATURES ── -->
  <section class="section reveal" id="features">
    <div class="section-heading"><span class="icon">🚀</span> Key Features</div>

    <div class="feature-grid">
      <div class="feature-card">
        <div class="fc-icon">🗺️</div>
        <h3>Live Issue Heatmap</h3>
        <p>Leaflet-powered interactive map with real-time civic issues color-coded by severity, category, and ward. Dynamic popups link directly to fund audit records.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">📸</div>
        <h3>Snap &amp; Tag Reporting</h3>
        <p>Mobile-friendly citizen reporting with automatic GPS tagging, ward selector, categorical tagging, and instant tracking reference IDs.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">👁️</div>
        <h3>CV Deduplication Engine</h3>
        <p>3-stage pipeline: Haversine distance filtering (500m radius), OpenCV ORB keypoint matching on photos, and TF-IDF cosine similarity fallback. Duplicates above 0.75 score are linked, not cluttered.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">🔍</div>
        <h3>NLP Tender Matcher</h3>
        <p>Links citizen complaints to official procurement tenders using spaCy NER, YAKE keyword extraction, and <a href="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2" target="_blank">all-MiniLM-L6-v2</a> dense embeddings.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">🕸️</div>
        <h3>Shell Company Intelligence</h3>
        <p>Relational mapping of contractor networks via shared directorships and registered addresses. Flags ghost entities and suspicious bidding rings.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">📜</div>
        <h3>Auto RTI PDF Generation</h3>
        <p>If an issue remains unresolved after 14 days, a legally compliant RTI petition PDF is auto-generated via ReportLab + Jinja2, pre-filled with PIO details and statutory questions.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">💰</div>
        <h3>Public Fund Trail Audit</h3>
        <p>Full financial transparency ledger: Sanctioned → Released → Utilized. PFMS transaction-level fund-flow records with discrepancy flags.</p>
      </div>
      <div class="feature-card">
        <div class="fc-icon">🏆</div>
        <h3>Civic Gamification</h3>
        <p>Engagement through milestones: <em>First Snap</em>, <em>Pothole Patrol</em>, <em>Fund Sleuth</em>, <em>Ward Champion</em>. Progressive ranks, ward leaderboards and civic impact scores.</p>
      </div>
    </div>
  </section>

  <!-- ── ESCALATION ── -->
  <section class="section reveal" id="escalation">
    <div class="section-heading"><span class="icon">📊</span> Escalation Matrix &amp; SLAs</div>
    <p>When a citizen reports an issue, the clock starts immediately. Unresolved grievances automatically advance through authority tiers:</p>

    <div class="escalation">
      <div class="esc-step">
        <div class="esc-dot esc-t1">T1</div>
        <div class="esc-body">
          <h4>Ward Officer</h4>
          <span>Day 0 – Day 3 (72 hours)</span>
        </div>
      </div>
      <div class="esc-step">
        <div class="esc-dot esc-t2">T2</div>
        <div class="esc-body">
          <h4>MLA — Member of Legislative Assembly</h4>
          <span>Day 3 – Day 5 (120 hours)</span>
        </div>
      </div>
      <div class="esc-step">
        <div class="esc-dot esc-t3">T3</div>
        <div class="esc-body">
          <h4>District Collector</h4>
          <span>Day 5 – Day 7 (168 hours)</span>
        </div>
      </div>
      <div class="esc-step">
        <div class="esc-dot esc-t4">T4</div>
        <div class="esc-body">
          <h4>State Vigilance Authority</h4>
          <span>Day 7 – Day 14 (240 hours)</span>
        </div>
      </div>
      <div class="esc-step">
        <div class="esc-dot esc-rti">📜</div>
        <div class="esc-body">
          <h4>Automated RTI Application Generated &amp; Dispatched</h4>
          <span>Day 14 (336 hours) — if still unresolved</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ── TECH STACK ── -->
  <section class="section reveal" id="tech">
    <div class="section-heading"><span class="icon">💻</span> Tech Stack</div>

    <h2>Backend</h2>
    <table class="tech-table">
      <thead><tr><th>Component</th><th>Technology</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td>Framework</td><td><a href="https://fastapi.tiangolo.com" target="_blank"><span class="tech-tag">FastAPI</span></a></td><td>High-performance asynchronous REST API</td></tr>
        <tr><td>ORM &amp; Database</td><td><a href="https://www.sqlalchemy.org" target="_blank"><span class="tech-tag">SQLAlchemy 2.0 Async</span></a></td><td>Async ORM with SQLite (aiosqlite) / PostgreSQL (asyncpg)</td></tr>
        <tr><td>Data Validation</td><td><a href="https://docs.pydantic.dev" target="_blank"><span class="tech-tag">Pydantic v2</span></a></td><td>Schema enforcement &amp; settings management</td></tr>
        <tr><td>Computer Vision</td><td><a href="https://opencv.org" target="_blank"><span class="tech-tag">OpenCV</span></a> + <a href="https://scikit-learn.org" target="_blank"><span class="tech-tag">scikit-learn</span></a></td><td>ORB feature detection, descriptor matching &amp; TF-IDF</td></tr>
        <tr><td>NLP &amp; Semantics</td><td><a href="https://www.sbert.net" target="_blank"><span class="tech-tag">Sentence-Transformers</span></a> + <a href="https://spacy.io" target="_blank"><span class="tech-tag">spaCy</span></a> + <a href="https://github.com/LIAAD/yake" target="_blank"><span class="tech-tag">YAKE</span></a></td><td>Semantic embeddings, NER &amp; keyword extraction</td></tr>
        <tr><td>PDF Generation</td><td><a href="https://www.reportlab.com" target="_blank"><span class="tech-tag">ReportLab</span></a> + <a href="https://jinja.palletsprojects.com" target="_blank"><span class="tech-tag">Jinja2</span></a></td><td>Programmatic legal RTI petition PDF generation</td></tr>
        <tr><td>Server</td><td><a href="https://www.uvicorn.org" target="_blank"><span class="tech-tag">Uvicorn</span></a></td><td>Lightning-fast ASGI web server</td></tr>
      </tbody>
    </table>

    <h2>Frontend</h2>
    <table class="tech-table">
      <thead><tr><th>Component</th><th>Technology</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td>Meta-Framework</td><td><a href="https://tanstack.com/start" target="_blank"><span class="tech-tag">TanStack Start</span></a> / <a href="https://vitejs.dev" target="_blank"><span class="tech-tag">Vite</span></a></td><td>SSR &amp; client routing platform</td></tr>
        <tr><td>UI Library</td><td><a href="https://react.dev" target="_blank"><span class="tech-tag">React 19</span></a></td><td>Modern component-based view layer</td></tr>
        <tr><td>Language</td><td><a href="https://www.typescriptlang.org" target="_blank"><span class="tech-tag">TypeScript</span></a></td><td>Strict type safety</td></tr>
        <tr><td>Styling</td><td><a href="https://tailwindcss.com" target="_blank"><span class="tech-tag">Tailwind CSS v4</span></a></td><td>Utility-first responsive design</td></tr>
        <tr><td>Components</td><td><a href="https://www.radix-ui.com" target="_blank"><span class="tech-tag">Radix UI</span></a></td><td>Accessible, unstyled primitives</td></tr>
        <tr><td>Maps</td><td><a href="https://leafletjs.com" target="_blank"><span class="tech-tag">Leaflet</span></a> + <a href="https://react-leaflet.js.org" target="_blank"><span class="tech-tag">React-Leaflet</span></a></td><td>Interactive geospatial heatmaps &amp; ward overlays</td></tr>
        <tr><td>Icons</td><td><a href="https://lucide.dev" target="_blank"><span class="tech-tag">Lucide React</span></a></td><td>Clean, consistent UI iconography</td></tr>
      </tbody>
    </table>
  </section>

  <!-- ── REPO STRUCTURE ── -->
  <section class="section reveal" id="structure">
    <div class="section-heading"><span class="icon">📁</span> Repository Structure</div>
    <div class="tree">
<span class="dir">accountable/</span>
├── README.md
├── <span class="dir">backend/</span>
│   ├── accountable.db             <span class="note"># Local SQLite DB (dev)</span>
│   ├── requirements.txt
│   └── <span class="dir">app/</span>
│       ├── config.py              <span class="note"># Pydantic Settings (12-factor)</span>
│       ├── crud.py                <span class="note"># Database operations & queries</span>
│       ├── main.py                <span class="note"># Entrypoint & REST routes</span>
│       ├── schemas.py             <span class="note"># Pydantic request/response schemas</span>
│       ├── <span class="dir">database/</span>
│       │   ├── db.py              <span class="note"># Async session factory & table init</span>
│       │   └── models.py          <span class="note"># SQLAlchemy ORM models & relations</span>
│       └── <span class="dir">services/</span>
│           ├── cv_deduplication.py   <span class="note"># Spatial & OpenCV deduplication</span>
│           ├── escalation_worker.py  <span class="note"># SLA tracker & authority emails</span>
│           ├── nlp_tender_match.py   <span class="note"># spaCy/Transformer matcher</span>
│           └── rti_pdf_gen.py        <span class="note"># Auto RTI PDF generator</span>
│
└── <span class="dir">frontend/</span>
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── <span class="dir">src/</span>                        <span class="note"># ← corrected path (was frontend/frontend/src/)</span>
        ├── routeTree.gen.ts
        ├── router.tsx
        ├── <span class="dir">routes/</span>
        │   ├── __root.tsx         <span class="note"># Root HTML shell & nav providers</span>
        │   └── index.tsx          <span class="note"># Main dashboard entrypoint</span>
        ├── styles.css
        ├── App.jsx
        ├── <span class="dir">components/</span>
        │   ├── LiveIssueMap.jsx   <span class="note"># Leaflet civic heatmap</span>
        │   ├── SnapTagForm.jsx    <span class="note"># Report form with photo upload</span>
        │   ├── FundTrailTable.jsx <span class="note"># Financial audit ledger</span>
        │   ├── GamificationCard.jsx
        │   └── LeafletMap.jsx     <span class="note"># Client-only Leaflet wrapper</span>
        └── <span class="dir">services/</span>
            └── api.js             <span class="note"># API client for backend</span>
    </div>
  </section>

  <!-- ── GETTING STARTED ── -->
  <section class="section reveal" id="start">
    <div class="section-heading"><span class="icon">⚡</span> Getting Started</div>

    <h2>Prerequisites</h2>
    <p>Python 3.11+ · Node.js 20+ (or Bun) · Git</p>

    <h2>Backend Setup (FastAPI)</h2>
    <pre><span class="comment"># 1. Enter backend directory</span>
<span class="cmd">cd backend</span>

<span class="comment"># 2. Create and activate a virtual environment</span>
<span class="cmd">python3 -m venv venv && source venv/bin/activate</span>   <span class="comment"># macOS / Linux</span>
<span class="comment"># .\venv\Scripts\Activate.ps1                         # Windows PowerShell</span>

<span class="comment"># 3. Install dependencies</span>
<span class="cmd">pip install -r requirements.txt</span>

<span class="comment"># 4. (Optional) Download the spaCy language model</span>
<span class="cmd">python -m spacy download en_core_web_sm</span>

<span class="comment"># 5. Start the API server</span>
<span class="cmd">uvicorn app.main:app --reload --host 0.0.0.0 --port 8000</span>
<span class="note"># → API:     http://localhost:8000
# → Swagger: http://localhost:8000/docs
# → ReDoc:   http://localhost:8000/redoc</span></pre>

    <h2>Frontend Setup (TanStack Start / React)</h2>
    <pre><span class="comment"># 1. Enter frontend directory</span>
<span class="cmd">cd frontend</span>

<span class="comment"># 2. Install dependencies</span>
<span class="cmd">npm install</span>   <span class="comment"># or: bun install</span>

<span class="comment"># 3. Start the dev server</span>
<span class="cmd">npm run dev</span>   <span class="comment"># or: bun run dev</span>
<span class="note"># → http://localhost:3000</span></pre>
  </section>

  <!-- ── CONFIG ── -->
  <section class="section reveal" id="config">
    <div class="section-heading"><span class="icon">⚙️</span> Configuration &amp; Environment Variables</div>
    <p>Create a <code>backend/.env</code> file. Settings are loaded via Pydantic Settings (<code>backend/app/config.py</code>).</p>
    <table class="env-table">
      <thead><tr><th>Variable</th><th>Default</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td>DATABASE_URL</td><td>sqlite+aiosqlite:///./accountable.db</td><td>Async DB URI (use postgresql+asyncpg://… in production)</td></tr>
        <tr><td>DB_ECHO</td><td>False</td><td>Verbose SQLAlchemy SQL logging</td></tr>
        <tr><td>SMTP_HOST</td><td>""</td><td>SMTP relay server for escalation emails</td></tr>
        <tr><td>SMTP_PORT</td><td>587</td><td>SMTP port (587 for STARTTLS)</td></tr>
        <tr><td>SMTP_USE_TLS</td><td>True</td><td>TLS encryption for outgoing emails</td></tr>
        <tr><td>SMTP_USERNAME</td><td>""</td><td>SMTP authentication user</td></tr>
        <tr><td>SMTP_PASSWORD</td><td>""</td><td>SMTP authentication password</td></tr>
        <tr><td>SMTP_FROM_EMAIL</td><td>noreply@accountable.gov.in</td><td>Sender address for statutory escalations</td></tr>
        <tr><td>DEFAULT_WARD_OFFICER_EMAIL</td><td>ward.officer@municipality.gov.in</td><td>Default Tier 1 contact</td></tr>
        <tr><td>DEFAULT_MLA_EMAIL</td><td>mla.office@assembly.gov.in</td><td>Default Tier 2 contact</td></tr>
        <tr><td>DEFAULT_COLLECTOR_EMAIL</td><td>collector@district.gov.in</td><td>Default Tier 3 contact</td></tr>
        <tr><td>DEFAULT_STATE_AUTHORITY_EMAIL</td><td>grievance@state.gov.in</td><td>Default Tier 4 contact</td></tr>
        <tr><td>RTI_PDF_DIR</td><td>/tmp/accountable/rti_pdfs</td><td>Filesystem path for generated RTI PDFs</td></tr>
        <tr><td>DEFAULT_PIO_ADDRESS</td><td>The Public Information Officer…</td><td>Default PIO designation block for RTI filings</td></tr>
      </tbody>
    </table>
  </section>

  <!-- ── API ── -->
  <section class="section reveal" id="api">
    <div class="section-heading"><span class="icon">📡</span> API Reference</div>

    <div class="api-group">
      <h3>COMPLAINTS</h3>
      <div class="endpoint"><span class="method post">POST</span><span class="ep-path">/api/v1/complaints</span><span class="ep-desc">Submit a citizen complaint — triggers CV deduplication &amp; NLP tender match in background</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/v1/complaints</span><span class="ep-desc">Paginated complaint listings (filterable by status and ward)</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/v1/complaints/{id}</span><span class="ep-desc">Fetch detailed complaint record by ID</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="ep-path">/api/v1/complaints/{id}/deduplicate</span><span class="ep-desc">Manually trigger CV/spatial deduplication</span></div>
    </div>

    <div class="api-group">
      <h3>FUND FLOWS &amp; PFMS</h3>
      <div class="endpoint"><span class="method post">POST</span><span class="ep-path">/api/v1/fund-flows</span><span class="ep-desc">Ingest a PFMS fund disbursement or utilization record</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/v1/fund-flows</span><span class="ep-desc">List fund flows (filterable by project_id)</span></div>
    </div>

    <div class="api-group">
      <h3>CONTRACTORS &amp; SHELL COMPANY MAPPING</h3>
      <div class="endpoint"><span class="method post">POST</span><span class="ep-path">/api/v1/contractors</span><span class="ep-desc">Register contractor entity records</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/v1/contractors</span><span class="ep-desc">List registered contractors</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/v1/contractors/{id}/network</span><span class="ep-desc">Shell-company network graph via shared directors &amp; addresses</span></div>
    </div>

    <div class="api-group">
      <h3>ESCALATIONS &amp; RTI</h3>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/v1/escalations</span><span class="ep-desc">List historical escalation logs</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="ep-path">/api/v1/complaints/{id}/escalate</span><span class="ep-desc">Trigger next-tier escalation for a complaint</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="ep-path">/api/v1/complaints/{id}/rti</span><span class="ep-desc">Generate and download the statutory RTI petition PDF</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/v1/complaints/{id}/tender-matches</span><span class="ep-desc">NLP-matched tenders and contractor risk scores</span></div>
    </div>

    <div class="api-group">
      <h3>FRONTEND LIVE INTEGRATIONS</h3>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/issues/heatmap</span><span class="ep-desc">Real-time issue coordinates &amp; intensity weights for Leaflet map</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/gamification/me</span><span class="ep-desc">Current user civic score, rank &amp; badges (session-scoped)</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/api/gamification/{user_id}</span><span class="ep-desc">Civic score profile for a specific user ID</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="ep-path">/health</span><span class="ep-desc">Health &amp; liveness probe</span></div>
    </div>
  </section>

  <!-- ── ROADMAP ── -->
  <section class="section reveal" id="roadmap">
    <div class="section-heading"><span class="icon">🗺️</span> Roadmap</div>
    <div class="roadmap-item">
      <div class="ri-checkbox"></div>
      <div>
        <h4>Low-Bandwidth Channels</h4>
        <p>WhatsApp &amp; Telegram bots for filing reports without requiring browser access.</p>
      </div>
    </div>
    <div class="roadmap-item">
      <div class="ri-checkbox"></div>
      <div>
        <h4>Multilingual Voice Reporting</h4>
        <p>Speech-to-text intake in regional languages — Kannada, Hindi, Urdu, Tamil.</p>
      </div>
    </div>
    <div class="roadmap-item">
      <div class="ri-checkbox"></div>
      <div>
        <h4>Satellite &amp; Drone Change Detection</h4>
        <p>Cross-verifying road and drainage completion using Sentinel-2 imagery and drone ortho-mosaics.</p>
      </div>
    </div>
    <div class="roadmap-item">
      <div class="ri-checkbox"></div>
      <div>
        <h4>Public Blockchain Notarization</h4>
        <p>Immutable cryptographic anchoring of tender disbursements to prevent back-dated accounting tampering.</p>
      </div>
    </div>
    <div class="roadmap-item">
      <div class="ri-checkbox"></div>
      <div>
        <h4>Open Data Export</h4>
        <p>Bulk export in standard CKAN format for investigative civic journalists and transparency NGOs.</p>
      </div>
    </div>
  </section>

  <!-- ── CONTRIBUTING ── -->
  <section class="section reveal" id="contributing">
    <div class="section-heading"><span class="icon">🤝</span> Contributing</div>
    <p>Contributions are welcome from civic hackers, urban planners, designers, and developers!</p>
    <div class="steps">
      <div class="step"><div class="step-num">1</div><div class="step-body"><h4>Fork the repository</h4><p>Click <strong>Fork</strong> on GitHub to create your own copy.</p></div></div>
      <div class="step"><div class="step-num">2</div><div class="step-body"><h4>Create your feature branch</h4><pre style="margin:6px 0;padding:10px 14px;font-size:.78rem"><span class="cmd">git checkout -b feat/my-new-feature</span></pre></div></div>
      <div class="step"><div class="step-num">3</div><div class="step-body"><h4>Commit your changes</h4><pre style="margin:6px 0;padding:10px 14px;font-size:.78rem"><span class="cmd">git commit -m "feat: add WhatsApp webhook handler"</span></pre></div></div>
      <div class="step"><div class="step-num">4</div><div class="step-body"><h4>Push and open a Pull Request</h4><pre style="margin:6px 0;padding:10px 14px;font-size:.78rem"><span class="cmd">git push origin feat/my-new-feature</span></pre></div></div>
    </div>
  </section>

  <!-- ── LICENSE ── -->
  <section class="section reveal" id="license">
    <div class="section-heading"><span class="icon">📄</span> License</div>
    <p>This project is licensed under the <strong><a href="https://opensource.org/licenses/MIT" target="_blank">MIT License</a></strong>.</p>
  </section>

</div>

<footer>
  Built with dedication for open governance, civic empowerment, and public accountability. <span class="flag">🇮🇳</span><br>
  <span style="color:rgba(139,148,158,.4); font-size:.75rem; margin-top:6px; display:block">Accountable · MIT License · Pilot: Bhatkal, Karnataka</span>
</footer>

<script>
  // Scroll reveal
  const reveals = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.08 });
  reveals.forEach(el => io.observe(el));

  // Escalation step stagger animation
  document.querySelectorAll('.esc-step').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(-12px)';
    el.style.transition = `opacity .4s ${i * .12}s ease, transform .4s ${i * .12}s ease`;
    const stepIo = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { el.style.opacity = '1'; el.style.transform = 'none'; stepIo.unobserve(el); }
    }, { threshold: 0.2 });
    stepIo.observe(el);
  });

  // Feature card stagger
  document.querySelectorAll('.feature-card').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(16px)';
    el.style.transition = `opacity .4s ${i * .07}s ease, transform .4s ${i * .07}s ease, border-color .2s, box-shadow .2s`;
    const cio = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { el.style.opacity = '1'; el.style.transform = 'translateY(0)'; cio.unobserve(el); }
    }, { threshold: 0.1 });
    cio.observe(el);
  });
</script>
</body>
</html>

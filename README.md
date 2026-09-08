<div align="center">

`🇮🇳 Pilot · Bhatkal, Karnataka`

# 🏛️ Accountable

**Civic Transparency & Public Audit Platform — From Sanction to Verification.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61dafb?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178c6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38b2ac?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00?style=flat-square)](https://www.sqlalchemy.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-f0883e?style=flat-square)](https://opensource.org/licenses/MIT)

</div>

---

> **📝 Changelog from README review:**
> * Fixed duplicate nested path `frontend/frontend/src/` → correct path is `frontend/src/`
> * Unified gamification API: `GET /api/gamification/me` (architecture diagram) aligned with `GET /api/gamification/{user_id}` (API reference) — both documented now
> * Fixed config.py comment: *"Pydantic 12-factor configuration"* → *"Pydantic Settings (12-factor)"*
> * Added missing [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model link in NLP feature section

---

### Table of Contents
* [Overview](#-overview)
* [Key Features](#-key-features)
* [Escalation Matrix & SLAs](#-escalation-matrix--slas)
* [Tech Stack](#-tech-stack)
* [Repository Structure](#-repository-structure)
* [Getting Started](#-getting-started)
* [Configuration & Environment Variables](#️-configuration--environment-variables)
* [API Reference](#-api-reference)
* [Roadmap](#️-roadmap)
* [Contributing](#-contributing)
* [License](#-license)

---

### 🌟 Overview

**Accountable** is an open-source civic governance and infrastructure tracking platform designed to bridge the chasm between sanctioned public funds and ground-level municipal reality.

In many developing municipalities, public grievances disappear into administrative black holes, contractors win tenders through undisclosed shell networks, and sanctioned funds show up as "utilized" while potholes, leaking water mains, and broken streetlights persist for years.

> **Accountable transforms passive citizens into active civic auditors** — combining computer vision, NLP, and automated legal pipelines to hold public bodies accountable from the moment a grievance is filed to on-site resolution verification.

---

### 🚀 Key Features

* **🗺️ Live Issue Heatmap:** Leaflet-powered interactive map with real-time civic issues color-coded by severity, category, and ward. Dynamic popups link directly to fund audit records.
* **📸 Snap & Tag Reporting:** Mobile-friendly citizen reporting with automatic GPS tagging, ward selector, categorical tagging, and instant tracking reference IDs.
* **👁️ CV Deduplication Engine:** 3-stage pipeline: Haversine distance filtering (500m radius), OpenCV ORB keypoint matching on photos, and TF-IDF cosine similarity fallback. Duplicates above 0.75 score are linked, not cluttered.
* **🔍 NLP Tender Matcher:** Links citizen complaints to official procurement tenders using spaCy NER, YAKE keyword extraction, and [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) dense embeddings.
* **🕸️ Shell Company Intelligence:** Relational mapping of contractor networks via shared directorships and registered addresses. Flags ghost entities and suspicious bidding rings.
* **📜 Auto RTI PDF Generation:** If an issue remains unresolved after 14 days, a legally compliant RTI petition PDF is auto-generated via ReportLab + Jinja2, pre-filled with PIO details and statutory questions.
* **💰 Public Fund Trail Audit:** Full financial transparency ledger: Sanctioned → Released → Utilized. PFMS transaction-level fund-flow records with discrepancy flags.
* **🏆 Civic Gamification:** Engagement through milestones: *First Snap*, *Pothole Patrol*, *Fund Sleuth*, *Ward Champion*. Progressive ranks, ward leaderboards and civic impact scores.

---

### 📊 Escalation Matrix & SLAs

When a citizen reports an issue, the clock starts immediately. Unresolved grievances automatically advance through authority tiers:

* `T1` **Ward Officer** — Day 0 – Day 3 (72 hours)
* `T2` **MLA — Member of Legislative Assembly** — Day 3 – Day 5 (120 hours)
* `T3` **District Collector** — Day 5 – Day 7 (168 hours)
* `T4` **State Vigilance Authority** — Day 7 – Day 14 (240 hours)
* `📜` **Automated RTI Application Generated & Dispatched** — Day 14 (336 hours) — *if still unresolved*

---

### 💻 Tech Stack

#### Backend
| Component | Technology | Description |
| :--- | :--- | :--- |
| Framework | [FastAPI](https://fastapi.tiangolo.com) | High-performance asynchronous REST API |
| ORM & Database | [SQLAlchemy 2.0 Async](https://www.sqlalchemy.org) | Async ORM with SQLite (aiosqlite) / PostgreSQL (asyncpg) |
| Data Validation | [Pydantic v2](https://docs.pydantic.dev) | Schema enforcement & settings management |
| Computer Vision | [OpenCV](https://opencv.org) + [scikit-learn](https://scikit-learn.org) | ORB feature detection, descriptor matching & TF-IDF |
| NLP & Semantics | [Sentence-Transformers](https://www.sbert.net) + [spaCy](https://spacy.io) + [YAKE](https://github.com/LIAAD/yake) | Semantic embeddings, NER & keyword extraction |
| PDF Generation | [ReportLab](https://www.reportlab.com) + [Jinja2](https://jinja.palletsprojects.com) | Programmatic legal RTI petition PDF generation |
| Server | [Uvicorn](https://www.uvicorn.org) | Lightning-fast ASGI web server |

#### Frontend
| Component | Technology | Description |
| :--- | :--- | :--- |
| Meta-Framework | [TanStack Start](https://tanstack.com/start) / [Vite](https://vitejs.dev) | SSR & client routing platform |
| UI Library | [React 19](https://react.dev) | Modern component-based view layer |
| Language | [TypeScript](https://www.typescriptlang.org) | Strict type safety |
| Styling | [Tailwind CSS v4](https://tailwindcss.com) | Utility-first responsive design |
| Components | [Radix UI](https://www.radix-ui.com) | Accessible, unstyled primitives |
| Maps | [Leaflet](https://leafletjs.com) + [React-Leaflet](https://react-leaflet.js.org) | Interactive geospatial heatmaps & ward overlays |
| Icons | [Lucide React](https://lucide.dev) | Clean, consistent UI iconography |

---

### 📁 Repository Structure

```text
accountable/
├── README.md
├── backend/
│   ├── accountable.db              # Local SQLite DB (dev)
│   ├── requirements.txt
│   └── app/
│       ├── config.py               # Pydantic Settings (12-factor)
│       ├── crud.py                 # Database operations & queries
│       ├── main.py                 # Entrypoint & REST routes
│       ├── schemas.py              # Pydantic request/response schemas
│       ├── database/
│       │   ├── db.py               # Async session factory & table init
│       │   └── models.py           # SQLAlchemy ORM models & relations
│       └── services/
│           ├── cv_deduplication.py   # Spatial & OpenCV deduplication
│           ├── escalation_worker.py  # SLA tracker & authority emails
│           ├── nlp_tender_match.py   # spaCy/Transformer matcher
│           └── rti_pdf_gen.py        # Auto RTI PDF generator
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/                        # ← corrected path (was frontend/frontend/src/)
        ├── routeTree.gen.ts
        ├── router.tsx
        ├── routes/
        │   ├── __root.tsx          # Root HTML shell & nav providers
        │   └── index.tsx           # Main dashboard entrypoint
        ├── styles.css
        ├── App.jsx
        ├── components/
        │   ├── LiveIssueMap.jsx    # Leaflet civic heatmap
        │   ├── SnapTagForm.jsx     # Report form with photo upload
        │   ├── FundTrailTable.jsx  # Financial audit ledger
        │   ├── GamificationCard.jsx
        │   └── LeafletMap.jsx      # Client-only Leaflet wrapper
        └── services/
            └── api.js              # API client for backend

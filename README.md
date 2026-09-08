# 🏛️ Accountable — Civic Transparency & Public Audit Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_(Async)-D71F00.svg?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **From Sanction to Verification:** Bringing complete public transparency to civic infrastructure, public financial management (PFMS), contractor accountability, and citizen grievances.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
  - [1. Live Issue Heatmap & Geo-Tracking](#1-live-issue-heatmap--geo-tracking)
  - [2. "Snap & Tag" Citizen Reporting](#2-snap--tag-citizen-reporting)
  - [3. Computer Vision (CV) Deduplication Engine](#3-computer-vision-cv-deduplication-engine)
  - [4. NLP Procurement & Tender Matcher](#4-nlp-procurement--tender-matcher)
  - [5. Shell-Company & Contractor Risk Intelligence](#5-shell-company--contractor-risk-intelligence)
  - [6. SLA-Driven Multi-Tier Escalation Pipeline](#6-sla-driven-multi-tier-escalation-pipeline)
  - [7. Automated Day-14 RTI PDF Generation](#7-automated-day-14-rti-pdf-generation)
  - [8. Public Fund Trail Audit](#8-public-fund-trail-audit)
  - [9. Civic Gamification & Community Impact](#9-civic-gamification--community-impact)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup (FastAPI)](#backend-setup-fastapi)
  - [Frontend Setup (TanStack Start / React)](#frontend-setup-tanstack-start--react)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [API Reference](#-api-reference)
- [Escalation Matrix & SLAs](#-escalation-matrix--slas)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Accountable** is an open-source civic governance and infrastructure tracking platform designed to bridge the chasm between sanctioned public funds and ground-level municipal reality.

In many developing municipalities, public grievances disappear into administrative black holes, contractors win tenders through undisclosed shell networks, and sanctioned funds show up as "utilized" while potholes, leaking water mains, and broken streetlights persist for years.

**Accountable transforms passive citizens into active civic auditors by:**
1. Allowing citizens to report civic failures with geo-stamped photos.
2. Deduplicating submissions automatically via computer vision (OpenCV ORB) and spatial clustering to prevent administrative clutter.
3. Semantically matching citizen grievances to official government procurement tenders using natural language processing (spaCy & SentenceTransformers).
4. Mapping contractor networks to identify conflicts of interest and shell companies.
5. Escalating unresolved complaints across municipal, legislative, and district authorities on strict SLAs.
6. Automatically drafting legal Right to Information (RTI) petitions when civic bodies fail to act within 14 days.
7. Providing a transparent, public fund trail from initial government sanction to final on-site verification.

*Pilot deployment focused on Bhatkal, Karnataka, India.*

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend (TanStack Start / React 19)"]
        UI[User Interface / Leaflet Map]
        SnapForm[Snap & Tag Report Form]
        FundTable[Public Fund Trail Table]
        GamerCard[Civic Score & Gamification]
    end

    subgraph API["FastAPI Backend (Async)"]
        Router[FastAPI REST Router & Middlewares]
        CRUD[SQLAlchemy Async CRUD Layer]
        DB[(SQLite / PostgreSQL DB)]
    end

    subgraph Background["AI / ML & Automation Workers"]
        CV[CV Deduplication\n- Haversine Distance (<500m)\n- OpenCV ORB Keypoints\n- TF-IDF Text Cosine]
        NLP[NLP Tender Matcher\n- spaCy NER\n- YAKE Keywords\n- all-MiniLM-L6-v2 Embeddings]
        Shell[Contractor Network & Shell Detector\n- Shared Directors\n- Registered Addresses]
        Escalator[Escalation Worker\n- 72h: Ward Officer\n- 120h: MLA\n- 168h: Collector\n- 240h: State Auth]
        RTI[RTI PDF Generator\n- Day-14 Auto-Trigger\n- ReportLab + Jinja2 Legal PDF]
    end

    UI -->|GET /api/issues/heatmap| Router
    GamerCard -->|GET /api/gamification/me| Router
    FundTable -->|GET /api/v1/fund-flows| Router
    SnapForm -->|POST /api/v1/complaints| Router

    Router --> CRUD --> DB
    Router -.->|Background Task| CV
    Router -.->|Background Task| NLP
    CV --> DB
    NLP --> DB
    Shell --> DB
    Escalator --> DB
    RTI --> DB
```

---

## 🚀 Key Features

### 1. Live Issue Heatmap & Geo-Tracking
- Interactive Leaflet-powered map displaying real-time civic issues.
- Points color-coded by severity, category (Pothole, Drainage, Garbage, Water Leak, Streetlight, Encroachment), and municipal ward.
- Dynamic popups with issue status, live photos, and direct links to audited fund allocations.

### 2. "Snap & Tag" Citizen Reporting
- Simple, mobile-friendly reporting interface.
- Automatic GPS tagging with fallback manual coordinate entry.
- Ward selector and categorical tagging with rich description input.
- Instant submission feedback with live tracking reference IDs.

### 3. Computer Vision (CV) Deduplication Engine
Municipalities often receive hundreds of duplicate complaints for the same prominent pothole or broken pipe. Accountable solves this using an automated 3-stage deduplication pipeline:
- **Geographic Radius Filter**: Computes Haversine distance between incidents (`GEO_RADIUS_METRES = 500m`).
- **Visual Keypoint Matching**: Employs OpenCV ORB (Oriented FAST and Rotated BRIEF) feature extraction and Lowe's ratio test on attached incident photos.
- **Textual Fallback**: TF-IDF vectorization with cosine similarity matching on complaint descriptions when photos are absent or unclear.
- High-confidence duplicates (`score >= 0.75`) are linked to the primary complaint to aggregate citizen upvotes without cluttering the workflow.

### 4. NLP Procurement & Tender Matcher
Links free-form citizen complaints with official municipal procurement tenders:
- **Entity & Keyword Extraction**: Uses spaCy Named Entity Recognition (NER) and YAKE keyword extraction.
- **Dense Vector Semantic Matching**: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to encode complaints and tender descriptions into high-dimensional embeddings for cosine similarity matching.
- Highlights whether an active or completed tender already covers the reported location.

### 5. Shell-Company & Contractor Risk Intelligence
- Relational mapping of contractors, corporate registration records, and shared directorships (`ContractorDirector`).
- Flags suspicious bidding rings, ghost entities, and high-risk vendors winning bids across overlapping wards without past delivery records.

### 6. SLA-Driven Multi-Tier Escalation Pipeline
Unresolved grievances automatically advance through authority tiers based on pre-defined Service Level Agreements (SLAs):
- **Tier 1 (Ward Officer)**: 72 hours (3 days)
- **Tier 2 (MLA - Member of Legislative Assembly)**: 120 hours (5 days)
- **Tier 3 (District Collector)**: 168 hours (7 days)
- **Tier 4 (State Authority / Vigilance)**: 240 hours (10 days)
- Sends automated, formal escalation notices via SMTP to official authority email inboxes with direct case tracking links.

### 7. Automated Day-14 RTI PDF Generation
- If a legitimate civic issue remains unaddressed after **14 days**, the system automatically generates a formatted, legally compliant **Right to Information (RTI) application PDF**.
- Built with **ReportLab** and **Jinja2**, adhering to standard Indian RTI petition formats.
- Pre-fills Public Information Officer (PIO) address details, project sanction codes, tender disbursement anomalies, and structured statutory questions.
- Ready for one-click citizen download and submission.

### 8. Public Fund Trail Audit
- Complete financial transparency ledger tracking projects through each fiscal stage:
  - `Sanctioned Amount` ➔ `Released Amount` ➔ `Utilized Amount`.
  - Transaction-level fund-flow records (PFMS integration).
  - Status indicators: Verified On-Ground, Pending Inspection, Discrepancy Flagged.

### 9. Civic Gamification & Community Impact
- Encourages continuous civic engagement through recognized milestones:
  - **Badges**: *First Snap*, *Pothole Patrol*, *Fund Sleuth*, *Ward Champion*, *Civic Marathon*.
  - **Civic Levels**: Progressive ranks (e.g., *Ward Watchdog*).
  - Ward-level rankings and citizen impact scoreboards.

---

## 💻 Tech Stack

### Backend
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com) | High-performance asynchronous REST API |
| **ORM & Database** | [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org) | Async ORM with SQLite (aiosqlite) / PostgreSQL (asyncpg) |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev) | Schema enforcement & settings management |
| **Computer Vision** | [OpenCV](https://opencv.org) + [scikit-learn](https://scikit-learn.org) | ORB feature detection, descriptor matching & TF-IDF |
| **NLP & Semantics** | [Sentence-Transformers](https://www.sbert.net) + [spaCy](https://spacy.io) + [YAKE](https://github.com/LIAAD/yake) | Semantic embeddings, NER & keyword extraction |
| **PDF Generation** | [ReportLab](https://www.reportlab.com) + [Jinja2](https://jinja.palletsprojects.com) | Programmatic legal RTI petition PDF generation |
| **Server** | [Uvicorn](https://www.uvicorn.org) | Lightning-fast ASGI web server |

### Frontend
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Meta-Framework** | [TanStack Start](https://tanstack.com/start) / [Vite](https://vitejs.dev) | SSR & client routing platform |
| **UI Library** | [React 19](https://react.dev) | Modern component-based view layer |
| **Language** | [TypeScript](https://www.typescriptlang.org) | Strict type safety |
| **Styling** | [Tailwind CSS v4](https://tailwindcss.com) | Utility-first responsive design |
| **Components** | [Radix UI](https://www.radix-ui.com) | Accessible, unstyled primitives |
| **Maps** | [Leaflet](https://leafletjs.com) + [React-Leaflet](https://react-leaflet.js.org) | Interactive geospatial heatmaps & ward overlays |
| **Icons** | [Lucide React](https://lucide.dev) | Clean, consistent UI iconography |

---

## 📁 Repository Structure

```
accountable/
├── README.md                          # Repository documentation & guide
├── backend/                           # FastAPI backend application
│   ├── accountable.db                 # Local SQLite database (development)
│   ├── requirements.txt               # Python package dependencies
│   └── app/
│       ├── __init__.py
│       ├── config.py                  # Pydantic 12-factor configuration
│       ├── crud.py                    # Database operations & queries
│       ├── main.py                    # Application entrypoint & REST routes
│       ├── schemas.py                 # Pydantic request/response schemas
│       ├── database/
│       │   ├── __init__.py
│       │   ├── db.py                  # Async session factory & table initializers
│       │   └── models.py              # SQLAlchemy ORM models & entity relations
│       └── services/
│           ├── __init__.py
│           ├── cv_deduplication.py    # Spatial & OpenCV image deduplication
│           ├── escalation_worker.py   # SLA time-tracker & authority notification
│           ├── nlp_tender_match.py    # spaCy/Transformer procurement matcher
│           └── rti_pdf_gen.py         # Automated RTI petition PDF generator
│
└── frontend/                          # React + TanStack application
    ├── package.json                   # Node.js dependencies & scripts
    ├── vite.config.ts                 # Vite bundler configuration
    ├── tsconfig.json                  # TypeScript compiler settings
    ├── src/
    │   ├── routeTree.gen.ts           # Generated route hierarchy
    │   ├── router.tsx                 # TanStack Router configuration
    │   ├── routes/                    # File-based application routes
    │   │   ├── __root.tsx             # Root HTML shell & navigation providers
    │   │   └── index.tsx              # Main dashboard entrypoint
    │   └── styles.css                 # Global CSS & Tailwind definitions
    └── frontend/src/                  # Core frontend implementation
        ├── App.jsx                    # Application view switcher & header layout
        ├── components/
        │   ├── LiveIssueMap.jsx       # Interactive Leaflet civic heatmap
        │   ├── SnapTagForm.jsx        # Issue reporting form with photo upload
        │   ├── FundTrailTable.jsx     # Financial audit & project ledger
        │   ├── GamificationCard.jsx   # Civic score, badges & impact status
        │   └── LeafletMap.jsx         # Client-only Leaflet wrapper
        └── services/
            └── api.js                 # API client for backend communication
```

---

## ⚡ Getting Started

### Prerequisites
- **Python 3.11+** installed (`python --version`)
- **Node.js 20+** or **Bun** installed (`node --version` / `bun --version`)
- **Git** installed

---

### Backend Setup (FastAPI)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. *(Optional)* **Download the spaCy language model** for enhanced NLP extraction:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure environment variables**:
   Create a `.env` file in the `backend/` directory (see [Configuration](#-configuration--environment-variables)).

6. **Start the API server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The API will be available at `http://localhost:8000`.
   - Interactive Swagger Docs: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`

---

### Frontend Setup (TanStack Start / React)

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or with bun
   bun install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   # or with bun
   bun run dev
   ```

4. **Access the application**:
   Open [http://localhost:3000](http://localhost:3000) (or the port specified in terminal output) in your browser.

---

## ⚙️ Configuration & Environment Variables

The backend loads settings via Pydantic (`backend/app/config.py`). You can create a `backend/.env` file with the following keys:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./accountable.db` | Async database URI (`postgresql+asyncpg://...` for production) |
| `DB_ECHO` | `False` | Enable verbose SQLAlchemy SQL logging |
| `SMTP_HOST` | `""` | SMTP relay server for escalation email dispatches |
| `SMTP_PORT` | `587` | SMTP port (e.g., 587 for STARTTLS) |
| `SMTP_USE_TLS` | `True` | Enable TLS encryption for outgoing emails |
| `SMTP_USERNAME` | `""` | SMTP authentication user |
| `SMTP_PASSWORD` | `""` | SMTP authentication password |
| `SMTP_FROM_EMAIL` | `noreply@accountable.gov.in` | Sender email address for statutory escalations |
| `DEFAULT_WARD_OFFICER_EMAIL` | `ward.officer@municipality.gov.in` | Default contact for Tier 1 escalations |
| `DEFAULT_MLA_EMAIL` | `mla.office@assembly.gov.in` | Default contact for Tier 2 escalations |
| `DEFAULT_COLLECTOR_EMAIL` | `collector@district.gov.in` | Default contact for Tier 3 escalations |
| `DEFAULT_STATE_AUTHORITY_EMAIL`| `grievance@state.gov.in` | Default contact for Tier 4 escalations |
| `RTI_PDF_DIR` | `/tmp/accountable/rti_pdfs` | Filesystem path where generated RTI PDFs are stored |
| `DEFAULT_PIO_ADDRESS` | `The Public Information Officer...` | Default PIO designation block for RTI filings |

---

## 📡 API Reference

### Complaints API
- `POST /api/v1/complaints` — Submit a citizen complaint (triggers CV deduplication & NLP tender match in background).
- `GET /api/v1/complaints` — Paginated complaint listings (filterable by status and ward).
- `GET /api/v1/complaints/{id}` — Fetch detailed complaint record by ID.
- `POST /api/v1/complaints/{id}/deduplicate` — Manually trigger CV/spatial deduplication.

### Fund Flows & PFMS
- `POST /api/v1/fund-flows` — Ingest a PFMS fund disbursement or utilization record.
- `GET /api/v1/fund-flows` — List fund flows (filterable by `project_id`).

### Contractors & Shell Company Mapping
- `POST /api/v1/contractors` — Register contractor entity records.
- `GET /api/v1/contractors` — List registered contractors.
- `GET /api/v1/contractors/{id}/network` — Retrieve shell-company network graph based on shared directors & addresses.

### Escalations & RTI
- `GET /api/v1/escalations` — List historical escalation logs.
- `POST /api/v1/complaints/{id}/escalate` — Trigger next-tier escalation for a complaint.
- `POST /api/v1/complaints/{id}/rti` — Generate and download the statutory RTI petition PDF.
- `GET /api/v1/complaints/{id}/tender-matches` — Retrieve NLP-matched tenders and contractor risks.

### Frontend Live Integrations
- `GET /api/issues/heatmap` — Real-time issue coordinates and intensity weights for Leaflet map.
- `GET /api/gamification/{user_id}` — Citizen civic score profile, ranks, and earned badges.
- `GET /health` — Health and liveness probe.

---

## 📊 Escalation Matrix & SLAs

When a citizen reports an issue, the clock begins ticking immediately:

```
[Issue Reported]
       │
       ▼ (Day 0)
 Tier 1: Ward Officer ───────────► Resolved? ──► [Issue Closed]
       │
       ▼ (Day 3 / 72 Hours)
 Tier 2: MLA Office ─────────────► Resolved? ──► [Issue Closed]
       │
       ▼ (Day 5 / 120 Hours)
 Tier 3: District Collector ─────► Resolved? ──► [Issue Closed]
       │
       ▼ (Day 7 / 168 Hours)
 Tier 4: State Vigilance Authority
       │
       ▼ (Day 14 / 336 Hours)
 📜 Automated Legal RTI Application Generated & Dispatched
```

---

## 🗺️ Roadmap

- [ ] **Low-Bandwidth Channels**: WhatsApp & Telegram bots for filing reports without requiring browser access.
- [ ] **Multilingual Voice Reporting**: Speech-to-text intake in regional languages (Kannada, Hindi, Urdu, Tamil).
- [ ] **Satellite & Drone Change Detection**: Cross-verifying road and drainage completion using Sentinel-2 and drone ortho-mosaics.
- [ ] **Public Blockchain Notarization**: Immutable cryptographic anchoring of tender disbursements to prevent back-dated accounting tampering.
- [ ] **Open Data Export**: Bulk export in standard CKAN format for investigative civic journalists and transparency NGOs.

---

## 🤝 Contributing

Contributions are welcome from civic hackers, urban planners, designers, and developers!

1. **Fork the repository**.
2. **Create your feature branch**:
   ```bash
   git checkout -b feat/my-new-feature
   ```
3. **Commit your changes**:
   ```bash
   git commit -m "feat: add WhatsApp webhook handler"
   ```
4. **Push to the branch**:
   ```bash
   git push origin feat/my-new-feature
   ```
5. **Open a Pull Request**.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with dedication for open governance, civic empowerment, and public accountability. 🇮🇳
</p>

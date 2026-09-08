<div align="center">

`🇮🇳 Pilot Deployment · Bhatkal, Karnataka, India`

# 🏛️ Accountable
### Civic Transparency & Public Audit Platform — From Sanction to Verification

Bringing radical public transparency to civic infrastructure, public financial management (PFMS), contractor accountability, and citizen grievances.

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-38B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_(Async)-D71F00.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-f0883e.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

> **📝 Changelog & Repository Fixes Applied:**
> * **Fixed Nested Directory Path:** Resolved duplicate path `frontend/frontend/src/` down to `frontend/src/`.
> * **Unified Gamification Routes:** Documented and synchronized both session context (`GET /api/gamification/me`) and user-specific lookup (`GET /api/gamification/{user_id}`).
> * **12-Factor Settings Annotation:** Standardized `backend/app/config.py` as *Pydantic Settings (12-Factor)*.
> * **Linked NLP Semantic Model:** Linked Hugging Face model repository for [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).

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
- [Escalation Matrix & SLAs](#-escalation-matrix--slas)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup (FastAPI)](#backend-setup-fastapi)
  - [Frontend Setup (TanStack Start / React)](#frontend-setup-tanstack-start--react)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [API Reference](#-api-reference)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Accountable** is an open-source civic governance and infrastructure tracking platform engineered to bridge the gap between sanctioned public funds and ground-level municipal reality.

In many developing municipalities, public grievances disappear into administrative black holes, contractors win tenders through undisclosed shell networks, and sanctioned funds show up as "utilized" while potholes, leaking water mains, and broken streetlights persist for years.

> **Accountable transforms passive citizens into active civic auditors** — combining computer vision, natural language processing, and automated statutory legal pipelines to hold municipal bodies accountable from the moment a grievance is filed to on-site resolution verification.

### Core Pillars
1. **Field Auditing:** Citizens capture civic failures with GPS and timestamp validation.
2. **Automated Deduplication:** OpenCV ORB keypoints and spatial clustering stop administrative queue bloat.
3. **Procurement Cross-Auditing:** Grievances match directly to sanctioned municipal contracts using semantic vector search.
4. **Shell Company Intelligence:** Shared addresses and director networks surface collusive bidding rings.
5. **Hard SLA Escalations:** Strict statutory countdown timers escalate unaddressed complaints through authority tiers.
6. **Programmatic RTI Petitions:** Auto-generates ready-to-file legal Right to Information (RTI) petitions when SLAs lapse.
7. **Fund-Flow Traceability:** Audits financial disbursements across `Sanctioned` ➔ `Released` ➔ `Utilized`.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Layer (TanStack Start / React 19)"]
        UI[User Interface / Leaflet Map]
        SnapForm[Snap & Tag Report Form]
        FundTable[Public Fund Trail Table]
        GamerCard[Civic Score & Gamification]
    end

    subgraph API["FastAPI Asynchronous Gateway"]
        Router[FastAPI REST Router & Middlewares]
        CRUD[SQLAlchemy 2.0 Async CRUD Layer]
        DB[(SQLite / PostgreSQL DB)]
    end

    subgraph Background["AI / ML & Automation Workers"]
        CV[CV Deduplication Engine\n- Haversine Distance <500m\n- OpenCV ORB Keypoint Matching\n- TF-IDF Text Cosine Fallback]
        NLP[NLP Tender Matcher\n- spaCy NER & YAKE Keywords\n- all-MiniLM-L6-v2 Embeddings]
        Shell[Contractor Network Detector\n- Shared Directorships\n- Registered Entity Addresses]
        Escalator[Escalation Worker\n- 72h: Ward Officer\n- 120h: MLA\n- 168h: Collector\n- 240h: State Auth]
        RTI[RTI PDF Generator\n- Day-14 Auto-Trigger\n- ReportLab + Jinja2 Templates]
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
🚀 Key Features1. Live Issue Heatmap & Geo-TrackingGeospatial Visualization: Interactive Leaflet-powered map displaying active civic issues in real-time.Granular Filtering: Color-coded by severity, status, category (Pothole, Drainage, Garbage, Water Leak, Streetlight, Encroachment), and municipal ward.Audit-Linked Popups: Dynamic map cards connect issues directly to municipal fund allocation records.2. "Snap & Tag" Citizen ReportingStreamlined Intake: Lightweight, mobile-first issue submission interface.Automated Geolocation: High-accuracy browser GPS capture with fallback manual pin placement.Categorization Engine: Ward selection, category tagging, and multi-photo file uploads.Instant Verification: Issues receive immediate public tracking IDs upon submission.3. Computer Vision (CV) Deduplication EngineMunicipalities often receive hundreds of redundant complaints for the same prominent pothole or broken pipe. Accountable filters redundancy through a 3-stage pipeline:Spatial Gatekeeper: Computes Haversine distance between incidents (GEO_RADIUS_METRES = 500m).Visual Keypoint Matching: Employs OpenCV ORB (Oriented FAST and Rotated BRIEF) extraction with Lowe's ratio test on attached photos.Textual Fallback: Evaluates TF-IDF vector cosine similarity across report descriptions when photos are ambiguous or absent.Consolidation: High-confidence matches (score >= 0.75) merge into an existing parent ticket, incrementing an upvote counter instead of creating duplicates.4. NLP Procurement & Tender MatcherDirectly connects unstructured citizen complaints to public procurement tenders:Entity & Keyword Extraction: spaCy Named Entity Recognition (NER) paired with YAKE keyword extraction processes raw complaint text.Semantic Embeddings: Uses sentence-transformers/all-MiniLM-L6-v2 to map complaints and published tender documents into a shared vector space.Discrepancy Detection: Identifies whether active or recently billed contracts encompass the defective location.5. Shell-Company & Contractor Risk IntelligenceNetwork Graphing: Relational mapping linking contractors, registration IDs, and shared board members (ContractorDirector).Collusion Alerts: Flags shell entities, common bidding addresses, and vendors winning bids across overlapping jurisdictions without verified equipment or past execution records.6. SLA-Driven Multi-Tier Escalation PipelineUnresolved grievances advance through a statutory chain of responsibility using rigid countdown timers:Dispatches templated, automated notices to verified administrative email addresses.Surfaces ticket history, photo proofs, and time elapsed to hold each administrative tier accountable.7. Automated Day-14 RTI PDF GenerationIf an issue remains unaddressed after 14 days (336 hours), the system auto-compiles a legally valid Right to Information (RTI) application PDF.Engineered using ReportLab and Jinja2, matching statutory Indian RTI formats.Pre-populates the competent Public Information Officer (PIO) address, project tender codes, fiscal discrepancies, and structured statutory interrogatories.Ready for one-click citizen download, digital signing, or physical postal dispatch.8. Public Fund Trail AuditFull ledger tracing funds through fiscal checkpoints: Sanctioned Amount ➔ Released Amount ➔ Utilized Amount.Transaction-level fund flows integrated with Public Financial Management System (PFMS) data standards.Automated flags for cost overruns, idle funds, and incomplete work marked as complete.9. Civic Gamification & Community ImpactBadges: Earn recognition (First Snap, Pothole Patrol, Fund Sleuth, Ward Champion, Civic Marathon).Ranks: Tiered citizen ranks based on verified reporting accuracy and community audits (e.g., Ward Watchdog).Ward Leaderboards: Visual rankings highlighting the most active civic auditors by neighbourhood.📊 Escalation Matrix & SLAsWhen a citizen reports an issue, the accountability countdown begins immediately:Plaintext[Issue Reported]
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
TierAuthority LevelSLA WindowEscalation ChannelAction RequiredT1Ward OfficerDay 0 – Day 3 (72h)Municipal Notification & EmailDirect site inspection & initial contractor noticeT2MLA (Member of Legislative Assembly)Day 3 – Day 5 (120h)Legislative Constituency Office AlertAdministrative inquiry & ward-level reviewT3District CollectorDay 5 – Day 7 (168h)District Grievance Cell NoticeDepartmental audit & executive compliance noticeT4State Vigilance AuthorityDay 7 – Day 14 (240h)Anti-Corruption & Vigilance IngestionIngestion into state anti-corruption audit queueRTIPublic Information Officer (PIO)Day 14 (336h)Auto-Generated Legal PetitionStatutory Section 6(1) RTI application dispatch💻 Tech StackBackendComponentTechnologyDescriptionFrameworkFastAPIAsynchronous, high-performance REST APIORM & DatabaseSQLAlchemy 2.0 (Async)Async ORM supporting SQLite (aiosqlite) and PostgreSQL (asyncpg)ValidationPydantic v2Strict data parsing and 12-factor application settingsComputer VisionOpenCV + scikit-learnORB keypoint extraction, descriptor matching, and TF-IDFNLP & VectorsSentence-Transformers + spaCy + YAKEDense vector search (all-MiniLM-L6-v2), NER, and keyword scoringDocument EngineReportLab + Jinja2Programmatic statutory RTI petition PDF generationASGI ServerUvicornProduction-grade ASGI runtimeFrontendComponentTechnologyDescriptionMeta-FrameworkTanStack Start / ViteFile-based SSR and client routing platformUI LibraryReact 19Modern concurrent component-based view layerLanguageTypeScript 5.8+End-to-end strict type safetyStylingTailwind CSS v4Utility-first responsive design tokensPrimitivesRadix UIWAI-ARIA compliant accessible component primitivesGeospatialLeaflet + React-LeafletInteractive geospatial heatmaps & ward overlaysIconsLucide ReactClean, consistent UI iconography📁 Repository StructurePlaintextaccountable/
├── README.md                          # Platform documentation & deployment guide
├── backend/                           # FastAPI application root
│   ├── accountable.db                 # Local SQLite database (development)
│   ├── requirements.txt               # Locked Python dependencies
│   └── app/
│       ├── __init__.py
│       ├── config.py                  # Pydantic Settings (12-factor configuration)
│       ├── crud.py                    # Database operations & ORM queries
│       ├── main.py                    # Application bootstrap & route definitions
│       ├── schemas.py                 # Pydantic request/response schemas
│       ├── database/
│       │   ├── __init__.py
│       │   ├── db.py                  # Async engine, sessionmaker & table init
│       │   └── models.py              # SQLAlchemy declarative models & relationships
│       └── services/
│           ├── __init__.py
│           ├── cv_deduplication.py    # Spatial & OpenCV image deduplication
│           ├── escalation_worker.py   # SLA time tracker & authority email sender
│           ├── nlp_tender_match.py    # spaCy & Transformer procurement matching
│           └── rti_pdf_gen.py         # Automated RTI petition PDF generator
│
└── frontend/                          # TanStack Start & React frontend
    ├── package.json                   # NPM dependencies & workspace scripts
    ├── vite.config.ts                 # Bundler configurations & plugins
    ├── tsconfig.json                  # TypeScript compiler settings
    └── src/                           # Cleaned source tree root
        ├── routeTree.gen.ts           # Generated TanStack route tree
        ├── router.tsx                 # Router instance and history settings
        ├── routes/
        │   ├── __root.tsx             # Root layout shell & global providers
        │   └── index.tsx              # Primary civic dashboard entrypoint
        ├── styles.css                 # Tailwind directives & theme definitions
        ├── App.jsx                    # View switcher & page shell
        ├── components/
        │   ├── LiveIssueMap.jsx       # Leaflet civic heatmap component
        │   ├── SnapTagForm.jsx        # Issue reporting modal with photo upload
        │   ├── FundTrailTable.jsx     # Financial audit ledger table
        │   ├── GamificationCard.jsx   # Civic score, badges & impact overview
        │   └── LeafletMap.jsx         # Client-only Leaflet boundary wrapper
        └── services/
            └── api.js                 # Unified API client for backend communication
⚡ Getting StartedPrerequisitesPython 3.11+ (python3 --version)Node.js 20+ or Bun (node --version / bun --version)Git (git --version)Backend Setup (FastAPI)Enter the backend directory:Bashcd backend
Initialize a virtual environment:Bash# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
Install dependencies:Bashpip install -r requirements.txt
(Optional) Download the spaCy language model:Bashpython -m spacy download en_core_web_sm
Start the API development server:Bashuvicorn app.main:app --reload --host 0.0.0.0 --port 8000
API Base: http://localhost:8000Interactive Swagger UI: http://localhost:8000/docsReDoc Documentation: http://localhost:8000/redocFrontend Setup (TanStack Start / React)Enter the frontend directory:Bashcd frontend
Install dependencies:Bashnpm install
# or with bun
bun install
Launch the local development server:Bashnpm run dev
# or with bun
bun run dev
Access the application:Open http://localhost:3000 in your browser.⚙️ Configuration & Environment VariablesCreate a backend/.env file. Settings are validated at runtime via Pydantic Settings (backend/app/config.py).VariableDefault ValueDescriptionDATABASE_URLsqlite+aiosqlite:///./accountable.dbAsync DB URI (postgresql+asyncpg://... in production)DB_ECHOFalseEnables verbose SQL logging in standard outputSMTP_HOST""Outgoing SMTP host for statutory escalation dispatchesSMTP_PORT587Outgoing SMTP port (587 for STARTTLS)SMTP_USE_TLSTrueEnforce TLS encryption for outbound emailsSMTP_USERNAME""SMTP authentication usernameSMTP_PASSWORD""SMTP authentication passwordSMTP_FROM_EMAILnoreply@accountable.gov.inFrom address on escalation noticesDEFAULT_WARD_OFFICER_EMAILward.officer@municipality.gov.inTier 1 notification recipientDEFAULT_MLA_EMAILmla.office@assembly.gov.inTier 2 notification recipientDEFAULT_COLLECTOR_EMAILcollector@district.gov.inTier 3 notification recipientDEFAULT_STATE_AUTHORITY_EMAILgrievance@state.gov.inTier 4 notification recipientRTI_PDF_DIR/tmp/accountable/rti_pdfsLocal filesystem directory for generated RTI PDFsDEFAULT_PIO_ADDRESSThe Public Information Officer...Default PIO designation block for legal filings📡 API ReferenceComplaints APIPOST /api/v1/complaints — Submit a new citizen complaint (triggers CV deduplication & NLP tender match background tasks).GET /api/v1/complaints — Paginated complaint listings (filterable by status and ward).GET /api/v1/complaints/{id} — Retrieve detailed complaint record by ID.POST /api/v1/complaints/{id}/deduplicate — Manually trigger the spatial + CV deduplication pipeline.Fund Flows & PFMSPOST /api/v1/fund-flows — Ingest a PFMS fund disbursement or utilization record.GET /api/v1/fund-flows — List historical fund flow records (filterable by project_id).Contractors & Corporate Network IntelligencePOST /api/v1/contractors — Register contractor entity records.GET /api/v1/contractors — List registered contractors.GET /api/v1/contractors/{id}/network — Generate shell-company relation graph based on shared directors and registered addresses.Escalations & RTI PetitionsGET /api/v1/escalations — List historical escalation logs and delivery states.POST /api/v1/complaints/{id}/escalate — Trigger next-tier escalation for a complaint.POST /api/v1/complaints/{id}/rti — Generate and download the statutory RTI petition PDF.GET /api/v1/complaints/{id}/tender-matches — List NLP-matched public procurement contracts and risk indices.Frontend Live IntegrationsGET /api/issues/heatmap — Retrieve active coordinates, category codes, and weights for Leaflet heatmap layers.GET /api/gamification/me — Retrieve current authenticated citizen score, rank, and badges (session-scoped).GET /api/gamification/{user_id} — Public civic profile lookup for a specific user ID.GET /health — Service liveness and readiness probe.🗺️ Roadmap[ ] Low-Bandwidth Channels: WhatsApp & Telegram conversational bots for offline and low-bandwidth report filing.[ ] Multilingual Voice Intake: Automated regional language transcription (Kannada, Hindi, Urdu, Tamil).[ ] Satellite & Drone Change Detection: Optical verification of road resurfacing and canal projects via Sentinel-2 imagery.[ ] Public Blockchain Notarization: Cryptographic anchoring of municipal disbursements to prevent back-dated accounting adjustments.[ ] Open Data Export: Public data endpoints structured in CKAN format for investigative journalism and transparency NGOs.🤝 ContributingContributions are welcomed from civic technologists, urban developers, lawyers, and designers!

📄 License
This project is licensed under the MIT License.

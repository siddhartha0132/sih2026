# PROJECT BLUEPRINT — GramVyapaar AI

**One file, full context.** Give this file to any AI coding assistant (Claude
Code, Cursor, etc.) alongside this repository and it has everything needed to
continue, fix, or extend the project without re-reading the original PPT.

---

## 1. Problem Statement (source of truth)

- **SIH ID:** SIH26091
- **Title:** AI-Driven Hyper-Local Business Advisory and Financial Structuring
  Assistant for Rural Micro-Entrepreneurs
- **Organization:** Ministry of Social Justice and Empowerment (MoSJE)
- **Theme:** Agriculture, FoodTech & Rural Development
- **Category:** Software

### Background
Government schemes give rural entrepreneurs concessional credit for
income-generating activities. The beneficiary contributes **10% margin
money**; the Channelizing Agency (CA/SCA) lends the remaining **90%**.

Two scheme tiers **as literally worded in the PS text**:

| Scheme | Project cost range | Max loan | Interest | Tenure | Moratorium |
|---|---|---|---|---|---|
| Micro Finance Scheme | up to ₹1.40 Lakh | ₹1.25 Lakh | 6.5% p.a. | 3 years | 3 months |
| Term Loan Scheme | ₹1.40 Lakh – ₹50.00 Lakh | ₹45 Lakh | 8% p.a. | 7 years | 6 months |

> **This "Term Loan Scheme" no longer exists at NSFDC and this repo does NOT
> implement it as written above.** Verified live against nsfdc.nic.in on
> 2026-09-03: NSFDC restructured it on 01.10.2023 into two real, currently
> active schemes. See §3 below and `backend/app/services/financial_calculator.py`
> for what's actually implemented and why — this is a deliberate, documented
> deviation from the literal PS text in favor of scheme reality, not a bug.

### Challenge
First-time rural entrepreneurs pick businesses based on anecdote, not data,
and can't calculate their own capital-to-loan eligibility or which scheme
applies. No tool exists that combines local market intelligence with
automatic financial structuring.

### Required deliverables (this is the grading checklist)

**Module 1 — Hyper-Local Business Feasibility Report**
1. Market Reach (consumer base within 5–10 km, distribution channels)
2. Opportunity Analysis (underserved niches)
3. General Business Analysis — **SWOT**
4. Threats Identification (supply chain, seasonality, buyer dependency)
5. Competitor Mapping (density of similar businesses nearby)
6. Product Market Value (pricing strategy + predicted local market value)

**Module 2 — Smart Financial Calculator & Scheme Router**
- Project Cost = Available Margin Capital ÷ 10%
- Max Loan = 90% of Project Cost
- Auto-select scheme by project cost (Logic A / Logic B above)
- EMI & moratorium-aware repayment schedule
- Working capital / operational cost outline

### Inputs (exactly as specified in the PS)
1. Geographic Location (Village / Block / District)
2. Available Margin Capital (e.g. ₹1,00,000)
3. Proposed Business Category (Dairy, Retail, Textiles, etc.)

### Impact goals
- Reduce failure rate of newly funded micro-enterprises
- Eliminate financial confusion between margin, loan, and repayment
- Empower marginalized youth with data-backed entrepreneurship

---

## 2. What the team pitched (from the SIH Idea PPT — team "Lumicore")

- **Product name:** GramVyapaar AI
- Positioned for three user types: rural entrepreneurs, CSC/field officers
  (assisted mode for low-literacy users), and government/SCAs (better
  outreach, data-driven planning, reduced default risk).
- Differentiators claimed: combines feasibility + scheme discovery + financial
  structuring in one platform; hyper-local (not generic) analysis;
  voice-first multilingual (Hindi + regional languages); transparent data
  confidence (source + freshness + confidence score per data point);
  explainable "why this scheme?" recommendation.
- Proposed tech stack: React/Next.js + Tailwind (frontend), Python/FastAPI
  (backend), PostgreSQL/MongoDB (data), Redis (cache), LLM + RAG for the
  conversational/reasoning layer, Bhashini for regional speech.
- Data sources referenced: Census (data.gov.in), OpenStreetMap/Overpass API,
  Agmarknet/e-NAM commodity prices, NSFDC/myScheme government scheme data,
  Udyam/MSME registration data.
- Explicit self-identified risks: rural business data is incomplete, Census
  data is old, OSM may undercount rural competitors, scheme rules change,
  low connectivity/digital literacy among users. Mitigations: show source +
  freshness per data point, confidence scores instead of false precision,
  offline/low-bandwidth fallback, voice + CSC-assisted mode.
- **Critical framing the team already committed to:** "Final recommendation
  always marked as ADVISORY, NOT GOVERNMENT APPROVAL." Keep this framing
  everywhere — in the disclaimer field, in the pitch, in any judge Q&A.

---

## 3. What THIS repository currently implements

This scaffold is a **working, runnable prototype** — not just a mockup. Here
is exactly what is real vs. simulated, so nothing is overstated in a demo.

### ✅ Fully real / deterministic (no external dependency, no mocking)
- **Module 2, the entire financial engine** (`backend/app/services/financial_calculator.py`):
  - Project cost & loan amount formulas exactly as specified in the PS
  - Scheme auto-selection across **three** real, currently-live NSFDC schemes
    (not the PS's literal two — see the callout above and the big comment at
    the top of `financial_calculator.py` for the full "why", with citations):
    | Scheme | Project cost | Max loan | Interest | Tenure | Moratorium | Verified against |
    |---|---|---|---|---|---|---|
    | Micro Finance | ≤ ₹1.40L | ₹1.25L | 6.5% | 3 yrs | 3 mo | [nsfdc.nic.in/en/micro-credit-finance](https://nsfdc.nic.in/en/micro-credit-finance) |
    | SUVIDHA | ₹1.40L–₹10L | ₹9L | 8% | 5 yrs | 6 mo | [nsfdc.nic.in/en/suvidha-loan](https://nsfdc.nic.in/en/suvidha-loan) |
    | UTKARSH | ₹10L–₹50L | ₹45L | 9% | 7 yrs | 6 mo | [nsfdc.nic.in/en/utkarsh-loan](https://nsfdc.nic.in/en/utkarsh-loan) |
    Includes a warning branch for project cost > ₹50L (out of scope for all
    three — the PS doesn't say what to do here, so this is handled explicitly
    and flagged, not silently dropped). Every `FinancialPlan` response carries
    `official_source_url` + `terms_verified_on` so the UI can render a live,
    clickable citation next to the numbers — this is the single strongest
    "we did real diligence" moment in the demo; lead with it if a judge asks
    "how do you know these rates are right?"
  - Full quarterly amortization schedule, moratorium-aware (interest
    capitalizes during the moratorium, then standard reducing-balance annuity
    afterward — this specific mechanic is an **assumption**, documented
    in-code, since none of the NSFDC pages specify EMI mechanics exactly)
  - This module has zero external dependencies and is fully unit-testable today.
- **Citation links throughout Module 1** — `MarketReach`, `CompetitorMapping`,
  and `PricingRecommendation` all now carry a `source_url` pointing at the
  relevant data.gov.in catalog page (Census, Udyam/MSME, Agmarknet), rendered
  as a clickable "Source:" link in `FeasibilityCard.jsx` instead of a plain
  string.
- **FastAPI backend** (`backend/app/main.py`, `api/routes.py`, `schemas.py`):
  real, runs today, `/api/advisory` returns both modules in one response,
  `/docs` gives interactive Swagger UI for free.
- **React frontend**: real, functional, calls the live backend, renders both
  reports, handles loading/error states, responsive.

### ⚠️ Mocked / simulated (clearly labeled in code and in API responses)
- **All hyper-local market data** (`backend/app/services/market_data.py`):
  population estimates, competitor density, commodity price trends, and
  geocoding are all **deterministic pseudo-random mocks** seeded by the
  input location + category (same input always gives same output, so demos
  are reproducible). Every mock function's docstring states exactly which
  real API should replace it.
- Every mocked data point is surfaced to the frontend with a `data_source`
  string starting with `"MOCK —"` and a `confidence: Medium` (never `High`) —
  this makes the "transparent data confidence" pitch claim literally true in
  the running code, not just a slide graphic.
- **The narrative summary** in the feasibility report is currently a
  deterministic string template (`feasibility_engine.py:_narrative_summary`),
  not an LLM call. It's written as an isolated function specifically so it
  can be swapped for a real Claude API call with a one-function change.

### ✅ Newly added — Personal-use login + saved history (real, not mocked)
- Two entry modes, chosen on the landing page before anything else:
  - **Open use** (`/advisor/open`) — no login, nothing saved, stateless exactly
    like the original single-mode app. For "anyone can try it" demos.
  - **Personal use** (`/advisor/personal`, behind `ProtectedRoute`) — requires
    a real login (`backend/app/auth.py`: bcrypt-hashed passwords, signed JWT,
    SQLite via SQLAlchemy in `backend/app/db.py` + `models_db.py`). Every
    advisory run made while logged in is auto-saved server-side
    (`api/routes.py::get_advisory`, via the optional-auth dependency) as a
    `HistoryEntry` row — no separate "save" click needed.
  - `AdvisoryRequest.business_name` (optional) lets the same venture's
    repeated check-ins group together in `/history` as one timeline —
    this is the field to use for the "1 hour in → 3 hours later → 5 hours
    later, now with 15 clients" growth-over-time demo: create multiple real
    history entries under the same `business_name`, each with updated inputs,
    and the engine computes real numbers at each stage. Not yet built: the
    actual scripted demo data/walkthrough itself — see next-task checklist.
  - New endpoints: `POST /api/auth/signup`, `POST /api/auth/login`,
    `GET /api/auth/me`, `GET /api/history` (optional `?business_name=`
    filter), `GET /api/history/{id}`.
  - `gramvyapaar.db` (SQLite file, gitignored) is created automatically on
    backend startup — nothing to provision manually.

### ❌ Not yet built
- Voice input / Bhashini integration
- Multilingual UI + translated AI narrative (only English strings exist
  right now; `language` field is accepted by the API but unused) —
  citation links themselves are done, see §3
- The scripted "growth over time" demo walkthrough itself (the login/history/
  business_name plumbing above is ready for it, but the actual pre-built
  multi-checkpoint mock business scenario for personal-use mode isn't)
- The "describe your idea → suggested category/investment/scheme" reverse-flow
- CSC/field-officer assisted mode UI
- Real integrations for OSM (competitor mapping beyond the static MSME file)
  and data.gov.in live Census (currently static Rajasthan-only Kaggle CSVs —
  see market_data.py; other states fall back to generic estimated defaults)

---

## 4. Architecture

```
┌─────────────────┐        POST /api/advisory        ┌──────────────────────┐
│   React (Vite)   │ ───────────────────────────────▶ │   FastAPI backend     │
│   frontend/       │ ◀─────────────────────────────── │   backend/            │
└─────────────────┘         AdvisoryResponse JSON      └──────────┬───────────┘
                                                                    │
                                     ┌──────────────────────────────┼──────────────────────────────┐
                                     ▼                              ▼                              ▼
                     financial_calculator.py          feasibility_engine.py              market_data.py
                     (deterministic, real)             (scoring + orchestration)         (MOCKED data layer)
                                                                    │
                                                        ┌───────────┴───────────┐
                                                        ▼                       ▼
                                            SWOT / threats / opportunity   pricing / competitor /
                                            (rule-based)                   market reach (from market_data)
```

Request flow for one advisory call:
1. Frontend `Advisor.jsx` collects village/block/district/state, margin
   capital, business category → `POST /api/advisory`.
2. `routes.py` calls `financial_calculator.build_financial_plan()` first
   (needed because `project_cost` feeds into the feasibility scoring).
3. Then calls `feasibility_engine.build_feasibility_report()`, which pulls
   from `market_data.py` (mocked) and produces all six Module 1 deliverables.
4. Both results combine into one `AdvisoryResponse`, returned as JSON.
5. Frontend renders `FeasibilityCard` + `FinancialPlanCard`.

---

## 5. Running it

### Local (no Docker)
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
# -> API docs at http://localhost:8000/docs

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# -> App at http://localhost:5173
```

### Docker
```bash
docker compose up --build
# frontend: http://localhost:5173
# backend:  http://localhost:8000/docs
```

---

## 6. Data integration roadmap (priority order for a judge demo)

If you have time before submission/demo, do these in order — each one
directly closes a gap a judge is likely to probe:

1. **OpenStreetMap Overpass API for competitor mapping** — highest
   demo-impact-to-effort ratio. Replace `market_data.get_competitor_density()`
   with a real Overpass query (`shop=*` near geocoded coordinates). No API
   key needed, generous rate limits.
2. **data.gov.in Census dataset for population** — replace
   `market_data.get_population_estimate()`. Needs a free data.gov.in API
   key (`DATA_GOV_IN_API_KEY` already stubbed in `.env.example`).
3. **Real LLM narrative** — swap `feasibility_engine._narrative_summary()`
   for a Claude API call (`ANTHROPIC_API_KEY` already stubbed). Keep the
   deterministic template as a fallback if the call fails or the key is
   unset — never let the app break because an LLM call failed.
4. **Agmarknet/e-NAM pricing** — replace `market_data.get_commodity_price_trend()`.
   Requires scraping or their public bulk-download CSVs; there is no clean
   public REST API, budget more time for this one.
5. **PDF export** — "Download / Share" from the original pitch. Use a
   backend endpoint that renders the `AdvisoryResponse` into a PDF
   (e.g. `weasyprint` or `reportlab`) rather than a frontend print-to-PDF,
   so CSC operators can generate it in low-bandwidth conditions.
6. **Persistence** — add PostgreSQL + SQLAlchemy, store submitted advisory
   requests + their reports keyed by a session/phone number, so a CSC
   operator can pull up a past report.

## 7. Known limitations to state proactively in a demo (don't let a judge "catch" these — say them first)

- Market/competitor/pricing data is currently simulated, not live — clearly
  labeled as such in the UI and API (`data_source` fields). This is
  intentional for a hackathon prototype timeline; section 6 above is the
  concrete plan to close it.
- The moratorium-interest-capitalization assumption in the EMI calculator is
  one reasonable interpretation, not dictated by the PS — flag this
  explicitly if asked "how did you compute the EMI?"
- Open-use requests are still fully stateless (by design). Personal-use now
  has real authentication + persistence (bcrypt + JWT + SQLite) — see §3.
- English-only UI right now; multilingual is a planned next step, not yet built.

## 8. If something breaks — where to look first

- **Backend won't start:** check `backend/.env` exists (copy from
  `.env.example`) — `pydantic-settings` will still work with defaults, but
  copy it anyway to avoid surprises.
- **CORS errors in browser console:** check `FRONTEND_ORIGIN` in
  `backend/.env` matches the actual frontend URL (default `http://localhost:5173`).
- **Frontend "Request failed" error box:** almost always means the backend
  isn't running, or `VITE_API_BASE` in the frontend doesn't match where the
  backend is actually listening — check `frontend/.env` (create one with
  `VITE_API_BASE=http://localhost:8000/api` if it doesn't exist) or the
  `docker-compose.yml` environment block.
- **Financial numbers look wrong:** everything in `financial_calculator.py`
  is deterministic and covered by the docstring at the top of the file —
  read the moratorium-capitalization assumption there first before assuming
  it's a bug.
- **Feasibility numbers look "too random" between runs:** they shouldn't be —
  `market_data.py`'s `_seed()` function makes all mock data deterministic
  per (village, category, ...) input. If it's changing between calls with
  identical input, something upstream is passing inconsistent strings
  (e.g. trailing whitespace, casing) — `_seed()` already lowercases and
  strips, so check the caller isn't bypassing it.

## 9. File map

```
gramvyapaar-ai/
├── PROJECT_BLUEPRINT.md        <- this file
├── README.md                   <- quick-start only, points here for full context
├── docker-compose.yml
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── app/
│       ├── main.py             <- FastAPI app + CORS, wires auth/history routers
│       ├── config.py           <- env-based settings (incl. jwt_secret_key)
│       ├── db.py                <- SQLAlchemy engine/session (SQLite for the demo)
│       ├── models_db.py         <- User + HistoryEntry ORM models
│       ├── auth.py              <- bcrypt hashing, JWT issue/verify, optional-auth dependency
│       ├── schemas.py          <- ALL request/response models (read this first)
│       ├── api/
│       │   ├── routes.py            <- /api/advisory, /api/financial-plan, /api/health
│       │   ├── auth_routes.py       <- /api/auth/signup, /login, /me
│       │   └── history_routes.py    <- /api/history, /api/history/{id}
│       └── services/
│           ├── financial_calculator.py   <- Module 2, fully real
│           ├── feasibility_engine.py     <- Module 1 orchestration + scoring
│           └── market_data.py            <- MOCKED data layer, swap-in points marked
└── frontend/
    ├── package.json / vite.config.js / index.html
    ├── Dockerfile
    └── src/
        ├── main.jsx / App.jsx     <- routes + Header, wraps app in AuthProvider
        ├── index.css            <- design tokens (palette, type, spacing)
        ├── api/client.js        <- fetch wrapper (advisory + auth + history calls)
        ├── context/AuthContext.jsx <- login/signup/logout, token+user in localStorage
        ├── pages/
        │   ├── Landing.jsx        <- Personal vs Open use choice (replaces Home.jsx)
        │   ├── Login.jsx          <- login/signup form
        │   ├── Advisor.jsx        <- form + report orchestration, mode="open"|"personal"
        │   ├── History.jsx        <- saved plans grouped by business_name
        │   └── HistoryDetail.jsx  <- replay one saved report via ReportView
        └── components/
            ├── InputForm.jsx
            ├── ProtectedRoute.jsx <- redirects to /login when not authenticated
            ├── ReportView.jsx     <- shared FeasibilityCard+FinancialPlanCard+PDF renderer
            ├── FeasibilityCard.jsx
            └── FinancialPlanCard.jsx
```

## 10. Immediate next-task checklist (hand this straight to an AI coding assistant)

- [ ] Build the scripted growth-over-time demo scenario for personal-use
      mode: pre-create 3 history entries for one mock business (same
      `business_name`) with realistic escalating inputs, so the demo can
      show "hour 1 plan → 3 hours: 2 clients → 5 hours: 15 clients, expand
      radius?" as real saved/recalculated reports, not a fake timer
- [x] Turn `data_source` fields into real clickable citation links — done,
      see §3. Still open: link each district's specific Agmarknet mandi
      record rather than only the general data.gov.in catalog page, if time
      allows before the demo.
- [ ] Add a language selector + translate the narrative/UI (Hindi first),
      via Bhashini or an LLM translation call — keep all numbers/formulas
      untouched, translate only the surrounding text
- [ ] Add the "describe your business idea" reverse-flow that suggests a
      category, investment level, and matching scheme
- [ ] Add `frontend/.env` support for `VITE_API_BASE` (currently relies on
      Vite's default env handling — verify a `.env` file works end-to-end)
- [ ] Write unit tests for `financial_calculator.py` (it's pure functions —
      easiest, highest-value tests in the repo)
- [ ] Implement OpenStreetMap Overpass integration (roadmap item #1)
- [ ] Add loading skeletons instead of the plain "Generating…" button label
- [ ] Add a PDF/print stylesheet for the report view (cheap win before
      building the real backend PDF export)
- [ ] Add basic input validation feedback (e.g. margin capital must be > 0
      is already enforced server-side by Pydantic `gt=0`, but surface a
      friendly client-side message before the request round-trip)

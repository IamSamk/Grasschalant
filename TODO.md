# 🌿 Grasschalant — TODO Tracker

> Touch Grass Edition: Outdoor Exploration Companion & Digital Memory Book Generator

---

## Phase 1: Repository Structure & Planning
- [x] Inspect existing repo and credentials
- [x] Create `TODO.md` with full breakdown
- [x] Update `.env` with Grasschalant-specific database/collection names
- [x] Scaffold `backend/` directory layout
- [x] Scaffold `frontend/` directory layout (Vite + React + TypeScript)
- [x] Create `backend/requirements.txt`
- [x] Create `backend/app/main.py` (FastAPI entry)
- [x] Create `backend/app/core/config.py` (Settings from `.env`)

## Phase 2: Meme Vault Seeding & Vector Pipeline
- [x] Create `backend/app/scripts/seed_memes.py` with curated meme archetypes
- [x] Implement CLIP embedding generation (`clip-ViT-B-32`, 512-dim)
- [x] Upsert meme documents into `grasschalant.meme_vault` (435 archetypes seeded)
- [x] Document Atlas `$vectorSearch` index JSON in `README.md`
- [x] Verify seed data via test query (`Surprised Pikachu` 90.57% match)

## Phase 3: PaliGemma Analogy Reasoner
- [x] Create `backend/app/services/vlm.py` — HF Serverless API inference
- [x] Implement PaliGemma prompt for pareidolia/meme analogy detection
- [x] Implement LM Studio fallback path
- [x] Create `backend/app/services/embedder.py` — CLIP embedding for query text
- [x] Create `backend/app/services/meme_search.py` — Atlas `$vectorSearch` pipeline + exact cosine fallback
- [x] Integration test: photo → PaliGemma → CLIP query → vector match

## Phase 4: Outings Storage & API Gateway
- [x] Create `backend/app/api/endpoints.py`
- [x] `POST /api/outings/start` — initialize outing session
- [x] `POST /api/outings/{id}/snap` — upload photo, run VLM + vector search
- [x] `GET /api/outings/{id}` — return full outing with all pages
- [x] Create `backend/app/services/cloudinary_upload.py`
- [x] Wire up CORS and mount routers in `main.py`
- [x] Test all endpoints via unit test suite (`TestAPIEndpoints`)

## Phase 5: Mobile Pedometer HUD (Frontend)
- [x] Initialize Vite + React + TypeScript project in `frontend/`
- [x] Install dependencies: `react-pageflip`, `jspdf`, `html2canvas`, `lucide-react`
- [x] Create `src/hooks/usePedometer.ts` — DeviceMotion step counter + simulator
- [x] Create `src/hooks/useCamera.ts` — MediaDevices camera access
- [x] Create `src/views/mobile/MobilePedometerHUD.tsx` — circular progress, shutter
- [x] Implement milestone unlock gating logic
- [x] Implement haptic feedback on milestone

## Phase 6: 3D Day Out Storybook & PDF Export (Frontend)
- [x] Create `src/views/desktop/StoryBookViewer.tsx` — 3D flip book
- [x] Cover page: title, total steps, date, duration
- [x] Left page: outdoor photo, step badge, literal description
- [x] Right page: meme match, confidence badge, explanation
- [x] Keyboard navigation (arrow keys)
- [x] Create `src/utils/PDFExport.ts` — jspdf + html2canvas
- [x] Wire up `App.tsx` with routing (mobile vs desktop views)
- [x] Style all components with premium CSS

## Phase 7: Deployment & Verification
- [x] Create `backend/Dockerfile` for Render deployment
- [x] Create `render.yaml` service definition
- [x] Configure frontend for static hosting build
- [x] End-to-end smoke test (Python test suite + Vite production build)
- [x] Update `README.md` with setup, architecture, and vector index instructions
- [x] Final `TODO.md` verification pass — all boxes checked

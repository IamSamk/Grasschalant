# 🌿 Grasschalant — Touch Grass Edition

> **Hacktoberfest Week 1: "Touch Grass"**  
> An outdoor exploration companion and digital memory book generator that turns your real-world walks into uncanny meme storybooks using vision AI and vector search.

---

## 📖 Overview

**Grasschalant** incentivizes software engineers and indoor dwellers to put down the keyboard and go outside ("touch grass").

1. **Step Milestones**: Set an outdoor step goal (e.g., 6,000 steps). As you walk, the app connects to your device's accelerometer / pedometer using HTML5 `DeviceMotion` sensor fusion.
2. **Photo Unlocks**: At regular step intervals (e.g., every 600 steps = 10 unlocks), the camera shutter unlocks so you can capture real-world nature, textures, urban architecture, or street scenes.
3. **PaliGemma Pareidolia AI**: Each photo is analyzed by Google's **PaliGemma** Vision-Language Model to detect accidental pareidolia, facial contours, or hilarious internet culture analogies in everyday outdoor objects.
4. **Atlas Vector Search**: The meme analogy concept is projected into a 512-dimensional vector space using **CLIP (`clip-ViT-B-32`)** and matched against an indexed memory vault in **MongoDB Atlas** using `$vectorSearch`.
5. **Interactive 3D Day Out Storybook**: At the end of the walk, your expedition is compiled into an interactive 3D flip-book:
   - **Left Page**: Your raw outdoor photo, exact step badge, and literal physical description.
   - **Right Page**: Matched meme archetype, similarity confidence score, and humorous analogy explanation.
6. **Zero-Server Client PDF Export**: Export high-resolution A4 landscape digital memory books directly in the browser via `jsPDF`.

---

## 🏗️ Architecture

```
                      ┌──────────────────────────────────────────────┐
                      │              MOBILE PEDOMETER HUD            │
                      │  - DeviceMotion accelerometer peak detector  │
                      │  - MediaDevices rear camera capture          │
                      │  - Circular SVG progress ring                │
                      └──────────────────────┬───────────────────────┘
                                             │ Photo Capture + Steps
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │            FASTAPI API GATEWAY               │
                      │  - POST /api/outings/start                   │
                      │  - POST /api/outings/{id}/snap               │
                      │  - GET  /api/outings/{id}                    │
                      └───────┬──────────────┬──────────────┬────────┘
                              │              │              │
           Upload Real Photo  │              │              │ Analogy Concept
                              ▼              │              ▼
                  ┌──────────────────────┐   │   ┌──────────────────────┐
                  │    CLOUDINARY CDN    │   │   │   CLIP TEXT ENCODER  │
                  │   Optimized image    │   │   │  (clip-ViT-B-32)     │
                  │   storage & delivery │   │   │  512-dim vector      │
                  └──────────────────────┘   │   └──────────┬───────────┘
                                             ▼              │
                  ┌──────────────────────────────────────┐  │
                  │       PALIGEMMA VISION AGENT         │  │ Query Vector
                  │  - HF Serverless Inference API       │  │
                  │  - LM Studio local fallback          │  │
                  │  - Pareidolia / metaphor detection   │  │
                  └──────────────────────────────────────┘  │
                                                            ▼
                                         ┌──────────────────────────────────────┐
                                         │         MONGODB ATLAS                │
                                         │  - Collection: meme_vault            │
                                         │  - Collection: outings               │
                                         │  - Index: meme_vector_index          │
                                         │  - $vectorSearch cosine similarity   │
                                         └──────────────────┬───────────────────┘
                                                            │
                                                            ▼
                                         ┌──────────────────────────────────────┐
                                         │       3D STORYBOOK VIEWER & PDF      │
                                         │  - Dual-page CSS 3D transforms       │
                                         │  - Left: Outdoor photo + Step badge  │
                                         │  - Right: Matched Meme + Explanation │
                                         │  - Client-side A4 Landscape PDF      │
                                         └──────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Vanilla CSS Design System, Lucide Icons |
| **Mobile Sensors** | HTML5 `DeviceMotion` API (peak acceleration magnitude detection) |
| **Camera** | `navigator.mediaDevices.getUserMedia` (environment facing mode) |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Motor (Async MongoDB), Pydantic v2 |
| **Vision AI** | Google PaliGemma 3B (Hugging Face Serverless Inference API / LM Studio fallback) |
| **Embeddings** | `sentence-transformers` CLIP (`clip-ViT-B-32`, 512-dimensional normalized vectors) |
| **Database & Vector Search** | MongoDB Atlas `$vectorSearch` with cosine similarity |
| **Media Hosting** | Cloudinary CDN (`grasschalant_walks` folder) |
| **Storybook & PDF** | CSS 3D Transforms, `jsPDF` client-side vector renderer |
| **Deployment** | Docker, Render (`render.yaml`), Static Web Hosting |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- MongoDB Atlas cluster with Vector Search capability
- Cloudinary account for photo hosting
- Hugging Face API token (with access to PaliGemma models)

### 2. Environment Variables
Create a `.env` file in the project root (see `.env.example`):

```bash
# MongoDB Atlas
MONGODB_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=Cluster0"
MONGODB_DB_NAME="grasschalant"
MONGODB_COLLECTION_MEMES="meme_vault"
MONGODB_COLLECTION_OUTINGS="outings"
MONGODB_VECTOR_INDEX_NAME="meme_vector_index"

# Hugging Face Serverless Vision API
HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
HF_VISION_MODEL="google/paligemma-3b-pt-224"

# LM Studio Fallback (Optional)
LMSTUDIO_BASE_URL="http://localhost:1234/v1"
LMSTUDIO_API_KEY="lm-studio"
LOCAL_VISION_MODEL="abetlen/paligemma-3b-mix-224-gguf"

# Cloudinary
CLOUDINARY_CLOUD_NAME="your_cloud_name"
CLOUDINARY_API_KEY="your_api_key"
CLOUDINARY_API_SECRET="your_api_secret"
CLOUDINARY_FOLDER="grasschalant_walks"

# Server
PORT=8000
HOST="0.0.0.0"
CORS_ORIGINS="*"
```

### 3. Backend Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run backend unit tests
python -m unittest discover -s backend/tests -p "test_*.py"

# Start FastAPI server
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 4. Seed the Meme Vault
To populate MongoDB Atlas with curated meme archetype templates and their 512-dim CLIP vectors:

```bash
python -m backend.app.scripts.seed_memes
```

### 5. MongoDB Atlas Vector Search Index Configuration
In your MongoDB Atlas dashboard:
1. Navigate to **Database** > **Browse Collections**.
2. Select database `grasschalant` and collection `meme_vault`.
3. Open the **Search Indexes** tab and click **Create Search Index**.
4. Choose the **JSON Editor** and configure:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 512,
      "similarity": "cosine"
    }
  ]
}
```
5. Name the index **`meme_vector_index`** and click **Create Index**.

### 6. Frontend Setup
```bash
cd frontend
npm install
npm run build
npm run dev
```

---

## 📱 Features

- **Sensory Walking HUD**: Real-time step counter with dynamic SVG progress ring and milestone markers.
- **Haptic Feedback**: Vibrates mobile devices when a photo milestone is unlocked.
- **Simulation Mode**: Built-in `+100`, `+200`, `+500` step simulator for testing without having to run outside.
- **3D Interactive Storybook**: Turn pages with arrow keys, click buttons, or mobile swipe gestures.
- **Direct PDF Export**: Download a high-res landscape memory book keepsake with step counts and timestamps.
- **Offline Resilience**: Automatically falls back if network or device sensors are unavailable.

---

## 📄 License
MIT License. Built with 🌿 for Hacktoberfest Week 1.

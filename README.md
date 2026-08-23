# Simpantun

An Artificial Intelligence (AI)-based system for processing, storing, and searching Malay Pantuns. This system integrates Optical Character Recognition (OCR) technology to extract pantuns from images, along with a smart search engine using FAISS.

## 🌟 Features
- **Smart Search:** Similarity-based pantun search using vector models and the FAISS algorithm.
- **Image Text Recognition (OCR):** Upload images (JPG, PNG, WEBP) to extract pantun text using EasyOCR.
- **Visual Image Search:** Upload an image without text, and the AI will analyze its contents (e.g., nature, animals) to recommend related pantuns.
- **Modern & Responsive Interface:** Built with modern frontend technologies (Vite + React) for fast performance.

## 🛠️ Technology Stack
- **Backend:** Python, Flask
- **AI Model:** SentenceTransformers (CLIP), FAISS (Vector Search)
- **Computer Vision:** OpenCV, EasyOCR
- **Frontend:** React, Vite

## 📋 Prerequisites
- **Git** (for cloning)
- **Docker Desktop** (Recommended)
- *OR* **Python 3.10+ and Node.js 16+** (if running manually)

---

## 🚀 Getting Started

You can run this application either using **Docker (Recommended)** or by running it manually.

### Option 1: Using Docker (Recommended)
Using Docker guarantees that all dependencies (including heavy libraries like OpenCV and FAISS) are correctly installed without messing up your local environment.

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hfzuddin/Simpantun.git
   cd Simpantun
   ```

2. **Start Docker Desktop** on your computer.

3. **Run the Application**
   Open your terminal in the project directory and run:
   ```bash
   docker-compose up -d --build
   ```
   *Note: The first time you run this, it may take several minutes to download the Python image, compile the frontend, and install the AI libraries.*

4. **Access the Web App**
   Open your browser and navigate to: [http://localhost:5500](http://localhost:5500)

5. **Stop the Application**
   ```bash
   docker-compose down
   ```

### Option 2: Traditional Manual Installation (Without Docker)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hfzuddin/Simpantun.git
   cd Simpantun
   ```

2. **Backend Setup**
   Open a terminal in the main folder and install the Python dependencies:
   ```bash
   # (Optional but recommended) Create a virtual environment
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate # Mac/Linux

   # Install requirements
   pip install -r requirements.txt

   # Run the Flask backend
   python run.py
   ```
   *The backend server will start loading. Once ready, it runs at `http://127.0.0.1:5500`.*

3. **Frontend Setup**
   Open a separate, new terminal, and navigate to the frontend folder:
   ```bash
   cd frontend

   # Install Node Modules
   npm install

   # Launch Web Application
   npm run dev
   ```
   *Vite will provide a local URL (typically `http://localhost:5173`). Open this URL in your browser to view the application.*

---

## ☁️ Deployment (Google Cloud Run)

The backend serves the built frontend directly (see `app/__init__.py`), so the whole app deploys as a single container. Cloud Run's free tier is used here because the AI stack (PyTorch, CLIP, EasyOCR) needs more RAM than most free hosts (Render, Fly.io, Railway) offer on their no-cost plans.

**One-time setup** (in [Google Cloud Console](https://console.cloud.google.com) or [Cloud Shell](https://console.cloud.google.com/?cloudshell=true)):
1. Create/select a GCP project and [enable billing](https://console.cloud.google.com/billing) (a card is required to activate Cloud Run, even for free-tier usage).
2. Enable the required APIs:
   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
   ```

**Deploy:**
```bash
gcloud run deploy simpantun \
  --source . \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 3 \
  --timeout 300 \
  --allow-unauthenticated
```
Cloud Build reads the `Dockerfile` automatically — no image push needed. On success it prints a public `*.run.app` URL.

**Free tier notes:**
- The Always Free quota (2M requests, 180,000 vCPU-sec, 360,000 GiB-sec per month) only applies in `us-central1`, `us-east1`, or `us-west1`. Deploying elsewhere bills from the first request.
- Keep `--min-instances 0` — the service scales to zero and costs nothing while idle. Setting a minimum instance count keeps a container warm 24/7 and will incur real charges.
- `requirements.txt` pins the CPU-only PyTorch build (`+cpu` wheels via the PyTorch CPU index) — the default PyPI `torch` wheel drags in ~2GB of unused CUDA/NVIDIA packages since this app never sets `gpu=True`. The resulting image is ~1.1GB, just over Artifact Registry's 0.5GB free storage, so expect a negligible storage charge (well under $0.10/month).
- Every cold start reloads the CLIP/EasyOCR models from scratch (Cloud Run's filesystem isn't persisted between instances), so the first request after idle time can take 30-90s; subsequent requests are fast until it scales back down.

---

## 📖 How to Use

Once the server is running and you have the application open in your browser, you can search for pantuns in two ways:

### Text Search
1. Locate the search bar on the dashboard.
2. Type any keyword, phrase, or topic (e.g., "kasih sayang", "nasihat budi", or "alam sekitar").
3. The system's AI will understand the context of your search and instantly retrieve the most relevant pantuns from the database based on a similarity score.

### Image / OCR Search
1. Click the upload button to provide an image (JPG, PNG, or WEBP).
2. **If the image contains text:** The system uses OCR to read the words in the picture and instantly finds pantuns that match the extracted text.
3. **If the image has no text:** The system analyzes the picture using Computer Vision to detect objects or scenes (e.g., detecting a "cat" or "beach"), and automatically recommends pantuns related to that visual theme.

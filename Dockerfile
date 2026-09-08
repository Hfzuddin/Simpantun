# ==========================================
# STAGE 1: Build the React Frontend
# ==========================================
FROM node:22 AS frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the Vite React app for production. VITE_API_BASE is deliberately left
# unset here: in this image Flask serves dist/ itself, so the frontend and the
# API share an origin and relative /api paths work. Only the Vercel build sets
# it (see vercel.json + frontend/.env.example).
RUN npm run build


# ==========================================
# STAGE 2: Build the Python Backend
# ==========================================
FROM python:3.10-slim

# Hugging Face Spaces runs containers as uid 1000, not root. Create that user
# up front so everything the app writes at runtime is already owned by it:
# /app (Flask creates uploads/ and the FAISS cache there on boot) and the
# model caches under $HOME.
RUN useradd -m -u 1000 user

# Install system dependencies (important for OpenCV, EasyOCR, etc)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements file
COPY requirements.txt .

# Install Python dependencies
# Note: Using --no-cache-dir for a smaller Docker image size
RUN pip install --no-cache-dir -r requirements.txt

# Hand /app to the runtime user, then drop root for everything after this.
RUN chown -R user:user /app
USER user

ENV HOME=/home/user \
    HF_HOME=/home/user/.cache/huggingface \
    EASYOCR_MODULE_PATH=/home/user/.EasyOCR

# Bake the model weights into the image. Without this, every cold start
# downloads them again before the first request can be served — and a free
# HF Space cold-starts every time it wakes from sleep. Mirrors the models
# named in app/services.py: keep the two in sync.
RUN python -c "import easyocr; easyocr.Reader(['ms', 'en'], gpu=False)" \
    && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1')" \
    && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('clip-ViT-B-32')"

# Copy entire backend source code into container
COPY --chown=user:user . .

# Copy the compiled frontend (dist) from Stage 1
COPY --from=frontend-builder --chown=user:user /app/dist /app/dist

# Expose port 5500 used by Flask. Hugging Face routes to the port declared as
# app_port in README.md; Cloud Run overrides it via $PORT at runtime.
EXPOSE 5500

# Run via gunicorn. 1 worker on purpose: each worker would load its own
# ~2GB copy of the CLIP/EasyOCR models, so more workers risks OOM. threads
# capped at 4 (not 8) so concurrent image-analysis requests can't stack up
# too many simultaneous OCR/CLIP inference calls and blow the memory limit.
# timeout=300 matches Cloud Run's own request timeout: cold-start model
# loading measured at ~82s locally, so this leaves headroom on slower runs.
CMD exec gunicorn --bind :${PORT:-5500} --workers 1 --threads 4 --timeout 300 run:app

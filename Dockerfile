# ==========================================
# STAGE 1: Build the React Frontend
# ==========================================
FROM node:18 AS frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the Vite React app for production
RUN npm run build


# ==========================================
# STAGE 2: Build the Python Backend
# ==========================================
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (important for OpenCV, EasyOCR, etc)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements file
COPY requirements.txt .

# Install Python dependencies
# Note: Using --no-cache-dir for a smaller Docker image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend source code into container
COPY . .

# Copy the compiled frontend (dist) from Stage 1
COPY --from=frontend-builder /app/dist /app/dist

# Expose port 5500 used by Flask
EXPOSE 5500

# Run application (run.py is already set to host='0.0.0.0')
CMD ["python", "run.py"]

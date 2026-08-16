# 📝 Simpantun

An Artificial Intelligence (AI)-based system for processing, storing, and searching Malay Pantuns. This system integrates Optical Character Recognition (OCR) technology to extract pantuns from images, along with a smart search engine using FAISS.

## 🚀 Key Features
- **Smart Search:** Similarity-based pantun search using vector models and the FAISS algorithm.
- **Image Text Recognition (OCR):** Upload images (JPG, PNG, WEBP) to extract pantun text using EasyOCR.
- **Modern & Responsive Interface:** Built with modern frontend technologies (Vite + React) for fast performance.
- **High-Performance API:** Backend powered by Flask with automated caching and data processing.
- **Docker Support:** The codebase is ready for deployment using Docker containers.

## 🛠️ Tech Stack
**Backend (Python/Flask)**
- Flask
- EasyOCR & OpenCV (Image Processing and Computer Vision)
- FAISS (Vector Search/Similarity Search)
- NumPy & Pandas (Dataset Management)

**Frontend (React/Vite)**
- Vite (Build Tool)
- React.js / JavaScript

## 📁 Project Structure

```text
Simpantun/
├── app/                  # Backend API Routes and Modules (Flask)
├── dataset/              # Raw dataset directory (Excel/CSV)
├── frontend/             # Frontend user interface source code (React + Vite)
├── requirements.txt      # Python package dependencies
├── config.py             # System configuration and global parameters
├── run.py                # Backend server launch script
├── Dockerfile            # Docker container specifications
└── .gitignore            # GitHub file exclusion rules
```

## ⚙️ Prerequisites
Ensure the following software is installed on your computer:
- [Python 3.10+](https://www.python.org/)
- [Node.js](https://nodejs.org/) (Version 16 or latest)
- [Git](https://git-scm.com/)

---

## 💻 Local Setup Guide

### 1. Backend Configuration (Server)
Open a new terminal in the main project folder (`Simpantun`):

```bash
# (Optional) Create and activate a Python Virtual Environment
python -m venv venv
# For Windows:
venv\Scripts\activate
# For Mac/Linux:
source venv/bin/activate

# Install all requirements
pip install -r requirements.txt

# Run the system
python run.py
```
*The backend will run by default at `http://127.0.0.1:5500`.*

### 2. Frontend Configuration (Interface)
Open a separate terminal, and navigate to the `frontend` directory:

```bash
cd frontend

# Install Node Modules packages
npm install

# Launch Web Application
npm run dev
```

---

## 🐳 Docker Guide (Deployment)
You can also launch the backend system using Docker to streamline the production deployment process:

```bash
# Build the Docker image
docker build -t simpantun-app .

# Run the container
docker run -p 5500:5500 simpantun-app
```

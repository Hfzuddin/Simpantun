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

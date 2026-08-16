FROM python:3.10-slim

# Tetapkan direktori kerja
WORKDIR /app

# Install sistem dependencies (penting untuk OpenCV, EasyOCR, dll)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Salin fail keperluan Python
COPY requirements.txt .

# Install dependencies Python
# Nota: Menggunakan --no-cache-dir untuk saiz imej Docker yang lebih kecil
RUN pip install --no-cache-dir -r requirements.txt

# Salin keseluruhan kod sumber ke dalam kontena
COPY . .

# Dedahkan port 5500 yang digunakan oleh Flask
EXPOSE 5500

# Jalankan aplikasi (run.py sudah ditetapkan host='0.0.0.0')
CMD ["python", "run.py"]

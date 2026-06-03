# Menggunakan Python 3.10 versi slim agar container ringan
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Menentukan direktori kerja di dalam container
WORKDIR /app

# Menyalin file requirements.txt
COPY requirements.txt .

# Menginstall library sistem yang dibutuhkan (opsional, jika ada library C++)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Menginstall library Python
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode aplikasi ke dalam container
COPY . .

# Mengekspos port yang digunakan oleh Cloud Run (8080)
EXPOSE 8080

# Perintah untuk menjalankan FastAPI dengan Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

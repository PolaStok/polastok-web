# Gunakan image Python 3.11 yang ringan
FROM python:3.11-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Copy requirements terlebih dahulu agar Docker bisa memanfaatkan cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi
COPY . .

# Expose port (biasanya 8080)
EXPOSE 8080

# Jalankan server FastAPI menggunakan Uvicorn dengan environment variable PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}

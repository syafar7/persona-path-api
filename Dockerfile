# 1. Gunakan sistem operasi dasar yang sudah berisi Python resmi
FROM python:3.11-slim

# 2. Buat folder kerja di dalam server internet
WORKDIR /app

# 3. Copy daftar library dan instal semuanya sekaligus
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy seluruh file kodinganmu dari laptop ke server
COPY . .

# 5. Hugging Face mewajibkan aplikasi berjalan di Port 7860
EXPOSE 7860

# 6. Perintah sakral untuk menyalakan Flask menggunakan Gunicorn di port 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
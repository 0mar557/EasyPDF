FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer et définir le dossier de travail
WORKDIR /app

# Copier les fichiers requis
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers
COPY . .

# Spécifier le port 8080 pour Railway
ENV PORT=8080

# Lancer avec gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]

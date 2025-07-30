# Étape 1 : Choisir une image Debian slim + Python
FROM python:3.11-slim

# Étape 2 : Installer les dépendances système (Poppler + Tesseract)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Étape 3 : Définir le dossier de travail
WORKDIR /app

# Étape 4 : Copier les fichiers
COPY . .

# Étape 5 : Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Étape 6 : Exposer le port utilisé par Flask/Gunicorn
EXPOSE 8080

# Étape 7 : Démarrer l’application avec Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

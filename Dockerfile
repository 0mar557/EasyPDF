# Étape 1 : base
FROM python:3.11-slim

# Étape 2 : installation des dépendances système
RUN apt update && apt install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    libgl1 \
    && apt clean

# Étape 3 : copie du code
WORKDIR /app
COPY . .

# Étape 4 : installation des dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Étape 5 : port exposé
EXPOSE 8080

# Étape 6 : lancement avec Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

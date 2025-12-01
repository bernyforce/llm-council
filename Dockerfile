FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Installer uv (gestionnaire de paquets Python moderne)
RUN pip install uv

# Copier tous les fichiers du projet
COPY . .

# Installer les dépendances Python avec uv
RUN uv sync --frozen

# Exposer le port 8000
EXPOSE 8000

# Commande de démarrage
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]

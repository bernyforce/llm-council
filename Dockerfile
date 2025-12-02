FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN pip install uv

# Copier les fichiers
COPY . .

# Installer les dépendances Python
RUN uv sync --frozen

# Port pour FastAPI
EXPOSE 8000

# Lancer le backend FastAPI
CMD ["uv", "run", "python", "-m", "backend.main"]

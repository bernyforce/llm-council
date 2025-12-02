# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend Python + Frontend servi
FROM python:3.11-slim
WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN pip install uv

# Copier le code backend
COPY . .

# Installer les dépendances Python
RUN uv sync --frozen

# Copier le frontend buildé depuis le stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Port FastAPI
EXPOSE 8001

# Lancer avec serveur de fichiers statiques
CMD ["uv", "run", "python", "-m", "backend.main", "--serve-frontend"]

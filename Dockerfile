# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Corriger l'API URL avant le build
RUN sed -i "s|http://localhost:8001|https://llm.iatuto.com|g" src/api.js
RUN npm run build

# Stage 2: Backend Python + Frontend servi
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install \
    fastapi \
    uvicorn \
    httpx \
    pydantic \
    python-dotenv

# Copier le frontend buildé
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

EXPOSE 8001

# Modifier le backend pour servir le frontend
RUN echo "from fastapi.staticfiles import StaticFiles" >> /tmp/serve.py && \
    echo "from fastapi.responses import FileResponse" >> /tmp/serve.py && \
    echo "import os" >> /tmp/serve.py && \
    cat backend/main.py >> /tmp/serve.py && \
    echo "" >> /tmp/serve.py && \
    echo "if os.path.exists('frontend/dist'):" >> /tmp/serve.py && \
    echo "    app.mount('/assets', StaticFiles(directory='frontend/dist/assets'), name='static')" >> /tmp/serve.py && \
    echo "    @app.get('/')" >> /tmp/serve.py && \
    echo "    async def serve_frontend():" >> /tmp/serve.py && \
    echo "        return FileResponse('frontend/dist/index.html')" >> /tmp/serve.py && \
    mv /tmp/serve.py backend/main.py

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]

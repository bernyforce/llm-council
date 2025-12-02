FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY . .

# Installer directement avec pip (plus fiable)
RUN pip install streamlit openai anthropic google-generativeai

# Installer les autres dépendances depuis requirements.txt si il existe
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Port pour Streamlit  
EXPOSE 8000

# Lancer directement avec python
CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]

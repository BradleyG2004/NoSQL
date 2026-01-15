# Image officielle Ollama
FROM ollama/ollama:latest

# Dossier de travail
WORKDIR /root

# Pré-téléchargement du modèle (au build)
RUN ollama serve & \
    sleep 10 && \
    ollama pull llama3.1:8b && \
    pkill ollama

# Exposition du port Ollama
EXPOSE 11434

# Lancement du serveur Ollama
CMD ["ollama", "serve"]

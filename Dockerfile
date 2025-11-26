# --- 1. Imagen base con Python ---
FROM python:3.11-slim

# --- 2. Instalar Node.js + PM2 dentro del contenedor ---
# PM2 necesita Node para funcionar
RUN apt update && apt install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt install -y nodejs && \
    npm install -g pm2

# --- 3. Crear carpeta de trabajo dentro del contenedor ---
WORKDIR /app

# --- 4. Copiar tu proyecto entero dentro del contenedor ---
COPY . .

# --- 5. Instalar dependencias de Python ---
# Requiere tener requirements.txt en tu proyecto
RUN pip install --no-cache-dir -r requirements.txt

# --- 6. Exponer el puerto donde corre Flask ---
EXPOSE 5000

# --- 7. Comando con el que Docker arrancará PM2 ---
# pm2-runtime es la forma correcta en producción
CMD ["pm2-runtime", "ecosystem.config.js"]

# Imagen ligera de Python para producción
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías de ML
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias sin cache para reducir tamaño de imagen
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copiar el código de la aplicación y los modelos
COPY ./app ./app
COPY ./models ./models

# Exponer el puerto en el que correrá FastAPI
EXPOSE 8000

# Comando para arrancar la aplicación
# Usamos workers=1 porque los modelos de ML consumen mucha RAM; 
# para escalar es mejor subir más réplicas del contenedor.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

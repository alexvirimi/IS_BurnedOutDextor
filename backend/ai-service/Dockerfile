# Imagen de Python más ligera
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias sin cache para reducir tamaño de imagen
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copiar el modelo y el servicio en el contenedor
COPY random_forest_burnout.pkl features.pkl main.py ./

# Variable de entorno para el puerto
ENV PORT=8001

# Exponer puerto
EXPOSE 8001

# Arrancar el servicio
# Usamos sh -c para permitir expandir la variable de entorno PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8001"]
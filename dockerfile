# Dockerfile
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de dependencias primero para cachearlos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto 5000 (el puerto predeterminado de Flask)
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]

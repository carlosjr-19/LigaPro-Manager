# Usamos una imagen de Python ligera y moderna
FROM python:3.12-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias
# libpq-dev es util si decides usar Postgres en el futuro
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el archivo de requerimientos
COPY ligapro_manager/requirements.txt requirements.txt

# Instalamos las dependencias de Python sin cache para ahorrar espacio
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del proyecto al contenedor
COPY . .

# Variables de entorno predeterminadas
ENV PORT=5000
# Importante: Agregamos el directorio actual al PYTHONPATH para que Python encuentre 'ligapro_manager'
ENV PYTHONPATH=/app

# Exponemos el puerto
EXPOSE $PORT

# Comando de inicio:
# Entramos a la carpeta 'ligapro_manager' y ejecutamos gunicorn apuntando al servidor
# server:flask_app se refiere a ligapro_manager/server.py -> objeto flask_app
CMD python ligapro_manager/bootstrap.py && cd ligapro_manager && gunicorn --bind 0.0.0.0:$PORT ligapro_manager:app

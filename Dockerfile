FROM python:3.11

# RUN apt-get update -y
WORKDIR /usr/src/app
# Install package dependencies as recommended 
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir --requirement /tmp/requirements.txt
# Copia la API 
# REVISAR LOS PERMISOS CON CHMOD
COPY image_tags_api/* image_tags_api/
# Copia las credenciales 
COPY credentials.json .
# Expone el puerto
EXPOSE 80
# Ejecuta waitress 
CMD [ "waitress-serve", "--port=80", "--call", "image_tags_api:create_app" ]
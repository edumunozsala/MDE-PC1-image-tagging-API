from typing import List

from imagekitio import ImageKit
import os
import requests
import uuid
import base64
import datetime

from . import models

def delete_image_url(file_id):
    # Connec to  imagekitio
    imagekit = ImageKit(
        public_key=os.environ["IMAGEKIT_PUBLIC_KEY"],
        private_key=os.environ["IMAGEKIT_PRIVATE_KEY"],
        url_endpoint = os.environ["IMAGEKIT_URL_ENDPOINT"]
    )
    
    # Delete the image from  imagekitio
    delete = imagekit.delete_file(file_id=file_id)
    
    return delete
    
def get_image_url(imagenb64: str, filename: str):
    # Upload the image to imagekitio
    imagekit = ImageKit(
        public_key=os.environ["IMAGEKIT_PUBLIC_KEY"],
        private_key=os.environ["IMAGEKIT_PRIVATE_KEY"],
        url_endpoint = os.environ["IMAGEKIT_URL_ENDPOINT"]
    )

    # upload the image to imagekitio
    upload_info = imagekit.upload(file=imagenb64, file_name=filename)
    # Devuelve la url publica de la imagen
    return upload_info

def get_tags_url(image_url, min_confidence: str):
    # Requests the tags of the image to imagga
    response = requests.get(f"https://api.imagga.com/v2/tags?image_url={image_url}", auth=(os.environ["IMAGGAN_API_KEY"], os.environ["IMAGGAN_API_SECRET"]))
    # Define the list of tags with confidence > min_confidence
    tags = [
        {
            "tag": t["tag"]["en"],
            "confidence": t["confidence"]
        }
        for t in response.json()["result"]["tags"]
    ]    
    # Devuelve los tags de la imagen
    return tags

def get_tags_image_minconfidence(imagenb64: str, filename: str, min_confidence: str):
    # Upload the image to imagekitio
    upload_info = get_image_url(imagenb64,filename)    
    # Requests the tags of the image to imagga
    all_tags= get_tags_url(upload_info.response_metadata.raw['url'], min_confidence)
    # Define the list of tags with confidence > min_confidence
    tags = [t for t in all_tags if t["confidence"] > min_confidence]
    # Delete the image from  imagekitio
    delete_image_url(upload_info.file_id)
    # Devuelve los tags de la imagen con confidence > min_confidence
    return tags

def register_image_tags_bd(myuuid: str, path: str,  tags:str, date: str, size: int):
    # Insertamos la imagen y sus tags en la base de datos
    models.insert_picture_tags(myuuid, date, path, size, tags)
    # Creamos la respuesta
    response={"id": myuuid, "date": date, "size":size,
            "tags": tags}
    # Devolvemos un dict con los datos de la imagen y sus tags
    return response

def register_image_tags(imagenb64: str, min_confidence: str):
    # Generamos un uuid para la imagen
    myuuid = str(uuid.uuid4())
    # Definimos el nombre y el path para la imagen
    filename = f"img_{myuuid}"
    path=os.path.abspath(os.path.join(os.environ["IMAGE_FOLDER"], filename))
    # Obtiene los tags de la imagen
    tags = get_tags_image_minconfidence(imagenb64,filename,min_confidence)
    # Convertimos la imagen a binario y calculamos su tamaño en bytes
    image_bin = base64.b64decode(imagenb64.encode())
    size = len(image_bin)
    # Registramos la imagen y sus tags en la base de datos
    # Obtenemos el json con los datos de la imagen y sus tags
    response= register_image_tags_bd(myuuid, path, tags, 
                                     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), size)
    # Guardamos la imagen en la carpeta de imagene
    models.save_image(image_bin, path)
    # Devolvemos la respuesta
    return response

def get_images_by_date(min_date: str, max_date: str):
    # Obtenemos las imagenes entre las fechas min_date y max_date
    pictures = models.get_images_by_date(min_date, max_date)

    return pictures

def get_images_by_date_tags(min_date: str, max_date: str, tags: List):
    # inicializamos la respuesta
    response=[]
    # Obtenemos las imagenes entre las fechas min_date y max_date
    pictures = models.get_images_by_date(min_date, max_date)
    # Recorremos las imagenes y buscamos las que tienen todas las etiquetas
    for picture in pictures:
        # Si la imagen tiene etiquetas, las buscamos en las etiquetas del usuario
        if len(picture["tags"])>0:
            # Si la imagen tiene todas las etiquetas del usuario, la añadimos a la respues
            tags_encontrados=[tag["tag"] for tag in picture["tags"] if tag['tag'] in tags]
            if len(tags_encontrados)==len(tags):
                response.append(picture)

    return response

def get_image_by_id(id: str):
    # Obtenemos la imagen por su id
    picture = models.get_image_by_id(id)
    # Si picture contiene el path de la imagen
    if "path" in picture:
        # Leemos la imagen de la carpeta de imagenes y eliminamos la key path de la respuesta
        image_str = models.read_image(picture.pop("path", None))
        # Incluimos la imagen en la respuesta en formato base64 y tipo string
        picture["data"]=base64.b64encode(image_str).decode()
    
    return picture

def get_tags_by_date(min_date: str, max_date: str):
    # Inicializamos el diccionario de etiquetas
    tags={}
    # Obtenemos las imagenes y sus tags entre las fechas min_date y max_date
    pictures = models.get_images_by_date(min_date, max_date)
    # Recorremos las imagenes y extraemos sus tags
    for picture in pictures:
        # Si la imagen tiene etiquetas
        if len(picture["tags"])>0:
            # Recorremos las etiquetas y añadimos el tag a la lista de tags
            for tag in picture["tags"]:
                # Si ya tenemos la tag
                if tag['tag'] in tags:
                    #tags[tag['tag']]["n"]+=1# tags[tag['tag']]["n"]+1
                    tags[tag['tag']]["confidences"].append(tag['confidence'])
                else:
                    tags[tag['tag']] = {"confidences":[tag['confidence']]} 

    return tags
from typing import List

import os
import uuid
import base64
import datetime

from . import models
from .appexceptions import ImageKitError, ImaggaError


def get_tags_image_minconfidence(imagenb64: str, filename: str, min_confidence: int):
    """
        Obtiene los tags de una imagen (imagenb64) invocando la API de Imagga y devolviendo los tags con confidence > min_confidence.
        Emplea imagekitio como repositorio temporal de la imagen.
    Args:
        imagenb64 (str): imagen en base 64 en formato str.
        filename (str): nombre de la imagen
        min_confidence (int): confianza minima de los tags a aceptar.

    Returns:
        list: lsta de tags asociados a la imagen con confianza mayor que min_confidence
    """
    try:
        # Upload the image to imagekitio
        upload_info = models.get_image_url(imagenb64,filename)    
    except Exception as error:
        raise ImageKitError(f"Error al subir la imagen a Imagekitio: {error}")
    try:
        # Requests the tags of the image to imagga
        all_tags= models.get_tags_url(upload_info.response_metadata.raw['url'])
        # Define the list of tags with confidence > min_confidence
        tags = [t for t in all_tags if t["confidence"] > min_confidence]
    except Exception as error:
        raise ImaggaError(f"Error al obtener los tags de la imagen de Imagga: {error}")
    
    try:
        # Delete the image from  imagekitio
        models.delete_image_url(upload_info.file_id)
    except Exception as error:
        raise ImageKitError(f"Error al borrar la imagen de Imagekitio: {error}")
    
    # Devuelve los tags de la imagen con confidence > min_confidence
    return tags

def register_image_tags_bd(myuuid: str, path: str,  tags:str, date: str, size: int):
    """
        Registra una imagen y sus tags en la base de datos.
        Devuelve un dict con los datos de la imagen y sus tags.
    
    Args:
        myuuid (str): UUID de la imagen en version 4, 32 caracteres
        path (str): path en local de la imagen
        tags (str): lista de tag-confidence asociados a la imagen
        date (str): fecha de registro de la imagen
        size (int): tamaño de la imagen en bytes

    Returns:
        json: con los campos:
        - `id`: identificador de la imagen
        - `size`: tamaño de la imagen en KB
        - `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
        - `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
            - `tag`: nombre de la tag
            - `confidence`: confianza con la que la etiqueta está asociada a la imagen
        - `data`: imagen como string codificado en base64
    """
    # Insertamos la imagen y sus tags en la base de datos
    models.insert_picture_tags(myuuid, date, path, size, tags)
    # Creamos la respuesta
    response={"id": myuuid, "date": date, "size":size,
            "tags": tags}
    # Devolvemos un dict con los datos de la imagen y sus tags
    return response

def register_image_tags(imagenb64: str, min_confidence: str):
    """
        Registra una imagen y sus tags con confianza superior a min confidence en la base de datos.
        Devuelve un dict con los datos de la imagen y sus tags.
        Emplea los servicios Imagga e Imagekitio como repositorio temporal de la imagen y para obtener todos sus tags.
    
    Args:
        imagenb64 (str): imagen en base 64 en formato str.
        min_confidence (int): confianza minima de los tags a aceptar.

    Returns:
        json: con los campos:
        - `id`: identificador de la imagen
        - `size`: tamaño de la imagen en KB
        - `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
        - `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
            - `tag`: nombre de la tag
            - `confidence`: confianza con la que la etiqueta está asociada a la imagen
    """
    # Generamos un uuid para la imagen
    myuuid = str(uuid.uuid4())
    # Definimos el nombre y el path para la imagen
    filename = f"img_{myuuid}"
    path=os.path.abspath(os.path.join(os.environ["IMAGE_FOLDER"], filename))
    # Comprobamos que existe el directorio de imagenes
    assert os.path.exists(os.environ["IMAGE_FOLDER"]), "El directorio de imagenes no existe. Consulte con su admin"

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
    """
        Devuelve todas las id, atributos y tags registrados en la base de datos de imagenes cuya fecha de creacion este entre
        un valor min_date y otro max date.
    
    Args:
        min_date (str): fecha minima de creacion
        max_date (str): fecha máxima de creacion

    Returns:
        list: cada elmento es un dict con campos:
        id: , 
        date: ,
        size: , 
        tags: tag y confidence
    """
    # Obtenemos las imagenes entre las fechas min_date y max_date
    pictures = models.get_images_by_date(min_date, max_date)

    return pictures

def get_images_by_date_tags(min_date: str, max_date: str, tags: List):
    """
    
        Devuelve todas las id, atributos y tags registrados en la base de datos de imagenes cuya fecha de creacion este entre
        un valor min_date y otro max date y que tiene todas las tags incluidas en el parametro tags.
    Args:
        min_date (str): fecha minima de creacion
        max_date (str): fecha máxima de creacion
        tags (List): lista de tags

    Returns:
        list: cada elmento es un dict con campos:
        id: , 
        date: ,
        size: , 
        tags: tag y confidence
    """
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
    """
        Devuelve la imagen con id id y sus tags.
    
    Returns:
        json: con los campos:
        - `id`: identificador de la imagen
        - `size`: tamaño de la imagen en KB
        - `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
        - `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
            - `tag`: nombre de la tag
            - `confidence`: confianza con la que la etiqueta está asociada a la imagen
        - `data`: imagen como string codificado en base64
    """
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
    """
        Devuelve las tags registradas entre las fechas min_date y max_date
    Args:
        min_date (str): fecha minima de creacion
        max_date (str): fecha máxima de creacion

    Returns:
        list: cada elemento es un dict con los campos:
        - `tag`: nombre de la tag
        - `n_images`: número de imágenes que tienen asociada esta tag
        - `min_confidence`, `max_confidence`, `mean_confidence`: confianza mínima, máxima y media de esta tag para todas las imágenes con las que está asignada.
    """
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
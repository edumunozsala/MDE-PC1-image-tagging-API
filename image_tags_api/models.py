from typing import List

from imagekitio import ImageKit
import requests

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import exc

import os
from .appexceptions import BBDDConexionError, BBDDObjetoError


#
# Funciones de 
#
def delete_image_url(file_id):
    """
    Delete the image from imagekitio.

    Args:
        file_id (str): id de la imagen

    Returns:
        response: respuesta de Imagekitio
    """
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
    """
        Upload la imagen en base 64 imagenb64 a Imagekitio con el nombre filename.
        
    Args:
        imagenb64 (str): imagen en base 64 en formato str.
        filename (str): nombre de la imagen

    Returns:
        json: respuesta del metodo upload de Imagekitio
    """
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

def get_tags_url(image_url: str):
    """
        Devuelve las tags de una imagen (imagen_url) invocando la API de Imagga       
    Args:
        image_url (str): url de la imagen.

    Returns:
        list: lista de tags: cada elemento es un Dict con claves:
            - tag
            -confidence
    """
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

#
# Funciones para el acceso a la base de datos
#
def insert_picture_tags(myuuid: str, date: str, path: str, size: int, tags: List):
    """
        Inserta una imagen en la tabla Pictures y sus tags asociados en la tabla Tags
    Args:
        myuuid (str): id de la imagen
        date (str): fecha de registro
        path (str): path local de la imagen
        size (int): tamaño en bytes de la imagen
        tags (List): lista de tags y su confidence

    Returns:
        obj: engine de la bd
    """
    # Definimos la conexion a la base de datos
    connection_str=f"mysql+pymysql://{os.environ['MYSQL_USERNAME']}:{ os.environ['MYSQL_USER_PASSWORD']}@{os.environ['MYSQL_SERVER']}/{ os.environ['MYSQL_USER_DATABASE']}"
    tags_db=[{"tag": t['tag'], "picture_id": myuuid, "confidence": t['confidence'], "date": date} for t in tags]
    try:
        # Creamos la conexion a la base de datos
        engine = create_engine(connection_str)
        # Ejecutamos las sentencias sql para insertar la imagen y sus tags en la base de datos en una transaccion
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO pictures (id,path,date, size) VALUES (:id, :path, :date, :size)"), {"id": myuuid, "path": path, "date": date, "size": size})
            conn.execute(text("INSERT INTO tags (tag,picture_id,confidence,date) VALUES (:tag, :picture_id, :confidence, :date)"), tags_db)
            conn.commit()
            
        return engine
    except exc.OperationalError as error:
        raise BBDDConexionError(f"Verifique credenciales de acceso a BBDD. Error de conexión: {error}")
    except exc.ProgrammingError as error:
        raise BBDDObjetoError(f"Verifique la existencia de los objetos de BBDD. Error de Objeto de la BBDD: {error}")
    

def set_sql_pictures_by_date(min_date: str, max_date: str):
    """
        Define la sentencia SELECT para extraer las imagenes cuya fecha de registro esté entre min_date y max_date
    Args:
        min_date (str): fecha minima de creacion
        max_date (str): fecha máxima de creacion

    Returns:
        str: sentencia select
    """
    # Definimos la select base
    sql = "SELECT `id`, `date`, `size` FROM `pictures` p"
    params=()
    # Si min_date y max_date son diferentes de vacio, añadimos los filtros a la select base
    if min_date!='' and max_date!='':
        sql = sql + " WHERE p.date>:min_date AND p.date<:max_date"
        params = {"min_date": min_date, "max_date":max_date}
    # Si min_date es diferente de vacio, añadimos el filtro a la select bas
    elif min_date!='':
        sql = sql + " WHERE p.date>:min_date"
        params = {"min_date": min_date}
    # Si max_date es diferente de vacio, añadimos el filtro a la select bas
    elif max_date!='':
        sql = sql + " WHERE p.date<:max_date"
        params = {"max_date":max_date}
        
    sql += " ORDER BY p.date DESC"
    return sql,params

def run_query(sql, params):
    """
        Ejecuta una sentencia select en la base de datos y devuelve el resultado
    Args:
        sql (str): sentencia select a ejecutar
        params (tuple): tuplas con los parametros de la sentencia select

    Returns:
        list: cada elemento es un registro devuelto por la select en forma de dict la clave el nombre de la columna y el valor de esa columna
    """
    try:
        # Definimos la conexion a la base de datos
        connection_str=f"mysql+pymysql://{os.environ['MYSQL_USERNAME']}:{ os.environ['MYSQL_USER_PASSWORD']}@{os.environ['MYSQL_SERVER']}/{ os.environ['MYSQL_USER_DATABASE']}"
        # Creamos la conexion a la base de datos
        engine = create_engine(connection_str)
        # Obtenemos las imagenes de la base de datos
        with engine.connect() as conn:
            # Obtenemos las picture_id de las imagenes que cumplan con los filtros de min y max date
            result = conn.execute(text(sql), params)
                            
        return result.all()
    except exc.OperationalError as error:
        raise BBDDConexionError(f"Verifique credenciales de acceso a BBDD. Error de conexión: {error}")
    except exc.ProgrammingError as error:
        raise BBDDObjetoError(f"Verifique la existencia de los objetos de BBDD. Error de Objeto de la BBDD: {error}")


def get_tags_by_picture_id(picture_id: str):
    """
        Devuelve el listado de tags asociados a una imagen dada su picture_id.
        Si la imagen no tiene tags, devuelve un listado vacio.
        Si la imagen no existe, devuelve un listado vacio.
        
        Devuelve un listado de dict con la clave tag y confidence.
        Ejemplo: [{"tag":"tag1", "confidence":0.8}, {"tag":"tag2", "confidence":0.6}]
    Args:
        picture_id (str): id de la imagen

    Returns:
        list: dict con la clave tag y confidence. 
    """
    # Definimos la select base
    sql = "SELECT `tag`,`confidence` FROM `tags` t WHERE t.picture_id = :id"
    params = {"id": picture_id}
     # Ejecutamos la select para extraer las tags
    result= run_query(sql, params)
    # Si hay tags, obtenemos sus tags y los añadimos a la respuesta
    if len(result)>0:
        result_tags=[{"tag": t, "confidence":c} for t,c in result]
    else:
        result_tags=[]
                
    return result_tags

def get_images_by_date(min_date: str, max_date: str):
    """
        Devuelve el listado de imagenes cuya fecha de registro esté entre min_date y max_date.
        Si la imagen no tiene tags, devuelve un listado vacio.
        Si la imagen no existe, devuelve un listado vacio.
        
        Devuelve un listado de dict con la clave id, date, size y tags.
        Ejemplo: [{"id":"id1", "date":"date1", "size":100, "tags":[{"tag":"tag1", "confidence":0.8}, {"tag":"tag2", "confidence":0.6}]}, {"id":"id2", "date":"date2", "size":200, "tags":[{"tag":"tag1", "confidence":0.8}, {"tag":"tag2", "confidence":0.6}]}]
    Args:
        min_date (str): fecha minima de creacion
        max_date (str): fecha máxima de creacion

    Returns:
        list: dict con la clave id, date, size y tags. 
    """
    # Obtenemos la select
    sql, params = set_sql_pictures_by_date(min_date, max_date)
    # Ejecutamos la select para extraer las imagenes
    result= run_query(sql, params)
    # Si hay imagenes, obtenemos sus tags y los añadimos a la respuesta
    if len(result)>0:
        result_img=[{"id": p_id, "date":p_date,"size": p_size, "tags": get_tags_by_picture_id(p_id)} for p_id,p_date,p_size in result]
    else:
        result_img=[]
                        
    return result_img

def get_image_by_id(picture_id: str):
    """
        Devuelve la imagen dada su picture_id.
        Si la imagen no tiene tags, devuelve un listado vacio.
        Si la imagen no existe, devuelve un dict vacio.
        
        Devuelve un dict con la clave id, date, size y tags.
        Ejemplo: {"id":"id1", "date":"date1", "size":100, "tags":[{"tag":"tag1", "confidence":0.8}, {"tag":"tag2", "confidence":0.6}]}
    Args:
        picture_id (str): id de la imagen

    Returns:
        dict: dict con la clave id, date, size y tags. 
    """
    # Obtenemos la select por id
    sql= "SELECT `id`, `date`, `size`, `path`  FROM `pictures` p WHERE p.id=:p_id"
    params = {"p_id":picture_id}
    
    # Inicializamos la lista de imagenes a vacio
    results=run_query(sql, params)
    # Si hay imagenes, obtenemos sus tags y los añadimos a la respuesta
    if len(results)==1:
        result_img={"id": results[0][0], "date":results[0][1],"size": results[0][2], "path": results[0][3], "tags": get_tags_by_picture_id(results[0][0])}
    else:
        result_img={}

    return result_img

# Funciones para el acceso a disco
def save_image(imagen: bytes, filename: str):
    """
        Guarda una imagen en disco local con el nombre filename
    Args:
        imagen (bytes): imagen en binario
        filename (str): nombre del archivo a generar

    Returns:
        str: filename
    """
    # Guardamos la imagen en la carpeta de imagenes
    with open(filename, 'wb') as f:
        f.write(imagen)
        
    return filename

# Funciones para el acceso a disco
def read_image(filename: str):
    """
        Lee una imagen de disco local con el nombre filename
    Args:
        filename (str): nombre del archivo a leer

    Returns:
        bytes: imagen
    """
    # Guardamos la imagen en la carpeta de imagenes
    with open(filename, "rb") as f:
        # Leemos la imagen en binario
        image_bin = f.read()
        
    return image_bin



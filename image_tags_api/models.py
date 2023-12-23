from typing import List
from sqlalchemy import create_engine
from sqlalchemy import text

import os

# Funciones para el acceso a la base de datos
def insert_picture_tags(myuuid: str, date: str, path: str, size: int, tags: List):
    # Definimos la conexion a la base de datos
    connection_str=f"mysql+pymysql://{os.environ['MYSQL_USERNAME']}:{ os.environ['MYSQL_USER_PASSWORD']}@{os.environ['MYSQL_SERVER']}/{ os.environ['MYSQL_USER_DATABASE']}"
    tags_db=[{"tag": t['tag'], "picture_id": myuuid, "confidence": t['confidence'], "date": date} for t in tags]
    # Creamos la conexion a la base de datos
    engine = create_engine(connection_str)
    # Ejecutamos las sentencias sql para insertar la imagen y sus tags en la base de datos en una transaccion
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO pictures (id,path,date, size) VALUES (:id, :path, :date, :size)"), {"id": myuuid, "path": path, "date": date, "size": size})
        conn.execute(text("INSERT INTO tags (tag,picture_id,confidence,date) VALUES (:tag, :picture_id, :confidence, :date)"), tags_db)
        conn.commit()
        
    return engine

# Funciones para el acceso a disco
def save_image(imagen: bytes, filename: str):
    # Guardamos la imagen en la carpeta de imagenes
    with open(filename, 'wb') as f:
        f.write(imagen)
        
    return filename

def set_sql_pictures_by_date(min_date: str, max_date: str):
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

def get_tags_by_picture_id(picture_id: str):
    # Definimos la select base
    sql = "SELECT `tag`,`confidence` FROM `tags` t WHERE t.picture_id = :id"
    # Definimos la conexion a la base de datos
    connection_str=f"mysql+pymysql://{os.environ['MYSQL_USERNAME']}:{ os.environ['MYSQL_USER_PASSWORD']}@{os.environ['MYSQL_SERVER']}/{ os.environ['MYSQL_USER_DATABASE']}"
    # Creamos la conexion a la base de datos
    engine = create_engine(connection_str)
    # Obtenemos las imagenes de la base de datos
    result_tags=[]
    with engine.connect() as conn:
        result = conn.execute(text(sql),{"id":picture_id})
        for t,c in result:
            result_tags.append({"tag":t,"confidence":c})
                
    return result_tags

def get_images_by_date(min_date: str, max_date: str):
    # Obtenemos la select
    sql, params = set_sql_pictures_by_date(min_date, max_date)
    # Inicializamos la lista de imagenes a vacio
    result_img=[]
    # Definimos la conexion a la base de datos
    connection_str=f"mysql+pymysql://{os.environ['MYSQL_USERNAME']}:{ os.environ['MYSQL_USER_PASSWORD']}@{os.environ['MYSQL_SERVER']}/{ os.environ['MYSQL_USER_DATABASE']}"
    # Creamos la conexion a la base de datos
    engine = create_engine(connection_str)
    # Obtenemos las imagenes de la base de datos
    with engine.connect() as conn:
        # Obtenemos las picture_id de las imagenes que cumplan con los filtros de min y max date
        result = conn.execute(text(sql), params)
        # Si hay imagenes, obtenemos sus tags y los añadimos a la respuesta
        if result.rowcount>0:
            result_img=[{"id": p_id, "date":p_date,"size": p_size, "tags": []} for p_id,p_date,p_size in result]
                        
    return result_img

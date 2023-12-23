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

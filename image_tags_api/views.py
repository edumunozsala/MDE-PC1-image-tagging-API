from flask import Blueprint, request, make_response
import datetime
import os

from . import controller

image_bp = Blueprint('image', __name__, url_prefix='/')

@image_bp.post('/image')
def post_image():
    try:
        # Leemos el query parameter min_confidence
        min_confidence= int(request.args.get("min_confidence", 80))
    except ValueError:
        return make_response({"description": "min_confidence debe ser un entero"}, 400)
    
    # Leemos la imagen del json del body
    if not request.is_json:
        return make_response("Body debe ser un objeto json", 400)
    
    try:
        imagenb64 = request.json['data']
    except ValueError:
        return make_response({"description": "data debe ser una imagen en base64"}, 400)

    # Registramos la imagen y sus tags en la base de datos
    # Guardamos la imagen en la carpeta de imagenes y 
    response= controller.register_image_tags(imagenb64, min_confidence)
    # Completamos la respuesta
    response["data"]= imagenb64

    return response

@image_bp.get('/images')
def get_images():
    try:
        # Leemos el query parameter min_date
        if 'min_date' in request.args:
            min_date= datetime.datetime.strptime(request.args.get("min_date"), "%Y-%m-%d %H:%M:%S")
        else:
            min_date=""
    except ValueError:
        return make_response({"description": "min_date debe ser una fecha en formato %Y-%m-%d %H:%M:%S"}, 400)

    try:
        # Leemos el query parameter max_date
        if 'max_date' in request.args:
            max_date= datetime.datetime.strptime(request.args.get("max_date"), "%Y-%m-%d %H:%M:%S")
        else:
            max_date=""
            
    except ValueError:
        return make_response({"description": "max_date debe ser una fecha en formato %Y-%m-%d %H:%M:%S"}, 400)

    try:
        # Leemos el query parameter tags
        if 'tags' in request.args:
            tags= request.args.get("tags").split(",")
            # Eliminamos los tags duplicados
            tags = list(dict.fromkeys(tags))
        else:
            tags=[]
    except ValueError:
        return make_response({"description": "tags debe ser una lista de tags separados por comas"}, 400)

    # Obtenemos las imagenes con las tags y fecha de creacion entre min_date y max_date
    if len(tags)>0:
        response= controller.get_images_by_date_tags(min_date, max_date, tags)
    else:
        response= controller.get_images_by_date(min_date, max_date)

    return response


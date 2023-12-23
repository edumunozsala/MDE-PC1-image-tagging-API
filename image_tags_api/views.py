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

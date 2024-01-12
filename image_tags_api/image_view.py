from flask import Blueprint, request, make_response
import datetime
import logging
from uuid import UUID

from image_tags_api import controller
from image_tags_api.appexceptions import ImageKitError, ImaggaError, BBDDConexionError, BBDDObjetoError

image_bp = Blueprint('image', __name__, url_prefix='/')

@image_bp.post('/image')
def post_image():
    """
        Implementacion del metodo POST /image. Registramos la imagen recibida en la tabla de Pictures y los tags asociadas a la misma
        cuya confidence sea superior a min_confidence.
        La imagen se recibe en el body del request como un json con el campo data.
        La respuesta incluye la imagen en base64 y los tags asociados.
    Query parameters:
        min_confidence: valor de confianza minimo para aceptar la tag de una imagen.
    Returns:
        Un json con los siguientes campos:
            - `id`: identificador de la imagen
            - `size`: tamaño de la imagen en KB
            - `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
            - `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
                - `tag`: nombre de la tag
                - `confidence`: confianza con la que la etiqueta está asociada a la imagen
            - `data`: imagen como string codificado en base64
    """
    try:
        # Leemos el query parameter min_confidence
        min_confidence= int(request.args.get("min_confidence", 80))
        # Validamos que min_confidence este entre 0 y 100
        if min_confidence < 0 or min_confidence > 100:
            return make_response({"description": "min_confidence debe estar entre 0 y 100"}, 400)
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
    try:
        response= controller.register_image_tags(imagenb64, min_confidence)
        print("Imagen insertada")
        # Completamos la respuesta
        logging.info("Imagen insertada en BBDD")
        response["data"]= imagenb64
        logging.info("Imagen en base 64 incluida en la respuesta")
    except AssertionError as error:
        logging.critical(error)
        return make_response({"description": str(error)}, 501)
    except ImageKitError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)
    except ImaggaError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)
    except BBDDConexionError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)
    except BBDDObjetoError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)
        
    return response

@image_bp.get('/images')
def get_images():
    """
        Implementacion del metodo GET /images. Obtenemos todas las imagenes registradas en la base de datos cuya fecha de creacion este entre
        un valor min_date y otro max date y además si se proporciona el parametro tags todos los tags de la imagen deben estar entre los proporcionados.
        La respuesta incluye la imagen en base64 y los tags asociados.
    Query parameters:
        min_date: fecha minima de creacion de la imagen.
        max_date: fecha maxima de creacion de la imagen.
        tags: lista de tags separados por comas.
    Returns:
        Un json con los siguientes campos:
            - `id`: identificador de la imagen
            - `size`: tamaño de la imagen en KB
            - `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
            - `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
                - `tag`: nombre de la tag
                - `confidence`: confianza con la que la etiqueta está asociada a la imagen
    """
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

    try:
        # Obtenemos las imagenes con las tags y fecha de creacion entre min_date y max_date
        if len(tags)>0:
            response= controller.get_images_by_date_tags(min_date, max_date, tags)
        else:
            response= controller.get_images_by_date(min_date, max_date)
            
        logging.info("Imagenes obtenidas de BBDD")
    except BBDDConexionError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)
    except BBDDObjetoError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)

    return response

@image_bp.get('/image/<picture_id>')
def get_image(picture_id):
    """
    Implementacion del metodo GET /image. Obtenemos la imagen con el id proporcionado.
    Path parameter:
        id: identificador de la imagen.
    Returns:
        Un json con los siguientes campos:
            - `id`: identificador de la imagen
            - `size`: tamaño de la imagen en KB
            - `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
            - `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
                - `tag`: nombre de la tag
                - `confidence`: confianza con la que la etiqueta está asociada a la imagen
            - `data`: imagen como string codificado en base64
    """
    
    try:
        _ = UUID(picture_id, version=4)
    except ValueError:
        return make_response({"description": "el path parametro id debe ser una cadena uuid valida"}, 400)

    try:
        #Obtenemos la imagen y sus tags de la base de datos
        response= controller.get_image_by_id(picture_id)
        logging.info("Imagen obtenidas de BBDD")
    except BBDDConexionError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)
    except BBDDObjetoError as error:
        logging.error(error)
        return make_response({"description": str(error)}, 501)

    return response

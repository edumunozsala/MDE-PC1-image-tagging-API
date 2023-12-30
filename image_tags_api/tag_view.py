from flask import Blueprint, request, make_response
import datetime

from image_tags_api.controller import get_tags_by_date

tag_bp = Blueprint('tag', __name__, url_prefix='/')

@tag_bp.get('/tags')
def get_tags():
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

    # Inicializamos la respuesta
    response=[]
    # Obtenemos las tags de las imagenes entre min_date y max_date
    tags= get_tags_by_date(min_date, max_date)
    # Recorremos los tags y calculamos el minimo, maximo y promedio de confianza
    _ = [response.append({"tag":tag, "n": len(tags[tag]['confidences']), "min_confidence":min(tags[tag]['confidences']), 
                      "max_confidence":max(tags[tag]['confidences']),
                     "mean_confidence":sum(tags[tag]['confidences'])/len(tags[tag]['confidences'])}) for tag in tags.keys()]

    return response

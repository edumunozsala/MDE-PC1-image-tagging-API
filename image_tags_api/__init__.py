from flask import Flask
import os
import json

def create_app():
    app = Flask(__name__)
    # Cargamos las credenciales
    credentials="credentials.json"
    with open(credentials, 'r') as f:
            data = json.load(f)
    # Definimos las credenciales como variables de entorno
    os.environ["IMAGGAN_API_SECRET"] = data['imaggan']['api_secret']
    os.environ["IMAGGAN_API_KEY"] = data['imaggan']['api_key']
    os.environ["IMAGEKIT_URL_ENDPOINT"] = data['imagekitio']['url_endpoint']
    os.environ["IMAGEKIT_PUBLIC_KEY"] = data['imagekitio']['public_key']
    os.environ["IMAGEKIT_PRIVATE_KEY"] = data['imagekitio']['private_key']
    
    #os.environ["IMAGE_FOLDER"]="images"
    #os.environ["MYSQL_USERNAME"]="mbit"
    #os.environ["MYSQL_USER_PASSWORD"]="mbit"
    #os.environ["MYSQL_USER_DATABASE"]="Pictures"

    # Import views
    from . import views
    app.register_blueprint(views.image_bp)

    return app
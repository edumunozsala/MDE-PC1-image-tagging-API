# Creación de una Rest API con Flask para extraer etiquetas de images
# Building a Rest API Flask to extract tags from images

 **Proyecto de Consolidacion 1 del Master en Data Engineering y Big Data por la MBIT School**

 Construir una API que permita subir imagenes y extraer de ella los tags identificados en la imagén, registrará la imagen y sus tags en una BBDD MySQL para su posterior extracción y consulta. Proporcionará metodos para consultar y extraer imagenes previamente almacenadas junto con sus tags en base a diferentes filtros. A su vez se podrán consultar tags registrados en el sistema.

 La solución se compone de dos contendores docker:
 - **api-server**: contenedor que publica la API Flask y recibe las invocaciones del usuario.
 - **mysql-server**: contenedor con una instancia MySQL donde el api-server almacena la información de las imagenes que recibe.

# Instalación
Para poner en marcha la API debemos seguir los siguientes pasos:

1. Clonar el repositorio git a una carpeta local

`git clone https://github.com/edumunozsala/MDE-PC1-image-tagging-API.git`

2. Ir al directorio creado:

`cd MDE-PC1-image-tagging-API`

3. Crear el archivo `credentials.json` que contiene las API Keys y secrets para acceder a los servicios `ImageKitio` e `Imagga`. Si no dispones de cuentas en dichos servicios puedes crearlas facilmente en sus correspondientes sites [Imagekit.io](https://imagekit.io/registration/) y [Imagga](https://imagga.com/auth/signup). 

El archivo credentials debe ser un JSON con los siguientes campos:
```py
{
    "imagekitio":{
        "public_key":"<your_public_key>",
        "private_key": "<your_private_key>",
        "url_endpoint": "<your_url>"
    },
    "imaggan":{
        "api_key": "<your_key>",
        "api_secret": "<your_secret>"
    }
}
```

4. Asegurarse la existencia de una carpeta `Images` y de un archivo `.env` con los datos y credenciales de acceso a la BBDD. 

Al clonar el repositorio se crean ambos objetos pero si se desean modificar los contenedores y dichos valores debemos actualizar el fichero `.env`.

5. Levantar la estructura de contenedores según la definición del fichero `docker-compose.yml`. 

`docker compose up`

Esta operación puede tardar 2-3 minutos para la descarga y/o la creación de las imágenes docker y su puesta en marcha.


# Métodos disponibles

#### POST image

`POST http://localhost:80/image`

Python:
```py 
# Convert the image to base64 format
with open(file, "rb") as f:
    b64str_image = base64.b64encode(f.read()).decode()

response = requests.post(f'http://localhost:80/image?min_confidence=60', json={"data": b64str_image})
```

Este endpoint espera como input un body que será un `json` con un campo `data` que es la imagen codificada en base64. También se especificará un _query parameter_ (**opcional**) llamado `min_confidence`, que nos servirá para exigir el valor minimo de certeza a las etiquetas generadas para la imagen. Su valor por defecto es `80`. Una vez recibida utilizará un [servicio cloud mediante una API](https://imagga.com/) para extraer tags a partir de esta imagen. Esta API requiere que le pasemos la imagen como una URL pública, por lo que usaremos en primer lugar otro [servicio cloud mediante una API](https://docs.imagekit.io/) para subir temporalmente esta imagen a la nube.

La **respuesta** de este endpoint debe ser un **json** con los siguientes campos:

- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
    - `tag`: nombre de la tag
    - `confidence`: confianza con la que la etiqueta está asociada a la imagen
- `data`: imagen como string codificado en base64

**NOTA**: será necesario en primer lugar crearse una cuenta en `https://docs.imagekit.io/` y en `https://imagga.com/`, y utilizar credenciales correctamente:

- `imagekit.io`: ir a dashboard, crearnos una cuenta, y al loguearnos ir a **Developer options**. Ahí veremos nuestro `URL-endpoint`, y unas credenciales por defecto ya creadas (`Public Key` y `Private Key`).
- `imagga.com`: Crearnos una cuenta y al loguearnos ir a Dashboard. Ahí veremos nuestra `API Key`, `API Secret`. 

#### GET images
`GET http://localhost:80/images`

Python:
```py 
#Definimos las query parameters
max_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
min_date = "2024-01-11 08:00:00"
tags1=["car","motor vehicle"]

response = requests.get(f'http://localhost:80/images?min_date={min_date}&max_date={max_date}&tags={",".join(tags1)}')
```

Este endpoint sirve para obtener una lista de imágenes filtradas por fecha y tags. Se proporcionará mediante _query parameters_ la siguiente información:

- `min_date`/`max_date`: opcionalmente se puede indicar una fecha mínima y máxima, en formato `YYYY-MM-DD HH:MM:SS`, para obtener imágenes cuya fecha de registro esté entre ambos valores. Si no se proporciona `min_date` no se filtrará ninguna fecha inferiormente. Si no se proporciona `max_date` no se filtrará ninguna fecha superiormente.

- `tags`: optionalmente se puede indicar una lista de tags. Las imágenes devueltas serán aquellas que incluyan **todas** las tags indicadas. El formato de este campo será un string donde las tags estarán separadas por comas, por ejemplo `"tag1,tag2,tag3"`. Si no se proporciona el parametro no se aplicará ningún filtro.

La **respuesta** del endpoint será una lista de objetos imagen con los siguientes campos:

- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
    - `tag`: nombre de la tag
    - `confidence`: confianza con la que la etiqueta está asociada a la imagen

#### GET image
`GET http://localhost:80/image/<picture_id>`

Python:
```py 
# Una uuid de una imagen
picture_id='7e0a214c-8f7e-44c3-bdc6-3ffa4d0cb777'

response1 = requests.get(f'http://localhost:80/image/{picture_id}')
```

Este endpoint sirve para descargarse una imágen, sus propiedades y sus tags. Se proporcionará mediante _path parameter_ el id de la imagen y la **respuesta** será un json con los siguientes campos:

- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
    - `tag`: nombre de la tag
    - `confidence`: confianza con la que la etiqueta está asociada a la imagen
- `data`: imagen como string codificado en base64

#### GET tags
`GET http://localhost:80/tags`

```py 
#Definimos las query parameters
max_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
min_date = "2024-01-11 08:00:00"

response = requests.get(f'http://localhost:80/tags?min_date={min_date}&max_date={max_date}')
```

Este endpoint sirve para obtener la lista de tags (cualquier tag asignada a una imagen registrada) filtradas por fecha. Se proporcionará mediante _query parameters_ la siguiente información:

- `min_date`/`max_date`: opcionalmente se puede indicar una fecha mínima y máxima, en formato `YYYY-MM-DD HH:MM:SS`, para obtener imágenes cuya fecha de registro esté entre ambos valores. Si no se proporciona `min_date` no se filtrará ningúna fecha inferiormente. Si no se proporciona `max_date` no se filtrará ningúna fecha superiormente.

El endpoint devolvera una respuesta que será una lista de objetos imagen con los siguientes campos:

- `tag`: nombre de la etiqueta
- `n_images`: número de imágenes que tienen asociada esta tag
- `min_confidence`, `max_confidence`, `mean_confidence`: confianza mínima, máxima y media de esta tag para todas las imágenes con las que está asignada.


# License

Copyright 2023 Eduardo Muñoz

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

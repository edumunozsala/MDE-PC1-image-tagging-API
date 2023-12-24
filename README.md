# Creación de una Rest API con Flask para extraer etiquetas de images
# Building a Rest API Flask to extract tags from images

 Proyecto de Consolidacion 1 del MAster en Data Engineering y Big Data por la MBIT School

#### This repository is still in progress.

# Content

# Metodos

#### POST image

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

Este endpoint sirve para obtener una lista de imágenes filtradas por fecha y tags. Se proporcionará mediante _query parameters_ la siguiente información:

- `min_date`/`max_date`: opcionalmente se puede indicar una fecha mínima y máxima, en formato `YYYY-MM-DD HH:MM:SS`, para obtener imágenes cuya fecha de registro esté entre ambos valores. Si no se proporciona `min_date` no se filtrará ninguna fecha inferiormente. Si no se proporciona `max_date` no se filtrará ninguna fecha superiormente.

- `tags`: optionalmente se puede indicar una lista de tags. Las imágenes devueltas serán aquellas que incluyan **todas** las tags indicadas. El formato de este campo será un string donde las tags estarán separadas por comas, por ejemplo `"tag1,tag2,tag3"`. Si no se proporciona el parametro no se aplicará ningún filtro. **POR REVISAR: Si se proporciona un string vacio, se aplicará el filtro y no devolvera ninguna imagen**.

La **respuesta** del endpoint será una lista de objetos imagen con los siguientes campos:

- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
    - `tag`: nombre de la tag
    - `confidence`: confianza con la que la etiqueta está asociada a la imagen

#### GET image

Este endpoint sirve para descargarse una imágen, sus propiedades y sus tags. Se proporcionará mediante _path parameter_ el id de la imagen y la **respuesta** será un json con los siguientes campos:

- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
    - `tag`: nombre de la tag
    - `confidence`: confianza con la que la etiqueta está asociada a la imagen
- `data`: imagen como string codificado en base64

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

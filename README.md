Este bot permite recopilar información de apis y otras fuentes públicas,
aplicar transformaciones a esos datos y publicarlas en twitter mediante
el uso de la API de inteligencia artificial OpenAI de ChatGPT.

Por el momento, se usa el modelo ChatGPT 3.5 para la generación de texto.

Los dos bots disponibles actualmente son:

* **bot_nba**: Recopila información sobre los últimos partidos de la NBA y publica un resumen en twitter
* **bot_kl**: Genera comentarios sobre los partidos y noticias de la kings league

# Uso

## Prompts
Los archivos [nba_prompts.py](blob/kings-league/src/script/nba_prompts.py) y [kl_prompts.py](/blob/kings-league/src/script/kl_prompts.py) controlan los prompts que se se pueden usar para interactuar con ChatGPT para generar los tweets. El formato es el siguiente: son listas de diccionarios en Python que contienen 2 claves:

* *text*: el texto que se incluirá al principio de cada prompt antes de enviarse a ChatGPT
* *weight*: el peso que tendra en comparación con los otros prompts. A mayor peso, más probable es que se elija ese prompt.

El prompt se elige de manera aleatoria entre los posibles.

## Configuración

Los bots requiren crear un archive de entorno (.env) en el directorio raíz del proyecto con las claves y secretos necesarias de OpenAI, Twitter (y opcionalmente, Discord):

* **OPENAI_API_KEY**: la clave de API de OpenAI https://platform.openai.com/account/api-keys
* **TWITTER_API_KEY** y **TWITTER_API_KEY_SECRET**: la clave y secreto de aplicación de Twitter. https://developer.twitter.com/en/portal/dashboard Es necesario configurar la aplicación como *"Read and write and Direct message"* en App permissions
* **TWITTER_ACCESS_TOKEN** y **TWITTER_ACCESS_TOKEN_SECRET** : el token y token secreto de consumidor de Twitter.
* **DISCORD_KEY** (opcional): Para la integración con discord (en pruebas)

En el archivo [.env.example](blob/kings-league/.env.example) se puede ver un ejemplo vacío de las claves necesarias. Renómbrelo a .env y rellenelo para usar el bot (pero IMPORTANTE: no comparta con nadie ni streamees en directo mostrando las claves o de lo contrario la gente podría usar ChatGPT con tu cuenta, gastándote la tarjeta de crédito o escribir en tu cuenta de Twitter!)

## Ejecución

*TODO*

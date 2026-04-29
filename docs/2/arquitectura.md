# Arquitectura de SVAIA

En la práctica 4 SVAIA era una sola app Flask que lo hacía todo: pintaba
plantillas, hablaba con la base de datos y resolvía el chat. Aquí eso se
parte en tres piezas que corren en puertos distintos y se hablan por HTTP.

## Qué hace cada componente

### Web (`src/2/web`, puerto 5201)
Es lo que ve el usuario. Flask sirviendo plantillas Jinja2 y estáticos. Lo
único que guarda es la sesión: el token JWT que recibe al hacer login y los
datos básicos del usuario (username, rol). No toca MariaDB en ningún sitio.
Cuando necesita persistir algo se lo pide a la API pasando el token en la
cabecera.

El cliente HTTP (`services/api_client.py`) usa `requests` para hablar con
la API desde el servidor. El chat, en cambio, lo llama el navegador
directamente.

### API (`src/2/api`, puerto 5202)
La única que tiene acceso a MariaDB. Expone una API RESTful con
Flask-RESTful y emite los JWT con Flask-Praetorian. Endpoints:

- `POST /api/auth/login` — valida credenciales y devuelve token.
- `GET/POST /api/mensajes` — historial del usuario autenticado. Si el rol
  es `admin` se puede filtrar por `owner_id`.
- `GET/DELETE /api/mensajes/<id>` — consulta y borrado con chequeo de
  propiedad; un usuario normal no puede tocar mensajes ajenos.
- `GET /api/users` — solo admin.

### Chat (`src/2/chat`, puerto 5203)
API independiente para el chat. Recibe el mensaje, valida el JWT contra la
misma tabla `users` y responde con una frase de `AnimalFactsService`. Al
llamarse desde el navegador (origen distinto), expone cabeceras CORS con la
lista blanca que le pasa `CORS_ORIGINS`.

## Cómo se hablan

```
Navegador ──HTML/JS──▶ Web (5201) ──requests + JWT──▶ API (5202) ──▶ MariaDB
    │                                                                      
    └────────── fetch + Authorization: Bearer <token> ──▶ Chat (5203) ─────┘
```

El flujo típico de una sesión autenticada:

1. El usuario manda usuario y contraseña a `/login` de la web.
2. La web reenvía eso a la API. La API valida, firma un JWT y lo
   devuelve junto al usuario.
3. La web guarda `access_token` y `user` en la sesión Flask y redirige al
   panel.
4. Al abrir el chat, la plantilla inyecta el token en `window.SVAIA_TOKEN`.
5. Cuando el usuario escribe, `chat.js` hace `fetch` directo al chat en
   `:5203` con `Authorization: Bearer <token>`. Aquí actúa CORS.
6. El chat valida el token y responde con la frase.
7. Al recibir la respuesta, el mismo `chat.js` llama a `/api/mensajes` de
   la web (proxy) para persistir el par mensaje/respuesta en MariaDB a
   través de la API.

## Por qué está separado así

- **La web no ve la base de datos.** Es el límite más importante de la
  práctica. Si algo necesita SQL, va a la API.
- **Sesión y JWT no son lo mismo.** La sesión Flask existe para que el
  navegador sepa si la UI es pública o autenticada. El JWT es lo que
  aceptan los microservicios como prueba de identidad. Los dos son
  necesarios y cumplen papeles distintos.
- **CORS solo en el chat.** La web y la API viven en el mismo origen
  lógico (el navegador habla con la web, la web habla con la API en el
  servidor). El chat es el único al que el JS del navegador llega
  directamente en otro puerto, así que es el único que necesita CORS.
- **URLs por entorno.** Nada hardcodeado: `API_BASE_URL`, `CHAT_BASE_URL`,
  `DB_*`, `SECRET_KEY` y `CORS_ORIGINS` salen todos de variables de
  entorno. Eso hace que el mismo código funcione en local y en
  PythonAnywhere sin tocar nada.

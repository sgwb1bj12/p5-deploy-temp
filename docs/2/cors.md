# CORS en el microservicio de chat

## Por qué hace falta

La web sirve sus páginas en `http://127.0.0.1:5201`. Cuando el navegador
carga `chat.html` y ejecuta `chat.js`, ese script hace un `fetch` a
`http://127.0.0.1:5203/api/chat`. Son dos orígenes distintos (cambia el
puerto), así que el navegador aplica la Same-Origin Policy: si el servidor
de `:5203` no responde con las cabeceras CORS adecuadas, el `fetch` falla
en el propio navegador antes de que el JS vea nada.

Esto no se puede "resolver desde el cliente". CORS es una política que
tiene que permitir el servidor del recurso. La API de datos no necesita
CORS porque el navegador nunca la llama directamente: siempre va a través
de la web.

## Cómo está configurado

En `src/2/chat/app.py`:

```python
cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5201,http://127.0.0.1:5201",
).split(",")

CORS(
    app,
    resources={r"/api/*": {"origins": cors_origins}},
    allow_headers=["Authorization", "Content-Type"],
)
```

Qué hace cada parte:

- `resources={r"/api/*": ...}`: solo aplica a rutas bajo `/api/`.
- `origins=cors_origins`: lista blanca de orígenes permitidos. Por defecto
  los dos puertos locales de la web. En PythonAnywhere se sobrescribe con
  la URL pública real.
- `allow_headers=["Authorization", "Content-Type"]`: el chat necesita
  recibir `Authorization: Bearer <token>`, y ese header no está en la
  lista CORS por defecto. Sin añadirlo el preflight rebotaría.

## Flujo del preflight

Como la petición lleva `Authorization` y `Content-Type: application/json`,
no es simple. El navegador manda antes un `OPTIONS`:

```
OPTIONS /api/chat HTTP/1.1
Origin: http://127.0.0.1:5201
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization, content-type
```

Y Flask-CORS responde:

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://127.0.0.1:5201
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
```

Solo cuando el preflight pasa, el navegador manda el `POST` real.

## Qué probar para verificarlo

Una petición desde `curl` o Postman no demuestra que CORS funcione, porque
CORS lo aplica el navegador, no el servidor. Hay que mirar tres cosas:

1. En DevTools → Network, la petición `OPTIONS /api/chat` devuelve 200
   con las cabeceras `Access-Control-Allow-*`.
2. El `POST /api/chat` posterior aparece con status 200 y respuesta JSON.
3. Si cambio `CORS_ORIGINS` a un origen distinto (ej. solo
   `http://example.com`) y recargo, el `fetch` desde la web falla con un
   error "CORS policy" en consola, aunque el servidor siga devolviendo
   200. Eso prueba que el bloqueo lo hace el navegador.

## En producción

Al desplegar en PythonAnywhere la web queda en una URL como
`https://sgwb26.pythonanywhere.com` y el chat en otra distinta. Hay que
actualizar `CORS_ORIGINS` en el chat para que incluya el origen público
exacto de la web. Si no coincide el esquema (http vs https) o falta la
URL pública, el chat desplegado dejará de funcionar desde el navegador.

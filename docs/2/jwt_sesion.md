# Sesión Flask, JWT y autorización

En SVAIA conviven dos mecanismos de autenticación que cumplen funciones
distintas. No es que uno reemplace al otro: cada uno resuelve un problema
diferente y los dos son necesarios.

## Sesión Flask

Vive en la web (`src/2/web`). Sirve para que el navegador sepa si el
usuario está o no autenticado al pintar cada página. Cuando el login va
bien, en `auth_controller.py` se guardan dos cosas:

```python
session["access_token"] = data["access_token"]
session["user"] = data["user"]  # id, username, role
```

Con eso la Web puede:

- Mostrar "Iniciar sesión" o "Cerrar sesión" en la barra.
- Restringir las rutas `/panel` y `/chat` a usuarios logueados.
- Adjuntar el JWT a las peticiones que hace la web contra la API por el
  servidor (`services/api_client.py` con `requests`).

La sesión no valida nada en los microservicios. Es solo estado de UI.

## JWT

Lo emite la API con Flask-Praetorian en `POST /api/auth/login`. Dentro del
token viaja el `id` del usuario y el rol. La web lo guarda en sesión y lo
reenvía en cada petición protegida con:

```
Authorization: Bearer <token>
```

Dos sitios consumen el token:

1. **La web desde el servidor**, cuando hace `requests.get/post` contra la
   API para listar o crear mensajes.
2. **El navegador directamente**, cuando `chat.js` hace `fetch` al chat en
   `:5203`. El token se inyecta en la plantilla (`window.SVAIA_TOKEN`) y
   se añade al header del `fetch`.

La API y el chat ambos llaman a `guard.init_app(app, User)`, así que los
dos validan el token con la misma clave y el mismo modelo de usuario.

## Qué endpoints están protegidos

En la API (`controllers/api_controllers.py`):

| Endpoint                       | Decorador                          |
|--------------------------------|------------------------------------|
| `POST /api/auth/login`         | público                            |
| `GET/POST /api/mensajes`       | `@flask_praetorian.auth_required`  |
| `GET/DELETE /api/mensajes/<id>`| `@flask_praetorian.auth_required`  |
| `GET /api/users`               | `@flask_praetorian.roles_required("admin")` |

En el chat (`controllers/chat_controller.py`):

| Endpoint         | Decorador                          |
|------------------|------------------------------------|
| `POST /api/chat` | `@flask_praetorian.auth_required`  |

## Autorización por rol y por propiedad

`auth_required` solo comprueba que el token es válido. La autorización
real va aparte:

- `GET /api/mensajes`: si el usuario no es admin, la query se filtra por
  `user_id=current.id`. Un usuario normal nunca ve mensajes ajenos aunque
  su token sea válido.
- `GET/DELETE /api/mensajes/<id>`: antes de responder se comprueba
  `current.is_admin or mensaje.user_id == current.id`. Si no pasa, devuelve
  403.
- `GET /api/users`: `roles_required("admin")` bloquea a todo el que no sea
  admin con 401/403 sin entrar al handler.

Esa separación es intencional. Autenticación es "este token es tuyo".
Autorización es "aunque lo seas, este recurso no es para ti".

## Qué pasa cuando el token falla

Flask-Praetorian responde automáticamente:

- Token ausente → 401 `"Missing JWT"`.
- Token expirado → 401 `"Token has expired"`.
- Token manipulado → 401 `"Invalid token"`.
- Usuario sin el rol requerido → 403.

En el frontend, `chat.js` distingue el 401 del resto de errores y pinta
"Error de autenticación: token ausente o inválido" en el chat.
